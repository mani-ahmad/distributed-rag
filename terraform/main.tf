
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}


resource "aws_security_group" "rds_sg" {
  name        = "rds-security-group"
  description = "Allow Postgres access"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "PostgreSQL from anywhere (or replace with your IP)"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rds-security-group"
  }
}

resource "aws_security_group" "ecs_backend_sg" {
  name        = "ecs-backend-security-group"
  description = "Allow HTTP access to ECS containers"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP traffic to ALB"
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] #curr allowing public acces
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ecs-backend-security-group"
  }
}


module "rds" {
  source              = "./modules/rds"
  db_name             = var.db_name
  db_password         = var.db_password
  security_group_ids  = [aws_security_group.rds_sg.id]
  subnet_ids          = data.aws_subnets.default.ids
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "14.13"
  instance_class       = "db.t3.micro"
}

//s3
module "s3_file_upload_bucket" {
  source      = "./modules/s3"
  bucket_name = ""
}

module "s3_vector_bucket" {
  source      = "./modules/s3"
  bucket_name = ""
}

//sagemaker
module "sagemaker" {
  source     = "./modules/sagemaker"
  role_name  = "drag-sagemaker-execution-role"
  bucket_arn = module.s3_vector_bucket.bucket_arn
  alert_email = ""
}



module "ecr" {
  source     = "./modules/ecr"
  repo_name  = "flask-backend"
}

//ecs
module "ecs_backend" {
  source             = "./modules/ecs"
  app_name           = "flask-backend"
  container_image    = var.ecr_image_url  
  container_port     = 8000
  vpc_id             = data.aws_vpc.default.id
  subnet_ids         = data.aws_subnets.default.ids
  security_group_ids = [aws_security_group.ecs_backend_sg.id]
  region         = var.aws_region
  db_url                  = local.db_url
  s3_file_upload_bucket   = module.s3_file_upload_bucket.bucket_name
  s3_vector_bucket        = module.s3_vector_bucket.bucket_name
  sagemaker_role_arn      = module.sagemaker.role_arn
  ecr_repository_url      = module.ecr.repository_url

  s3_file_upload_bucket_arn   = module.s3_file_upload_bucket.bucket_arn
  s3_vector_bucket_arn        = module.s3_vector_bucket.bucket_arn
}



module "s3_frontend" {
  source             = "./modules/s3_frontend"
  bucket_name        = "drag-frontend-hosting"
  frontend_build_dir = "./deploy_dist"
}



//constructing db url 
locals {
  db_url = "postgresql://${var.db_username}:${var.db_password}@${module.rds.db_endpoint}/${var.db_name}"
}


//cognito

module "cognito" {
  source         = "./modules/cognito"
  user_pool_name = "drag-auth-pool"
  app_client_name = "drag-app-client"
  # callback_urls  = ["http://localhost:8080/"]
  # logout_urls    = ["http://localhost:8080/"]
  region         = var.aws_region
}


module "bedrock" {
  source = "./modules/bedrock"
  region = var.aws_region
}

#ouputs stored in a file
resource "local_file" "env_file" {
  content = <<EOT
# AWS
AWS_REGION=${var.aws_region}
DB_URL=${local.db_url}
S3_BUCKET_NAME_FILE_UPLOAD=${module.s3_file_upload_bucket.bucket_name}
S3_BUCKET_VECTOR=${module.s3_vector_bucket.bucket_name}
SAGEMAKER_ROLE=${module.sagemaker.role_arn}
ECR_REPOSITORY_URL=${module.ecr.repository_url}
BACKEND_URL=http://${module.ecs_backend.alb_dns_name}
FRONTEND_URL=http://${module.s3_frontend.website_endpoint}

# Cognito
COGNITO_USER_POOL_ID=${module.cognito.user_pool_id}
COGNITO_USER_POOL_CLIENT_ID=${module.cognito.user_pool_client_id}
COGNITO_USER_POOL_DOMAIN=${module.cognito.user_pool_domain}

BEDROCK_ROLE_ARN=${module.bedrock.bedrock_inference_role_arn}



EOT

  filename = "${path.module}/outputs.env"
}






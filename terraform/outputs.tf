
//Database, we are using rds
output "db_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.db_endpoint
}

output "db_instance_identifier" {
  description = "RDS instance identifier"
  value       = module.rds.db_instance_identifier
}

//Bucket for file uploading
output "S3_BUCKET_NAME_FILE_UPLOAD" {
  description = "S3 bucket name for file uploads"
  value       = module.s3_file_upload_bucket.bucket_name
}

output "S3_BUCKET_VECTOR" {
  description = "S3 bucket name for vector storage"
  value       = module.s3_vector_bucket.bucket_name
}

output "SAGEMAKER_ROLE" {
  description = "SageMaker execution role ARN"
  value       = module.sagemaker.role_arn
}

output "backend_url" {
  description = "Public HTTP endpoint of the backend ALB"
  value       = "http://${module.ecs_backend.alb_dns_name}"
}



output "user_pool_id" {
  value = module.cognito.user_pool_id
}

output "user_pool_client_id" {
  value = module.cognito.user_pool_client_id
}

output "user_pool_domain" {
  value = module.cognito.user_pool_domain
}



output "bedrock_model_id" {
  description = "ID of the Bedrock model being used"
  value       = "mistral.mistral-small-2402-v1:0"
}

output "bedrock_region" {
  description = "AWS region where Bedrock is configured"
  value       = var.aws_region
}



output "ecr_repository_url" {
  description = "URL of the ECR repository for the backend"
  value       = module.ecr.repository_url
}

# output "ecr_repository_arn" {
#   description = "ARN of the ECR repository for the backend"
#   value       = module.ecr.repository_arn
# }

output "website_endpoint" {
  value = module.s3_frontend.website_endpoint
}
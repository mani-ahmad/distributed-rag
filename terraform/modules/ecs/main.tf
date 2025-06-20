resource "aws_ecs_cluster" "this" {
  name = "${var.app_name}-cluster"
}

# Execution role (used by ECS to pull image, write logs)
resource "aws_iam_role" "task_execution_role" {
  name = "${var.app_name}-task-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "execution_role_policy" {
  role       = aws_iam_role.task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name = "${var.app_name}-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "ecs_task_policy" {
  name = "${var.app_name}-s3-sagemaker-policy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
        Resource = [
          var.s3_file_upload_bucket_arn,
          "${var.s3_file_upload_bucket_arn}/*",
          var.s3_vector_bucket_arn,
          "${var.s3_vector_bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow",
        Action = ["sagemaker:*"],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "iam:PassRole"
        ],
        Resource = "" 
      },
      {
        Effect = "Allow",
        Action = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = ["bedrock:InvokeModel"],
        Resource = "arn:aws:bedrock:us-east-1::foundation-model/*"
      }
    ]
  })
}


resource "aws_ecs_task_definition" "this" {
  family                   = "${var.app_name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
  name      = var.app_name
  image     = var.container_image
  essential = true
  portMappings = [{
    containerPort = var.container_port
    protocol      = "tcp"
  }]
  environment = [
  {
    name  = "REDEPLOY_VERSION"
    value = "12"
  },
  {
    name  = "DB_URL"
    value = ""
  },
  {
    name  = "AWS_REGION"
    value = ""
  },
  {
    name  = "S3_BUCKET_NAME_FILE_UPLOAD"
    value = ""
  },
  {
    name  = "S3_BUCKET_VECTOR"
    value = ""
  },
  {
    name  = "SAGEMAKER_ROLE"
    value = ""
  },
  {
    name  = "ECR_REPOSITORY_URL"
    value = ""
  },
  {name  = "PINECONE_API_KEY"
    value = ""
  }


]

  logConfiguration = {
    logDriver = "awslogs"
    options = {
      awslogs-group         = "/ecs/${var.app_name}"
      awslogs-region        = var.region
      awslogs-stream-prefix = "ecs"
    }
  }
}])

}

resource "aws_lb" "this" {
  name               = "${var.app_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups = var.security_group_ids
  subnets            = var.subnet_ids
}


resource "aws_lb_target_group" "this" {
  name     = "${var.app_name}-tg"
  port     = var.container_port
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  target_type = "ip"
  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = "200-399"
  }
}

resource "aws_lb_listener" "this" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
}



resource "aws_ecs_service" "this" {
  name            = "${var.app_name}-service"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.this.arn
  launch_type     = "FARGATE"

  desired_count = 1

  network_configuration {
    subnets         = var.subnet_ids
    assign_public_ip = true
    security_groups = var.security_group_ids
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.this.arn
    container_name   = var.app_name
    container_port   = var.container_port
  }

  depends_on = [aws_lb_listener.this]
}


resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/${var.app_name}"
  retention_in_days = 7
}
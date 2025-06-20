variable "app_name" {
  type        = string
  description = "Application name (used in naming resources)"
}

variable "container_image" {
  type        = string
  description = "Docker image to deploy"
}

variable "container_port" {
  type        = number
  description = "Port your container listens on"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID to deploy into"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnet IDs to deploy into"
}
variable "security_group_ids" {
  description = "List of security group IDs for ECS service and ALB"
  type        = list(string)
}

variable "region"{}
variable "db_url" {}
variable "s3_file_upload_bucket" {}
variable "s3_vector_bucket" {}
variable "sagemaker_role_arn" {}
variable "ecr_repository_url" {}

variable "s3_vector_bucket_arn" {
  description = "ARN of the S3 bucket used for vector storage"
  type        = string
}
variable "s3_file_upload_bucket_arn" {
  description = "ARN of the S3 bucket used for file uploads"
  type        = string
}
variable "role_name" {
  description = "Name of the SageMaker execution role"
  type        = string
}

variable "bucket_arn" {
  description = "ARN of the S3 bucket used for input/output"
  type        = string
}

variable "alert_email" {
  description = "Email to receive SageMaker failure alerts"
  type        = string
}


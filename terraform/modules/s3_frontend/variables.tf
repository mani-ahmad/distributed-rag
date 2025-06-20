variable "bucket_name" {
  description = "Name of the S3 bucket to host frontend"
  type        = string
}

variable "frontend_build_dir" {
  description = "Path to frontend files to upload"
  type        = string
}
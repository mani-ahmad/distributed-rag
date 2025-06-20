output "bucket_name" {
  value = aws_s3_bucket.frontend.bucket
}

output "website_endpoint" {
  value = aws_s3_bucket.frontend.website_endpoint
}

output "bucket_regional_domain_name" {
  value = aws_s3_bucket.frontend.bucket_regional_domain_name
}
output "resolved_frontend_build_dir" {
  value = var.frontend_build_dir
}
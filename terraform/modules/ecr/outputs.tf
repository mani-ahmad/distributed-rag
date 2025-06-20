output "repository_url" {
  value       = aws_ecr_repository.backend_repo.repository_url
  description = "URL of the ECR repo to use in docker tag/push"
}

output "bedrock_inference_role_name" {
  description = "Name of Bedrock IAM Role"
  value       = aws_iam_role.bedrock_inference_role.name
}

output "bedrock_inference_role_arn" {
  description = "ARN of Bedrock IAM Role"
  value       = aws_iam_role.bedrock_inference_role.arn
}

output "bedrock_inference_policy_arn" {
  description = "ARN of Bedrock IAM Policy"
  value       = aws_iam_policy.bedrock_inference_policy.arn
}


output "role_arn" {
  description = "SageMaker execution role ARN"
  value       = aws_iam_role.sagemaker_execution.arn
}
output "alarm_topic_arn" {
  description = "SNS topic for SageMaker failure alerts"
  value       = aws_sns_topic.sagemaker_alarm_topic.arn
}
resource "aws_iam_role" "sagemaker_execution" {
  name = var.role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "sagemaker_policy" {
  name = "sagemaker-batch-transform-policy"
  role = aws_iam_role.sagemaker_execution.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ],
        Resource = [
          var.bucket_arn,
          "${var.bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "sagemaker:CreateModel",
          "sagemaker:DescribeModel",
          "sagemaker:DeleteModel",
          "sagemaker:CreateTransformJob",
          "sagemaker:DescribeTransformJob",
          "sagemaker:StopTransformJob"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_sns_topic" "sagemaker_alarm_topic" {
  name = "sagemaker-job-failure-alerts"
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.sagemaker_alarm_topic.arn
  protocol  = "email"
  endpoint  = var.alert_email 
}

resource "aws_cloudwatch_log_group" "sagemaker_transform_jobs" {
  name              = "/aws/sagemaker/TransformJobs"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_metric_filter" "failed_transform_jobs" {
  name           = "SageMakerFailedJobs"
  log_group_name = aws_cloudwatch_log_group.sagemaker_transform_jobs.name

  pattern        = "{ $.status = \"Failed\" }"

  metric_transformation {
    name      = "FailedSageMakerJobs"
    namespace = "SageMakerMetrics"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "sagemaker_failure_alarm" {
  alarm_name          = "SageMakerTransformJobFailure"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "FailedSageMakerJobs"
  namespace           = "SageMakerMetrics"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Triggers when a SageMaker transform job fails"
  alarm_actions       = [aws_sns_topic.sagemaker_alarm_topic.arn]
  ok_actions          = [aws_sns_topic.sagemaker_alarm_topic.arn]
}

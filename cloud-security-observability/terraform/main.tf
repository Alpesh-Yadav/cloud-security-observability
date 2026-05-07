resource "aws_s3_bucket" "security_logs_bucket" {
  bucket = "security-logs-bucket"
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_iam_role" "security_exporter_role" {
  name = "security-exporter-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_iam_policy" "security_exporter_policy" {
  name   = "security-exporter-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "s3:ListBucket",
          "s3:GetObject",
          "sqs:GetQueueAttributes",
          "cloudwatch:ListMetrics",
          "logs:DescribeLogGroups"
        ]
        Resource = "*"
      }
    ]
  })
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "exporter_policy_attachment" {
  role       = aws_iam_role.security_exporter_role.name
  policy_arn = aws_iam_policy.security_exporter_policy.arn
}

resource "aws_cloudwatch_log_group" "security_events_log_group" {
  name = "/security/events"
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_sns_topic" "security_alerts_topic" {
  name = "security-alerts"
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_sqs_queue" "alert_queue" {
  name = "alert-queue"
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

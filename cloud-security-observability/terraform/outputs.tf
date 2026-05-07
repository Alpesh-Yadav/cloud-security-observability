output "s3_bucket_name" {
  value = aws_s3_bucket.security_logs_bucket.bucket
}

output "iam_role_name" {
  value = aws_iam_role.security_exporter_role.name
}

output "iam_policy_arn" {
  value = aws_iam_policy.security_exporter_policy.arn
}

output "log_group_name" {
  value = aws_cloudwatch_log_group.security_events_log_group.name
}

output "sns_topic_arn" {
  value = aws_sns_topic.security_alerts_topic.arn
}

output "sqs_queue_url" {
  value = aws_sqs_queue.alert_queue.id
}

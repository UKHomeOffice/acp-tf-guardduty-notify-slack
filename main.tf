locals {
  lambda_filename         = "${path.module}/functions/notify_slack.py"
  lambda_archive_filename = "${path.module}/functions/notify_slack.zip"
}

data "archive_file" "notify_slack" {
  type        = "zip"
  source_file = local.lambda_filename
  output_path = local.lambda_archive_filename
}

resource "aws_cloudwatch_log_group" "lambda_function" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 365
}

resource "aws_lambda_function" "notify_slack" {
  filename = data.archive_file.notify_slack.output_path

  function_name = var.lambda_function_name

  role             = aws_iam_role.lambda.arn
  handler          = "notify_slack.lambda_handler"
  source_code_hash = data.archive_file.notify_slack.output_base64sha256
  runtime          = "python3.9"
  timeout          = 30

  environment {
    variables = {
      SLACK_WEBHOOK_URL = var.slack_webhook_url
      SLACK_CHANNEL     = var.slack_channel
      SLACK_USERNAME    = var.slack_username
      SLACK_EMOJI       = var.slack_emoji
    }
  }

  lifecycle {
    ignore_changes = [
      filename,
      last_modified,
    ]
  }

  depends_on = [
    data.archive_file.notify_slack,
    aws_cloudwatch_log_group.lambda_function
  ]
}

# Bucket notification

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.notify_slack.arn
  principal     = "s3.amazonaws.com"
  source_arn    = data.aws_s3_bucket.guardduty.arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.bucket_name

  lambda_function {
    lambda_function_arn = aws_lambda_function.notify_slack.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "AWSLogs/"
  }

  depends_on = [aws_lambda_permission.allow_bucket]
}


### Alerts

resource "aws_sns_topic" "alert" {
  count = length(var.alert_emails) > 0 ? 1 : 0
  name  = "lambda-${var.lambda_function_name}-error"
}

resource "aws_sns_topic_subscription" "alert-email" {
  for_each  = toset(var.alert_emails)
  topic_arn = aws_sns_topic.alert[0].arn
  protocol  = "email"
  endpoint  = each.value
}

resource "aws_cloudwatch_metric_alarm" "errorRate" {
  count                     = length(var.alert_emails) > 0 ? 1 : 0
  alarm_name                = "lambda-${var.lambda_function_name}-error"
  alarm_description         = "Alarm to detect errors in the GuardDuty Lambda"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "1"
  metric_name               = "Errors"
  namespace                 = "AWS/Lambda"
  period                    = "60"
  statistic                 = "Maximum"
  threshold                 = "0"
  insufficient_data_actions = []
  treat_missing_data        = "notBreaching"
  alarm_actions             = [aws_sns_topic.alert[0].arn]
  dimensions = {
    FunctionName = var.lambda_function_name
  }
}

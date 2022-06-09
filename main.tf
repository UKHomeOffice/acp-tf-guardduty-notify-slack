locals {
  lambda_filename         = "${path.module}/functions/notify_slack.py"
  lambda_archive_filename = "${path.module}/functions/notify_slack.zip"
}

# Bucket notification

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.notify_slack.arn
  principal     = "s3.amazonaws.com"
  source_arn    = var.bucket_arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.bucket_arn

  lambda_function {
    lambda_function_arn = aws_lambda_function.notify_slack.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "AWSLogs/"
    filter_suffix       = ".log"
  }

  depends_on = [aws_lambda_permission.allow_bucket]
}

#  the path the python or node.js file is stored in the directory
data "archive_file" "notify_slack" {
  count = var.create ? 1 : 0

  type        = "zip"
  source_file = local.lambda_filename
  output_path = local.lambda_archive_filename
}


resource "aws_cloudwatch_log_group" "lambda_function" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 365
}

resource "aws_lambda_function" "notify_slack" {
  count = var.create ? 1 : 0

  filename = data.archive_file.notify_slack[0].output_path

  function_name = var.lambda_function_name

  role             = aws_iam_role.lambda[0].arn
  handler          = "notify_slack.lambda_handler"
  source_code_hash = data.archive_file.notify_slack[0].output_base64sha256
  runtime          = "python3.6"
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
    data.archive_file.notify_slack[0],
    aws_cloudwatch_log_group.lambda_function
  ]
}
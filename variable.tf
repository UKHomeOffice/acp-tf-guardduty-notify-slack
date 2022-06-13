variable "lambda_function_name" {
  description = "The name of the Lambda function to create"
  default     = "guardduty_notify_slack"
}

variable "slack_webhook_url" {
  description = "The URL of the  Slack webhook"
}

variable "slack_channel" {
  description = "The name of the channel in Slack for notifications"
}

variable "slack_username" {
  description = "The username that will appear on Slack messages"
}

variable "slack_emoji" {
  description = "A custom emoji that will appear on Slack messages"
  default     = ":aws:"
}

variable "kms_key_arn" {
  description = "ARN of the KMS key used for decrypting slack webhook url"
}

variable "bucket_name" {
  description = "Bucket name of GuardDuty event logs"
}

variable "alert_emails" {
  description = "Emails to alert on if there is an error in the lambda"
  default     = []
}
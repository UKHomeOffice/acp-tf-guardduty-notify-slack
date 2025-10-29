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

variable "ignore_sample_events" {
  description = "Flag to toggle whether to ignore sample events"
  default     = "false"
}

variable "lambda_variable_kms_key" {
  description = "ARN of the KM keys used for decryption of lambda variables"
}

variable "bucket_name" {
  description = "Bucket name of GuardDuty event logs"
}

variable "bucket_kms_key" {
  description = "KMS key arn used to decrypt the GuardDuty s3 events"
}

variable "alert_emails" {
  description = "Emails to alert on if there is an error in the lambda"
  default     = []
}

variable "ignored_finding_types" {
  description = "Comma-separated list of GuardDuty finding types to ignore"
  default     = "Recon:EC2/PortProbeUnprotectedPort"
}

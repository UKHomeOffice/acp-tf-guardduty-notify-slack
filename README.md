# acp-tf-guardduty-notify-slack

This module creates a Lambda that gets notified on new GuardDuty log files being created in the S3 bucket and alerts Slack.


## Upgrade notes - v2

Version 1 worked through CloudWatch rule events with a corresponding lambda being configured into each region. This means there were 17 duplicate resources for all the regions.
Version 2 has been made to be notified of the logs from the central S3 bucket, which means only one lambda and no work is needed to add regions. In order to upgrade a bucket name is required.


## Example Usage

```
module "notify_slack" {
  source = "git::https://github.com/UKHomeOffice/acp-tf-guardduty-notify-slack?ref=v2.1.1"

  slack_webhook_url              = var.slack_webhook
  slack_channel                  = "GuardDuty-ALerts"
  slack_username                 = "testing"
  lambda_variable_kms_key        = "arn:aws:kms:eu-west-2:XXXX:key/XXX"
  bucket_name                    = "guardduty-bucket"
  bucket_kms_key                 = "arn:aws:kms:eu-west-2:XXXX:key/XXX"
  alert_emails                   = ["alerts@example.com"]
  lambda_function_name           = "guardduty_notify_slack"
}
```

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0 |
| <a name="requirement_archive"></a> [archive](#requirement\_archive) | ~> 2.2 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 3.70 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_archive"></a> [archive](#provider\_archive) | 2.2.0 |
| <a name="provider_aws"></a> [aws](#provider\_aws) | 3.72.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_log_group.lambda_function](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_metric_alarm.errorRate](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_metric_alarm) | resource |
| [aws_iam_role.lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_lambda_function.notify_slack](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_permission.allow_bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [aws_s3_bucket_notification.bucket_notification](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_notification) | resource |
| [aws_sns_topic.alert](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic) | resource |
| [aws_sns_topic_subscription.alert-email](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_subscription) | resource |
| [archive_file.notify_slack](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [aws_iam_policy_document.assume_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_s3_bucket.guardduty](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/s3_bucket) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_alert_emails"></a> [alert\_emails](#input\_alert\_emails) | Emails to alert on if there is an error in the lambda | `list` | `[]` | no |
| <a name="input_bucket_kms_key"></a> [bucket\_kms\_key](#input\_bucket\_kms\_key) | KMS key arn used to decrypt the GuardDuty s3 events | `any` | n/a | yes |
| <a name="input_bucket_name"></a> [bucket\_name](#input\_bucket\_name) | Bucket name of GuardDuty event logs | `any` | n/a | yes |
| <a name="input_lambda_function_name"></a> [lambda\_function\_name](#input\_lambda\_function\_name) | The name of the Lambda function to create | `string` | `"guardduty_notify_slack"` | no |
| <a name="input_lambda_variable_kms_key"></a> [lambda\_variable\_kms\_key](#input\_lambda\_variable\_kms\_key) | ARN of the KM keys used for decryption of lambda variables | `any` | n/a | yes |
| <a name="input_slack_channel"></a> [slack\_channel](#input\_slack\_channel) | The name of the channel in Slack for notifications | `any` | n/a | yes |
| <a name="input_slack_emoji"></a> [slack\_emoji](#input\_slack\_emoji) | A custom emoji that will appear on Slack messages | `string` | `":aws:"` | no |
| <a name="input_slack_username"></a> [slack\_username](#input\_slack\_username) | The username that will appear on Slack messages | `any` | n/a | yes |
| <a name="input_slack_webhook_url"></a> [slack\_webhook\_url](#input\_slack\_webhook\_url) | The URL of the  Slack webhook | `any` | n/a | yes |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
data "aws_s3_bucket" "guardduty" {
  bucket = var.bucket_name
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "lambda" {
  statement {
    actions = [
      "s3:GetObject",
    ]

    resources = [
      "${data.aws_s3_bucket.guardduty.arn}/*"
    ]
  }
  statement {
    sid = "AllowWriteToCloudwatchLogs"

    effect = "Allow"

    actions = [
      "logs:PutLogEvents",
      "logs:CreateLogStream"
    ]
    resources = [
      "${aws_cloudwatch_log_group.lambda_function.arn}:*",
      "${aws_cloudwatch_log_group.lambda_function.arn}:log-stream:*"
    ]
  }
  statement {
    sid = "AllowKMSDecrypt"

    effect = "Allow"

    actions = ["kms:Decrypt"]

    resources = [
      var.lambda_variable_kms_key,
      var.bucket_kms_key
    ]
  }
}


resource "aws_iam_role" "lambda" {
  name_prefix        = "lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy" "lambda" {

  name_prefix = "lambda-policy-"
  role        = aws_iam_role.lambda.id

  policy = data.aws_iam_policy_document.lambda.json
}

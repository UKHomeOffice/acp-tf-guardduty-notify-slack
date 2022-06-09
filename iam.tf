data "aws_iam_policy_document" "assume_role" {
  count = var.create ? 1 : 0

  statement {
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "lambda_basic" {
  count = var.create ? 1 : 0

  statement {
    sid = "AllowWriteToCloudwatchLogs"

    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["${aws_cloudwatch_log_group.lambda_function.arn}:*"]
  }
}

data "aws_iam_policy_document" "lambda" {
  count = var.create_with_kms_key && var.create ? 1 : 0

  source_json = data.aws_iam_policy_document.lambda_basic[0].json

  statement {
    sid = "AllowKMSDecrypt"

    effect = "Allow"

    actions = ["kms:Decrypt"]

    resources = ["*"]
  }
}

resource "aws_iam_role" "lambda" {
  count = var.create ? 1 : 0

  name_prefix        = "lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role[0].json
}

resource "aws_iam_role_policy" "lambda" {
  count = var.create ? 1 : 0

  name_prefix = "lambda-policy-"
  role        = aws_iam_role.lambda[0].id

  policy = element(
    compact(
      concat(
        data.aws_iam_policy_document.lambda.*.json,
        data.aws_iam_policy_document.lambda_basic.*.json,
      ),
    ),
    0,
  )
}

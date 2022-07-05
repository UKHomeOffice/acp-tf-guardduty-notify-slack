import os, boto3, json, base64, gzip
import urllib.request, urllib.parse
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Decrypt encrypted URL with KMS
def decrypt(encrypted_url):
    region = os.environ["AWS_REGION"]
    try:
        kms = boto3.client("kms", region_name="eu-west-2")
        plaintext = kms.decrypt(CiphertextBlob=base64.b64decode(encrypted_url))[
            "Plaintext"
        ]
        return plaintext.decode()
    except Exception:
        logging.exception("Failed to decrypt URL with KMS")


def alert_severity_color(severity):
    if severity < 4.0:
        return "good"
    elif severity < 7.0:
        return "warning"
    else:
        return "danger"


def alert_severity_name(severity):
    if severity < 4.0:
        return "LOW"
    elif severity < 7.0:
        return "MEDIUM"
    else:
        return "HIGH"


def make_message_text(**kwargs):
    return "\n".join("*%s:* %s" % (key.title(), val) for (key, val) in kwargs.items())


def make_guardduty_alert_payload(guardduty_event):
    slack_username = os.environ["SLACK_USERNAME"]
    slack_emoji = os.environ["SLACK_EMOJI"]

    title = guardduty_event["title"]

    if "sample" in guardduty_event["service"]["additionalInfo"] and guardduty_event["service"]["additionalInfo"]["sample"] == True:
        title = "[SAMPLE EVENT]" + title

    return {
        "username": slack_username,
        "icon_emoji": slack_emoji,
        "text": title,
        "attachments": [
            {
                "fallback": "Something",
                "color": alert_severity_color(guardduty_event["severity"]),
                "text": make_message_text(
                    region=guardduty_event["region"],
                    account=guardduty_event["accountId"],
                    severity=alert_severity_name(guardduty_event["severity"]),
                ),
            }
        ],
    }


# Send a message to a slack channel
def notify_slack(payload):
    slack_url = decrypt(os.environ["SLACK_WEBHOOK_URL"])

    data = urllib.parse.urlencode({"payload": json.dumps(payload)}).encode("utf-8")
    req = urllib.request.Request(slack_url)
    result = urllib.request.urlopen(req, data).read()
    return result


def get_guardduty_event(bucket, key):
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=bucket, Key=key)

    object_bytes = response["Body"].read()
    object_string = gzip.decompress(object_bytes).decode("utf-8")

    return json.loads(object_string)


def lambda_handler(event, context):
    logger.info("s3 event:")
    logger.info(event)

    for record in event["Records"]:
        if record["eventName"] == "Replication:OperationFailedReplication":
            logger.info("S3 replication failed")
            notify_slack({"text": "Replication failed"})
        elif record["eventName"] == "ObjectCreated:Put":
            guardduty_event = get_guardduty_event(
                record["s3"]["bucket"]["name"], record["s3"]["object"]["key"]
            )
            logger.info("GuardDuty event:")
            logger.info(guardduty_event)
            alert_payload = make_guardduty_alert_payload(guardduty_event)
            result = notify_slack(alert_payload)
            logger.info("HTTP Result:")
            logger.info(result)
    return

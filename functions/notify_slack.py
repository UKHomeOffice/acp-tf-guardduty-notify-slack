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

    return {
        "username": slack_username,
        "icon_emoji": slack_emoji,
        "text": guardduty_event["title"],
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

def get_s3_object(bucket, key):
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read()

def get_guardduty_events(object_bytes):
    object_string = gzip.decompress(object_bytes).decode("utf-8")
    object_lines = object_string.splitlines()
    return [json.loads(line) for line in object_lines]

def lambda_handler(event, context):
    logger.info(f's3 event: {event}')

    for record in event["Records"]:
        if record["eventName"] == "Replication:OperationFailedReplication":
            logger.info("S3 replication failed")
            notify_slack({"text": "Replication failed"})
        elif record["eventName"] == "ObjectCreated:Put":
            guardduty_events_list = get_guardduty_events(
                get_s3_object(record["s3"]["bucket"]["name"], record["s3"]["object"]["key"])
            )
            for guardduty_event in guardduty_events_list:
                logger.info(f'GuardDuty Event: {guardduty_event}')

                # Check if finding type should be ignored (only done for LOW severity events).
                # Prevents spamming the Slack channel with LOW severity events that don't need to be investigated.
                ignored_types = os.environ.get("IGNORED_FINDING_TYPES", "").split(",")
                ignored_types = [t.strip() for t in ignored_types if t.strip()]
                finding_type = guardduty_event.get("type", "")
                severity = guardduty_event.get("severity", 0)

                if finding_type in ignored_types and severity < 4.0:
                    logger.info(f'Finding type {finding_type} with LOW severity ({severity}) is in the ignored list. Skipping.')
                    continue

                if "sample" in guardduty_event["service"]["additionalInfo"] and guardduty_event["service"]["additionalInfo"]["sample"] == True:
                    logger.info("IS SAMPLE EVENT")
                    guardduty_event["title"] = "[SAMPLE EVENT]" + guardduty_event["title"]
                    if "IGNORE_SAMPLE_EVENTS" in os.environ and os.environ["IGNORE_SAMPLE_EVENTS"] == "true":
                        logger.info("SAMPLE EVENT SKIPPED")
                        continue 
                alert_payload = make_guardduty_alert_payload(guardduty_event)
                result = notify_slack(alert_payload)
                logger.info(f'HTTP Result: + {result}')
    return

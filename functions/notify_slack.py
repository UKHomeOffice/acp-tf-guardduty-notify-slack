import os, boto3, json, base64, gzip
import urllib.request, urllib.parse
import logging

# Decrypt encrypted URL with KMS
def decrypt(encrypted_url):
    region = os.environ['AWS_REGION']
    try:
        kms = boto3.client('kms', region_name="eu-west-2")
        plaintext = kms.decrypt(CiphertextBlob=base64.b64decode(encrypted_url))['Plaintext']
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

# Send a message to a slack channel
def notify_slack(message):
    slack_url = decrypt(os.environ['SLACK_WEBHOOK_URL'])
    slack_channel = os.environ['SLACK_CHANNEL']
    slack_username = os.environ['SLACK_USERNAME']
    slack_emoji = os.environ['SLACK_EMOJI']

    payload = {
        "channel": slack_channel,
        "username": slack_username,
        "icon_emoji": slack_emoji,
        "text": "Duplicate - " + message['title'],
        "attachments": [
            {
                "fallback": "Something",
                "color": alert_severity_color(message['severity']),
                "text": make_message_text(
                    region=message['region'],
                    account=message['accountId'],
                    severity=alert_severity_name(message["severity"]),
                ),
            }
        ]
    }

    data = urllib.parse.urlencode({"payload": json.dumps(payload)}).encode("utf-8")
    req = urllib.request.Request(slack_url)
    urllib.request.urlopen(req, data)
    return decrypt

def get_guardduty_event(bucket, key):
    s3_client = boto3.client('s3')
    response = s3_client.get_object(
        Bucket=bucket,
        Key=key
    )
    
    object_bytes = response['Body'].read()
    object_string = gzip.decompress(object_bytes).decode('utf-8')
    
    return json.loads(object_string)

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    logger.info("s3 event:")
    logger.info(event)

    for record in event['Records']:
      guardduty_event = get_guardduty_event(record['s3']['bucket']['name'], record['s3']['object']['key'])
      logger.info("GuardDuty event:")
      logger.info(guardduty_event)
      notify_slack(guardduty_event)

    return

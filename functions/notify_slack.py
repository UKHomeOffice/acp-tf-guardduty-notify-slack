import os, boto3, json, base64
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

    message = json.loads(message)

    payload = {
        "channel": slack_channel,
        "username": slack_username,
        "icon_emoji": slack_emoji,
        "text": message['detail']['title'],
        "attachments": [
            {
                "fallback": "Something",
                "color": alert_severity_color(message['detail']['severity']),
                "text": make_message_text(
                    region=message['region'],
                    account=message['detail']['accountId'],
                    severity=alert_severity_name(message["detail"]["severity"]),
                ),
            }
        ]

    }

    data = urllib.parse.urlencode({"payload": json.dumps(payload)}).encode("utf-8")
    req = urllib.request.Request(slack_url)
    urllib.request.urlopen(req, data)
    return decrypt


def lambda_handler(event, context):
    message = event['Records'][0]['Sns']['Message']
    notify_slack(message)

    return message

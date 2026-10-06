import unittest
from unittest import mock
import sys
sys.path.append('../')
from functions.notify_slack import * 


class TestLambda(unittest.TestCase):

    def helper_get_guardduty_events(self, filename, expected_length):
        with open(filename, 'rb') as filehandle:
            filecontent = filehandle.read()
        
        guardduty_events = get_guardduty_events(filecontent)

        self.assertEqual(len(guardduty_events), expected_length)

    def test_single_get_guardduty_events(self):
        self.helper_get_guardduty_events("single-guarddutyevent.json.gz", 1)
        
    def test_multiple_get_guardduty_events(self):
        self.helper_get_guardduty_events("multiple-guarddutyevent.json.gz", 2)

    def helper_load_guardduty_event(self):
        with open("single-guarddutyevent.json.gz", 'rb') as filehandle:
            return get_guardduty_events(filehandle.read())[0]

    def helper_lambda_handler(self, severity):
        guardduty_event = self.helper_load_guardduty_event()
        guardduty_event["severity"] = severity
        s3_object = gzip.compress(json.dumps(guardduty_event).encode("utf-8"))
        s3_event = {"Records": [{"eventName": "ObjectCreated:Put", "s3": {"bucket": {"name": "bucket"}, "object": {"key": "key"}}}]}
        env = {"SLACK_USERNAME": "test", "SLACK_EMOJI": ":aws:", "HIGH_SEVERITY_SNS_TOPIC_ARN": "arn"}

        with mock.patch.dict(os.environ, env), \
             mock.patch("functions.notify_slack.get_s3_object", return_value=s3_object), \
             mock.patch("functions.notify_slack.notify_slack"), \
             mock.patch("functions.notify_slack.notify_email") as mock_notify_email:
            lambda_handler(s3_event, None)

        return mock_notify_email

    def test_make_guardduty_email(self):
        subject, message = make_guardduty_email(self.helper_load_guardduty_event())

        self.assertEqual(subject, "GuardDuty HIGH: Resource discovery API ListObjects was invoked from a Tor exit node.")
        self.assertIn("Bucket: fooo", message)
        self.assertIn("Remote IP: 1.1.1.1 (Germany)", message)

    def test_high_severity_sends_email(self):
        self.helper_lambda_handler(8).assert_called_once()

    def test_medium_severity_does_not_send_email(self):
        self.helper_lambda_handler(5).assert_not_called()

if __name__ == '__main__':
    unittest.main()

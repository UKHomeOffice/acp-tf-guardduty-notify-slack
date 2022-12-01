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

if __name__ == '__main__':
    unittest.main()

import unittest
import json
import time
from datetime import datetime as dt
from datetime import timedelta as td
from tdxlib import tdx_asset_integration
from tdxlib import tdx_utils
import os


class TdxAssetTesting(unittest.TestCase):

    # Create TDXIntegration object for testing use. Called before testing methods.
    def setUp(self):
        testing_vars_file = 'testing_vars.json'
        self.tix = tdx_asset_integration.TDXAssetIntegration()
        right_now = dt.today()
        self.timestamp = right_now.strftime("%d-%B-%Y %H:%M:%S")
        if os.path.isfile(testing_vars_file):
            with open(testing_vars_file, 'r') as f:
                self.testing_vars = json.load(f)
        else:
            print('Testing variables need to be populated in file "testing_vars.json" in the working directory.',
                  'A sample file is available in testing/sample_ticket_testing_vars. ',
                  'Any *.json files are ignored by git.')

    def test_authn(self):
        self.assertGreater(len(self.tix.token), 200)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TdxAssetTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)
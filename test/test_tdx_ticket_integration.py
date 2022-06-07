import unittest
from tdxlib import tdx_integration
from unittest.mock import patch


class MockConfigParser(dict):

    def getboolean(self, key):
        return bool(self[key])

    def read(self, filename):
        pass


class TdxMockTesting(unittest.TestCase):

    def setUp(self):
        config = MockConfigParser({
            'TDX API Settings': MockConfigParser({
                'fullhost': 'tdx.myuniversity.org',
                'sandbox': True,
                'username': '',
                'password': 'not-a-real-password',
                'ticketAppId': '',
                'assetAppId': '',
                'caching': False,
                'timezone': '-0500',
                'logLevel': 'ERROR',
            })
        })
        patcher = patch("configparser.ConfigParser", return_value=config)
        self.mock_config = patcher.start()
        self.addCleanup(patcher.stop)

    @patch.object(tdx_integration.TDXIntegration, "auth")
    def test_api_url(self, config_parser):
        """Check for extra slashes in API URL"""
        tdx = tdx_integration.TDXIntegration('../tdxlib.ini')
        self.assertNotIn('//', tdx.api_url.lstrip('https://'),
                         f'Extra slash in URL { tdx.api_url }')


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TdxMockTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)

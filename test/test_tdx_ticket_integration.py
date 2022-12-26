import configparser
import unittest
from tdxlib import tdx_integration, tdx_ticket_integration
from unittest.mock import patch, Mock


class MockConfigParser(configparser.ConfigParser):

    def read(self, filename):
        pass


class TdxTesting(unittest.TestCase):

    def setUp(self):
        config = MockConfigParser()
        config.read = Mock()
        config.read_dict({
            'TDX API Settings': {
                'fullhost': 'tdx.myuniversity.org',
                'sandbox': True,
                'authType': 'password',
                'username': '',
                'password': 'not-a-real-password',
                'ticketAppId': '',
                'assetAppId': '',
                'caching': False,
                'timezone': '-0500',
                'logLevel': 'ERROR',
            }
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

    @patch.object(tdx_integration.TDXIntegration, "auth")
    def test_tdx_ticket_integration_from_dict(self, mock_auth):
        config = {
            'TDX API Settings': {
                "orgname": "myuniversity",
                "fullhost": "help.uillinois.edu",
                "sandbox": True,
                "username": "techsvc-securityapi",
                "password": "",
                "ticketAppId": 66,
                "assetAppId": "",
                "caching": False,
                "timezone": "-0500",
                "logLevel": "ERROR",
            },
        }
        tdx = tdx_ticket_integration.TDXTicketIntegration(config=config)
        assert not self.mock_config.read.called
        assert mock_auth.called
        assert tdx.org_name == config['TDX API Settings']['orgname']
        assert tdx.username == config['TDX API Settings']['username']


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TdxTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)

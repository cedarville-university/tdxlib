import unittest

from unittest.mock import patch, Mock

from tdxlib import tdx_integration

# python -m unittest test.test_setup.TdxSetupTesting.test_init

class TdxSetupTesting(unittest.TestCase):

	@patch.object(tdx_integration.TDXIntegration, "load_config_from_file")
	@patch.object(tdx_integration.TDXIntegration, "run_setup_wizard")
	def test_init(self, mock_wizzard, mock_load):
		"""Assert that functions for building configuration 
		interactively or from a file are not used when 
		dictionary settings are provided.
		"""
		tdx = tdx_integration.TDXIntegration(config=
			{
				"orgname":'example.edu'
			})
		assert mock_load.call_count == 0
		assert mock_wizzard.call_count == 0


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TdxSetupTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)
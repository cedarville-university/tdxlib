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
        self.tax = tdx_asset_integration.TDXAssetIntegration()
        right_now = dt.today()
        self.timestamp = right_now.strftime("%d-%B-%Y %H:%M:%S")
        if os.path.isfile(testing_vars_file):
            with open(testing_vars_file, 'r') as f:
                self.testing_vars = json.load(f)
        else:
            print('Testing variables need to be populated in file "testing_vars.json" in the working directory.',
                  'A sample file is available in testing/sample_ticket_testing_vars. ',
                  'Any *.json files are ignored by git.')

    def test_aaa(self):
        self.assertGreater(len(self.tax.token), 200)

    def test_asset_forms(self):
        forms = self.tax.get_all_asset_forms()
        self.assertGreater(len(forms), 1)

    def test_asset_form_name(self):
        form = self.tax.get_asset_form_by_name_id(self.testing_vars['asset_form']['Name'])
        self.assertEqual(int(form['ID']), self.testing_vars['asset_form']['ID'])

    def test_asset_form_id(self):
        form = self.tax.get_asset_form_by_name_id(self.testing_vars['asset_form']['ID'])
        self.assertEqual(form['Name'], self.testing_vars['asset_form']['Name'])

    def test_asset_statuses(self):
        statuses = self.tax.get_all_asset_statuses()
        self.assertGreater(len(statuses),3)

    def test_asset_status_id(self):
        status = self.tax.get_asset_status_by_name_id(self.testing_vars['asset_status']['ID'])
        self.assertEqual(status['Name'], self.testing_vars['asset_status']['Name'])

    def test_asset_status_name(self):
        status = self.tax.get_asset_status_by_name_id(self.testing_vars['asset_status']['Name'])
        self.assertEqual(int(status['ID']), self.testing_vars['asset_status']['ID'])

    def test_asset_product_types(self):
        product_types = self.tax.get_all_product_types()
        self.assertGreater(len(product_types),3)

    def test_asset_product_type_id(self):
        product_type = self.tax.get_product_type_by_name_id(self.testing_vars['product_type']['ID'])
        self.assertEqual(product_type['Name'], self.testing_vars['product_type']['Name'])

    def test_asset_product_type_name(self):
        product_type = self.tax.get_product_type_by_name_id(self.testing_vars['product_type']['Name'])
        self.assertEqual(int(product_type['ID']), self.testing_vars['product_type']['ID'])
        
    def test_asset_product_models(self):
        product_models = self.tax.get_all_product_models()
        self.assertGreater(len(product_models),3)

    def test_asset_product_model_id(self):
        product_model = self.tax.get_product_model_by_name_id(self.testing_vars['product_model']['ID'])
        self.assertEqual(product_model['Name'], self.testing_vars['product_model']['Name'])

    def test_asset_product_model_name(self):
        product_model = self.tax.get_product_model_by_name_id(self.testing_vars['product_model']['Name'])
        self.assertEqual(int(product_model['ID']), self.testing_vars['product_model']['ID'])

    # TODO: def test_update_product_type(self):
    # TODO: def test_create_product_type(self):
    # TODO: def test_delete_product_type(self):
    # TODO: def test_update_product_model(self):
    # TODO: def test_create_product_model(self):
    # TODO: def test_delete_product_model(self):
    # TODO: def test_get_all_vendors(self):
    # TODO: def test_update_vendor(self):
    # TODO: def test_create_vendor(self):
    # TODO: def test_delete_vendor(self):

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TdxAssetTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)
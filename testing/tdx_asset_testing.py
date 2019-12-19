import unittest
import json
import time
from datetime import datetime as dt
from datetime import timedelta as td
from tdxlib import tdx_asset_integration
from tdxlib import tdx_utils
import os
from sys import argv


class TdxAssetTesting(unittest.TestCase):

    # Create TDXIntegration object for testing use. Called before testing methods.
    def setUp(self):
        testing_vars_file = 'testing_vars.json'
        self.tax = tdx_asset_integration.TDXAssetIntegration()
        if not self.tax.sandbox:
            print("Not in Sandbox... Aborting")
            quit()
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
        status = self.tax.get_asset_status_by_name_id(self.testing_vars['asset_status1']['ID'])
        self.assertEqual(status['Name'], self.testing_vars['asset_status1']['Name'])

    def test_asset_status_name(self):
        status = self.tax.get_asset_status_by_name_id(self.testing_vars['asset_status1']['Name'])
        self.assertEqual(int(status['ID']), self.testing_vars['asset_status1']['ID'])

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

    def test_get_asset_id(self):
        asset = self.tax.get_asset_by_id(self.testing_vars['asset1']['ID'])
        self.assertEqual(asset['Name'], self.testing_vars['asset1']['Name'])

    def test_search_asset(self):
        assets = self.tax.search_assets(self.testing_vars['asset_search']['Text'])
        self.assertGreaterEqual(len(assets), self.testing_vars['asset_search']['Count'])

    def test_find_asset_tag(self):
        asset = self.tax.find_asset_by_tag(self.testing_vars['asset2']['Tag'])
        self.assertEqual(asset['SerialNumber'], self.testing_vars['asset2']['SerialNumber'])

    def test_find_asset_SN(self):
        asset = self.tax.find_asset_by_sn(self.testing_vars['asset2']['SerialNumber'])
        self.assertEqual(asset['Tag'].lstrip('0'), self.testing_vars['asset2']['Tag'].lstrip('0'))

    def test_get_assets_by_location(self):
        assets = self.tax.get_assets_by_location(self.testing_vars['location1'])
        self.assertGreaterEqual(len(assets), self.testing_vars['location1']['asset_count'])

    def test_get_assets_by_locations(self):
        assets = self.tax.get_assets_by_location([self.testing_vars['location1'],self.testing_vars['location2']])
        self.assertGreaterEqual(len(assets),
                                self.testing_vars['location1']['asset_count'] + self.testing_vars['location2']['asset_count'])

    def test_get_assets_by_room(self):
        location = self.tax.get_location_by_name(self.testing_vars['location3']['Name'])
        room1 = self.tax.get_room_by_name(location, self.testing_vars['room1']['Name'])
        assets = self.tax.get_assets_by_room(room1, max_results=100)
        self.assertGreaterEqual(len(assets), self.testing_vars['room1']['asset_count'])

    def test_get_assets_by_owner(self):
        assets = self.tax.get_assets_by_owner(self.testing_vars['owner']['PrimaryEmail'], max_results=100, disposed=True)
        self.assertGreaterEqual(len(assets), self.testing_vars['owner']['asset_count'])

    def test_get_assets_by_requesting_dept(self):
        assets = self.tax.get_assets_by_owner(self.testing_vars['department']['Name'], max_results=100, disposed=True)
        self.assertGreaterEqual(len(assets), self.testing_vars['department']['asset_count'])

    def test_update_asset_status(self):
        assets_to_update = self.tax.get_assets_by_owner(self.testing_vars['owner']['PrimaryEmail'], max_results=100, disposed=True)
        new_status = str(self.testing_vars['asset_status1']['ID'])
        first_status = str(assets_to_update[0]['StatusID'])
        if first_status == new_status:
            new_status = str(self.testing_vars['asset_status2']['ID'])
        updated_assets = self.tax.update_assets(assets_to_update, {'StatusID': new_status})
        self.assertEqual(len(assets_to_update), len(updated_assets))
        for i in range(len(updated_assets)):
            self.assertEqual(str(updated_assets[i]['StatusID']), new_status)

    def test_update_asset_owner(self):
        asset = self.tax.get_asset_by_id(self.testing_vars['asset1']['ID'])
        new_owner = self.testing_vars['owner']
        if asset['OwningCustomerID'] == new_owner['UID']:
            new_owner = self.testing_vars['owner_alt']
        updated_asset = self.tax.change_asset_owner(asset,new_owner)[0]
        self.assertTrue(updated_asset)
        self.assertEqual(updated_asset['OwningCustomerName'], new_owner['FullName'])

    def test_update_asset_requesting_dept(self):
        asset = self.tax.get_asset_by_id(self.testing_vars['asset1']['ID'])
        new_dept = self.testing_vars['department']
        if asset['RequestingDepartmentID'] == new_dept['ID']:
            new_dept = self.testing_vars['department_alt']
        updated_asset = self.tax.change_asset_requesting_dept(asset,new_dept)[0]
        self.assertEqual(updated_asset['RequestingDepartmentName'], new_dept['Name'])


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TdxAssetTesting)
    if len(argv) > 1:
        unittest.main()
    else:
        unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
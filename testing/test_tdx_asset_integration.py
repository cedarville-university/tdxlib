import unittest
import json
import os
from datetime import datetime as dt
from sys import argv
from tdxlib import tdx_asset_integration

class TdxAssetTesting(unittest.TestCase):
    tax = None
    is_admin = False

    # Create TDXIntegration object for testing use. Called before testing methods.
    @classmethod
    def setUpClass(cls):
        # only run admin tests if this is true
        cls.is_admin = False
        testing_vars_file = './asset_testing_vars.json'
        cls.tax = tdx_asset_integration.TDXAssetIntegration('../tdxlib.ini')
        if not cls.tax.config.sandbox:
            print("Not in Sandbox... Aborting")
            quit()

        if os.path.isfile(testing_vars_file):
            with open(testing_vars_file, 'r') as f:
                cls.testing_vars = json.load(f)
        else:
            print('Testing variables need to be populated in file "testing_vars.json" in the working directory.',
                  'A sample file is available in testing/sample_ticket_testing_vars. ',
                  'Any *.json files are ignored by git.')

    @classmethod
    def tearDownClass(cls):
        if cls.tax:
            cls.tax = None

    def setUp(self):
        """Set up test fixtures before each test method.

        Creates a timestamp for the test and validates that:
        1. The TDX integration object exists
        2. We're running in sandbox mode to prevent production changes
        """
        right_now = dt.now()
        self.timestamp = right_now.strftime("%d-%B-%Y %H:%M:%S")
        if not self.tax:
            self.fail("TDXAssetIntegration object not created. Please run setUpClass first.")
        if not self.tax.config.sandbox:
            self.fail("Not in Sandbox mode. Please set sandbox to True in tdxlib.ini.")

    def test_authentication_token_isvalid(self):
        """Test that authentication token has valid length."""
        self.assertGreater(len(self.tax.config.token), 200, "Authentication token should be longer than 200 characters")

    def test_asset_forms(self):
        """Test retrieving all asset forms."""
        forms = self.tax.get_all_asset_forms()
        self.assertGreater(len(forms), 1, "Should retrieve more than 1 asset form")

    def test_asset_form_name(self):
        """Test retrieving asset form by name returns correct ID."""
        form = self.tax.get_asset_form_by_name_id(self.testing_vars['asset_form']['Name'])
        self.assertEqual(int(form['ID']), self.testing_vars['asset_form']['ID'], 
                        f"Form ID should match expected value {self.testing_vars['asset_form']['ID']}")

    def test_asset_form_id(self):
        """Test retrieving asset form by ID returns correct name."""
        form = self.tax.get_asset_form_by_name_id(self.testing_vars['asset_form']['ID'])
        self.assertEqual(form['Name'], self.testing_vars['asset_form']['Name'],
                        f"Form name should match expected value {self.testing_vars['asset_form']['Name']}")

    def test_asset_statuses(self):
        """Test retrieving all asset statuses."""
        statuses = self.tax.get_all_asset_statuses()
        self.assertGreater(len(statuses), 3, "Should retrieve more than 3 asset statuses")

    def test_asset_status_id(self):
        """Test retrieving asset status by ID returns correct name."""
        status = self.tax.get_asset_status_by_name_id(self.testing_vars['asset_status1']['ID'])
        self.assertEqual(status['Name'], self.testing_vars['asset_status1']['Name'],
                        f"Status name should match expected value {self.testing_vars['asset_status1']['Name']}")

    def test_asset_status_name(self):
        """Test retrieving asset status by name returns correct ID."""
        status = self.tax.get_asset_status_by_name_id(self.testing_vars['asset_status1']['Name'])
        self.assertEqual(int(status['ID']), self.testing_vars['asset_status1']['ID'],
                        f"Status ID should match expected value {self.testing_vars['asset_status1']['ID']}")

    def test_asset_product_types(self):
        """Test retrieving all product types."""
        product_types = self.tax.get_all_product_types()
        self.assertGreater(len(product_types), 3, "Should retrieve more than 3 product types")

    def test_asset_product_type_id(self):
        """Test retrieving product type by ID returns correct name."""
        product_type = self.tax.get_product_type_by_name_id(self.testing_vars['product_type']['ID'])
        self.assertEqual(product_type['Name'], self.testing_vars['product_type']['Name'],
                        f"Product type name should match expected value {self.testing_vars['product_type']['Name']}")

    def test_asset_product_type_name(self):
        """Test retrieving product type by name returns correct ID."""
        product_type = self.tax.get_product_type_by_name_id(self.testing_vars['product_type']['Name'])
        self.assertEqual(int(product_type['ID']), self.testing_vars['product_type']['ID'],
                        f"Product type ID should match expected value {self.testing_vars['product_type']['ID']}")
        
    def test_asset_product_models(self):
        """Test retrieving all product models."""
        product_models = self.tax.get_all_product_models()
        self.assertGreater(len(product_models), 3, "Should retrieve more than 3 product models")

    def test_asset_product_model_id(self):
        """Test retrieving product model by ID returns correct name."""
        product_model = self.tax.get_product_model_by_name_id(self.testing_vars['product_model']['ID'])
        self.assertEqual(product_model['Name'], self.testing_vars['product_model']['Name'],
                        f"Product model name should match expected value {self.testing_vars['product_model']['Name']}")

    def test_asset_product_model_name(self):
        """Test retrieving product model by name returns correct ID."""
        product_model = self.tax.get_product_model_by_name_id(self.testing_vars['product_model']['Name'])
        self.assertEqual(int(product_model['ID']), self.testing_vars['product_model']['ID'],
                        f"Product model ID should match expected value {self.testing_vars['product_model']['ID']}")

    def test_update_product_type(self):
        """Test updating product type description."""
        product_type = self.tax.get_product_type_by_name_id(self.testing_vars['product_type']['Name'])
        changed_attributes = {'Description': self.timestamp}
        updated_product_type = self.tax.update_product_type(product_type, changed_attributes)
        self.assertEqual(updated_product_type['Description'], self.timestamp,
                        f"Product type description should be updated to {self.timestamp}")

    def test_create_product_type(self):
        """Test creating a new product type."""
        name = 'Temp Product Type ' + self.timestamp
        new_product_type = self.tax.create_product_type(name)
        self.assertIsNotNone(new_product_type['ID'], "New product type should have an ID")
        self.assertEqual(name, new_product_type['Name'], f"Product type name should be {name}")

    # TODO: def test_update_product_model(self):

    def test_create_product_model(self):
        """Test creating a new product model."""
        name = 'Temp Product Model ' + self.timestamp
        product_type = self.tax.get_product_type_by_name_id(self.testing_vars['product_type']['ID'])
        vendor = self.tax.get_vendor_by_name_id(self.testing_vars['vendor']['Name'])
        new_product_model = self.tax.create_product_model(name, product_type, vendor)
        self.assertIsNotNone(new_product_model['ID'], "New product model should have an ID")
        self.assertEqual(name, new_product_model['Name'], f"Product model name should be {name}")

    def test_get_all_vendors(self):
        """Test retrieving all vendors."""
        vendors = self.tax.get_all_vendors()
        self.assertGreaterEqual(len(vendors), 5, "Should retrieve at least 5 vendors")

    def test_get_vendor_by_name_id(self):
        """Test retrieving vendor by name returns correct ID."""
        name = self.testing_vars['vendor']['Name']
        vendor = self.tax.get_vendor_by_name_id(name)
        self.assertEqual(int(vendor['ID']), self.testing_vars['vendor']['ID'],
                        f"Vendor ID should match expected value {self.testing_vars['vendor']['ID']}")

    # TODO: def test_update_vendor(self):

    def test_create_vendor(self):
        """Test creating a new vendor."""
        name = 'Temp Vendor ' + self.timestamp
        new_vendor = self.tax.create_vendor(name)
        self.assertIsNotNone(new_vendor['ID'], "New vendor should have an ID")
        self.assertEqual(name, new_vendor['Name'], f"Vendor name should be {name}")

    def test_get_asset_id(self):
        """Test retrieving asset by ID returns correct name."""
        asset = self.tax.get_asset_by_id(self.testing_vars['asset1']['ID'])
        self.assertEqual(asset['Name'], self.testing_vars['asset1']['Name'],
                        f"Asset name should match expected value {self.testing_vars['asset1']['Name']}")

    def test_search_asset(self):
        """Test searching assets returns expected minimum count."""
        assets = self.tax.search_assets(self.testing_vars['asset_search']['Text'])
        expected_count = self.testing_vars['asset_search']['Count']
        self.assertGreaterEqual(len(assets), expected_count,
                              f"Search should return at least {expected_count} assets")

    def test_find_asset_tag(self):
        """Test finding asset by tag returns correct serial number."""
        asset = self.tax.find_asset_by_tag(self.testing_vars['asset2']['Tag'])
        expected_serial = self.testing_vars['asset2']['SerialNumber']
        self.assertEqual(asset['SerialNumber'], expected_serial,
                        f"Asset serial number should be {expected_serial}")

    def test_find_asset_SN(self):
        """Test finding asset by serial number returns correct tag."""
        asset = self.tax.find_asset_by_sn(self.testing_vars['asset2']['SerialNumber'])
        expected_tag = self.testing_vars['asset2']['Tag'].lstrip('0')
        actual_tag = asset['Tag'].lstrip('0')
        self.assertEqual(actual_tag, expected_tag, f"Asset tag should match {expected_tag}")

    def test_get_assets_by_location(self):
        """Test retrieving assets by location returns expected minimum count."""
        assets = self.tax.get_assets_by_location(self.testing_vars['location1'])
        expected_count = self.testing_vars['location1']['asset_count']
        self.assertGreaterEqual(len(assets), expected_count,
                              f"Location should have at least {expected_count} assets")

    def test_get_assets_by_locations(self):
        """Test retrieving assets by multiple locations returns expected minimum count."""
        locations = [self.testing_vars['location1'], self.testing_vars['location2']]
        assets = self.tax.get_assets_by_location(locations)
        expected_count = (self.testing_vars['location1']['asset_count'] + 
                         self.testing_vars['location2']['asset_count'])
        self.assertGreaterEqual(len(assets), expected_count,
                              f"Multiple locations should have at least {expected_count} assets")

    def test_get_assets_by_room(self):
        """Test retrieving assets by room returns expected minimum count."""
        location = self.tax.get_location_by_name(self.testing_vars['location3']['Name'])
        room1 = self.tax.get_room_by_name(location, self.testing_vars['room1']['Name'])
        assets = self.tax.get_assets_by_room(room1, max_results=100)
        expected_count = self.testing_vars['room1']['asset_count']
        self.assertGreaterEqual(len(assets), expected_count,
                              f"Room should have at least {expected_count} assets")

    def test_get_assets_by_owner(self):
        """Test retrieving assets by owner returns expected minimum count."""
        owner_email = self.testing_vars['owner']['PrimaryEmail']
        assets = self.tax.get_assets_by_owner(owner_email, max_results=100, disposed=True)
        expected_count = self.testing_vars['owner']['asset_count']
        self.assertGreaterEqual(len(assets), expected_count,
                              f"Owner should have at least {expected_count} assets")

    def test_get_assets_by_requesting_dept(self):
        """Test retrieving assets by requesting department returns expected minimum count."""
        dept_name = self.testing_vars['department']['Name']
        assets = self.tax.get_assets_by_requesting_department(dept_name, max_results=100, disposed=True)
        expected_count = self.testing_vars['department']['asset_count']
        self.assertGreaterEqual(len(assets), expected_count,
                              f"Department should have at least {expected_count} assets")

    def test_get_assets_by_product_model(self):
        """Test retrieving assets by product model returns expected minimum count."""
        model_name = self.testing_vars['product_model']['Name']
        assets = self.tax.get_assets_by_product_model(model_name, max_results=100, retired=True, disposed=True)
        expected_count = self.testing_vars['product_model']['asset_count']
        self.assertGreaterEqual(len(assets), expected_count,
                              f"Product model should have at least {expected_count} assets")

    def test_get_assets_by_product_type(self):
        """Test retrieving assets by product type returns expected minimum count."""
        type_name = self.testing_vars['product_type']['Name']
        assets = self.tax.get_assets_by_product_type(type_name, max_results=100, retired=True, disposed=True)
        expected_count = self.testing_vars['product_type']['asset_count']
        self.assertGreaterEqual(len(assets), expected_count,
                              f"Product type should have at least {expected_count} assets")

    def test_update_asset_status(self):
        """Test updating asset status for multiple assets and restore original states."""
        owner_email = self.testing_vars['owner']['PrimaryEmail']
        assets_to_update = self.tax.get_assets_by_owner(owner_email, max_results=100, disposed=True)
        
        # Store original statuses to restore later
        original_statuses = {}
        for asset in assets_to_update:
            original_statuses[asset['ID']] = str(asset['StatusID'])
        
        # Choose new status different from first asset's current status
        new_status = str(self.testing_vars['asset_status1']['ID'])
        first_status = str(assets_to_update[0]['StatusID'])
        if first_status == new_status:
            new_status = str(self.testing_vars['asset_status2']['ID'])
        
        # Test status update
        updated_assets = self.tax.update_assets(assets_to_update, {'StatusID': new_status})
        self.assertEqual(len(assets_to_update), len(updated_assets),
                        "Number of updated assets should match input count")
        for updated_asset in updated_assets:
            self.assertEqual(str(updated_asset['StatusID']), new_status,
                           f"Asset status should be updated to {new_status}")
        
        # Restore original statuses to not interfere with other tests
        for asset in updated_assets:
            if asset['ID'] in original_statuses:
                original_status = original_statuses[asset['ID']]
                if str(asset['StatusID']) != original_status:
                    try:
                        self.tax.update_assets(asset, {'StatusID': original_status})
                    except Exception:
                        # If restore fails, continue - better than failing the test entirely
                        pass

    def test_update_asset_owner(self):
        """Test updating asset owner and restore original state."""
        asset = self.tax.get_asset_by_id(self.testing_vars['asset1']['ID'])
        
        # Store original owner information
        original_owner_id = asset['OwningCustomerID']
        original_owner_name = asset['OwningCustomerName']
        
        # Choose a different owner for testing
        new_owner = self.testing_vars['owner']
        if asset['OwningCustomerID'] == new_owner['UID']:
            new_owner = self.testing_vars['owner_alt']
        
        # Test the owner change
        updated_asset = self.tax.change_asset_owner(asset, new_owner)[0]
        self.assertIsNotNone(updated_asset, "Asset should be successfully updated")
        self.assertEqual(updated_asset['OwningCustomerName'], new_owner['FullName'],
                        f"Asset owner should be updated to {new_owner['FullName']}")
        
        # Restore original owner to not interfere with other tests
        if original_owner_id:
            try:
                # Create owner data structure to restore original owner
                original_owner_data = {'UID': original_owner_id, 'FullName': original_owner_name}
                self.tax.change_asset_owner(updated_asset, original_owner_data)
            except Exception:
                # If restore fails, continue - better than failing the test entirely
                pass

    def test_update_asset_requesting_dept(self):
        """Test updating asset requesting department."""
        asset = self.tax.get_asset_by_id(self.testing_vars['asset1']['ID'])
        new_dept = self.testing_vars['department']
        if asset['RequestingDepartmentID'] == new_dept['ID']:
            new_dept = self.testing_vars['department_alt']
        updated_asset = self.tax.change_asset_requesting_dept(asset, new_dept)[0]
        self.assertEqual(updated_asset['RequestingDepartmentName'], new_dept['Name'],
                        f"Asset requesting department should be updated to {new_dept['Name']}")

    def test_custom_attribute_updating_id(self):
        asset = self.tax.get_asset_by_id(self.testing_vars['asset1']['ID'])
        new_attributes = self.testing_vars['attributes1']
        for i in asset['Attributes']:
            if str(i['ID']) == str(new_attributes[0]['ID']) and str(i['Value']) == str(new_attributes[0]['Value']):
                new_attributes = self.testing_vars['attributes2']
                break
        attrib_list = []
        for i in new_attributes:
            attrib_list.append(self.tax.build_asset_custom_attribute_value(i['ID'],i['Value']))
        updated_asset = self.tax.change_asset_custom_attribute_value(asset,attrib_list)[0]
        self.assertGreaterEqual(len(updated_asset['Attributes']),len(new_attributes))
        validate = self.tax.get_asset_by_id(self.testing_vars['asset1']['ID'])
        for desired in attrib_list:
            for existing in validate['Attributes']:
                if desired['ID'] == existing ['ID']:
                    self.assertEqual(str(desired['Value']), str(existing['Value']))

    def test_custom_attribute_updating_name(self):
        asset = self.tax.get_asset_by_id(self.testing_vars['asset1']['ID'])
        new_attributes = self.testing_vars['attributes1']
        for i in asset['Attributes']:
            if str(i['Name']) == str(new_attributes[0]['Name']) and str(i['Value']) == str(new_attributes[0]['Value']):
                new_attributes = self.testing_vars['attributes2']
        attrib_list = []
        for i in new_attributes:
            attrib_list.append(self.tax.build_asset_custom_attribute_value(i['Name'], i['Value']))
        updated_asset = self.tax.change_asset_custom_attribute_value(asset, attrib_list)[0]
        self.assertGreaterEqual(len(updated_asset['Attributes']),len(new_attributes))
        validate = self.tax.get_asset_by_id(self.testing_vars['asset1']['ID'])
        for desired in attrib_list:
            for existing in validate['Attributes']:
                if desired['ID'] == existing ['ID']:
                    self.assertEqual(str(desired['Value']), str(existing['Value']))

    def test_add_custom_attributes(self):
        asset = self.tax.get_asset_by_id(self.testing_vars['asset2']['ID'])
        change = {'Name': asset['Name']+'(Cleared)'}
        cleared_asset = self.tax.update_assets(asset, change, clear_custom_attributes=True)[0]
        validate = self.tax.get_asset_by_id(self.testing_vars['asset2']['ID'])
        self.assertEqual(len(validate['Attributes']), 0)
        self.assertEqual(len(cleared_asset['Attributes']), 0)
        new_attributes = self.testing_vars['attributes2']
        attrib_list = []
        for i in new_attributes:
            attrib_list.append(self.tax.build_asset_custom_attribute_value(i['ID'], i['Value']))
        updated_asset = self.tax.change_asset_custom_attribute_value(asset, attrib_list)[0]
        updated_asset = self.tax.update_assets(updated_asset,{'Name': asset['Name']})[0]
        self.assertGreaterEqual(len(updated_asset['Attributes']),len(new_attributes))
        validate = self.tax.get_asset_by_id(self.testing_vars['asset2']['ID'])
        self.assertEqual(len(validate['Attributes']), len(new_attributes))
        for desired in attrib_list:
            for existing in validate['Attributes']:
                if desired['ID'] == existing ['ID']:
                    self.assertEqual(str(desired['Value']), str(existing['Value']))

    def test_add_asset_user(self):
        """Test adding a user to an asset."""
        asset_id = self.testing_vars['asset2']['ID']
        person_uid = self.testing_vars['person1']['UID']
        
        # Clean up first to ensure consistent test state
        self.tax.delete_asset_users(asset_id, person_uid)
        users_before = self.tax.get_asset_users(asset_id)
        
        # Add the user
        self.tax.add_asset_user(asset_id, person_uid)
        users_after = self.tax.get_asset_users(asset_id)
        
        self.assertGreater(len(users_after), len(users_before),
                          "Asset should have more users after adding one")

    def test_get_asset_users(self):
        """Test retrieving asset users list."""
        asset_id = self.testing_vars['asset2']['ID']
        person_uid = self.testing_vars['person1']['UID']
        
        # Ensure there's at least one user
        self.tax.add_asset_user(asset_id, person_uid)
        asset_users = self.tax.get_asset_users(asset_id)
        
        self.assertGreater(len(asset_users), 0, "Asset should have at least one user")
        self.assertIn('Name', asset_users[0], "Asset user should have 'Name' field")

    def test_delete_asset_users(self):
        """Test deleting users from an asset."""
        asset_id = self.testing_vars['asset2']['ID']
        person_uid = self.testing_vars['person1']['UID']
        person_name = self.testing_vars['person1']['FullName']
        
        # Ensure user is added first
        self.tax.add_asset_user(asset_id, person_uid)
        
        # Delete the user
        self.tax.delete_asset_users(asset_id, person_uid)
        remaining_users = self.tax.get_asset_users(asset_id)
        
        for user in remaining_users:
            self.assertNotEqual(user['Name'], person_name,
                               "Deleted user should not appear in asset users list")

    def test_change_asset_location(self):
        """Test changing asset location."""
        asset_name = f'testing1.{self.timestamp}'
        new_asset = self.tax.create_asset(
            self.tax.build_asset(asset_name, asset_name,
                                 self.testing_vars['asset_status1']['Name'],
                                 self.testing_vars['location1']['Name']))
        
        target_location = self.testing_vars['location2']['Name']
        self.tax.change_asset_location(new_asset, target_location)
        updated_asset = self.tax.get_asset_by_id(new_asset['ID'])
        
        self.assertEqual(updated_asset['LocationName'], target_location,
                        f"Asset location should be updated to {target_location}")

    def test_clear_asset_custom_attributes(self):
        """Test clearing specific custom attributes from an asset."""
        asset_name = f'testing2.{self.timestamp}'
        new_asset = self.tax.create_asset(
            self.tax.build_asset(asset_name, asset_name,
                                 self.testing_vars['asset_status1']['Name'],
                                 asset_custom_attributes=self.testing_vars['attributes1']))
        
        attribute_name = self.testing_vars['attributes1'][0]['Name']
        updated_asset = self.tax.clear_asset_custom_attributes(new_asset, attribute_name)
        
        for attribute in updated_asset['Attributes']:
            self.assertNotEqual(attribute['Name'], attribute_name,
                               f"Attribute '{attribute_name}' should be cleared from asset")

    def test_get_asset_custom_attribute_value_by_name(self):
        new_asset = self.tax.create_asset(
            self.tax.build_asset(f'testing3.{self.timestamp}', f'testing3.{self.timestamp}',
                                 self.testing_vars['asset_status1']['Name'],
                                 asset_custom_attributes={'Attributes': [self.testing_vars['attributes1'][0]]}))
        validate = self.tax.get_asset_custom_attribute_value_by_name(new_asset,
                                                                     self.testing_vars['attributes1'][0]['Name'], True)
        self.assertEqual(validate, str(self.testing_vars['attributes1'][0]['choice1']['ID']))

    def test_copy_asset_attributes(self):
        sn1 = f'testing4.{self.timestamp}'
        new_asset1 = self.tax.create_asset(
            self.tax.build_asset(sn1, sn1, self.testing_vars['asset_status1']['Name'],
                                 asset_custom_attributes={'Attributes': [self.testing_vars['attributes1'][0]]}))
        sn2 = f'testing5.{self.timestamp}'
        new_asset2 = self.tax.create_asset(
            self.tax.build_asset(sn2, sn2, self.testing_vars['asset_status1']['Name']))
        self.tax.copy_asset_attributes(new_asset1, new_asset2, copy_name=True,
                                       new_status=self.testing_vars['asset_status2']['Name'])
        validate2 = self.tax.get_asset_by_id(new_asset2['ID'])
        validate1 = self.tax.get_asset_by_id(new_asset1['ID'])
        self.assertTrue(validate2['Attributes'][0]['Name'] == self.testing_vars['attributes1'][0]['Name'])
        self.assertTrue(validate1['StatusName'] == self.testing_vars['asset_status2']['Name'])

    def test_change_asset_custom_attributes(self):
        sn1 = f'testing4.{self.timestamp}'
        new_asset1 = self.tax.create_asset(
            self.tax.build_asset(sn1, sn1, self.testing_vars['asset_status1']['Name'],
                                 asset_custom_attributes={'Attributes': [self.testing_vars['attributes1'][0]]}))
        new_ca = self.tax.build_asset_custom_attribute_value(self.testing_vars['attributes1'][0]['Name'],
                                                             self.testing_vars['attributes1'][0]['choice1']['Name'])
        self.assertEqual(str(new_ca['Value']), str(self.testing_vars['attributes1'][0]['choice1']['Value']))
        changed_asset = self.tax.change_asset_custom_attribute_value(new_asset1['ID'], [new_ca])
        found = False
        for i in changed_asset[0]['Attributes']:
            if i['Name'] == self.testing_vars['attributes1'][0]['Name']:
                self.assertEqual(i['Value'], new_ca['Value'])
                found = True
        self.assertTrue(found)

    def test_move_child_assets(self):
        """Test moving child assets between parent assets."""
        child_asset_id = self.testing_vars['child_asset']['ID']
        original_parent_id = self.testing_vars['parent_asset']['ID']
        new_parent_id = self.testing_vars['asset1']['ID']
        
        # Move child to new parent
        self.tax.move_child_assets(original_parent_id, new_parent_id)
        child_asset = self.tax.get_asset_by_id(child_asset_id)
        self.assertEqual(str(child_asset['ParentID']), str(new_parent_id),
                        f"Child asset should be moved to parent {new_parent_id}")
        
        # Move child back to original parent
        self.tax.move_child_assets(new_parent_id, original_parent_id)
        child_asset_restored = self.tax.get_asset_by_id(child_asset_id)
        self.assertEqual(str(child_asset_restored['ParentID']), str(original_parent_id),
                        f"Child asset should be restored to original parent {original_parent_id}")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TdxAssetTesting)
    if len(argv) > 1:
        unittest.main()
    else:
        unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
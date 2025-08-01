import json
import os
import time
import unittest
from datetime import datetime as dt

from tdxlib import tdx_integration, tdx_config


class TdxIntegrationTesting(unittest.TestCase):
    """Test cases for TDX Integration base functionality."""
    
    tdx = None
    testing_vars = None
    is_admin = False
    timestamp = None
    temp_files = []

    @classmethod
    def setUpClass(cls):
        cls.tdx = tdx_integration.TDXIntegration('../tdxlib.ini', skip_initial_auth=True)
        testing_vars_file = './testing_vars.json'
        if os.path.isfile(testing_vars_file):
            with open(testing_vars_file, 'r') as f:
                cls.testing_vars = json.load(f)
        else:
            raise FileNotFoundError('Testing variables need to be populated in file "testing_vars.json" in the working '
                                   'directory. A sample file is available in testing/sample_ticket_testing_vars. '
                                   'Any *.json files are ignored by git.')
        cls.timestamp = dt.now().strftime('%Y%m%d%H%M%S')
    
    @classmethod
    def tearDownClass(cls):
        """Clean up any temporary files created during testing."""
        for temp_file in cls.temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_file_config(self):
        """Test configuration loading from a temporary INI file."""
        file_contents = """
[TDX API Settings]
org_name = loaded-from-file
sandbox = false
username = username
password = not-a-password
authtype = password
ticket_app_id = 987
asset_app_id = 876
caching = false
timezone = -0500
"""
        temp_file = f'./tdxlib_test{self.timestamp}.ini'
        self.__class__.temp_files.append(temp_file)
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        with open(temp_file, 'w') as f:
            f.write(file_contents)
        
        tdx = tdx_integration.TDXIntegration(temp_file, skip_initial_auth=True)
        self.assertIsInstance(tdx, tdx_integration.TDXIntegration)
        self.assertIsInstance(tdx.config, tdx_config.TDXConfig)
        self.assertGreater(len(tdx.config.api_url), 10)
        self.assertEqual(tdx.config.org_name, 'loaded-from-file')
        self.assertNotIn('//', tdx.config.api_url.lstrip('https://'),
                         f'Extra slash in URL {tdx.config.api_url}')

    def test_config_by_file(self):
        """Test configuration loading from INI file."""
        test_tdxlib = tdx_integration.TDXIntegration('../tdxlib.ini', skip_initial_auth=True)
        self.assertIsNotNone(test_tdxlib.config)
        self.assertGreater(len(test_tdxlib.config.api_url), 13)
        self.assertIn(self.testing_vars['org_name'], test_tdxlib.config.api_url)

    def test_config_by_dict(self):
        """Test configuration loading from dictionary."""
        test_dict = self.testing_vars['test_config_dict']
        test_tdxlib = tdx_integration.TDXIntegration(config=test_dict, skip_initial_auth=True)
        self.assertIsNotNone(test_tdxlib.config)
        self.assertGreater(len(test_tdxlib.config.api_url), 13)
        self.assertIn(self.testing_vars['org_name'], test_tdxlib.config.api_url)
        self.assertEqual(test_tdxlib.config.caching, test_dict['TDX API Settings']['caching'])

    def test_config_by_env(self):
        """Test configuration loading from environment variables."""
        test_dict = self.testing_vars['test_config_dict']['TDX API Settings']
        for k, v in test_dict.items():
            env_name = f'TDXLIB_{k.upper()}'
            os.environ[env_name] = str(v)
        os.environ.update()
        test_tdxlib = tdx_integration.TDXIntegration(skip_initial_auth=True)
        self.assertIsNotNone(test_tdxlib.config)
        self.assertGreater(len(test_tdxlib.config.api_url), 13)
        self.assertIn(self.testing_vars['org_name'], test_tdxlib.config.api_url)
        self.assertEqual(test_tdxlib.config.caching, test_dict['caching'])

    def test_authentication(self):
        """Test JWT authentication and token generation."""
        auth_result = self.tdx.auth()
        self.assertTrue(auth_result)
        self.assertIsNotNone(self.tdx.config.token)
        self.assertGreater(len(self.tdx.config.token), 200)

    def test_check_auth_exp(self):
        """Test automatic token refresh when expired."""
        # Set token exp to sometime in the past
        self.tdx.token_exp = 1579203044
        # Make an API call to check if old token will be refreshed
        standard = self.testing_vars['person1']
        result = self.tdx.get_person_by_uid(standard['UID'])
        self.assertIsNotNone(result)

    def test_get_location_by_id(self):
        """Test retrieving location by ID."""
        standard = self.testing_vars['location']
        result = self.tdx.get_location_by_id(standard['ID'])
        self.assertIsNotNone(result)
        self.assertEqual(result['Name'], standard['Name'])

    def test_get_account_by_id(self):
        """Test retrieving account by ID."""
        standard = self.testing_vars['account']
        result = self.tdx.get_account_by_id(standard['ID'])
        self.assertIsNotNone(result)
        self.assertEqual(result['Name'], standard['Name'])

    def test_get_group_by_id(self):
        """Test retrieving group by ID."""
        standard = self.testing_vars['group']
        result = self.tdx.get_group_by_id(standard['ID'])
        self.assertIsNotNone(result)
        self.assertEqual(result['Name'], standard['Name'])

    def test_get_person_by_uid(self):
        """Test retrieving person by UID."""
        standard = self.testing_vars['person1']
        result = self.tdx.get_person_by_uid(standard['UID'])
        self.assertIsNotNone(result)
        self.assertEqual(result['PrimaryEmail'], standard['PrimaryEmail'])

    def test_get_group_members_by_id(self):
        """Test retrieving group members by group ID."""
        result = self.tdx.get_group_members_by_id(self.testing_vars['group']['ID'])
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 2)

    def test_search_people_name(self):
        """Test searching for person by full name."""
        standard = self.testing_vars['person1']
        result = self.tdx.get_person_by_name_email(standard['FullName'])
        self.assertEqual(result['UID'], standard['UID'])

    def test_search_people_email(self):
        """Test searching for person by email address."""
        standard = self.testing_vars['person1']
        result = self.tdx.get_person_by_name_email(standard['PrimaryEmail'])
        self.assertEqual(result['UID'], standard['UID'])

    def test_get_all_accounts(self):
        """Test retrieving all accounts."""
        result = self.tdx.get_all_accounts()
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 2)

    def test_get_account_by_name(self):
        """Test retrieving account by exact name."""
        standard = self.testing_vars['account']
        result = self.tdx.get_account_by_name(standard['Name'])
        self.assertEqual(result['ID'], standard['ID'])

    def test_get_account_by_name_partial(self):
        """Test retrieving account by partial name match."""
        standard = self.testing_vars['account']
        result = self.tdx.get_account_by_name(standard['PartialName'])
        self.assertEqual(result['ID'], standard['ID'])

    def test_get_all_groups(self):
        """Test retrieving all groups."""
        result = self.tdx.get_all_groups()
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 2)

    def test_get_group_by_name(self):
        """Test retrieving group by exact name."""
        standard = self.testing_vars['group']
        result = self.tdx.get_group_by_name(standard['Name'])
        self.assertEqual(result['ID'], standard['ID'])

    def test_get_group_by_name_partial(self):
        """Test retrieving group by partial name match."""
        standard = self.testing_vars['group']
        result = self.tdx.get_group_by_name(standard['PartialName'])
        self.assertEqual(result['ID'], standard['ID'])

    def test_get_group_members_by_name(self):
        """Test retrieving group members by group name."""
        standard = self.testing_vars['group']
        result = self.tdx.get_group_members_by_name(standard['Name'])
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 2)

    def test_get_all_custom_attributes(self):
        """Test retrieving all custom attributes for ticket component."""
        result = self.tdx.get_all_custom_attributes(self.tdx.component_ids['ticket'])
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 2)

    def test_get_ca_by_name(self):
        """Test retrieving custom attribute by name and component ID."""
        standard = self.testing_vars['ticket_ca']
        type_id = self.tdx.component_ids[standard['type']]
        result = self.tdx.get_custom_attribute_by_name_id(standard['Name'], type_id)
        self.assertEqual(result['ID'], standard['ID'])

    def test_get_ca_value_by_name(self):
        """Test retrieving custom attribute choice value by name."""
        ca_standard = self.testing_vars['ticket_ca']
        standard = ca_standard['choice']
        type_id = self.tdx.component_ids[ca_standard['type']]
        ca = self.tdx.get_custom_attribute_by_name_id(ca_standard['Name'], type_id)
        result = self.tdx.get_custom_attribute_choice_by_name_id(ca, standard['Name'])
        self.assertEqual(result['ID'], standard['ID'])

    def test_get_all_locations(self):
        """Test retrieving all locations."""
        result = self.tdx.get_all_locations()
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 2)

    def test_get_location_by_name(self):
        """Test retrieving location by exact name."""
        standard = self.testing_vars['location']
        result = self.tdx.get_location_by_name(standard['Name'])
        self.assertEqual(result['ID'], standard['ID'])

    def test_get_location_by_name_partial(self):
        """Test retrieving location by partial name match."""
        standard = self.testing_vars['location']
        result = self.tdx.get_location_by_name(standard['PartialName'])
        self.assertEqual(result['ID'], standard['ID'])

    def test_get_room_by_name(self):
        """Test retrieving room by exact name within a location."""
        location = self.testing_vars['location']
        standard = self.testing_vars['room']
        location_obj = self.tdx.get_location_by_name(location['Name'])
        result = self.tdx.get_room_by_name(location_obj, standard['Name'])
        self.assertEqual(result['ID'], standard['ID'])

    def test_get_room_by_partial_name(self):
        """Test retrieving room by partial name match within a location."""
        location = self.testing_vars['location']
        standard = self.testing_vars['room']
        location_obj = self.tdx.get_location_by_name(location['Name'])
        result = self.tdx.get_room_by_name(location_obj, standard['PartialName'])
        self.assertEqual(result['ID'], standard['ID'])

    def test_create_account(self):
        """Test creating a new account (sandbox only)."""
        if not self.tdx.config.sandbox:
            self.skipTest('Skipping create test - not in sandbox environment')
            return
        
        name = 'Testing Account ' + self.timestamp
        additional_info = {'Address1': '123 Main Street'}
        ca = self.testing_vars['account_ca']
        custom_attributes = {ca['Name']: ca['choice']['Name']}
        
        account = self.tdx.create_account(name, self.tdx.config.username, additional_info,
                                          custom_attributes)
        self.assertIsNotNone(account)
        self.assertEqual(account['Address1'], additional_info['Address1'])
        self.assertEqual(account['Attributes'][0]['Value'], str(ca['choice']['ID']))
        self.assertEqual(account['Name'], name)

    def test_edit_account(self):
        """Test editing an existing account (sandbox only)."""
        if not self.tdx.config.sandbox:
            self.skipTest('Skipping edit test - not in sandbox environment')
            return
        
        # This will fail if test_create_account fails
        name = 'Testing Account ' + self.timestamp
        changed_attributes = {'Name': 'Edited Account' + self.timestamp}
        edited_account = self.tdx.edit_account(name, changed_attributes)
        self.assertEqual(edited_account['Name'], changed_attributes['Name'])

    def test_create_room(self):
        """Test creating a new room (sandbox only, admin required)."""
        if not self.tdx.config.sandbox:
            self.skipTest('Skipping create test - not in sandbox environment')
            return
        if not self.is_admin:
            self.skipTest('Skipping create test - admin privileges required')
            return
        
        location = self.tdx.get_location_by_name(self.testing_vars['location']['Name'])
        name = 'Testing Room ' + self.timestamp
        description = 'Testing room Description'
        new_room = self.tdx.create_room(location, name, description=description)
        time.sleep(2)
        retrieved_room = self.tdx.get_room_by_name(location, name)
        self.assertEqual(new_room['Name'], retrieved_room['Name'])


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TdxIntegrationTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)

import time
import unittest
import json
from datetime import datetime as dt
from tdxlib import tdx_integration, tdx_config
import os


class TdxIntegrationTesting(unittest.TestCase):
    timestamp = dt.today().strftime("%d-%B-%Y %H:%M:%S")
    # Create TDXIntegration object for testing use. Called before testing methods.

    def setUp(self):
        # Will only run non-admin tests
        self.is_admin = False
        testing_vars_file = './testing_vars.json'
        self.tdx = tdx_integration.TDXIntegration('../tdxlib.ini', skip_initial_auth=True)
        right_now = dt.today()
        if os.path.isfile(testing_vars_file):
            with open(testing_vars_file, 'r') as f:
                self.testing_vars = json.load(f)
        else:
            print('Testing variables need to be populated in file "testing_vars.json" in the working directory.',
                  'A sample file is available in testing/sample_ticket_testing_vars. Any *.json files are ignored by git.')

    def test_file_config(self, config_parser):
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
            if os.path.exists('./tdxlib_test.ini'):
                raise Exception("Testing ini file already exists. Please remove it before running tests.")
            with open('./tdxlib_test.ini', 'w') as f:
                f.write(file_contents)
            tdx = tdx_integration.TDXIntegration('./tdxlib_test.ini', skip_initial_auth=True)
            self.assertIsInstance(tdx, tdx_integration.TDXIntegration)
            self.assertIsInstance(tdx.config, tdx_config.TDXConfig)
            self.assertGreater(len(tdx.config.api_url), 10)
            self.assertEqual(tdx.config.org_name, 'loaded-from-file')
            self.assertNotIn('//', tdx.config.api_url.lstrip('https://'),
                             f'Extra slash in URL {tdx.config.api_url}')
            os.remove('./tdxlib_test.ini')

    def test_config_by_file(self):
        test_tdxlib = tdx_integration.TDXIntegration('../tdxlib.ini', skip_initial_auth=True)
        self.assertIsNotNone(test_tdxlib.config)
        self.assertGreater(len(test_tdxlib.config.api_url), 13)
        self.assertTrue(self.testing_vars['org_name'] in test_tdxlib.config.api_url)

    def test_config_by_dict(self):
        test_dict = self.testing_vars['test_config_dict']
        test_tdxlib = tdx_integration.TDXIntegration(config=test_dict, skip_initial_auth=True)
        self.assertIsNotNone(test_tdxlib.config)
        self.assertGreater(len(test_tdxlib.config.api_url), 13)
        self.assertTrue(self.testing_vars['org_name'] in test_tdxlib.config.api_url)
        self.assertFalse(test_tdxlib.config.caching)

    def test_config_by_env(self):
        test_dict = self.testing_vars['test_config_dict']['TDX API Settings']
        for k,v in test_dict.items():
            env_name = f'TDXLIB_{k.upper()}'
            os.environ[env_name] = str(v)
        os.environ.update()
        test_tdxlib = tdx_integration.TDXIntegration(skip_initial_auth=True)
        self.assertIsNotNone(test_tdxlib.config)
        self.assertGreater(len(test_tdxlib.config.api_url), 13)
        self.assertTrue(self.testing_vars['org_name'] in test_tdxlib.config.api_url)
        self.assertFalse(test_tdxlib.config.caching)

    def test_authentication(self):
        if not self.tdx:
            self.setUp()
        self.assertIsNotNone(self.tdx.config.token)
        self.assertGreater(len(self.tdx.config.token), 200)

    def test_check_auth_exp(self):
        if not self.tdx:
            self.setUp()
        # Set token exp to sometime in the past
        self.tdx.token_exp = 1579203044
        # Make an API call to check if old token will be refreshed
        standard = self.testing_vars['person1']
        test = self.tdx.get_person_by_uid(standard['UID'])
        self.assertTrue(test)

    def test_get_location_by_id(self):
        if not self.tdx:
            self.setUp()
        standard = self.testing_vars['location']
        test = self.tdx.get_location_by_id(standard['ID'])
        self.assertTrue(test)
        self.assertEqual(test['Name'], standard['Name'])

    def test_get_account_by_id(self):
        if not self.tdx:
            self.setUp()
        standard = self.testing_vars['account']
        test = self.tdx.get_account_by_id(standard['ID'])
        self.assertTrue(test)
        self.assertEqual(test['Name'], standard['Name'])

    def test_get_group_by_id(self):
        if not self.tdx:
            self.setUp()
        standard = self.testing_vars['group']
        test = self.tdx.get_group_by_id(standard['ID'])
        self.assertTrue(test)
        self.assertEqual(test['Name'], standard['Name'])

    def test_get_person_by_uid(self):
        if not self.tdx:
            self.setUp()
        standard = self.testing_vars['person1']
        test = self.tdx.get_person_by_uid(standard['UID'])
        self.assertTrue(test)
        self.assertEqual(test['PrimaryEmail'], standard['PrimaryEmail'])

    def test_get_group_members_by_id(self):
        if not self.tdx:
            self.setUp()
        test = self.tdx.get_group_members_by_id(self.testing_vars['group']['ID'])
        self.assertTrue(isinstance(test, list))
        self.assertGreaterEqual(len(test), 2)

    def test_search_people_name(self):
        if not self.tdx:
            self.setUp()
        standard = self.testing_vars['person1']
        test = self.tdx.get_person_by_name_email(standard['FullName'])
        self.assertEqual(test['UID'], standard['UID'])

    def test_search_people_email(self):
        if not self.tdx:
            self.setUp()
        standard = self.testing_vars['person1']
        test = self.tdx.get_person_by_name_email(standard['PrimaryEmail'])
        self.assertEqual(test['UID'], standard['UID'])

    def test_get_all_accounts(self):
        if not self.tdx:
            self.setUp()
        test = self.tdx.get_all_accounts()
        self.assertTrue(isinstance(test, list))
        self.assertGreaterEqual(len(test), 2)

    def test_get_account_by_name(self):
        if not self.tdx:
            self.setUp()
        standard = self.testing_vars['account']
        test = self.tdx.get_account_by_name(standard['Name'])
        self.assertEqual(test['ID'],standard['ID'])

    def test_get_account_by_name_partial(self):
        if not self.tdx:
            self.setUp()
        standard = self.testing_vars['account']
        test = self.tdx.get_account_by_name(standard['PartialName'])
        self.assertEqual(test['ID'], standard['ID'])

    def test_get_all_groups(self):
        if not self.tdx:
            self.setUp()
        test = self.tdx.get_all_groups()
        self.assertTrue(isinstance(test, list))
        self.assertGreaterEqual(len(test), 2)

    def test_get_group_by_name(self):
        if not self.tdx:
            self.setUp()
        standard = self.testing_vars['group']
        test= self.tdx.get_group_by_name(standard['Name'])
        self.assertEqual(test['ID'], standard['ID'])

    def test_get_group_by_name_partial(self):
        if not self.tdx:
            self.setUp()
        standard = self.testing_vars['group']
        test = self.tdx.get_group_by_name(standard['PartialName'])
        self.assertEqual(test['ID'], standard['ID'])

    def test_get_group_members_by_name(self):
        if not self.tdx:
            self.setUp()
        standard = self.testing_vars['group']
        test = self.tdx.get_group_members_by_name(standard['Name'])
        self.assertTrue(isinstance(test, list))
        self.assertGreaterEqual(len(test),2)

    def test_get_all_custom_attributes(self):
        if not self.tdx:
            self.setUp()
        test = self.tdx.get_all_custom_attributes(self.tdx.component_ids['ticket'])
        self.assertTrue(isinstance(test, list))
        self.assertGreaterEqual(len(test), 2)

    def test_get_ca_by_name(self):
        if not self.tdx:
            self.setUp()
        standard = self.testing_vars['ticket_ca']
        type_id = self.tdx.component_ids[standard['type']]
        test = self.tdx.get_custom_attribute_by_name_id(standard['Name'], type_id)
        self.assertEqual(test['ID'], standard['ID'])

    def test_get_ca_value_by_name(self):
        if not self.tdx:
            self.setUp()
        ca_standard = self.testing_vars['ticket_ca']
        standard = ca_standard['choice']
        type_id = self.tdx.component_ids[ca_standard['type']]
        ca = self.tdx.get_custom_attribute_by_name_id(ca_standard['Name'], type_id)
        test = self.tdx.get_custom_attribute_choice_by_name_id(ca, standard['Name'])
        self.assertEqual(test['ID'], standard['ID'])

    def test_get_all_locations(self):
        if not self.tdx:
            self.setUp()
        test = self.tdx.get_all_locations()
        self.assertTrue(isinstance(test, list))
        self.assertGreaterEqual(len(test), 2)

    def test_get_location_by_name(self):
        if not self.tdx:
            self.setUp()
        standard = self.testing_vars['location']
        test = self.tdx.get_location_by_name(standard['Name'])
        self.assertEqual(test['ID'], standard['ID'])

    def test_get_location_by_name_partial(self):
        if not self.tdx:
            self.setUp()
        standard = self.testing_vars['location']
        test = self.tdx.get_location_by_name(standard['PartialName'])
        self.assertEqual(test['ID'], standard['ID'])

    def test_get_room_by_name(self):
        if not self.tdx:
            self.setUp()
        location = self.testing_vars['location']
        standard = self.testing_vars['room']
        test_location = self.tdx.get_location_by_name(location['Name'])
        test_room = self.tdx.get_room_by_name(test_location, standard['Name'])
        self.assertEqual(test_room['ID'], standard['ID'])

    def test_get_room_by_partial_name(self):
        if not self.tdx:
            self.setUp()
        location = self.testing_vars['location']
        standard = self.testing_vars['room']
        test_location = self.tdx.get_location_by_name(location['Name'])
        test_room = self.tdx.get_room_by_name(test_location, standard['PartialName'])
        self.assertEqual(test_room['ID'], standard['ID'])

    def test_create_account(self):
        if not self.tdx:
            self.setUp()
        if not self.tdx.config.sandbox:
            return
        name = 'Testing Account ' + TdxIntegrationTesting.timestamp
        additional_info = {'Address1': '123 Main Street'}
        ca = self.testing_vars['account_ca']
        custom_attributes = {ca['Name']:ca['choice']['Name']}
        account = self.tdx.create_account(name, self.tdx.config.username, additional_info,
                                          custom_attributes)
        self.assertTrue(account)
        self.assertEqual(account['Address1'], additional_info['Address1'])
        self.assertEqual(account['Attributes'][0]['Value'], str(ca['choice']['ID']))
        self.assertEqual(account['Name'], name)

    def test_edit_account(self):
        if not self.tdx:
            self.setUp()
        if not self.tdx.config.sandbox:
            return
        # This will fail if test_create_account fails
        name = 'Testing Account ' + TdxIntegrationTesting.timestamp
        changed_attributes = {'Name': 'Edited Account' + TdxIntegrationTesting.timestamp}
        edited_account = self.tdx.edit_account(name, changed_attributes)
        self.assertEqual(edited_account['Name'], changed_attributes['Name'])

    def test_create_room(self):
        if not self.tdx:
            self.setUp()
        if not self.tdx.config.sandbox:
            return
        if not self.is_admin:
            return
        location = self.tdx.get_location_by_name(self.testing_vars['location']['Name'])
        name = 'Testing Room ' + TdxIntegrationTesting.timestamp
        description = 'Testing room Description'
        new_room = self.tdx.create_room(location, name, description=description)
        time.sleep(2)
        test_room = self.tdx.get_room_by_name(location, name)
        self.assertEqual(new_room['Name'], test_room['Name'])


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TdxIntegrationTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)

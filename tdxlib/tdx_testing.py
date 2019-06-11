import unittest
import json
from datetime import datetime as dt
from tdxlib import tdx_integration


class TdxTesting(unittest.TestCase):

    # Create TDXIntegration object for testing use. Called before testing methods.
    def setUp(self):
        self.tdx = tdx_integration.TDXIntegration()
        right_now = dt.today()
        self.timestamp = right_now.strftime("%d-%B-%Y %H:%M:%S")
        with open('testing_vars.json', 'r') as f:
            self.testing_vars = json.load(f)

    def test_authentication(self):
        self.assertGreater(len(self.tdx.token), 200)

    def test_get_location_by_id(self):
        standard = self.testing_vars['location']
        test = self.tdx.get_location_by_id(standard['ID'])
        self.assertTrue(test)
        self.assertEqual(test['Name'], standard['Name'])

    def test_get_account_by_id(self):
        standard = self.testing_vars['account']
        test = self.tdx.get_account_by_id(standard['ID'])
        self.assertTrue(test)
        self.assertEqual(test['Name'], standard['Name'])

    def test_get_group_by_id(self):
        standard = self.testing_vars['group']
        test = self.tdx.get_group_by_id(standard['ID'])
        self.assertTrue(test)
        self.assertEqual(test['Name'], standard['Name'])

    def test_get_person_by_uid(self):
        standard = self.testing_vars['person']
        test = self.tdx.get_person_by_uid(standard['UID'])
        self.assertTrue(test)
        self.assertEqual(test['PrimaryEmail'], standard['PrimaryEmail'])

    def test_get_group_members_by_id(self):
        test = self.tdx.get_group_members_by_id(self.testing_vars['group']['ID'])
        self.assertGreaterEqual(len(test), 2)

    def test_get_ca_by_name(self):
        standard = self.testing_vars['ca']
        type_id = self.tdx.component_ids[standard['type']]
        test = self.tdx.get_custom_attribute_by_name(standard['Name'], type_id)
        self.assertEqual(test['ID'],standard['ID'])

    def test_search_people_name(self):
        standard = self.testing_vars['person']
        test = self.tdx.search_people(standard['FullName'])
        self.assertEqual(test['UID'], standard['UID'])

    def test_search_people_email(self):
        standard = self.testing_vars['person']
        test = self.tdx.search_people(standard['PrimaryEmail'])
        self.assertEqual(test['UID'], standard['UID'])

    def test_get_all_accounts(self):
        test = self.tdx.get_all_accounts()
        self.assertGreaterEqual(len(test), 2)

    def test_get_all_accounts(self):
        test = self.tdx.get_all_accounts()
        self.assertGreaterEqual(len(test), 2)

    def test_get_account_by_name(self):
        standard = self.testing_vars['account']
        test = self.tdx.get_account_by_name(standard['Name'])
        self.assertEqual(test['ID'],standard['ID'])


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TdxTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)

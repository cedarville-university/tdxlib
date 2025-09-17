import json
import os
import unittest
from datetime import datetime as dt

from tdxlib import tdx_client_portal_integration
from tdxlib.tdx_api_exceptions import TdxApiHTTPRequestError


class TdxClientPortalIntegrationTesting(unittest.TestCase):
    """Test cases for TDX Client Portal Integration functionality."""
    
    tdx = None
    testing_vars = None
    timestamp = None

    @classmethod
    def setUpClass(cls):
        cls.tdx = tdx_client_portal_integration.TDXClientPortalIntegration('tdxlib.ini', skip_initial_auth=True)
        testing_vars_file = './testing/client_portal_testing_vars.json'
        if os.path.isfile(testing_vars_file):
            with open(testing_vars_file, 'r') as f:
                cls.testing_vars = json.load(f)
        else:
            raise FileNotFoundError('Testing variables need to be populated in file "client_portal_testing_vars.json" in the working '
                                   'directory. A sample file is available in testing/sample_client_portal_testing_vars. '
                                   'Any *.json files are ignored by git.')
        cls.timestamp = dt.now().strftime('%Y%m%d%H%M%S')

    def test_authentication(self):
        """Test JWT authentication and token generation."""
        auth_result = self.tdx.auth()
        self.assertTrue(auth_result)
        self.assertIsNotNone(self.tdx.config.token)
        self.assertGreater(len(self.tdx.config.token), 200)

    def test_get_article_by_id(self):
        """Test retrieving an article by ID."""
        standard = self.testing_vars['article']
        result = self.tdx.get_article_by_id(standard['ID'])
        self.assertIsNotNone(result)
        self.assertEqual(result['ID'], standard['ID'])
        self.assertEqual(result['Subject'], standard['Subject'])

    def test_get_article_by_id_invalid(self):
        """Test retrieving an article with invalid ID returns None."""
        result = self.tdx.get_article_by_id('999999')
        self.assertIsNone(result)

    def test_get_all_article_categories(self):
        """Test retrieving all article categories."""
        result = self.tdx.get_all_article_categories()
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        # Verify cache is working by checking cache was populated
        self.assertIn('article_category', self.tdx.cache)
        self.assertIsInstance(self.tdx.cache['article_category'], list)

    def test_get_all_article_categories_public_only(self):
        """Test retrieving all public article categories."""
        result = self.tdx.get_all_article_categories(public_only=True)
        self.assertIsInstance(result, list)
        # All returned categories should be public
        for category in result:
            self.assertTrue(category.get('IsPublic', False))

    def test_get_article_category_by_name_id(self):
        """Test retrieving article category by name or ID."""
        standard = self.testing_vars['article_category']
        # Test by ID
        result = self.tdx.get_article_category_by_name_id(standard['ID'])
        self.assertIsNotNone(result)
        self.assertEqual(result['ID'], standard['ID'])
        
        # Test by name
        result = self.tdx.get_article_category_by_name_id(standard['Name'])
        self.assertIsNotNone(result)
        self.assertEqual(result['Name'], standard['Name'])

    def test_get_article_category_by_name_id_invalid(self):
        """Test retrieving article category with invalid name/ID raises exception."""
        with self.assertRaises(TdxApiHTTPRequestError):
            self.tdx.get_article_category_by_name_id('NonExistentCategory')

    def test_get_all_service_categories(self):
        """Test retrieving all service categories."""
        result = self.tdx.get_all_service_categories()
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        # Verify cache is working by checking cache was populated
        self.assertIn('service_category', self.tdx.cache)
        self.assertIsInstance(self.tdx.cache['service_category'], list)

    def test_get_service_category_by_name_id(self):
        """Test retrieving service category by name or ID."""
        standard = self.testing_vars['service_category']
        # Test by ID
        result = self.tdx.get_service_category_by_name_id(standard['ID'])
        self.assertIsNotNone(result)
        self.assertEqual(result['ID'], standard['ID'])
        
        # Test by name
        result = self.tdx.get_service_category_by_name_id(standard['Name'])
        self.assertIsNotNone(result)
        self.assertEqual(result['Name'], standard['Name'])

    def test_get_service_category_by_name_id_invalid(self):
        """Test retrieving service category with invalid name/ID raises exception."""
        with self.assertRaises(TdxApiHTTPRequestError):
            self.tdx.get_service_category_by_name_id('NonExistentCategory')

    def test_get_service_by_id(self):
        """Test retrieving a service by ID."""
        standard = self.testing_vars['service']
        result = self.tdx.get_service_by_id(standard['ID'])
        self.assertIsNotNone(result)
        self.assertEqual(result['ID'], standard['ID'])
        self.assertEqual(result['Name'], standard['Name'])

    def test_get_service_by_id_invalid(self):
        """Test retrieving a service with invalid ID returns None."""
        result = self.tdx.get_service_by_id('999999')
        self.assertIsNone(result)

    def test_search_articles_string(self):
        """Test searching articles with string criteria."""
        search_term = self.testing_vars['article_search']['search_term']
        result = self.tdx.search_articles(search_term, max_results=5)
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 5)
        if len(result) > 0:
            # Verify articles contain search term
            found_match = any(search_term.lower() in article.get('Subject', '').lower() or 
                            search_term.lower() in article.get('Body', '').lower() 
                            for article in result)
            self.assertTrue(found_match)

    def test_search_articles_dict(self):
        """Test searching articles with dictionary criteria."""
        search_dict = {'SearchText': self.testing_vars['article_search']['search_term']}
        result = self.tdx.search_articles(search_dict, max_results=5)
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 5)

    def test_search_articles_with_category(self):
        """Test searching articles within a specific category."""
        search_term = self.testing_vars['article_search']['search_term']
        category = self.testing_vars['article_category']['Name']
        result = self.tdx.search_articles(search_term, max_results=5, category=category)
        self.assertIsInstance(result, list)

    def test_search_articles_invalid_criteria(self):
        """Test searching articles with invalid criteria type raises exception."""
        with self.assertRaises(TypeError):
            self.tdx.search_articles(12345)

    def test_search_services_string(self):
        """Test searching services with string criteria."""
        search_term = self.testing_vars['service_search']['search_term']
        result = self.tdx.search_services(search_term, max_results=5)
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 5)

    def test_search_services_dict(self):
        """Test searching services with dictionary criteria."""
        search_dict = {'SearchText': self.testing_vars['service_search']['search_term']}
        result = self.tdx.search_services(search_dict, max_results=5)
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 5)

    def test_search_services_with_category(self):
        """Test searching services within a specific category."""
        search_term = self.testing_vars['service_search']['search_term']
        category = self.testing_vars['service_category']['Name']
        result = self.tdx.search_services(search_term, max_results=5, category=category)
        self.assertIsInstance(result, list)

    def test_search_services_invalid_criteria(self):
        """Test searching services with invalid criteria type raises exception."""
        with self.assertRaises(TypeError):
            self.tdx.search_services(12345)

    def test_clean_cache(self):
        """Test cache cleaning functionality."""
        # First populate the cache
        self.tdx.get_all_article_categories()
        self.tdx.get_all_service_categories()
        self.assertIn('article_category', self.tdx.cache)
        self.assertIn('service_category', self.tdx.cache)
        
        # Clean cache and verify it's empty
        self.tdx.clean_cache()
        self.assertEqual(self.tdx.cache['article_category'], {})
        self.assertEqual(self.tdx.cache['service_category'], {})

    def test_make_call_kb(self):
        """Test making a call to knowledge base API."""
        result = self.tdx.make_call('categories', 'get', use_kb=True)
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)

    def test_make_call_services(self):
        """Test making a call to services API."""
        result = self.tdx.make_call('categories', 'get', use_kb=False)
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TdxClientPortalIntegrationTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)
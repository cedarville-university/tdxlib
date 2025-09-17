from tdxlib.tdx_integration import TDXIntegration
from tdxlib.tdx_api_exceptions import TdxApiHTTPRequestError

class TDXClientPortalIntegration(TDXIntegration):
    # These are hard-coded by TeamDynamix and not accessible through the API
    article_statuses = {
        'NotSubmitted': 1,
        'Submitted': 2 ,
        'Approved': 3,
        'Rejected': 4,
        'Archived': 5
    }

    def __init__(self, filename: str = "tdxlib.ini", config=None, skip_initial_auth: bool = False):
        TDXIntegration.__init__(self, filename, config, skip_initial_auth=skip_initial_auth)
        if self.config.client_portal_app_id is None:
            raise RuntimeError("Client Portal App Id is required. Check your configuration.")
        self.clean_cache()

    def clean_cache(self):
        """
        Clears the tdx_ticket_integration cache.

        :return:  None

        """
        super().clean_cache()
        self.cache['article_category'] = {}
        self.cache['service_category'] = {}

    def get_services_url(self, ):
        return '/' + str(self.config.client_portal_app_id) + '/services'

    def get_kb_url(self, ):
        return '/' + str(self.config.client_portal_app_id) + '/knowledgebase'

    def _make_client_portal_call(self, path: str, action: str, post_body: dict = None, use_kb: bool = False):
        if use_kb:
            url_string = self.get_kb_url()
        else:
            url_string = self.get_services_url()
        path_str = str(path)
        if len(path_str) > 0:
            url_string += '/' + path_str
        if action == 'get':
            return self.make_get(url_string)
        if action == 'delete':
            return self.make_delete(url_string)
        if action == 'post' and post_body:
            return self.make_post(url_string, post_body)
        if action == 'put' and post_body:
            return self.make_put(url_string, post_body)
        if action == 'patch' and post_body:
            return self.make_patch(url_string, post_body)
        raise TdxApiHTTPRequestError('No method ' + action + ' or no post information')

    def make_call(self, url: str, action: str, post_body: dict = None, use_kb: bool = False):
        """
        Makes an HTTP call using the Tickets API information.

        :param url: The URL (everything after tickets/) to call
        :param action: The HTTP action (get, put, post, delete, patch) to perform.
        :param post_body: A dict of the information to post, put, or patch. Not used for get/delete.

        :return: the API response as a python dict or list

        """
        return self._make_client_portal_call(url, action, post_body, use_kb=use_kb)

    def get_article_by_id(self, article_id: str) -> dict:
        """
        Gets an article by its ID.

        :param article_id: The ID of the article to get.

        :return: A dict of the article information.

        """
        return self.make_call(article_id, 'get', use_kb=True)

    def get_all_article_categories(self, public_only=True) -> list:
        """
        Gets all article categories.

        :return: A list of dicts of article categories.

        """
        if 'article_category' in self.cache and self.cache['article_category']:
            categories = self.cache['article_category']
        else:
            categories = self.make_call('categories', 'get', use_kb=True)
            self.cache['article_category'] = categories
        
        if public_only:
            categories = [cat for cat in categories if cat.get('IsPublic', False)]
        return categories

    def get_article_category_by_name_id(self, category_id: str) -> dict:
        """
        Gets an article category by its Name or ID.

        :param category_id: The name ID of the article category to get.

        :return: A dict of the article category information.

        """
        categories = self.get_all_article_categories()
        for category in categories:
            if category.get('ID', None) == category_id:
                return category
            if str(category_id) in category.get('Name', ""):
                return category
        raise TdxApiHTTPRequestError(f'No article category with name or id {category_id}')

    def get_all_service_categories(self) -> list:
        """
        Gets all service categories.

        :return: A list of dicts of service categories.

        """
        if 'service_category' in self.cache and self.cache['service_category']:
            return self.cache['service_category']
        categories = self.make_call('categories', 'get', use_kb=False)
        self.cache['service_category'] = categories
        return categories

    def get_service_category_by_name_id(self, category_id: str) -> dict:
        """
        Gets a service category by its Name or ID.

        :param id: The name ID of the service category to get.

        :return: A dict of the service category information.

        """
        categories = self.get_all_service_categories()
        for category in categories:
            if category.get('ID', None) == category_id:
                return category
            if str(category_id) in category.get('Name', ""):
                return category
        raise TdxApiHTTPRequestError(f'No service category with id {category_id}')

    def get_service_by_id(self, service_id: str) -> dict:
        """
        Gets a service by its ID.

        :param service_id: The ID of the service to get.

        :return: A dict of the service information.

        """
        return self.make_call(service_id, 'get', use_kb=False)

    def search_articles(self, criteria: (str, dict),
                        max_results: int = 10,
                        public_only: bool = True,
                        published_only: bool = True,
                        category: str = "") -> list:
        """
        Searches articles.

        :param criteria: A string or dict of search criteria.
        :param max_results: The maximum number of results to return.
        :param public_only: If True, only return public articles.
        :param category: The name or ID of the category to search within.

        :return: A list of dicts of articles.

        """
        # Set up search body
        search_body = {'ReturnCount': max_results,
                       'Status': self.article_statuses['Approved'],
                       'IncludeArticleBodies': True}
        if public_only:
               search_body['IsPublic'] = True
        if published_only:
            search_body['IsPublished'] = True
        if category:
            cat = self.get_article_category_by_name_id(category)
            if cat is not None and cat.get('ID', None) is not None:
                search_body['CategoryID'] = cat['ID']

        if type(criteria) is str:
            search_body['SearchText'] = criteria
        elif type(criteria) is dict:
            search_body.update(criteria)
        else:
            raise TypeError("Can't search articles with" + str(type(criteria)))
        article_list = self.make_call('search', 'post', search_body, use_kb=True)
        return article_list

    def search_services(self, criteria: (str, dict),
                        max_results: int = 10,
                        public_only: bool = True,
                        category: str = "") -> list:
        """
        Searches services.

        :param criteria: A string or dict of search criteria.
        :param max_results: The maximum number of results to return.
        :param public_only: If True, only return public services.
        :param category: The name or ID of the category to search within.

        :return: A list of dicts of services.

        """
        # Set up search body
        search_body = {'ReturnCount': max_results,
                       'IsActive': True,
                       'IncludeLongDescription': True}
        if public_only:
            search_body['IsPublic'] = True
        if category and len(category) > 0:
            cat = self.get_service_category_by_name_id(category)
            if cat is not None and cat.get('ID', None) is not None:
                search_body['CategoryID'] = cat['ID']
        if type(criteria) is str:
            search_body['SearchText'] = criteria
        elif type(criteria) is dict:
            search_body.update(criteria)
        else:
            raise TypeError("Can't search services with" + str(type(criteria)))
        service_list = self.make_call('search', 'post', search_body, use_kb=False)
        return service_list
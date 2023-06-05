import requests
import json
import tdxlib.tdx_api_exceptions
import tdxlib.tdx_constants
import tdxlib.tdx_config
import datetime
import time
from typing import BinaryIO
import jwt
import logging


class TDXIntegration:
    component_ids = tdxlib.tdx_constants.component_ids

    def __init__(self, filename: str = None, config: dict = None):
        self.cache = dict()
        self.logger = logging.getLogger('tdx_integration')
        self.config = tdxlib.tdx_config.TDXConfig(filename, config)
        self.setup_logs()
        self.clean_cache()
        self.check_auth_init()

    def setup_logs(self):
        if self.config.log_level:
            self.logger = logging.getLogger('tdx_integration')
            self.logger.setLevel(logging.getLevelName(self.config.log_level))

    def check_auth_init(self):
        if not self.config.auth_type or self.config.auth_type == 'password':
            if not self.auth():
                self.logger.error(f"Login Failed. Username or password in {self.config.filename} likely incorrect.")
        elif self.config.auth_type == 'token':
            if self.config.token is None:
                self.config.token_exp = time.time()
                self.logger.info("Skipping initial authentication, no token provided yet.")
            else:
                if not (self.auth()):
                    self.logger.error(f"Login Failed. Username or password in {self.config.filename} likely incorrect.")

    def set_token(self, token: str):
        self.config.token = token

    def auth(self) -> bool:
        """
        Internal method to authenticate to the TDX api using the selected method
        Stores a token in the token property, used for future calls. Returns true for success, false for failure.
        """
        if not self.config.auth_type or self.config.auth_type == 'password':
            try:
                response = requests.post(
                    url=str(self.config.api_url) + '/auth',
                    headers={
                        "Content-Type": "application/json; charset=utf-8",
                    },
                    data=json.dumps({
                        "username": self.config.username,
                        "password": self.config.password
                    })
                )
                if response.status_code != 200:
                    raise tdxlib.tdx_api_exceptions.TdxApiHTTPError(" Response code: " + str(response.status_code) +
                                                                    " " + response.reason + " " + " Returned: " +
                                                                    response.text)
                else:
                    self.config.token = response.text
                    time.sleep(1)
                    # Decode token to identify expiration date
                    decoded = jwt.decode(self.config.token,
                                         algorithms=['HS256'],
                                         options={'verify_signature': False},
                                         audience="https://www.teamdynamix.com/")
                    self.config.token_exp = decoded['exp']
                    return True

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Auth request Failed. Exception: {str(e)}")
                return False
            except tdxlib.tdx_api_exceptions.TdxApiHTTPError as e:
                self.logger.error(str(e))
                return False
        elif self.config.auth_type == 'token':
            if self.config.token is None:
                self.config.token_exp = time.time()
                self.logger.info("Skipping initial authentication, no token provided yet.")
            # Decode token to identify expiration date
            decoded = jwt.decode(self.config.token,
                                 algorithms=['HS256'],
                                 options={'verify_signature': False},
                                 audience="https://www.teamdynamix.com/")
            self.config.token_exp = decoded['exp']
            return True
        else:
            return False

    def _check_auth_exp(self) -> bool:
        """
        Internal method to check the expiration of the stored access token.
        If it is expired, call auth() to get a new token.
        """
        # If token is expired or will expire in the next minute, get new token
        if self.config.token_exp:
            if self.config.token_exp < time.time() + 60:
                self.logger.info(f"Token expires at {str(datetime.datetime.utcfromtimestamp(self.config.token_exp))}. "
                                 f"Getting new token...")
                return self.auth()
            else:
                return True
        else:
            return self.auth()

    def _rate_limit(self, skew_mitigation_secs=5):
        """
        Internal method to check the rate-limited headers from TDX.
        If the rate-limiting is within 1 request of sending a 429, will sleep until the timer resets.
        """
        if 'remaining' in self.cache['rate_limit']:
            if not self.cache['rate_limit']['remaining'] > 1:
                if 'reset_time' in self.cache['rate_limit']:
                    reset_datetime = datetime.datetime.strptime(self.cache['rate_limit']['reset_time'],
                                                                '%a, %d %b %Y %H:%M:%S GMT')
                    now = datetime.datetime.utcnow()
                    if reset_datetime > now:
                        difference = reset_datetime - now
                        sleep_time = difference + datetime.timedelta(0, skew_mitigation_secs)
                        self.logger.info("Rate-limited by TeamDynamix. Sleeping "
                                         + str(sleep_time.seconds) + " seconds.")
                        time.sleep(sleep_time.seconds)

    def make_get(self, request_url: str, retries: int = 3):
        """
        Makes an HTTP GET request to the TDX Api.

        :param request_url: the path (everything after /TDWebAPI/api/) to call
        :param retries: the number of times to retry a failed request (defaults to 3)

        :return: the API's response as a python dict or list

        """
        self._rate_limit()
        get_url = self.config.api_url + request_url
        response = None
        attempts = 0
        while attempts < retries:
            try:
                if not (self._check_auth_exp()):
                    raise tdxlib.tdx_api_exceptions.TdxApiHTTPError(
                        f"Login Failed. Username or password in config likely incorrect.")
                response = requests.get(
                    url=get_url,
                    headers={
                        "Authorization": 'Bearer ' + self.config.token,
                        "Content-Type": "application/json; charset=utf-8",
                    }
                )
                if response.status_code != 200:
                    err_string = " Response code: " + str(response.status_code) + \
                        " " + response.reason + " " + " Returned: " + response.text
                    raise tdxlib.tdx_api_exceptions.TdxApiHTTPError(err_string)
                val = response.json()
                self.cache['rate_limit']['remaining'] = int(response.headers['X-RateLimit-Remaining'])
                self.cache['rate_limit']['reset_time'] = str(response.headers['X-RateLimit-Reset'])
                self.cache['rate_limit']['limit'] = int(response.headers['X-RateLimit-Limit'])
                self.cache['rate_limit']['last_url'] = request_url
                return val
            except requests.exceptions.RequestException as e:
                self.logger.error(f"GET to {request_url} failed. Exception: {str(e)}")
            except tdxlib.tdx_api_exceptions.TdxApiHTTPError as e:
                self.logger.error(f"GET to {request_url} returned non-success code. {str(e)}")
            except json.decoder.JSONDecodeError:
                message = 'Invalid JSON received from ' + get_url + ':'
                if response:
                    message += response.text
                self.logger.error(f"{message}")
            finally:
                attempts += 1

    def make_post(self, request_url: str, body: dict):
        """
        Makes an HTTP POST request to the TDX Api

        :param request_url: the path (everything after /TDWebAPI/api/) to call
        :param body: dumped JSON data to send with the POST

        :return: the API's response as a python dict or list

        """
        self._rate_limit()
        post_url = self.config.api_url + request_url
        response = None
        try:
            if not (self._check_auth_exp()):
                raise tdxlib.tdx_api_exceptions.TdxApiHTTPError(
                    f"Login Failed. Username or password in config likely incorrect.")
            response = requests.post(
                url=post_url,
                headers={
                    "Authorization": 'Bearer ' + self.config.token,
                    "Content-Type": "application/json; charset=utf-8",
                },
                data=json.dumps(body))
            if response.status_code not in [200, 201]:
                raise tdxlib.tdx_api_exceptions.TdxApiHTTPError(
                    " Response code: " + str(response.status_code) + " " +
                    response.reason + "\n" + "Returned: " + response.text)
            if len(response.text) == 0:
                val = None
            else:
                val = response.json()
            self.cache['rate_limit']['remaining'] = int(response.headers['X-RateLimit-Remaining'])
            self.cache['rate_limit']['reset_time'] = str(response.headers['X-RateLimit-Reset'])
            self.cache['rate_limit']['limit'] = int(response.headers['X-RateLimit-Limit'])
            return val
        except requests.exceptions.RequestException as e:
            self.logger.error(f"POST to {request_url} failed. Exception: {str(e)}")
        except tdxlib.tdx_api_exceptions.TdxApiHTTPError as e:
            self.logger.error(f"POST to {request_url} returned non-success code. {str(e)}")
        except json.decoder.JSONDecodeError:
            message = 'Invalid JSON received POST to ' + post_url + ':\n'
            if response:
                message += response.text
            self.logger.error(f"{message}")

    def make_file_post(self, request_url: str, file: BinaryIO, filename: str = None):
        """
        Makes an HTTP POST request to the TDX Api with a Multipart-Encoded File
        
        :param request_url: the path (everything after /TDWebApi/api/) to call
        :param file: BinaryIO object opened in read mode to upload as attachment.
        (read documentation at requests.readthedocs.io/en/master/user/quickstart/#post-a-multipart-encoded-file)
        :param filename: (optional), allows to explicitly specify filename header. If None, requests will determine
        from passed-in file object.
        This is useful for if you want to upload a file in memory without a filename, which is required
        for uploading to TeamDynamix.

        :return: the API's response as a python dict
        """
        self._rate_limit()
        post_url = self.config.api_url + request_url
        response = None
        if filename:
            files = {'file': (filename, file)}
        else:
            files = {'file': file}
        try:
            if not (self._check_auth_exp()):
                raise tdxlib.tdx_api_exceptions.TdxApiHTTPError(
                    f"Login Failed. Username or password in config likely incorrect.")
            response = requests.post(
                url=post_url,
                headers={
                    "Authorization": 'Bearer ' + self.config.token,
                },
                files=files
            )
            if response.status_code not in [200, 201]:
                raise tdxlib.tdx_api_exceptions.TdxApiHTTPError(
                    " Response code: " + str(response.status_code) + " " +
                    response.reason + "\n" + "Returned: " + response.text)
            val = response.json()
            self.cache['rate_limit']['remaining'] = int(response.headers['X-RateLimit-Remaining'])
            self.cache['rate_limit']['reset_time'] = str(response.headers['X-RateLimit-Reset'])
            self.cache['rate_limit']['limit'] = int(response.headers['X-RateLimit-Limit'])
            return val
        except requests.exceptions.RequestException as e:
            self.logger.error(f"POST File to {request_url} failed. Exception: {str(e)}")
        except tdxlib.tdx_api_exceptions.TdxApiHTTPError as e:
            self.logger.error(f"POST File to {request_url} returned non-success code. {str(e)}")
        except json.decoder.JSONDecodeError:
            message = 'Invalid JSON received from POSTing File to ' + request_url + ':\n'
            if response:
                message += response.text
            self.logger.error(f"{message}")

    def make_put(self, request_url: str, body: dict):
        """
        Makes an HTTP PUT request to the TDX API.

        :param request_url: the path (everything after /TDWebAPI/api/) to call
        :param body: dumped JSON data to send with the PUT

        :return: the API's response as a python dict or list

        """
        self._rate_limit()
        put_url = self.config.api_url + request_url
        response = None
        try:
            if not (self._check_auth_exp()):
                raise tdxlib.tdx_api_exceptions.TdxApiHTTPError(
                    f"Login Failed. Username or password in config likely incorrect.")
            response = requests.put(
                url=put_url,
                headers={
                    "Authorization": 'Bearer ' + self.config.token,
                    "Content-Type": "application/json; charset=utf-8",
                },
                data=json.dumps(body))
            if response.status_code not in [200, 201, 202, 204]:
                raise tdxlib.tdx_api_exceptions.TdxApiHTTPError(
                    " Response code: " + str(response.status_code) + " " +
                    response.reason + "\n" + "Returned: " + response.text)
            val = response.json()
            self.cache['rate_limit']['remaining'] = int(response.headers['X-RateLimit-Remaining'])
            self.cache['rate_limit']['reset_time'] = str(response.headers['X-RateLimit-Reset'])
            self.cache['rate_limit']['limit'] = int(response.headers['X-RateLimit-Limit'])
            return val
        except requests.exceptions.RequestException as e:
            self.logger.error(f"PUT to {request_url} failed. Exception: {str(e)}")
        except tdxlib.tdx_api_exceptions.TdxApiHTTPError as e:
            self.logger.error(f"PUT to {request_url} returned non-success code. {str(e)}")
        except json.decoder.JSONDecodeError:
            message = 'Invalid JSON received from ' + request_url + ':\n'
            if response:
                message += response.text
            self.logger.error(f"{message}")

    def make_delete(self, request_url: str):
        """
        Makes an HTTP DELETE request to the TDX Api.

        :param request_url: the path (everything after /TDWebAPI/api/) to call

        :return: None

        """
        self._rate_limit()

        delete_url = self.config.api_url + request_url
        try:
            if not (self._check_auth_exp()):
                raise tdxlib.tdx_api_exceptions.TdxApiHTTPError(
                    f"Login Failed. Username or password in config likely incorrect.")
            response = requests.delete(
                url=delete_url,
                headers={
                    "Authorization": 'Bearer ' + self.config.token,
                    "Content-Type": "application/json; charset=utf-8",
                })
            if response.status_code not in [200, 201]:
                raise tdxlib.tdx_api_exceptions.TdxApiHTTPError(
                    " Response code: " + str(response.status_code) + " " +
                    response.reason + "\n" + "Returned: " + response.text)
            self.cache['rate_limit']['remaining'] = int(response.headers['X-RateLimit-Remaining'])
            self.cache['rate_limit']['reset_time'] = str(response.headers['X-RateLimit-Reset'])
            self.cache['rate_limit']['limit'] = int(response.headers['X-RateLimit-Limit'])
        except requests.exceptions.RequestException as e:
            self.logger.error(f"DELETE to {request_url} failed. Exception: {str(e)}")
        except tdxlib.tdx_api_exceptions.TdxApiHTTPError as e:
            self.logger.error(f"DELETE to {request_url} returned non-success code. {str(e)}")

    def make_patch(self, request_url: str, body: dict):
        """
        Makes an HTTP PATCH request to the TDX API.

        The TeamDynamix API supports limited PATCH functionality. Since TDX data is highly structured, items are
        referenced explicitly by their TDX ID, and not by their order in the object. Likewise, since the fields
        in a TDX object are all predefined, a PATCH call cannot add or remove any fields in the object.

        :param request_url: the path (everything after /TDWebAPI/api/) to call
        :param body: a list of PATCH operations as dictionaries, each including the keys "op", "path", and "value"

        :return: the API's response, as a python dict or list

        """
        self._rate_limit()
        patch_url = self.config.api_url + request_url
        response = None
        try:
            if not (self._check_auth_exp()):
                raise tdxlib.tdx_api_exceptions.TdxApiHTTPError(
                    f"Login Failed. Username or password in config likely incorrect.")
            response = requests.patch(
                url=patch_url,
                headers={
                    "Authorization": 'Bearer ' + self.config.token,
                    "Content-Type": "application/json; charset=utf-8",
                },
                data=json.dumps(body)
            )

            if response.status_code not in [200, 201]:
                raise tdxlib.tdx_api_exceptions.TdxApiHTTPError(
                    " Response code: " + str(response.status_code) + " " +
                    response.reason + "\n" + "Returned: " + response.text)
            val = response.json()
            self.cache['rate_limit']['remaining'] = int(response.headers['X-RateLimit-Remaining'])
            self.cache['rate_limit']['reset_time'] = str(response.headers['X-RateLimit-Reset'])
            self.cache['rate_limit']['limit'] = int(response.headers['X-RateLimit-Limit'])
            return val
        except requests.exceptions.RequestException as e:
            self.logger.error(f"PATCH to {request_url} failed. Exception: {str(e)}")
        except tdxlib.tdx_api_exceptions.TdxApiHTTPError as e:
            self.logger.error(f"PATCH to {request_url} returned non-success code. {str(e)}")
        except json.decoder.JSONDecodeError:
            message = 'Invalid JSON received from PATCH to ' + request_url + ':\n'
            if response:
                message += response.text
            self.logger.error(f"{message}")

    def clean_cache(self):
        """
        Internal method to refresh the cache in a tdxlib object.
        """
        self.cache = {
            'locations': {},
            'rooms': {},
            'people': {},
            'groups': {},
            'accounts': {},
            'custom_attributes': {},
            'ca_search': {},
            'rate_limit': {}
        }

    # #### GETTING TDX OBJECTS #### #

    def get_tdx_item_by_id(self, obj_type: str, key):
        """
        A generic function to get something from the TDX API using its ID/UID.

        Since the TDX API endpoints are almost all in the form /<object type>/id, this method gives an easy way
        to template all the different get_<object>_by_id methods.

        :param obj_type: the type of object to get.
        :param key: the ID number of an object to get, as a string

        :return: list of person data

        """
        url_string = f'/{obj_type}/{str(key)}'
        return self.make_get(url_string)

    def get_location_by_id(self, location_id: int) -> dict:
        """
        Gets a location by the location ID.

        :param location_id: ID number of location to get information about

        :return: dict of location data

        :rtype: dict
        """
        return self.get_tdx_item_by_id('locations', location_id)

    def get_account_by_id(self, account_id: int) -> dict:
        """
        Gets an account by the account ID.

        :param account_id: ID number of account to get information about

        :return: dict of account data

        :rtype: dict
        """
        return self.get_tdx_item_by_id('accounts', account_id)

    def get_group_by_id(self, group_id: int) -> dict:
        """
        Gets a group by the group ID.

        :param group_id: ID number of group to get information about

        :return: dict of group data, including members

        :rtype: dict
        """
        return self.get_tdx_item_by_id('groups', group_id)

    def get_person_by_uid(self, uid: str) -> dict:
        """
        Gets a person by their UID.

        :param uid: UID string corresponding to a person

        :return: dict of person data

        :rtype: dict
        """
        return self.get_tdx_item_by_id('people', uid)

    def get_group_members_by_id(self, group_id: int) -> list:
        """
        Gets a list of group members by the group ID.

        :param group_id: ID number of group to get members of

        :return: list of person data for people in the group

        :rtype: list
        """
        return self.get_tdx_item_by_id('groups', str(group_id) + '/members')
    
    def get_person_by_name_email(self, key: str) -> dict:
        """
        Gets the top match of people with based on a simple text search, such as:
        - Name
        - Email
        - Username
        - Organizational ID

        :param key: string with search text of person to search with

        :return: dict of person data

        :rtype: dict

        """
        return self.search_people(key, 1)[0]

    def search_people(self, key: str, max_results: int = 20) -> list:
        """
        Gets a list of people, based on a simple text search, which may match Name, Email, Username or ID

        :param key: string with search text of person to search with
        :param max_results: maximum number of matches to return (Default: 20)

        :return: list of dicts of person data

        :rtype: list
        """
        if key in self.cache['people']:
            return self.cache['people'][key]
        else:
            url_string = "/people/lookup?searchText=" + str(key) + "&maxResults=" + str(max_results)
            people = self.make_get(url_string)
            if len(people) == 0:
                raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError("No person found for " + key)
            self.cache['people'][key] = people
            return people

    def get_all_accounts(self) -> list:
        """
        Gets a list of all accounts in TDX

        :return: list of dicts containing account data

        :rtype: list

        """
        url_string = "/accounts"
        return self.make_get(url_string)

    def get_account_by_name(self, key: str, additional_params: dict = None) -> dict:
        """
        Gets an account with by searching on its name.
        
        :param key: a partial or full name of an account to search for
        :param additional_params: other search items, as a python dict, as described in TDX Api Docs
        
        :return: dict of account data (not complete, but including the ID)

        :rtype: dict

        """
        if key in self.cache['accounts']:
            return self.cache['accounts'][key]
        else:
            url_string = '/accounts/search'
            search_params = {'SearchText': key, 'IsActive': True, 'MaxResults': 5}
            if additional_params:
                search_params.update(additional_params)
            post_body = dict({'search': search_params})
            accounts = self.make_post(url_string, post_body)
            for account in accounts:
                if key.lower() in account['Name'].lower():
                    self.cache['accounts'][key] = account
                    return account
            raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError('No account found for ' + key)

    def get_all_groups(self) -> list:
        """
        Gets a list of all groups in TDX

        :return: list of dicts containing group data

        :rtype: list

        """
        url_string = "/groups/search"
        post_body = {'search': {'NameLike': "", 'IsActive': 'True'}}
        return self.make_post(url_string, post_body)

    def get_group_by_name(self, key: str, additional_params=None) -> dict:
        """
        Gets a group by searching on its name.

        :param key: a partial or full name of Group to search for
        :param additional_params: other search items, as a dict, as described in TDX Api Docs

        :return: a dict of group data (not complete, but including the ID)

        :rtype: dict

        """
        if key in self.cache['groups']:
            return self.cache['groups'][key]
        else:
            url_string = '/groups/search'
            search_params = {'NameLike': key, 'IsActive': True}
            if additional_params:
                search_params.update(additional_params)
            post_body = dict({'search': search_params})
            groups = self.make_post(url_string, post_body)
            if type(groups) is not list:
                if key.lower() in groups['Name'].lower():
                    self.cache['groups'][key] = groups
                    return groups
            else:
                for group in groups:
                    if key.lower() in group['Name'].lower():
                        self.cache['groups'][key] = group
                        return group
            raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError('No group found for ' + key)

    def get_group_members_by_name(self, key: str) -> list:
        """
        Gets all the members of a group as person objects by searching on the group's name.

        :param key: a partial or full name of a group

        :return: list of group members

        :rtype: list

        """
        group = self.get_group_by_name(key)
        return self.get_group_members_by_id(group['ID'])

    def get_all_custom_attributes(self, object_type: int, associated_type: int = 0, app_id: int = 0) -> list:
        """
        Gets all custom attributes for the component type in TDX.
        See https://solutions.teamdynamix.com/TDClient/KB/ArticleDet?ID=22203 for possible values.

        :param object_type: the object type to get attributes for (tickets = 9, assets = 27, CI's = 63)
        :param associated_type: the associated type of object to get attributes for, default: 0
        :param app_id: the application number to get attributes from, default: 0

        :return: list of dicts containing custom attributes, including choices and choice ID's

        :rtype: list

        """
        url_string = '/attributes/custom?componentId=' + str(object_type) + '&associatedTypeId=' + \
            str(associated_type) + '&appId=' + str(app_id)
        return self.make_get(url_string)

    # TODO: look into figuring out what type the attribute is based on information from API,
    #  for use in get_custom_attribute_value_by_name
    def get_custom_attribute_by_name_id(self, key: str, object_type: int) -> dict:
        """
        Gets a custom attribute for the component type.
        See https://solutions.teamdynamix.com/TDClient/KB/ArticleDet?ID=22203 for possible values for component_type.

        *NOTE: The best way to assign CA's is to test for an existing value (for choice-based CA's) using
        get_custom_attribute_value_by_name, and then if it returns false, directly assign the desired value to the CA.
        Because of this, date-type and other format-specific attributes need to be in a TDX-acceptable format, this
        means that a field designated to hold person objects needs to be set to a UID.*

        :param key: a partial or full name of the custom attribute to search for
        :param object_type: the object type ID to get attributes for

        :return: the attribute as a dict, with all choice items included

        :rtype: dict

        """
        search_key = str(key) + "_" + str(object_type)
        if search_key in self.cache['ca_search']:
            return self.cache['ca_search'][search_key]
        if str(object_type) not in self.cache['custom_attributes']:
            # There is no API for searching attributes -- the only way is to get them all.
            self.cache['custom_attributes'][str(object_type)] = self.get_all_custom_attributes(object_type)
        for item in self.cache['custom_attributes'][str(object_type)]:
            if str(key).lower() in item['Name'].lower() or str(key) == str(item['ID']):
                self.cache['ca_search'][search_key] = item
                return item
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(
            "No custom attribute found for " + str(key) + ' and object type ' + str(object_type))

    def get_custom_attribute_choice_by_name_id(self, attribute, key):
        """
        Gets the choice item from a custom attribute, maybe from get_custom_attribute_by_name()

        *NOTE: The best way to assign CA's is to test for an existing value (for choice-based CA's), and then if this
        method returns false, directly assign the desired value to the CA. Because of this, date-type and other format
        specific attributes need to be in a TDX-acceptable format, this means that a field designated to hold person
        objects needs to be set to a UID.*

        :param key: a partial or full name of the choice to look for
        :param attribute: a dict of custom attribute data (as retrieved from get_attribute_by_name())

        :return: the the choice object from this attribute whose name matches 'key', or False if none matches.

        :rtype: dict

        """
        if len(attribute['Choices']) > 0:
            for i in attribute['Choices']:
                if str(key).lower() == str(i['Name']).lower() or str(key) == str(i['ID']):
                    return i
            raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(
                f"No custom attribute choice \"{str(key)}\" found in CA {attribute['Name']}")
        elif attribute['FieldType'] == 'datefield':
            value = tdxlib.tdx_utils.import_tdx_date(key)
            return tdxlib.tdx_utils.export_tdx_date(value, self.config.timezone)
        else:
            return str(key)

    def get_all_locations(self) -> list:
        """
        Gets all locations in TDX.

        :return: a list of dicts containing location information

        :rtype: list

        """
        url_string = '/locations'
        return self.make_get(url_string)

    def get_location_by_name(self, key: str, additional_params: dict = None) -> dict:
        """
        Gets a location by searching its name.

        :param key: a partial or full name of the location to search for
        :param additional_params: other search items, as a dict, as described in TDX Api Docs

        :return: a dict of location data

        :rtype: dict

        """
        if key in self.cache['locations']:
            return self.cache['locations'][key]
        else:
            url_string = '/locations/search'
            search_params = {'NameLike': key, 'IsActive': True}
            if additional_params:
                search_params.update(additional_params)
            post_body = dict({'search': search_params})
            locations = self.make_post(url_string, post_body)
            if isinstance(locations, list):
                list_of_locations = list(locations)
            else:
                list_of_locations = locations
            for location in list_of_locations:
                if key.lower() in location['Name'].lower():
                    full_location = self.get_location_by_id(location['ID'])
                    self.cache['locations'][key] = full_location
                    return full_location
            raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError("No location found for " + key)

    @staticmethod
    def get_room_by_name(location: dict, room: str) -> dict:
        """
        Gets a room by searching its name in location information, maybe from get_location_by_name().

        :param location: dict of location info
        :param room: partial or full name of a room to search for

        :return: a dict with all the information regarding the room. Use this to retrieve the ID attribute.

        :rtype: dict

        """
        for i in location['Rooms']:
            if str(room).lower() in i['Name'].lower():
                return i
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(
            "No room found for " + room + " in location " + location['Name'])

    # #### CREATING TDX OBJECTS #### #

    def create_account(self, name: str, manager: str, additional_info: dict = None,
                       custom_attributes: dict = None) -> dict:
        """
        Creates an account in TeamDynamix.

        :param name: Name of account to create.
        :param manager: email address of the TDX Person who will be the manager of the group
        :param additional_info: dict of other attributes to set on account. Retrieved from:
                                https://api.teamdynamix.com/TDWebApi/Home/type/TeamDynamix.Api.Accounts.Account
        :param custom_attributes: dict of names of custom attributes and corresponding names of the choices to set
                                  on each attribute. These names must match the names in TDX, not IDs.

        :return: a dict with information about the created account

        :rtype: dict

        """
        editable_account_attributes = ['Address1', 'Address2', 'Address3', 'Address4', 'City', 'StateAbbr',
                                       'PostalCode', 'Country', 'Phone', 'Fax', 'Url', 'Notes', 'Code', 'IndustryID']
        url_string = '/accounts'
        data = dict()
        data['Name'] = name
        data['ManagerUID'] = self.get_person_by_name_email(manager)['UID']
        if additional_info.items():
            for attrib, value in additional_info.items():
                if attrib in editable_account_attributes:
                    data[attrib] = additional_info[attrib]
                else:
                    raise tdxlib.tdx_api_exceptions.TdxApiObjectTypeError(f'Account attribute {attrib} is not editable')
        if custom_attributes:
            data['Attributes'] = list()
            for attrib, value in custom_attributes.items():
                tdx_attrib = self.get_custom_attribute_by_name_id(attrib, TDXIntegration.component_ids['account'])
                tdx_attrib_value = self.get_custom_attribute_choice_by_name_id(tdx_attrib, value)
                if not tdx_attrib_value:
                    tdx_attrib_value_final = value
                else:
                    tdx_attrib_value_final = tdx_attrib_value['ID']
                data['Attributes'].append({'ID': tdx_attrib['ID'], 'Value': tdx_attrib_value_final})
        return self.make_post(url_string, data)

    def edit_account(self, name: str, changed_attributes: dict) -> dict:
        """
        Edits an account in TeamDynamix

        :param name: Name of account to edit.
        :param changed_attributes: dict of names of attributes and corresponding data to set on each attribute.

        :return: a dict with information about the edited account

        :rtype: dict

        """
        editable_account_attributes = ['Name', 'Address1', 'Address2', 'Address3', 'Address4', 'City', 'StateAbbr',
                                       'PostalCode', 'Country', 'Phone', 'Fax', 'Url', 'Notes', 'Code', 'IndustryID']
        url_string = '/accounts'
        for k in changed_attributes.keys():
            if k not in editable_account_attributes:
                raise tdxlib.tdx_api_exceptions.TdxApiObjectTypeError("Account Attribute " + k + " is not editable")
        existing_account = self.get_account_by_name(name)
        existing_account.update(changed_attributes)
        return self.make_put(url_string + "/" + str(existing_account['ID']), existing_account)

    # #### #### GROUPS #### #### #
    # https://api.teamdynamix.com/TDWebApi/Home/section/Group

    # TODO: def create_group()

    # TODO: def edit_group()
    #    https://api.teamdynamix.com/TDWebApi/Home/type/TeamDynamix.Api.Users.Group

    # TODO: def delete_group()

    # TODO: def set_group_members()
    #  This should ingest a list of people. We need to decide whether or not it should be a list of email
    #  addresses, or a list of UUID's that could be generated from another method.

    # #### PEOPLE #### #
    # https://api.teamdynamix.com/TDWebApi/Home/section/People #summary

    # TODO: def create_person()

    # TODO: def edit_person()

    # TODO: def get_person_functional_roles() -- accept UUID or email

    # TODO: def delete_person_functional_role() -- accept UUID or email

    # TODO: def add_person_functional_role() -- accept UUID or email

    # TODO: def get_groups_by_person() -- accept UUID or email

    # TODO: def remove_user_from_group() -- accept UUID or email

    # TODO: def add_person_to_groups() -- accept single or multiple groups, support removal from all other groups

    # TODO: def set_person_status() -- enable/disable

    # TODO: def person_import() -- this could be difficult -- have to figure out how to upload an xlsx file via API.

    # #### #### LOCATIONS & ROOMS #### #### #
    # https://api.teamdynamix.com/TDWebApi/Home/section/Locations

    # TODO: create_location()

    # TODO: edit_location()

    def create_room(self, location, name: str,  external_id: str = None, description: str = None,
                    floor: str = None, capacity: int = None, attributes: dict = None) -> dict:
        """
        Creates a room in a location in TDX.

        :param location:     Dict of location information (or ID), possibly from get_location_by_name()
        :param name:            Name of new room
        :param external_id:     External ID of new room as a string (optional)
        :param description:     Description of new room as a string (optional)
        :param floor:           Floor for new room as a string (optional)
        :param capacity:        Capacity of the room, as an integer (optional)
        :param attributes:      Dict of Custom Attributes (optional)

        :return:                Dict with newly created room information

        """
        if isinstance(location, dict):
            location_id = location['ID']
        elif isinstance(location, str):
            location_id = location
        else:
            raise tdxlib.tdx_api_exceptions.TdxApiObjectTypeError("Location must be dict or str, not " +
                                                                  str(type(location)))
        url_string = f'/locations/{location_id}/rooms'
        room_data = {'Name': name}
        if external_id:
            room_data['ExternalID'] = external_id
        if description:
            room_data['Description'] = description
        if floor:
            room_data['Floor'] = floor
        if capacity:
            room_data['Capacity'] = capacity
        if attributes:
            room_data['Attributes'] = attributes
        return self.make_post(url_string, room_data)

    # TODO: delete_room()

    # TODO: edit_room()

    # #### #### ATTRIBUTE CHOICES #### #### #
    # https: // api.teamdynamix.com / TDWebApi / Home / section / Attributes

    # TODO: add_custom_attribute_choice()

    # TODO: delete_custom_attribute_choice()

    # TODO: edit_custom_attribute_choice():

    # TODO: generate_custom_attributes()

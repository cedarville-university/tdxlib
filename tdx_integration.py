import configparser
import requests
import json
import os
import getpass
import dateutil.parser
import tdx_api_exceptions
import datetime

class TDXIntegration:
    # Hard-coded into TDX
    component_ids = {
        'account': 14,
        'asset': 27,
        'configuration_item': 63,
        'contract': 29,
        'file_cabinet': 8,
        'issue': 3,
        'opportunity': 11,
        'person': 31,
        'product': 37,
        'product_model': 30,
        'project': 1,
        'ticket': 9,
        'vendor': 28
    }

    def __init__(self, filename=None):
        self.settings = None
        self.api_url = None
        self.username = None
        self.password = None
        self.token = None
        self.config = configparser.ConfigParser()
        if filename is not None:
            self.config.read(filename)
        else:
            filename = 'TicketMaster.ini'
            self.config.read(filename)
        if 'TDX API Settings' in self.config:
            self.settings = self.config['TDX API Settings']
            self.org_name = self.settings.get('orgname')
            self.sandbox = bool(self.settings.get('sandbox'))
            self.username = self.settings.get('username')
            self.password = self.settings.get('password')
            self.ticket_app_id = self.settings.get('ticketAppId')
            self.asset_app_id = self.settings.get('assetAppId')
            if self.sandbox:
                api_end = '/SBTDWebApi/api'
            else:
                api_end = '/TDWebApi/api'
            self.api_url = 'https://' + self.org_name + '.teamdynamix.com' + api_end
            if self.password == 'Prompt':
                pass_prompt = 'Enter the TDX Password for user ' + self.username + ': '
                self.password = getpass.getpass(pass_prompt)
        else:
            self.config['TDX API Settings'] = {
                'orgname': 'myuniversity',
                'sandbox': True,
                'username': '',
                'password': 'Prompt',
                'ticketAppId': '',
                'assetAppId': '',
                'caching': False
                                       }
            with open(filename, 'w') as configfile:
                self.config.write(configfile)
            raise FileNotFoundError('No config settings at ' + filename + ", writing sample config to" +
                                    os.path.join(os.getcwd(), filename))
        try:
            response = requests.post(
                url=str(self.api_url) + '/auth',
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                },
                data=json.dumps({
                    "username": self.username,
                    "password": self.password
                })
            )
            if response.status_code != 200:
                raise tdx_api_exceptions.TdxApiHTTPError(" Response code: " + str(response.status_code) + " " +
                                                         response.reason + "\n" + " Returned: " + response.text)
            else:
                self.token = response.text
                self.password = None
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
        except tdx_api_exceptions.TdxApiHTTPError as e:
            print('Authorization failed.\n' + str(e))
            exit(1)
        self.cache = {}
        self.clean_cache()

    def make_get(self, request_url):
        """
        Makes a HTTP GET request to the TDX Api
        :param request_url: the path (everything after /TDWebAPI/api/) to call
        :return: the API response
        """
        get_url = self.api_url + request_url
        response = None
        try:
            response = requests.get(
                url=get_url,
                headers={
                    "Authorization": 'Bearer ' + self.token,
                    "Content-Type": "application/json; charset=utf-8",
                }
            )
            if response.status_code != 200:
                raise tdx_api_exceptions.TdxApiHTTPError(" Response code: " + str(response.status_code) + " " +
                                                         response.reason + "\n" + " Returned: " + response.text)
            val = response.json()
            return val
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
        except tdx_api_exceptions.TdxApiHTTPError as e:
            print('GET failed: to ' + get_url + "\nReturned: " + str(e))
        except json.decoder.JSONDecodeError:
            message = 'Invalid JSON received from ' + get_url + ':'
            if response:
                message += response.text
            print(message)

    def make_post(self, request_url, body):
        """
        Makes a HTTP POST request to the TDX Api
        :param request_url: the path (everything after /TDWebAPI/api/) to call
        :param body: dumped JSON data to send with the POST
        :return: the API response
        """
        post_url = self.api_url + request_url
        response = None
        try:
            response = requests.post(
                url=post_url,
                headers={
                    "Authorization": 'Bearer ' + self.token,
                    "Content-Type": "application/json; charset=utf-8",
                },
                data=json.dumps(body))
            if response.status_code not in [200, 201]:
                raise tdx_api_exceptions.TdxApiHTTPError(
                    " Response code: " + str(response.status_code) + " " +
                    response.reason + "\n" + "Returned: " + response.text)
            val = response.json()
            return val
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
        except tdx_api_exceptions.TdxApiHTTPError as e:
            print('POST failed: to ' + post_url + "\nReturned: " + str(e))
        except json.decoder.JSONDecodeError:
            message = 'Invalid JSON received from ' + post_url + ':\n'
            if response:
                message += response.text
            print(message)

    def make_put(self, request_url, body):
        """
        Makes an HTTP PUT request to the TDX API
        :param request_url: the path (everything after /TDWebAPI/api/) to call
        :param body: dumped JSON data to send with the PUT
        :return: the API response
        """
        put_url = self.api_url + request_url
        response = None
        try:
            response = requests.put(
                url = put_url,
                headers={
                    "Authorization": 'Bearer ' + self.token,
                    "Content-Type": "application/json; charset=utf-8",
                },
                data=json.dumps(body))
            if response.status_code not in [200, 202, 204]:
                raise tdx_api_exceptions.TdxApiHTTPError(
                    " Response code: " + str(response.status_code) + " " +
                    response.reason + "\n" + "Returned: " + response.text)
            val = response.json()
            return val
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
        except tdx_api_exceptions.TdxApiHTTPError as e:
            print('PUT failed: to ' + put_url + "\nReturned: " + str(e))
        except json.decoder.JSONDecodeError:
            message = 'Invalid JSON received from ' + put_url + ':\n'
            if response:
                message += response.text
            print(message)

    # TODO: def make_delete(self, request_url body):

    # TODO: def make_patch(self, request_url, body?): ?????

    def clean_cache(self):
        self.cache = {
            'locations': {},
            'rooms': {},
            'people': {},
            'groups': {},
            'accounts': {},
            'custom_attributes': {}
        }

    # TODO: Move this method into tdx_asset_integration
    def make_asset_call(self, url, action, post_body=None):
        url_string = '/' + str(self.asset_app_id) + '/assets'
        if len(url) > 0:
            url_string += '/' + url
        if action == 'get':
            return self.make_get(url_string)
        if action == 'post' and post_body:
            return self.make_post(url_string, post_body)
        raise tdx_api_exceptions.TdxApiHTTPRequestError('No method' + action + 'or no post information')

    # #### GETTING TDX OBJECTS #### #

    def get_tdx_item_by_id(self, obj_type, key):
        url_string = f'/{obj_type}/{key}'
        return self.make_get(url_string)

    def get_location_by_id(self, key):
        return self.get_tdx_item_by_id('locations', key)

    def get_account_by_id(self, key):
        return self.get_tdx_item_by_id('accounts', key)

    def get_group_by_id(self, key):
        return self.get_tdx_item_by_id('groups', key)

    def get_person_by_uid(self, uid):
        return self.get_tdx_item_by_id('people', uid)
    
    def search_people(self, key):
        """
        Gets the top match of people with search text, such as:
         - Name
         - Email
         - Username
         - Organizational ID
        :param key: string with search text of person to search with
        :return: person data in json format
        """
        if key in self.cache['people']:
            return self.cache['people'][key]
        else:
            url_string = "/people/lookup?searchText=" + str(key) + "&maxResults=1"
            people = self.make_get(url_string)
            if len(people) == 0:
                raise tdx_api_exceptions.TdxApiObjectNotFoundError("No person found for " + key)
            self.cache['people'][key] = people[0]
            return people[0]

    def get_all_accounts(self):
        """
        Gets all accounts
        :return: list of Account data in json format
        """
        url_string = "/accounts"
        return self.make_get(url_string)

    def get_account_by_name(self, key, additional_params=None):
        """
        Gets an account with name key
        :param key: name of an account to search for
        :param additional_params: other search items, as a dict, as described in TDX Api Docs
        :return: dict of account data (not complete, but including the ID)
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
                if account['Name'] == key:
                    self.cache['accounts'][key] = account
                    return account
            raise tdx_api_exceptions.TdxApiObjectNotFoundError('No account found for ' + key)

    def get_all_groups(self):
        """
        Gets a list of groups
        :return: list of group data in json format
        """
        url_string = "/groups/search"
        post_body = {'search': {'NameLike': "", 'IsActive': 'True'}}
        return self.make_post(url_string, post_body)

    def get_group_by_name(self, key, additional_params=None):
        """
        Gets a group with name key
        :param key: name of Group to search for
        :param additional_params: other search items, as a dict, as described in TDX Api Docs
        :return: a dict of group data (not complete, but including the ID)
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
                if groups['Name'] == key:
                    self.cache['groups'][key] = groups
                    return groups
            else:
                for group in groups:
                    if group['Name'] == key:
                        self.cache['groups'][key] = group
                        return group
            raise tdx_api_exceptions.TdxApiObjectNotFoundError('No group found for ' + key)

    # TODO: def get_all_group_members()

    def get_all_custom_attributes(self, object_type, associated_type=0, app_id=0):
        """
        Gets all custom attributes for the component type. 
        See https://solutions.teamdynamix.com/TDClient/KB/ArticleDet?ID=22203 for possible values
        :param associated_type: the associated type of object to get attributes for, default: 0
        :param app_id: the application number to get attributes from, default: 0
        :param object_type: the object type to get attributes for (tickets = 9, assets = 27, CI's = 63)
        :return: the API response
        """
        url_string = '/attributes/custom?componentId=' + str(object_type) + '&associatedTypeId=' + \
            str(associated_type) + '&appId=' + str(app_id)
        return self.make_get(url_string)

    def get_custom_attribute_by_name(self, key, object_type):
        """
        Gets a custom attribute for the component type.
        See https://solutions.teamdynamix.com/TDClient/KB/ArticleDet?ID=22203 for possible values
        :param key: the name of the custom attribute to search for
        :param object_type: the object type to get attributes for (tickets = 9, assets = 27, CI's = 63)
        :return: the attribute as a dict, with all choice items included
        """
        if not self.cache['custom_attributes'][str(object_type)]:
            # There is no API for searching attributes -- the only way is to get them all.
            self.cache['custom_attributes'][str(object_type)] = self.get_all_custom_attributes(object_type)
        for item in self.cache['custom_attributes'][str(object_type)]:
            if item['Name'] == key:
                self.cache['custom_attributes'][str(object_type)][key] = item
                return item
        raise tdx_api_exceptions.TdxApiObjectNotFoundError(
            "No custom attribute found for " + key + ' and object type ' + str(object_type))

    def get_asset_attribute_by_name(self, key):
        return self.get_custom_attribute_by_name(key, 27)

    # TODO: other object type attributes by hard-coded IDs -- May want to move the above into their own integrations.

    @staticmethod
    def get_custom_attribute_value_by_name(attribute, key):
        """
        Gets the choice item from a custom attribute for the component type.
        See https://solutions.teamdynamix.com/TDClient/KB/ArticleDet?ID=22203 for possible values
        :param key: the name of the choice to look for
        :param attribute: the attribute (as retrieved from get_attribute_by_name())
        :return: the the choice object from this attribute whose name matches the key
        """
        for i in attribute['Choices']:
            if key in i['Name']:
                return i
        raise tdx_api_exceptions.TdxApiObjectNotFoundError(
            "No custom attribute value for " + key + " found in " + attribute['Name'])

    def get_all_locations(self):
        url_string = '/locations'
        return self.make_get(url_string)

    def get_location_by_name(self, key, additional_params=None):
        """
        Gets a location with name key
        :param key: name of location to search for
        :param additional_params: other search items, as a dict, as described in TDX Api Docs
        :return: a dict of location data
        """
        if key in self.cache['locations']:
            return self.cache['locations']['key']
        else:
            url_string = '/locations/search'
            search_params = {'NameLike': key, 'IsActive': True}
            if additional_params:
                search_params.update(additional_params)
            post_body = dict({'search': search_params})
            locations = self.make_post(url_string, post_body)
            for location in locations:
                if key in location['Name']:
                    self.cache['locations']['key']['key'] = location
                    return location
            raise tdx_api_exceptions.TdxApiObjectNotFoundError("No location found for " + key)

    @staticmethod
    def get_room_by_name(location, room):
        """
        Gets a room with name key
        :param location: dict of location info from get_location_by_name()
        :param room: name/number of a room to search for (must be exact)
        :return: a dict of room data (including ID)
        """
        for i in location['Rooms']:
            if room in i['Name']:
                return i
        raise tdx_api_exceptions.TdxApiObjectNotFoundError(
            "No room found for " + room + " in location " + location['Name'])

    # #### CREATING TDX OBJECTS #### #

    # #### #### ACCOUNTS #### #### #
    # https://api.teamdynamix.com/TDWebApi/Home/section/Accounts

    # TODO: def create_account()

    # TODO: def edit_account()
    #   https://api.teamdynamix.com/TDWebApi/Home/type/TeamDynamix.Api.Accounts.Account

    # #### #### GROUPS #### #### #
    # https://api.teamdynamix.com/TDWebApi/Home/section/Group

    # TODO: def create_group()

    # TODO: def edit_group()
    #    https://api.teamdynamix.com/TDWebApi/Home/type/TeamDynamix.Api.Users.Group

    # TODO: def delete_group()

    # TODO: def set_group_members()
    #  This should ingest a list of people. We need to decide whether or not it should be a list of email
    #  addresses, or a list of UUID's that could be generated from another method.

    # #### #### PEOPLE #### #### #
    # https: // api.teamdynamix.com / TDWebApi / Home / section / People  # summary

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

    # TODO: create_room()

    # TODO: delete_room()

    # TODO: edit_room()

    # #### #### ATTRIBUTE CHOICES #### #### #
    # https: // api.teamdynamix.com / TDWebApi / Home / section / Attributes

    # TODO: add_custom_attribute_choice()

    # TODO: delete_custom_attribute_choice()

    # TODO: edit_custom_attribute_choice()

    # #### HANDY UTILITIES #### #

    # Prints out dict as JSON with indents
    @staticmethod
    def print_nice(myjson):
        print(json.dumps(myjson, indent=4))
        print("")

    # Print summary of ticket, or dict of tickets
    @staticmethod
    def print_simple(myjson):
        for i in myjson:
            for j in i:
                print('ID:\t', j['ID'])
                print('Title:\t', j['Title'])
                print('Requestor:\t', j['Requestor'])
                print('Type:\t', j['TypeName'])

    # Print only ['Name'] attribute of list of objects
    @staticmethod
    def print_names(myjson):
        for i in myjson:
            print(i['Name'])

    # Imports a string from a TDX Datetime attribute, returns a python datetime object
    @staticmethod
    def import_tdx_date(date_string: str) -> datetime:
        return dateutil.parser.parse(date_string)

    # Takes a python datetime object, returns a string compatible with a TDX Datetime attribute
    @staticmethod
    def export_tdx_date(date: datetime) -> str:
        return date.strftime('%Y-%m-%dT%H:%M:%SZ')

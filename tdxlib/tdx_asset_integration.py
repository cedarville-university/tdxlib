import datetime
import tdxlib.tdx_integration


class TDXAssetIntegration(tdxlib.tdx_integration.TDXIntegration):
    def __init__(self, filename=None):
        tdxlib.tdx_integration.TDXIntegration.__init__(self, filename)
        if self.asset_app_id is None:
            raise ValueError("Asset App Id is required. Check your INI file for 'assetappid = 000'")
        self.clean_cache()

    def clean_cache(self):
        super().clean_cache()
        self.cache['asset_model'] = {}
        self.cache['product_type'] = {}
        self.cache['asset_form'] = {}
        self.cache['asset_status'] = {}
        self.cache['custom_attributes'] = self.get_all_custom_attributes(
            tdxlib.tdx_integration.TDXIntegration.component_ids['asset'], app_id=self.asset_app_id)
        self.cache['custom_attributes'].append(self.get_all_custom_attributes(
            tdxlib.tdx_integration.TDXIntegration.component_ids['configuration_item'], app_id=self.asset_app_id))

    def _make_asset_call(self, url, action, post_body=None):
        url_string = '/' + str(self.asset_app_id) + '/assets'
        if len(url) > 0:
            url_string += '/' + url
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
        raise tdxlib.tdx_api_exceptions.TdxApiHTTPRequestError('No method' + action + 'or no post information')

    def make_call(self, url, action, post_body=None):
        """
        Makes an HTTP call using the Assets API information.

        :param url: The URL (everything after assets/) to call
        :param action: The HTTP action (get, put, post, delete, patch) to perform.
        :param post_body: A python dict of the information to post, put, or patch. Not used for get/delete.

        :return: the API's response as a python dict or list

        """
        return self._make_asset_call(url, action, post_body)

    def get_asset_custom_attribute_by_name(self, key: str) -> dict:
        # Since there are two different types we may have to get, we cache them all
        search_key = str(key) + "_asset_ci"
        if search_key in self.cache['ca_search']:
            return self.cache['ca_search'][search_key]
        # There is no API for searching attributes -- the only way is to get them all.
        for item in self.cache['custom_attributes']:
            if str(key).lower() in item['Name'].lower():
                self.cache['ca_search'][search_key] = item
                return item
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(
            "No custom asset or CI attribute found for " + str(key))

    def get_all_asset_forms(self) -> list:
        """
        Gets a list asset forms

        :return: list of form data in json format
        """
        return self.make_call('forms', 'get')
        
    def get_asset_form_by_name_id(self, key: str) -> dict:
        """
        Gets an asset form

        :param key: name of AssetForm to search for

        :return: list of form data in json format
        """
        if not self.cache['asset_form']:
            self.cache['asset_form'] = self.get_all_asset_forms()
        for asset_form in self.cache['asset_form']:
            if str(key).lower() in asset_form['Name'].lower():
                return asset_form
            if asset_form['ID'].lower() == str(key):
                return asset_form
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(
            "No asset form found for " + str(key))

    def get_all_asset_statuses(self) -> list:
        """
        Gets a list asset statuses

        :return: list of status data
        """
        return self.make_call('statuses', 'get')

    def get_asset_status_by_name_id(self, key: str) -> dict:
        """
        Gets a list asset statuses

        :param key: name of an asset status to search for

        :return: dict of status data
        """
        if not self.cache['asset_status']:
            self.cache['asset_status'] = self.get_all_asset_statuses()
        for status in self.cache['asset_status']:
            if status['Name'].lower() == str(key).lower() or str(status['ID']) == str(key):
                return status
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(f'No asset status found for {str(key)}')

    def get_all_product_types(self) -> list:
        """
        Gets a list of product types

        :return: list of product type data
        """
        return self.make_call("models/types", 'get')

    def get_product_type_by_name_id(self, key: str) -> dict:
        """
        Gets a product type object

        :param key: name of product type to search for

        :return: dict of product type data
        """
        if not self.cache['product_type']:
            self.cache['product_type'] = self.get_all_asset_statuses()
        for product_type in self.cache['product_type']:
            if product_type['Name'].lower() == str(key).lower()or str(product_type['ID']) == str(key):
                return product_type
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(f'No product type found for {str(key)}')

    def get_all_product_models(self) -> list:
        """
        Gets a list asset models
        :return: list of model data
        """
        return self.make_call("models", 'get')

    def get_product_model_by_name_id(self, key: str) -> dict:
        """
        Gets a specific product model
        :param key: name of product model to search for
        :return: dict of model data
        """
        if not self.cache['product_model']:
            self.cache['product_model'] = self.get_all_asset_statuses()
        for product_model in self.cache['product_model']:
            if product_model['Name'].lower() == str(key).lower() or str(product_model['ID']) == str(key):
                return product_model
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(f'No product model found for {str(key)}')

    def get_asset_by_id(self, asset_id: str) -> dict:
        """
        Gets a full list of asset attributes and values

        :param asset_id: asset ID from TDX

        :return: dict of asset data
        """
        return self.make_call(str(asset_id), 'get')

    def search_assets(self, criteria, max_results=25, retired=False, disposed=False):
        """
        Gets a ticket, based on criteria

        :param max_results: maximum number of results to return
        :param criteria: a string or dict to search for tickets with. If a string, use as 'SearchString'
        :param retired: include retired assets in search if true
        :param disposed: include disposed assets in search if true

        :return: list of asset info (NOT FULL ASSET RECORDS, must do get asset by id to get full record)

        Common criteria to put in dict:
        {'SerialLike': [List of Int],
        'SearchText': [String],
        'StatusIDs': [List of Int],
        'CustomAttributes': [Dict of CA],
        'ParentIDs': [List of Int]}
        (https://api.teamdynamix.com/TDWebApi/Home/type/TeamDynamix.Api.Tickets.TicketSearch)
        
        """
        # Set default statuses
        statuses = list()
        statuses.append(self.get_asset_status_by_name_id("Inventory")['ID'])
        statuses.append(self.get_asset_status_by_name_id("In Use")['ID'])
        statuses.append(self.get_asset_status_by_name_id("Broken")['ID'])

        # Set conditional statuses
        if retired:
            statuses.append(self.get_asset_status_by_name_id("Retired")['ID'])
        if disposed:
            statuses.append(self.get_asset_status_by_name_id("Disposed")['ID'])

        # Set up search body
        search_body = dict()
        search_body = {'MaxResults': str(max_results), 'StatusIDs': statuses}
        if isinstance(criteria, str):
            search_body['SearchText'] = criteria
        elif isinstance(criteria, dict):
            search_body.update(criteria)
        else:
            raise tdxlib.tdx_api_exceptions.TdxApiObjectTypeError("Can't search assets with" +
                                                                  str(type(criteria)) + " as criteria.")
        asset_list = self.make_call('search', 'post', search_body)
        return asset_list

    def find_asset_by_tag(self, tag):
        """
        Gets an asset based on its asset tag

        :param tag: asset tag as a string or int

        :return: the asset with the corresponding tag
        """
        if type(tag) is str:
            tag = tag.lstrip('0')
        search_params = {'Tag': str(tag)}
        result = self.search_assets(search_params, disposed=True, retired=True)
        if len(result) == 1:
            return result
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(
            f"More than one serial number matching {str(tag)} was found.")

    def find_asset_by_sn(self, sn):
        """
        Gets an asset based on its serial number

        :param sn: serial number as a string or int

        :return: the asset with the corresponding serial number

        """
        search_params = {'SerialLike': sn}
        result = self.search_assets(search_params, disposed=True, retired=True)
        if len(result) == 1:
            return result
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(
            f"More than one serial number matching {str(sn)} was found.")

    def get_assets_by_location(self, location, max_results: int = 25):
        id_list = list()
        if isinstance(location, list):
            for this_location in location:
                id_list.append(this_location['ID'])
        else:
            id_list.append(location['ID'])
        return self.search_assets({'LocationIDs': id_list}, max_results=max_results)

    def get_assets_by_room(self, room: dict, max_results: int = 25):
        return self.search_assets({'RoomID': room['ID']}, max_results=max_results)

    def update_assets(self, asset, changed_attributes):
        """
        Updates data in a list of assets

        :param asset_list: a list of assets (maybe from search_assets()) or a single asset
        :param changed_attributes: a dict of attributes in the ticket to be changed

        :return: list of updated assets
        """
        if not isinstance(asset, list):
            asset_list = list()
            asset_list.append(asset)
        else:
            asset_list = asset
        updated_assets = list()
        post_body = dict()
        post_body['asset'] = changed_attributes
        for asset in asset_list:
            updated_assets.append(self.make_call(str(asset['ID']), 'post', post_body))
        return updated_assets

    def change_asset_owner(self, asset, new_owner_email, new_dept_name=None):
        """
        Gets updates data in a list of assets

        :param asset: asset to update (doesn't have to be full record)
        :param new_owner_email: email of new owner
        :param new_dept_name: name of new department

        :return: dict of the updated assets
        """
        new_owner_uid = self.get_person_by_name_email(new_owner_email)['UID']
        changed_attributes = {'OwningCustomerID': new_owner_uid}
        if new_dept_name:
            changed_attributes['OwningDepartmentID'] = self.get_account_by_name(new_dept_name)['ID']
        return self.update_assets(asset, changed_attributes)

    def move_child_assets(self, source_asset, target_asset):
        """
        Moves child assets from one asset to another

        :param source_asset: asset to move children from (doesn't have to be full record)
        :param target_asset: asset to move children to

        :return: dict of the updated assets
        """
        search_params = {'ParentID': source_asset['ID']}
        update_params = {'ParentID': target_asset['ID']}
        children = self.search_assets(search_params)
        return self.update_assets(children, update_params)

    def copy_asset_attributes(self, source_asset, target_asset, copy_name=False, exclude=None, new_status: str = None):
        """
        Copies asset attributes from one asset to another. Does not include attributes like Serial Number, Asset Tag,
            and other hardware-specific fields.


        :param source_asset: asset to copy attributes from (doesn't have to be full record)
        :param target_asset: asset to copy attributes to (doesn't have to full record) This asset will be OVERWRITTEN!
        :param copy_name: Set to true to copy the name of the source asset to the target asset
        :param exclude: List of attributes to be excluded, in addition to defaults
        :param new_status: Name or ID of new status for source asset

        :return: list of the target and source asset data
        """
        excluded_attributes = ['SerialNumber', 'Tag', 'ExternalID', 'ModelID', 'SupplierID', 'ManufacturerID',
                               'PurchaseCost', 'ExpectedReplacementDate', 'AcquisitionDate']
        if exclude:
            excluded_attributes.append(exclude)
        if not copy_name:
            excluded_attributes.append('Name')
        full_source = dict(self.get_asset_by_id(source_asset['ID']))
        for protected_attribute in excluded_attributes:
            full_source.pop(protected_attribute, None)
        updated_target = self.update_assets(target_asset, full_source)
        updated_source = None
        if new_status:
            update_params = {'StatusID': self.get_asset_status_by_name_id(new_status)}
            updated_source = self.update_assets(full_source, update_params)
        return [updated_target, updated_source]

    # TODO: make_basic_asset_json
    def make_basic_asset_json(self, asset_values, asset_name, serial_number, status_name, location_name, room_name,
                              asset_tag, acquisition_date=None, asset_lifespan=None, attrib_prefix=None, requester=None,
                              requesting_dept=None, owner=None, owning_dept=None, parent=None, external_id=None):
        """
        Makes a JSON object for inputting into makeTicket function

        :param asset_values: a dictionary (potentially loaded from google sheet) with asset info and custom attribs
        :param asset_name: a string containing the name for the asset
        :param serial_number: String with serial number of new asset
        :param status_name: String with name of status of new asset
        :param location_name: String with name of location for new asset
        :param room_name: String with name of room for new asset
        :param asset_tag: String with asset tag value for new asset
        :param acquisition_date: Building name of location (Default: date of execution)
        :param asset_lifespan: Years you expect this device to be in service (Default: 4)
        :param attrib_prefix: the string that prefixes all the custom attribute column names in the asset_values dict
        :param requester: String with email of requester for new asset (Default: integration username)
        :param requesting_dept: Account Name of requesting department for new asset
        :param owner: String with Email of owner of new asset
        :param owning_dept: String with Account name of owning department
        :param parent: Int with ID or String with serial number of a parent asset. Parent Asset must exist.
        :param external_id: String with external id for new asset (Default: serial Number)

        """
        # set defaults
        if not acquisition_date:
            acquisition_date = datetime.datetime.today()
        if not asset_lifespan:
            asset_lifespan = 4
        if not requester:
            requester = self.username
        if not external_id:
            external_id = serial_number

        expected_replacement_date = acquisition_date + datetime.timedelta(months=(asset_lifespan*12))

        # Required or defaulted parameters
        data = dict()
        data['Name'] = asset_name
        data['SerialNumber'] = serial_number
        data['StatusID'] = self.get_asset_status_by_name_id(status_name)['ID']
        data['LocationID'] = self.get_location_by_name(location_name)['ID']
        data['LocationRoomID'] = self.get_room_by_name(data['LocationID'], room_name)
        data['Tag'] = asset_tag
        data['AcquisitionDate'] = acquisition_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        data['ExpectedReplacementDate'] = expected_replacement_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        data['ExternalID'] = external_id

        # map per-ticket values into title and body

        # set up attribute values
        if attrib_prefix:
            data['Attributes'] = []
            # attrib_count = 0
            for key, value in asset_values.items():
                if attrib_prefix in key:
                    attrib_name = key.replace(attrib_prefix, "")
                    attrib = self.get_asset_custom_attribute_by_name(attrib_name)
                    value = self.get_custom_attribute_value_by_name(attrib, value)
                    new_attrib = dict()
                    new_attrib['ID'] = attrib['ID']
                    new_attrib['Value'] = value['ID']
                    data['Attributes'].append(new_attrib)
                    # attrib_count += 1
            # print("DEBUG: loaded " + str(attrib_count) + " attributes:")
            # print_nice(data['Attributes'])

        if location_name:
            building = self.get_location_by_name(location_name)
            data['LocationID'] = building['ID']
            if room_name:
                data['LocationRoomID'] = self.get_room_by_name(building, room_name)['ID']

        if requester:
            data['RequestingCustomerID'] = self.get_person_by_name_email(requester)['UID']
        if requesting_dept:
            data['RequestingDepartmentID'] = self.get_account_by_name(requesting_dept)['ID']
        if owner:
            data['OwningCustomerID'] = self.get_person_by_name_email(owner)['UID']
        if owning_dept:
            data['OwningDepartmentID'] = self.get_account_by_name(owning_dept)['ID']
        if parent:
            if type(parent) is int:
                data['ParentID'] = parent
            else:
                parent_asset = self.find_asset_by_sn(parent)
                if not parent_asset:
                    parent_asset = self.search_assets(parent, max_results=1)
                if parent_asset:
                    data['ParentID'] = parent_asset['ID']
        return data

    def create_asset(self, asset_json):
        """
        Creates an asset

        :param asset_json: a dict of asset info (maybe from make_asset_json()) to use in creation

        :return: dict of created asset details
        """
        url_string = '/' + str(self.asset_app_id) + 'assets'
        post_body = dict()
        post_body['asset'] = asset_json
        created_asset = self.make_post(url_string, post_body)
        return created_asset

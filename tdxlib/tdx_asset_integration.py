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
        self.cache['product_model'] = {}
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

    # TODO: Move this down to a more logical place
    def get_asset_custom_attribute_by_name_id(self, key: str) -> dict:
        # Since there are two different types we may have to get, we cache them all
        search_key = str(key) + "_asset_ci"
        if search_key in self.cache['ca_search']:
            return self.cache['ca_search'][search_key]
        # There is no API for searching attributes -- the only way is to get them all.
        for item in self.cache['custom_attributes']:
            if str(key).lower() == item['Name'].lower() or str(key) == str(item['ID']):
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
            if str(asset_form['ID']).lower() == str(key):
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

    # TODO: def update_asset_status(self, updated_values)-> dict:
    # TODO: def create_asset_status(self, params)-> dict:

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
            self.cache['product_type'] = self.get_all_product_types()
        for product_type in self.cache['product_type']:
            if product_type['Name'].lower() == str(key).lower()or str(product_type['ID']) == str(key):
                return product_type
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(f'No product type found for {str(key)}')

    # TODO: def update_product_type(self, updated_values)-> dict:
    # TODO: def create_product_type(self, params)-> dict:
    # TODO: def delete_product_type(self)-> dict:

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
            self.cache['product_model'] = self.get_all_product_models()
        for product_model in self.cache['product_model']:
            if product_model['Name'].lower() == str(key).lower() or str(product_model['ID']) == str(key):
                return product_model
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(f'No product model found for {str(key)}')

    # TODO: def update_product_model(self, updated_values)-> dict:
    # TODO: def create_product_model(self, params)-> dict:
    # TODO: def delete_product_model(self, updated_values)-> dict:

    # TODO: def get_all_vendors(self) -> list:
    # TODO: def update_vendor(self, updated_values)-> dict:
    # TODO: def create_vendor(self, params)-> dict:
    # TODO: def delete_vendor(self)-> dict:

    def get_asset_by_id(self, asset_id: str) -> dict:
        """
        Gets a full list of asset attributes and values

        :param asset_id: asset ID from TDX

        :return: dict of asset data
        """
        return self.make_call(str(asset_id), 'get')

    def search_assets(self, criteria, max_results=25, retired=False, disposed=False, full_record=False) -> list:
        """
        Gets a ticket, based on criteria

        :param max_results: maximum number of results to return
        :param criteria: a string or dict to search for tickets with. If a string, use as 'SearchString'
        :param retired: include retired assets in search if true
        :param disposed: include disposed assets in search if true
        :param full_record: get full asset record (Default: False). Takes more time, but returns full asset record

        :return: list of asset info (by default, NOT FULL ASSET RECORDS, must do get_asset_by_id() to get full record)

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
        if full_record:
            full_assets = []
            for asset in asset_list:
                full_assets.append(self.get_asset_by_id(asset['ID']))
            return full_assets
        else:
            return asset_list

    def find_asset_by_tag(self, tag) -> dict:
        """
        Gets an asset based on its asset tag

        :param tag: asset tag as a string or int

        :return: the single asset with the corresponding tag
        """
        if type(tag) is str:
            tag = tag.lstrip('0')
        search_params = {'SearchText': str(tag)}
        result = self.search_assets(search_params, disposed=True, retired=True)
        if len(result) == 1:
            return result[0]
        else:
            for asset in result:
                if asset['Tag'] == tag:
                    return asset
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(
            f"{str(len(result))} assets with tag {str(tag)} found.")

    def find_asset_by_sn(self, sn) -> dict:
        """
        Gets an asset based on its serial number

        :param sn: serial number as a string or int

        :return: the single asset with the corresponding serial number

        """
        search_params = {'SerialLike': sn}
        result = self.search_assets(search_params, disposed=True, retired=True)
        if len(result) == 1:
            return result[0]
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(
            f"{str(len(result))} assets with SN {str(sn)} found.")

    def get_assets_by_location(self, location, max_results: int = 5000) -> list:
        """
        Gets all asset in a location

        :param location: a single location (from get_location_by_name()) or list of same
        :param max_results: an integer indicating the maximum number of results that should be returned (default: 25)

        :return: a list of assets in the location(s)

        """
        id_list = list()
        if isinstance(location, list):
            for this_location in location:
                if isinstance(this_location, dict):
                    id_list.append(this_location['ID'])
                if isinstance(this_location, str):
                    id_list.append(self.get_location_by_name(this_location)['ID'])
        elif isinstance(location, dict):
            id_list.append(location['ID'])
        elif isinstance(location, str):
            id_list.append(self.get_location_by_name(location)['ID'])
        return self.search_assets({'LocationIDs': id_list}, max_results=max_results)

    def get_assets_by_room(self, room: dict, max_results: int = 25) -> list:
        """
        Gets all assets in a room

        :param room: a single room (from get_room_by_name())
        :param max_results: an integer indicating the maximum number of results that should be returned (default: 25)

        :return: a list of assets in the room

        """
        return self.search_assets({'RoomID': room['ID']}, max_results=max_results)

    def get_assets_by_owner(self, person: str, max_results: int = 25, retired=False, disposed=False) -> list:
        """
        Gets all assets assigned to a particular person in TDX

        :param person: the name or email of a person in TDX, or a dict containing their information
        :param max_results: an integer indicating the maximum number of results that should be returned (default: 25)

        :return: a list of assets owned by that person

        """
        if isinstance(person, str):
            person = self.get_person_by_name_email(person)
        if not isinstance(person, dict):
            raise tdxlib.tdx_api_exceptions.TdxApiObjectTypeError("Can't search assets with type" +
                                                                  str(type(person)) + " as person.")
        return self.search_assets({'OwningCustomerIDs': [person['UID']]},
                                  max_results=max_results,
                                  retired=retired,
                                  disposed=disposed)

    def get_assets_by_requesting_department(self, dept, max_results: int = 25) -> list:
        """
        Gets all assets requested by a particular account/department in TDX

        :param dept: the name or email of a account/department, or a dict containing its information
        :param max_results: an integer indicating the maximum number of results that should be returned (default: 25)

        :return: a list of assets requested by that department

        """
        if isinstance(dept, str):
            dept = self.get_account_by_name(dept)
        if not isinstance(dept, dict):
            raise tdxlib.tdx_api_exceptions.TdxApiObjectTypeError("Can't search assets with type" +
                                                                  str(type(dept)) + " as department.")
        return self.search_assets({'RequestingDepartmentIDs': [dept['ID']]}, max_results=max_results)

    def update_assets(self, assets, changed_attributes: dict, clear_custom_attributes=False) -> list:
        """
        Updates data in a list of assets

        :param assets: a list of assets (maybe from search_assets()) or a single asset (only ID required)
        :param changed_attributes: a dict of attributes in the ticket to be changed
        :param clear_custom_attributes: (default: False) A boolean indicating whether or not custom attributes should be cleared

        :return: list of updated assets
        """
        if not isinstance(assets, list):
            asset_list = list()
            asset_list.append(assets)
        else:
            asset_list = assets
        updated_assets = list()
        for this_asset in asset_list:
            this_asset=self.get_asset_by_id(this_asset['ID'])
            if 'Attributes' in changed_attributes and not clear_custom_attributes:
                for new_attrib in changed_attributes['Attributes']:
                    new_attrib_marker = True
                    for attrib in this_asset['Attributes']:
                        if str(new_attrib['ID']) == str(attrib['ID']):
                            attrib['Value'] = new_attrib['Value']
                            new_attrib_marker=False
                            continue
                    if new_attrib_marker:
                        this_asset['Attributes'].append(new_attrib)
            if clear_custom_attributes:
                changed_attributes['Attributes'] = []
            else:
                changed_attributes['Attributes'] = this_asset['Attributes']
            this_asset.update(changed_attributes)
            updated_assets.append(self.make_call(str(this_asset['ID']), 'post', this_asset))
        return updated_assets

    def change_asset_owner(self, asset, new_owner, new_dept=None) -> list:
        """
        Gets updates data in a list of assets

        :param asset: asset to update (doesn't have to be full record), or list of same
        :param new_owner: email or name of new owner, or dict of their information
        :param new_dept: name of new department, or dict of information

        :return: list of the updated assets
        """
        if isinstance(new_owner, str):
            new_owner_uid = self.get_person_by_name_email(new_owner)['UID']
        elif isinstance(new_owner, dict):
            new_owner_uid = new_owner['UID']
        else:
            raise tdxlib.tdx_api_exceptions.TdxApiObjectTypeError(
                f"New Owner of type {str(type(new_dept))} not searchable."
            )
        changed_attributes = {'OwningCustomerID': new_owner_uid}
        if new_dept:
            if isinstance(new_dept, str):
                changed_attributes['OwningDepartmentID'] = self.get_account_by_name(new_dept)['ID']
            elif isinstance(new_dept, dict):
                changed_attributes['OwningDepartmentID'] = new_dept['ID']
            else:
                raise tdxlib.tdx_api_exceptions.TdxApiObjectTypeError(
                    f"Department of type {str(type(new_dept))} not searchable."
                )
        return self.update_assets(asset, changed_attributes)

    def change_asset_requesting_dept(self, asset, new_dept)-> list:
        """
        Gets updates data in a list of assets

        :param asset: asset to update (doesn't have to be full record), or list of same
        :param new_dept: name of new department

        :return: list of the updated assets
        """
        changed_attributes = dict()
        if isinstance(new_dept, str):
            changed_attributes['RequestingDepartmentID'] = self.get_account_by_name(new_dept)['ID']
        elif isinstance(new_dept, dict):
            changed_attributes['RequestingDepartmentID'] = new_dept['ID']
        else:
            raise tdxlib.tdx_api_exceptions.TdxApiObjectTypeError(
                f"Department of type {str(type(new_dept))} not searchable."
            )
        return self.update_assets(asset, changed_attributes)

    def build_asset_custom_attribute_value(self, custom_attribute, value) -> dict:
        """
        Changes the value of a specific custom attribute on one or more tickets.

        :param asset: asset to update (doesn't have to be full record), or list of same
        :param custom_attribute: name of custom attribute (or dict of info)
        :param value: name of value to set, or value to set to
        :return: list of updated assets in dict format
        """
        if isinstance(custom_attribute, str) or isinstance(custom_attribute, int):
            ca = self.get_asset_custom_attribute_by_name_id(str(custom_attribute))
        elif isinstance(custom_attribute, dict):
            ca = str(custom_attribute)
        else:
            raise tdxlib.tdx_api_exceptions.TdxApiObjectTypeError(
                f"Custom Attribute of type {str(type(new_dept))} not searchable."
            )
        if len(ca['Choices'])> 0:
            ca_choice = self.get_custom_attribute_choice_by_name_id(ca, value)
            value = ca_choice['ID']
        return {'ID': ca['ID'], 'Value': value}

    def change_asset_custom_attribute_value(self, asset, custom_attributes: list) -> list:
        """
        Takes a correctly formatted list of CA's (from build_asset_custom_attribute_value, for instance)
        and updates one or more assets with the new values.

        :param asset: asset to update (doesn't have to be full record), or list of same
        :param custom_attributes: List of ID/Value dicts (from build_asset_custom_attribute_value())
        :return: list of updated assets in dict format
        """
        to_change = {'Attributes': custom_attributes}
        return self.update_assets(asset, to_change)

    def move_child_assets(self, source_asset: dict, target_asset: dict) -> list:
        """
        Moves child assets from one asset to another

        :param source_asset: asset to move children from (doesn't have to be full record)
        :param target_asset: asset to move children to

        :return: list of the updated assets
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
                    attrib = self.get_asset_custom_attribute_by_name_id(attrib_name)
                    value = self.get_custom_attribute_choice_by_name_id(attrib, value)
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

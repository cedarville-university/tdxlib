import datetime
import tdxlib.tdx_integration


class TDXAssetIntegration(tdxlib.tdx_integration.TDXIntegration):
    def __init__(self, filename):
        tdxlib.tdx_integration.TDXIntegration.__init__(self, filename)
        if self.asset_app_id is None:
            raise ValueError("Asset App Id is required. Check your config file")
        self.assetForms = self.get_all_asset_forms()
        self.custom_attributes = self.get_all_custom_attributes(27, app_id=self.asset_app_id)
        self.custom_attributes_ci = self.get_all_custom_attributes(63, app_id=self.asset_app_id)
        self.asset_form_cache = dict()
        self.asset_status_cache = dict()
        self.asset_model_cache = dict()
        self.asset_type_cache = dict()
        # Overriding parent method to limit re-definition

    def make_asset_call(self, url, action, post_body=None):
        url_string = '/' + str(self.asset_app_id) + '/assets'
        url_string = '/' + str(self.asset_app_id) + '/assets'
        if len(url) > 0:
            url_string += '/' + url
        if action == 'get':
            return self.make_get(url_string)
        if action == 'post' and post_body:
            return self.make_post(url_string, post_body)
        raise tdxlib.tdx_api_exceptions.TdxApiHTTPRequestError('No method' + action + 'or no post information')

    def make_call(self, url, action, post_body=None):
        return self.make_asset_call(url, action, post_body)

    def get_custom_attribute_by_name(self, key):
        super(key, 27)

    def get_all_asset_forms(self):
        """
        Gets a list asset forms

        :return: list of form data in json format
        """
        return self.make_call('forms', 'get')
        
    def get_asset_form_by_name(self, key):
        """
        Gets a list asset forms

        :param key: name of AssetForm to search for

        :return: list of form data in json format
        """
        forms = self.get_all_asset_forms()
        for form in forms:
            if form['Name'] == key:
                return form
        print('no Asset form found for ' + key)

    def get_all_asset_statuses(self):
        """
        Gets a list asset statuses

        :return: list of status data
        """
        return self.make_call('statuses', 'get')

    def get_asset_status_by_name(self, key):
        """
        Gets a list asset forms

        :param key: name of Asset Status to search for

        :return: list of status data
        """
        if key in self.asset_status_cache:
            return self.asset_status_cache[key]
        else:
            statuses = self.get_all_asset_statuses()
            for status in statuses:
                if status['Name'] == key:
                    self.asset_status_cache[key] = status
                    return status
            raise RuntimeError('no asset status found for ' + key)

    def get_all_product_types(self):
        """
        Gets a list of product types

        :return: list of product type data
        """
        return self.make_call("models/types", 'get')

    def get_product_type_by_name(self, key):
        """
        Gets a product type object

        :param key: name of product type to search for

        :return: dict of product type data
        """
        if key in self.asset_type_cache:
            return self.asset_type_cache[key]
        else:
            types = self.get_all_product_types()
            for product_type in types:
                if product_type['Name'] == key:
                    self.asset_type_cache[key] = product_type
                    return product_type
            raise RuntimeError('no asset status found for ' + key)

    def get_all_product_models(self):
        """
        Gets a list asset models
        :return: list of model data
        """
        return self.make_call("models", 'get')

    def get_product_model_by_name(self, key):
        """
        Gets a specific product model
        :param key: name of product model to search for
        :return: dict of model data
        """
        if key in self.asset_model_cache:
            return self.asset_model_cache[key]
        else:
            models = self.get_all_product_models()
            for product_model in models:
                if product_model['Name'] == key:
                    self.asset_model_cache[key] = product_model
                    return product_model
            raise RuntimeError('no asset status found for ' + key)

    def get_asset_by_id(self, asset_id):
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
        statuses.append(self.get_asset_status_by_name("Inventory")['ID'])
        statuses.append(self.get_asset_status_by_name("In Use")['ID'])
        statuses.append(self.get_asset_status_by_name("Broken")['ID'])

        # Set conditional statuses
        if retired:
            statuses.append(self.get_asset_status_by_name("Retired")['ID'])
        if disposed:
            statuses.append(self.get_asset_status_by_name("Disposed")['ID'])

        # Set up search body
        search_body = dict()
        search_body['search'] = {'MaxResults': str(max_results), 'StatusIDs': statuses}
        if type(criteria) is str:
            search_body['search']['SearchText'] = criteria
        elif type(criteria) is dict:
            search_body['search'].update(criteria)
        else:
            raise TypeError("Can't search assets with" + str(type(criteria)))

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
        return self.search_assets(search_params, max_results=1, disposed=True, retired=True)

    def find_asset_by_sn(self, sn):
        """
        Gets an asset based on its serial number

        :param sn: serial number as a string or int

        :return: the asset with the corresponding serial number

        """
        search_params = {'SerialLike': sn}
        return self.search_assets(search_params, max_results=1, disposed=True, retired=True)

    def update_assets(self, asset_list, changed_attributes):
        """
        Updates data in a list of assets

        :param asset_list: a list of assets (maybe from search_assets())
        :param changed_attributes: a dict of attributes in the ticket to be changed

        :return: list of updated assets
        """
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

    def copy_asset_attributes(self, source_asset, target_asset, copy_name=False, exclude=None, new_status_name=None):
        """
        Copies asset attributes from one asset to another

        :param source_asset: asset to copy attributes from (doesn't have to be full record)
        :param target_asset: asset to copy attributes to (doesn't have to full record (OVERWRITES FULL RECORD)
        :param copy_name: Set to true to copy the name of the asset
        :param exclude: List of attributes to be excluded, in addition to defaults
        :param new_status_name: String of name of new status for source asset

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
        if new_status_name:
            update_params = {'StatusID': self.get_asset_status_by_name(new_status_name)}
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
        data['StatusID'] = self.get_asset_status_by_name(status_name)['ID']
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
                    attrib = self.get_asset_attribute_by_name(attrib_name)
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
            data['RequestingCustomerID'] = self.get_person_by_email(requester)['UID']
        if requesting_dept:
            data['RequestingDepartmentID'] = self.get_account_by_name(requesting_dept)['ID']
        if owner:
            data['OwningCustomerID'] = self.get_person_by_email(owner)['UID']
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

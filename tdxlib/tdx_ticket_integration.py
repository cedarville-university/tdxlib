import tdxlib.tdx_ticket
import copy
import datetime
import tdxlib.tdx_integration
import tdxlib.tdx_api_exceptions
from typing import Union
from typing import BinaryIO


class TDXTicketIntegration(tdxlib.tdx_integration.TDXIntegration):
    # These are hard-coded by TeamDynamix and not accessible through the API
    ticket_classifications = {
        'Ticket': 9,
        'Incident': 32,
        'MajorIncident': 77,
        'Problem': 33,
        'Change': 34,
        'Release': 35,
        'TicketTemplate': 36,
        'ServiceRequest': 46
    }
    ticket_status_classes = {
        'None': 0,
        'New': 1,
        'InProcess': 2,
        'Completed': 3,
        'Cancelled': 4,
        'OnHold': 5,
        'Requested': 6
    }

    def __init__(self, filename: str = None, config=None):
        tdxlib.tdx_integration.TDXIntegration.__init__(self, filename, config)
        if self.config.ticket_app_id is None:
            raise RuntimeError("Ticket App Id is required. Check your configuration.")
        self.clean_cache()

    def clean_cache(self):
        """
        Clears the tdx_ticket_integration cache.

        :return:  None

        """
        super().clean_cache()
        self.cache['ticket_type'] = {}
        self.cache['ticket_status'] = {}
        self.cache['ticket_priority'] = {}
        self.cache['ticket_urgency'] = {}
        self.cache['ticket_impact'] = {}
        self.cache['ticket_source'] = {}
        self.cache['ticket_form'] = {}

    def get_url_string(self):
        return '/' + str(self.config.ticket_app_id) + '/tickets'

    def _make_ticket_call(self, url: str, action: str, post_body: dict = None):
        url_string = self.get_url_string()
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
        raise tdxlib.tdx_api_exceptions.TdxApiHTTPRequestError('No method ' + action + ' or no post information')

    def make_call(self, url: str, action: str, post_body: dict = None):
        """
        Makes an HTTP call using the Tickets API information.

        :param url: The URL (everything after tickets/) to call
        :param action: The HTTP action (get, put, post, delete, patch) to perform.
        :param post_body: A dict of the information to post, put, or patch. Not used for get/delete.

        :return: the API response as a python dict or list

        """
        return self._make_ticket_call(url, action, post_body)

    def get_all_ticket_custom_attributes(self):
        return self.get_all_custom_attributes(TDXTicketIntegration.component_ids['ticket'],
                                              app_id=self.config.ticket_app_id)

    def get_ticket_custom_attribute_by_name_id(self, key: str) -> dict:
        """
        Gets a ticket custom attribute based on its name or ID. This includes hard-coded the component ID for tickets.

        :param key: A full or partial name of the CA to get.

        :return: a dict of custom attribute information

        :rtype: dict

        """
        return self.get_custom_attribute_by_name_id(key, TDXTicketIntegration.component_ids['ticket'])

    # Alias names
    get_ticket_custom_attribute_by_name = get_ticket_custom_attribute_by_name_id

    def build_ticket_custom_attribute_value(self, custom_attribute: Union[str, dict], value: Union[str, int]) -> dict:
        """
        Builds a custom attribute for a ticket from the name of the attribute and value.

        :param custom_attribute: name of custom attribute (or dict of info from )
        :param value: name of value to set, or value to set to

        :return: list of updated assets in dict format (for use in change_custom_attribute_value())

        """
        if isinstance(custom_attribute, str) or isinstance(custom_attribute, int):
            ca = self.get_ticket_custom_attribute_by_name_id(str(custom_attribute))
        elif isinstance(custom_attribute, dict):
            ca = custom_attribute
        else:
            raise tdxlib.tdx_api_exceptions.TdxApiObjectTypeError(
                f"Custom Attribute of type {str(type(custom_attribute))} not searchable."
            )
        if len(ca['Choices']) > 0:
            ca_choice = self.get_custom_attribute_choice_by_name_id(ca, value)
            value = ca_choice['ID']
        if isinstance(value, datetime.datetime):
            value = tdxlib.tdx_utils.export_tdx_date(value)
        return {'ID': ca['ID'], 'Value': value}

    def change_ticket_custom_attribute_value(self, ticket: Union[dict, str, int, list],
                                             custom_attributes: list) -> Union[tdxlib.tdx_ticket.TDXTicket, list]:
        """
        Takes a correctly formatted list of CA's (from build_ticket_custom_attribute_value, for instance)
        and updates one or more assets with the new values.

        :param ticket: ticket/Ticket ID to update (doesn't have to be full record), or list of same
        :param custom_attributes: List of ID/Value dicts (from build_ticket_custom_attribute_value())
        :return: list of updated ticket in dict format
        """
        to_change = {'Attributes': custom_attributes}
        if isinstance(ticket, list):
            return self.edit_tickets(ticket, to_change)
        return self.edit_ticket(ticket, to_change)

    # #### GETTING TICKETS #### #

    def get_ticket_by_id(self, ticket_id: int) -> tdxlib.tdx_ticket.TDXTicket:
        """
        Gets a ticket, based on its ID

        :param ticket_id: ticket ID of required ticket

        :return: ticket info as python dict

        :rtype: dict
        """
        ticket_data = self.make_call(str(ticket_id), 'get')
        if ticket_data:
            return tdxlib.tdx_ticket.TDXTicket(self, ticket_data)

    def search_tickets(self, criteria: dict, max_results: int = 25, closed: bool = False, cancelled: bool = False,
                       other_status: bool = False) -> list:
        """
        Gets a ticket, based on a variety of criteria::

            {'TicketClassification': [List of Int],
            'SearchText': [String],
            'Status IDs': [List of Int],
            'ResponsibilityUids': [List of String (GUID)],
            'ResponsibilityGroupIDs': [List of String (ID)],
            'RequestorEmailSearch': [String],
            'LocationIDs': [List of Int],
            'LocationRoomIds': [List of Int],
            'CreatedDateFrom': [DateTime],
            'CreatedDateTo': [DateTime],
            'SlaViolationStatus': [Boolean -- true = SLA Violated]}

        (https://api.teamdynamix.com/TDWebApi/Home/type/TeamDynamix.Api.Tickets.TicketSearch)


        :param max_results: maximum number of results to return
        :param criteria: a string, list or dict to search for tickets with
        :param cancelled: include cancelled tickets in search if true
        :param closed: include closed tickets in search if true
        :param other_status: Status ID of a custom status

        :return: list of TDXTicket objects

        :rtype: list


        """
        # Set default statuses
        statuses = list()
        statuses.append(self.search_ticket_status("New")['ID'])
        statuses.append(self.search_ticket_status("Open")['ID'])
        statuses.append(self.search_ticket_status("On Hold")['ID'])

        # Set conditional statuses
        if closed:
            statuses.append(self.search_ticket_status("Closed")['ID'])
        if cancelled:
            statuses.append(self.search_ticket_status("Cancelled")['ID'])
        if other_status:
            statuses.append(other_status)

        # Set up search body
        search_body = {'MaxResults': max_results, 'StatusIDs': statuses}
        if type(criteria) is str:
            search_body['SearchText'] = criteria
        elif type(criteria) is dict:
            search_body.update(criteria)
        else:
            raise TypeError("Can't search tickets with" + str(type(criteria)))
        ticket_data_list = self.make_call('search', 'post', search_body)
        ticket_list = list()
        for ticket_data in ticket_data_list:
            ticket_list.append(tdxlib.tdx_ticket.TDXTicket(self, ticket_data))
        return ticket_list

    # #### CHANGING TICKETS #### #

    def edit_ticket(self, ticket: Union[tdxlib.tdx_ticket.TDXTicket, str, int], changed_attributes: dict,
                    notify: bool = False) -> tdxlib.tdx_ticket.TDXTicket:
        """
        Edits one ticket, based on a dict of parameters to change.

        :param ticket: a TDXTicket object or a Ticket ID
        :param changed_attributes: Attributes to alter in the ticket
        :param notify: If true, will notify newly-responsible resource if changed because of edit (default: false)

        :return: edited ticket as TDXTicket

        :rtype: tdxlib.tdx_ticket.TDXTicket

        """
        changed_custom_attributes = False
        if not isinstance(ticket, tdxlib.tdx_ticket.TDXTicket):
            full_ticket = self.get_ticket_by_id(ticket)
        else:
            full_ticket = ticket
        # Separate CA changes into their own object: 'changed_custom_attributes'.
        # need to make a full copy of this dict, so we can reuse it
        changed_attributes_copy = copy.deepcopy(changed_attributes)
        if 'Attributes' in changed_attributes:
            if isinstance(changed_attributes['Attributes'], list):
                changed_custom_attributes = changed_attributes['Attributes']
            else:
                changed_custom_attributes = [changed_attributes['Attributes']]
            # Remove attributes field of "changed_attributes" so it doesn't mess up the existing asset(s) CA's
            # need to set it to an empty list first, so it doesn't delete the object that was passed in
            del changed_attributes_copy['Attributes']
        # not totally sure the first part is necessary. I think it always comes through as an empty list if no CA's
        if 'Attributes' not in full_ticket.ticket_data.keys():
            full_ticket.ticket_data['Attributes'] = []
        if changed_custom_attributes:
            # Loop through each of the CAs to be changed
            for new_attrib in changed_custom_attributes:
                # Drop a marker so we know if
                new_attrib_marker = True
                # Loop through the existing CA's, to look for stuff to update
                for attrib in full_ticket.ticket_data['Attributes']:
                    # if we find a match, we update it in the existing asset record
                    if str(new_attrib['ID']) == str(attrib['ID']):
                        attrib['Value'] = new_attrib['Value']
                        new_attrib_marker = False
                # if we go through all the asset's  CA's, and haven't updated something, we just put it in.
                if new_attrib_marker:
                    full_ticket.ticket_data['Attributes'].append(new_attrib)
        # incorporate the non-custom changed attributes to the existing asset record, if they exist
        if changed_attributes_copy:
            full_ticket.update(changed_attributes_copy, validate=True)
        url_string = '{ID}?notifyNewResponsible=' + str(notify)
        post_body = full_ticket.export(validate=True)
        edited_dict = self.make_call(url_string.format_map(
            {'ID': str(full_ticket.get_id())}), 'post', post_body)
        return tdxlib.tdx_ticket.TDXTicket(self, json=edited_dict)

    # TODO: Implement a HTTP Patch version of this
    def edit_tickets(self, ticket_list: list, changed_attributes: dict,
                     notify: bool = False, visual: bool = False) -> list:
        """
        Edits one or more tickets, based on a dict of parameters to change

        :param ticket_list: list of TDXTicket objects, maybe from search_tickets
        :param changed_attributes: Attributes to alter in selected tickets
        :param notify: If true, will notify newly-responsible resource(s) if changed because of edit
        :param visual: If true, print a . for each successful ticket that is edited

        :return: list of edited TDXTicket objects, with complete data in json format

        :rtype: list

        """
        edited_tickets = list()
        for ticket in ticket_list:
            edited_ticket = self.edit_ticket(ticket, changed_attributes, notify)
            edited_tickets.append(edited_ticket)
            if visual and edited_ticket:
                print('.', end='')
        return edited_tickets

    def reassign_ticket(self, ticket_id: Union[str, int], responsible: str, group: bool = False) \
            -> tdxlib.tdx_ticket.TDXTicket:
        """
        Reassigns a ticket  to a person or group
    
        :param ticket_id: The ticket of the ticket you want to edit.
        :param responsible: a username, email, Full Name, or ID number to use to search for a person
        :param group: If this parameter is True, assign to group instead of individual
    
        :return: Edited TDXTicket object, if the operation was successful

        :rtype: tdxlib.tdx_ticket.TDXTicket
    
        """
        if group:
            reassign = {'ResponsibleGroupID': self.get_group_by_name(responsible)['ID']}
        else:
            reassign = {'ResponsibleUid': self.get_person_by_name_email(responsible)['UID']}
        return self.edit_ticket(ticket_id, reassign)

    def reschedule_ticket(self, ticket_id: Union[str, int], start_date: datetime.datetime = False,
                          end_date: datetime.datetime = False) -> tdxlib.tdx_ticket.TDXTicket:
        """
        Reschedules the start and end dates of a ticket. This is impossible if the ticket has a task.

        :param ticket_id: The ticket of the ticket you want to edit.
        :param start_date: datetime.datetime object for the start date of the ticket (defaults to now)
        :param end_date: datetime.datetime object for the end date of the ticket (defaults to now + 1 day)

        :return: Edited TDXTicket object, if the operation was successful

        :rtype: tdxlib.tdx_ticket.TDXTicket

        """
        if not start_date:
            start_date = datetime.datetime.utcnow()
        if not end_date:
            end_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        new_dates = {
            'StartDate': start_date,
            'EndDate': end_date
        }
        return self.edit_ticket(ticket_id, new_dates)

    def update_ticket(self, ticket_id: Union[str, int], comments: str, new_status: str = None, notify: list = None,
                      private: bool = True) -> dict:
        """
        Sends an update to a ticket feed.

        :param ticket_id: the ticket ID whose task to update
        :param comments: a string to provide as a comment to the update.
        :param new_status: The name of the new status to set for the ticket (Default: The status whose ID is 0)
        :param notify: a list of strings containing email addresses to notify regarding this ticket. Default: None
        :param private: boolean indicating whether the update to the task should be private. Default: True

        :return: python dict containing created ticket update information

        :rtype: dict

        """
        if not notify:
            notify = []
        url_string = f'{ticket_id}/feed'
        data = {
            'Comments': comments,
            'Notify': notify,
            'IsPrivate': str(private)
            }
        if new_status:
            data['NewStatusID'] = self.search_ticket_status(new_status)['ID']
        else:
            data['NewStatusID'] = 0
        return self.make_call(url_string, 'post', data)

    def upload_attachment(self, ticket_id: Union[str, int], file: BinaryIO, filename: str = None):
        """
        Uploads an attachment to a ticket.

        :param ticket_id: the ticket ID to upload the attachment
        :param file: Python file object opened in binary read mode to upload as attachment
        :param filename: (optional), explicitly specify filename header. If None, requests will determine from
        passed-in file object.

        :return: python dict containing created attachment information
        
        :rtype: dict
        """
        url = self.get_url_string()
        url += f"/{ticket_id}/attachments"
        return self.make_file_post(url, file, filename)

    # #### GETTING TICKET ATTRIBUTES #### #

    def get_ticket_feed(self, ticket_id: Union[str, int]) -> list:
        """
        Gets the feed entries from a ticket.

        :param ticket_id: The ticket ID on which the ticket task exists.

        :return: list of feed entries from the task as python dicts, if any exist

        :rtype: list

        """
        url_string = f'{ticket_id}/feed'
        return self.make_call(url_string, 'get')

    def get_all_ticket_forms(self) -> list:
        """
        Gets a list of all ticket forms from TDX.

        :return: list of ticket forms as python dicts

        :rtype: list

        """
        url_string = "forms"
        return self.make_call(url_string, 'get')

    def get_ticket_form_by_name_id(self, key: Union[str, int]) -> dict:
        """
        Gets ticket form based on ID or Name.

        :param key: Name or ID of form to search for

        :return: form data in python dict

        :rtype: dict

        """
        if not self.cache['ticket_form']:
            self.cache['ticket_form'] = self.get_all_ticket_forms()
        for ticket_form in self.cache['ticket_form']:
            if ticket_form['ID'] == key:
                return ticket_form
            if str(key).lower() in ticket_form['Name'].lower():
                return ticket_form
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(
                f'No type found with ID or Name {key}')

    def get_all_ticket_types(self) -> list:
        """
        Gets a list of all ticket types from TDX.

        :return: list of type data in python dicts

        :rtype: list

        """
        url_string = "types"
        return self.make_call(url_string, 'get')

    def get_ticket_type_by_name_id(self, key: Union[str, int]) -> dict:
        """
        Gets ticket type based on ID or Name.

        :param key: Name or ID of attribute to search for

        :return: type data in python dict

        :rtype: dict

        """
        if not self.cache['ticket_type']:
            self.cache['ticket_type'] = self.get_all_ticket_types()
        for ticket_type in self.cache['ticket_type']:
            if ticket_type['ID'] == key:
                return ticket_type
            if str(key).lower() in ticket_type['Name'].lower():
                return ticket_type
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(
                f'No type found with ID or Name {key}')

    def get_all_ticket_statuses(self) -> list:
        """

        Gets a list of all ticket statuses from TDX

        :return: list of status data in python dicts

        :rtype: list

        """
        url_string = "statuses"
        return self.make_call(url_string, 'get')

    def get_ticket_status_by_id(self, key: Union[str, int]) -> dict:
        """
        Gets ticket status based on ID or Name.

        :param key: ID of ticket status to search for

        :return: status data in python dict

        :rtype: dict

        """
        if key not in self.cache['ticket_status']:
            url_string = f'statuses/{key}'
            self.cache['ticket_status'][key] = self.make_call(url_string, 'get')
        return self.cache['ticket_status'][key]

    def search_ticket_status(self, key: str) -> dict:
        """
        Gets ticket status based on name.

        :param key: Name of ticket status to search for

        :return: status data in python dict

        :rtype: dict

        """
        if key in self.cache['ticket_status']:
            return self.cache['ticket_status'][key]
        else:
            post_body = {
                'SearchText': key
            }
            url_string = 'statuses/search'
            data = self.make_call(url_string, 'post', post_body)
            if data:
                # Add result to cache under searched key
                self.cache['ticket_status'][key] = data[0]
                if key != data[0]['Name']:
                    # Add result to cache under ['Name'] property too, just for extra fun
                    self.cache['ticket_status'][data[0]['Name']] = data[0]
                return data[0]
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(f"No status found for {key}")

    def get_all_ticket_priorities(self) -> list:
        """
        Gets a list of all ticket priorities from TDX.

        :return: list of priorities in python dict

        :rtype: list

        """
        url_string = "priorities"
        return self.make_call(url_string, 'get')

    def get_ticket_priority_by_name_id(self, key: Union[str, int]) -> dict:
        """
        Gets ticket priority based on ID or Name.

        :param key: ID or Name of priority to search for

        :return: priority data in python dict

        :rtype: dict

        """
        if not self.cache['ticket_priority']:
            self.cache['ticket_priority'] = self.get_all_ticket_priorities()
        for ticket_priority in self.cache['ticket_priority']:
            if ticket_priority['ID'] == key:
                return ticket_priority
            if str(key).lower() in ticket_priority['Name'].lower():
                return ticket_priority
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(f'No priority found for {key}')

    def get_all_ticket_urgencies(self) -> list:
        """
        Gets all ticket urgencies from the Tickets app.

        :return: list of priorities in python dict

        :rtype: dict

        """
        url_string = "urgencies"
        return self.make_call(url_string, 'get')

    def get_ticket_urgency_by_name_id(self, key: Union[str, int]) -> dict:
        """
        Gets ticket urgency based on ID or Name.

        :param key: ID or Name of urgency to search for

        :return: urgency data in python dict

        :rtype: dict

        """
        if not self.cache['ticket_urgency']:
            self.cache['ticket_urgency'] = self.get_all_ticket_urgencies()
        for ticket_urgency in self.cache['ticket_urgency']:
            if str(ticket_urgency['ID']) == str(key):
                return ticket_urgency
            if str(key).lower() in ticket_urgency['Name'].lower():
                return ticket_urgency
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(f'No urgency found for {key}')
    
    def get_all_ticket_impacts(self) -> list:
        """
        Gets a list of all ticket impacts from TDX.

        :return: list of impacts in as python dicts

        :rtype: dict

        """
        url_string = "impacts"
        return self.make_call(url_string, 'get')

    def get_ticket_impact_by_name_id(self, key: Union[str, int]) -> dict:
        """
        Gets ticket impact based on ID or Name

        :param key: Name or ID of impact to search for

        :return: impact data in python dict

        :rtype: dict

        """
        if not self.cache['ticket_impact']:
            self.cache['ticket_impact'] = self.get_all_ticket_impacts()
        for ticket_impact in self.cache['ticket_impact']:
            if str(ticket_impact['ID']) == str(key):
                return ticket_impact
            if str(key).lower() in ticket_impact['Name'].lower():
                return ticket_impact
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(f'No impact found for {key}')

    def get_all_ticket_sources(self) -> list:
        """
        Gets a list of all ticket sources from TDX

        :return: list of sources in python dict

        :rtype: list

        """
        url_string = "sources"
        return self.make_call(url_string, 'get')

    def get_ticket_source_by_name_id(self, key: Union[str, int]) -> dict:
        """
        Gets ticket source based on ID or Name

        :param key: Name or ID of source to search for.

        Supports search for exact name ('1. Phone'), or part of name ('Phone').

        :return: source data in python dict

        :rtype: dict

        """
        if not self.cache['ticket_source']:
            self.cache['ticket_source'] = self.get_all_ticket_sources()
        for ticket_source in self.cache['ticket_source']:
            if str(key) == str(ticket_source['ID']):
                return ticket_source
            if str(key).lower() in ticket_source['Name'].lower():
                return ticket_source
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError(f'No source found for {key}')

    # #### CREATING/EDITING CUSTOM TICKET STATUSES #### #

    def create_custom_ticket_status(self, name: str, order: float, status_class: str, description: str = None,
                                    active: bool = True) -> dict:
        """
        Creates a custom ticket status.

        :param name:            A string containing the name of the new status. (Required)
        :param order:           A float containing the order number for sorting purposes.
        :param status_class:    A name of a status class. These values are hard-coded into the TDWebApi, and stored in
                                this class as a class variable.
        :param description:     A string containing the description of the new status. (Default: Empty String)
        :param active:          A bool indicating whether this new status should be active. (Default: True)

        :return:                The new ticket status as a dict

        :rtype: dict

        """
        url_string = "statuses"
        status = dict({'Name': name, 'Order': order, 'IsActive': active})
        if status_class in self.ticket_status_classes:
            status['StatusClass'] = self.ticket_status_classes[status_class]
        else:
            raise tdxlib.tdx_api_exceptions.TdxApiObjectTypeError(f"No status class found for {status_class}")
        if description:
            status['Description'] = description
        return self.make_call(url_string, "post", status)

    def edit_custom_ticket_status(self, name: str, changed_attributes: dict) -> dict:
        """
        Edits a custom ticket status

        :param name: The name of the status (for finding the object to edit)
        :param changed_attributes: A dict containing values to substitute for the status's current values.

        :return: The edited status information

        :rtype: dict

        """
        status = self.search_ticket_status(name)
        url_string = f"statuses/{status['ID']}"
        status.update(changed_attributes)
        return self.make_call(url_string, 'put', status)

    # #### TICKET TASKS #### #

    def get_all_tasks_by_ticket_id(self, ticket_id: Union[str, int], is_eligible_predecessor: bool = None) -> list:
        """
        Gets a list of tasks currently on an open ticket. If the ticket is closed, no tasks will be returned.

        :param ticket_id: The ticket ID to retrieve ticket tasks for.

        :param is_eligible_predecessor: (optional) If true, will only retrieve tasks that can be assigned as a
                                        predecessor for other tasks.

        :return: list of ticket tasks as dicts

        :rtype: list

        """
        url_string = f'{ticket_id}/tasks?isEligiblePredecessor={is_eligible_predecessor}'
        return self.make_call(url_string, 'get')

    def get_ticket_task_by_id(self, ticket_id: Union[str, int], task_id: Union[str, int]) -> dict:
        """
        Gets ticket task by ID.

        :param ticket_id: The ticket ID on which the ticket task exists.
        :param task_id: The ticket task ID.

        :return: Task data in dict

        :rtype: dict

        """
        url_string = f'{ticket_id}/tasks/{task_id}'
        return self.make_call(url_string, 'get')

    def get_ticket_task_feed(self, ticket_id: Union[str, int], task_id: Union[str, int]) -> list:
        """
        Gets all the feed entries from a ticket task.

        :param ticket_id: The ticket ID on which the ticket task exists.
        :param task_id: The ticket task ID.

        :return: list of feed entries from the task, if any exist

        :rtype: list

        """
        url_string = f'{ticket_id}/tasks/{task_id}/feed'
        return self.make_call(url_string, 'get')

    def create_ticket_task(self, ticket_id: Union[str, int], task: dict) -> dict:
        """
        Adds a ticket task to a ticket.

        :param ticket_id: The ticket ID on which to create the ticket task.
        :param task: dict of task to create, possibly generated from generate_ticket_task

        :return: dict of created ticket task information

        :rtype: dict

        """
        self.validate_ticket_task(task, True)
        url_string = f'{ticket_id}/tasks'
        return self.make_call(url_string, 'post', task)

    @staticmethod
    def validate_ticket_task(task: dict, required=False):
        editable_task_attributes = [
            'Title', 'Description', 'StartDate', 'EndDate', 'CompleteWithinMinutes', 'EstimatedMinutes',
            'ResponsibleUid', 'ResponsibleGroupID', 'PredecessorID'
        ]
        if required:
            if 'Title' not in task:
                raise tdxlib.tdx_api_exceptions.TdxApiTicketValidationError(
                    "Title not found in ticket task creation argument. Title is required for ticket task creation."
                )
        for k in task.keys():
            if k not in editable_task_attributes:
                raise tdxlib.tdx_api_exceptions.TdxApiTicketValidationError(
                    f"Attribute {k} not a writeable ticket task attribute"
                )

    def edit_ticket_task(self, ticket_id: int, task: Union[str, int, dict], changed_attributes: dict) -> dict:
        """
        Edits a ticket task with a set of new values.

        :param ticket_id: The ticket ID on which the ticket task exists.
        :param task: a single ticket task in dict (maybe from get_ticket_task_by_id), or a task ID
        :param changed_attributes: The new values ot set on the ticket task.

        :return: The modified ticket task as a dict, if the operation was successful

        :rtype: dict

        """
        self.validate_ticket_task(changed_attributes)
        if isinstance(task, str) or isinstance(task, int):
            full_task = self.get_ticket_task_by_id(ticket_id, task)
        else:
            if not isinstance(task, dict) or 'ID' not in task or not task['ID']:
                raise tdxlib.tdx_api_exceptions.TdxApiObjectTypeError(
                    "The task provided does not contain \'ID\' attribute.")
            else:
                full_task = task
        full_task.update(changed_attributes)
        url_string = f'{ticket_id}/tasks/{full_task["ID"]}'
        return self.make_call(url_string, 'put', full_task)

    def delete_ticket_task(self, ticket_id: str, task_id: str) -> None:
        """
        Deletes a ticket task by ID

        :param ticket_id: The ticket ID on which the ticket task exists.
        :param task_id: The task ID of the task you want to delete.

        :return: none

        """
        url_string = f'{ticket_id}/tasks/{task_id}'
        self.make_call(url_string, 'delete')

    def reassign_ticket_task(self, ticket_id: int, task: Union[str, dict, int], responsible: str, group=False) -> dict:
        """
        Reassigns a ticket task to a person or group

        :param ticket_id: The ticket ID on which the ticket task exists.
        :param task: a single ticket task in dict (maybe from get_ticket_task_by_id), or a task ID
        :param responsible: a username, email, Full Name, or ID number to use to search for a person, or a group name.
        :param group: If this parameter is True, assign to group instead of individual

        :return: The modified ticket task as a dict, if the operation was successful

        :rtype: dict

        """
        if group:
            reassign = {'GroupID': self.get_group_by_name(responsible)['ID']}
        else:
            reassign = {'ResponsibleUid': self.get_person_by_name_email(responsible)}
        return self.edit_ticket_task(ticket_id, task, reassign)

    def reschedule_ticket_task(self, ticket_id, task,
                               start_date: datetime.datetime = None,
                               end_date: datetime.datetime = None) -> dict:
        """
        Sets the start date and end date for a ticket task. This will affect the start & end dates of the parent ticket.

        :param ticket_id: The ticket ID on which the ticket task exists.
        :param task: a single ticket task in dict (maybe from get_ticket_task_by_id), or a task ID
        :param start_date: datetime.datetime object to use as the starting date for a task, defaults to now.
        :param end_date: datetime.datetime object to use as the starting date for a task, defaults to now + 1 day.

        :return: The modified ticket task as a dict, if the operation was successful

        :rtype: dict

        """
        if not start_date:
            start_date = datetime.datetime.utcnow()
        if not end_date:
            end_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        new_dates = {
            'StartDate': tdxlib.tdx_utils.export_tdx_date(start_date, self.config.timezone),
            'EndDate': tdxlib.tdx_utils.export_tdx_date(end_date, self.config.timezone)
        }
        return self.edit_ticket_task(ticket_id, task, new_dates)

    def update_ticket_task(self, ticket_id: int, task_id: int, percent: int, comments: str = '',
                           notify: list = None, private: bool = True) -> dict:
        """
        Sends an update to a ticket task.

        :param ticket_id: the ticket ID whose task to update
        :param task_id: the ID of the task to update
        :param percent: the percent complete to set the task to after update
        :param comments: a string to provide as a comment to the update. Defaults to empty string.
        :param notify: a list of strings containing email addresses to notify regarding this ticket. Default: None
        :param private: boolean indicating whether the update to the task should be private. Default: True

        :return: dict of update info

        :rtype: dict

        """
        if not notify:
            notify = []
        url_string = f'{ticket_id}/tasks/{task_id}/feed'
        data = {
            'PercentComplete': percent - (percent % 10),
            'Comments': comments,
            'Notify': notify,
            'IsPrivate': str(private)
            }
        return self.make_call(url_string, 'post', data)

    def get_all_ticket_assets(self, ticket_id: int) -> list:
        """
        Gets all asset attached to a ticket.

        :param ticket_id: The Ticket ID to update

        :return: list of asset info

        :rtype: list

        """
        url_string = f'{ticket_id}/assets'
        return self.make_call(url_string, 'get')

    def add_asset_to_ticket(self, ticket_id: int, asset_id: int) -> dict:
        """
        Attaches an asset to a ticket.

        :param ticket_id: The Ticket ID to update
        :param asset_id: The ID of the Asset to associate with the Ticket

        :return: dict of update info

        :rtype: dict

        """
        url_string = f'{ticket_id}/assets/{asset_id}'
        # this does nothing, but it can't be blank
        data = {'AssetID': asset_id}
        return self.make_call(url_string, 'post', data)

    # #### TEMPLATING TICKETS #### #

    @classmethod
    def get_ticket_classification_id_by_name(cls, name: str):
        """
        Gets ticket classification data by searching by the name of the classification.

        :param name: the name of the classification to search for

        :return: dict of ticket classification info

        :rtype: dict

        """
        if name in TDXTicketIntegration.ticket_classifications:
            return TDXTicketIntegration.ticket_classifications[name]
        raise tdxlib.tdx_api_exceptions.TdxApiObjectNotFoundError("No classification found for name " + name)

    def generate_ticket(self, title_template: str, ticket_type: str, account: str, responsible: str,
                        template_values: dict = None, body_template: str = None, attrib_prefix: str = None,
                        due_date: Union[datetime.datetime, str] = None, location: str = None, room: str = None,
                        active_days: int = 5, priority: str = "Low", status: str = "New", requestor: str = None,
                        classification: str = "Incident", form: str = None, responsible_is_group: str = False,
                        custom_attributes: dict = None) -> tdxlib.tdx_ticket.TDXTicket:
        """
        Makes a TdxTicket object based on templates.

        :param title_template: a string with {placeholders} that correspond to keys in template_values dict (REQUIRED)
        :param ticket_type: name of ticket Type (REQUIRED)
        :param account: name of requesting Account for Ticket (REQUIRED)
        :param responsible: group or email address to set as responsible for ticket (REQUIRED)
        :param template_values: a dictionary with substitutions for title/body, using the {placeholders} as keys
        :param body_template: a string with {placeholders} that correspond to keys in template_values parameter
        :param attrib_prefix: [DEPRECATED]
                            the string that prefixes all the custom attribute column names in the template_values dict
        :param due_date: due date for ticket, default None
        :param location: Building name of location (optional)
        :param room: Room name of location (optional) Will not set room if location not included.
        :param active_days: number of days before due date to assign start date, default is 5
        :param priority: name of priority of ticket, default "Low"
        :param status: name of status for new ticket, default "New"
        :param requestor: name or email for requester of the ticket, defaults to username of integration (optional)
        :param classification: name of classification name for new ticket, default "Incident" (optional)
        :param form: name or ID of a form to use for the new ticket
        :param responsible_is_group: Boolean indicating whether 'responsible' refers to a group. (Default: False)
        :param custom_attributes: dict of attribute names and values

        :return: TdxTicket object ready to be created via create_ticket()

        :rtype: tdxlib.tdx_ticket.TDXTicket

        """
        # Required by TDX for a new ticket: Type, Title, Account, Status, Priority, Requestor

        # set defaults
        if not requestor:
            requestor = self.config.username

        # Required or defaulted parameters
        data = dict()
        data['TypeID'] = self.get_ticket_type_by_name_id(ticket_type)['ID']
        data['Classification'] = self.get_ticket_classification_id_by_name(classification)
        data['AccountID'] = self.get_account_by_name(account)['ID']
        data['StatusID'] = self.search_ticket_status(status)['ID']
        data['PriorityID'] = self.get_ticket_priority_by_name_id(priority)['ID']
        data['RequestorUid'] = self.get_person_by_name_email(requestor)['UID']
        if form:
            data['FormID'] = self.get_ticket_form_by_name_id(form)['ID']
        else:
            data['FormID'] = 0

        # map per-ticket values into title and body
        body = 'Auto-generated Ticket'
        if template_values:
            title = title_template.format_map(template_values)
            if body_template:
                body = body_template.format_map(template_values)
        else:
            title = title_template
        data['Title'] = title
        data['Description'] = body

        # set up attribute values
        if attrib_prefix:
            self.logger.warning(f"Deprecated parameter in generate_ticket(): \"attrib_prefix\". In future versions,"
                                f" use \"custom_attributes\"")
            if 'Attributes' not in data.keys() or not data['Attributes']:
                data['Attributes'] = []
            for key, value in template_values.items():
                if attrib_prefix in key:
                    data['Attributes'].append(
                        self.build_ticket_custom_attribute_value(key.replace(attrib_prefix, ""), value))

        if custom_attributes:
            if 'Attributes' not in data.keys() or not data['Attributes']:
                data['Attributes'] = []
            for key, value in custom_attributes.items():
                data['Attributes'].append(self.build_ticket_custom_attribute_value(key, value))

        if due_date:
            if isinstance(due_date, datetime.datetime):
                target_date = due_date
            else:
                target_date = tdxlib.tdx_utils.import_tdx_date(due_date)
            start_date = target_date - datetime.timedelta(days=active_days)
            data['StartDate'] = tdxlib.tdx_utils.export_tdx_date(start_date, self.config.timezone)
            data['EndDate'] = tdxlib.tdx_utils.export_tdx_date(target_date, self.config.timezone)

        if location:
            building = self.get_location_by_name(location)
            data['LocationID'] = building['ID']
            if room:
                data['LocationRoomID'] = self.get_room_by_name(building, room)['ID']

        if responsible_is_group:
            data['ResponsibleGroupID'] = self.get_group_by_name(responsible)['ID']
        else:
            data['ResponsibleUid'] = self.get_person_by_name_email(responsible)['UID']

        new_ticket = tdxlib.tdx_ticket.TDXTicket(self, data)
        new_ticket.validate()
        return new_ticket

    def generate_ticket_task(self, title: str, est_minutes: int = 30, description: str = None,
                             start: datetime.datetime = None, end: datetime.datetime = None,
                             completion_minutes: int = None, responsible: str = None, group: bool = False,
                             predecessor: int = None) -> dict:
        """
        Generates a dict with the information in the proper format for creating at ticket task.

        :param title: A string indicating the title of the ticket (Required)
        :param est_minutes: Estimation of minutes required to complete this task (Default: 30)
                            This is used for comparison to actual hours when using time tracking
        :param description: A string containing a description of the task (Default: Empty String)
        :param start:       Datetime object indicating the start date of the ticket task (Default: date of creation)
        :param end:         Datetime object indicating the end date of the ticket task. Sets the due date/time.
                            (Default: one hour after start)
        :param completion_minutes:  This parameter is used for tasks with predecessors.  (Default: 0)
                                    They set the due date/time based on the activation date and time.
        :param responsible: String containing the name or partial name of a group or individual to assign the task to.
                            (Default: None)
        :param group:       Boolean indicating whether the responsible parameter references a group (Default:false)
        :param predecessor: Task ID of another task in the destination ticket to set as the predecessor. (Default: None)

        :return: Dict of task information fit for creating a task on a ticket using create_task()

        """
        data = dict({'Title': title})
        data['EstimatedMinutes'] = est_minutes
        if description:
            data['Description'] = description
        if start and end:
            data['StartDate'] = tdxlib.tdx_utils.export_tdx_date(start, self.config.timezone)
            data['EndDate'] = tdxlib.tdx_utils.export_tdx_date(end, self.config.timezone)
        if completion_minutes:
            data['CompleteWithinMinutes'] = completion_minutes
        if group:
            data['ResponsibleGroupID'] = self.get_group_by_name(responsible)['ID']
        else:
            data['ResponsibleUid'] = self.get_person_by_name_email(responsible)['UID']
        if predecessor:
            data['PredecessorID'] = predecessor
        return data

    # #### CREATING TICKETS #### #

    def create_ticket(self, ticket: tdxlib.tdx_ticket.TDXTicket, silent: bool = True) -> tdxlib.tdx_ticket.TDXTicket:
        """
        Creates a ticket in TeamDynamix using a TdxTicket object

        :param ticket: TDXTicket Object
        :param silent: Boolean -- if False, notifications are sent to requestor and responsible, default: True

        :returns: Created ticket, if successful

        :rtype: tdxlib.tdx_ticket.TDXTicket

        """
        if silent:
            request_params = "?EnableNotifyReviewer=False&NotifyRequestor=False&" \
                             "NotifyResponsible=False&AllowRequestorCreation=False"
        else:
            request_params = "?EnableNotifyReviewer=False&NotifyRequestor=True&" \
                             "NotifyResponsible=True&AllowRequestorCreation=False"
        created_ticket_data = self.make_call(request_params, 'post', ticket.export(validate=True))
        return tdxlib.tdx_ticket.TDXTicket(self, created_ticket_data)

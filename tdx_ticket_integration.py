import tdx_ticket
from dateutil.parser import parse
import datetime
import tdx_integration
import tdx_api_exceptions


class TDXTicketIntegration(tdx_integration.TDXIntegration):
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

    def __init__(self, filename=None):
        tdx_integration.TDXIntegration.__init__(self, filename)
        if self.ticket_app_id is None:
            raise ValueError("Ticket App Id is required. Check your config file for 'ticketappid = 000'")
        self.cache['ticket_type'] = {}
        self.cache['ticket_status'] = {}
        self.cache['ticket_priority'] = {}
        self.cache['ticket_urgency'] = {}
        self.cache['ticket_impact'] = {}
        self.cache['ticket_source'] = {}

    def clean_cache(self):
        super().clean_cache()
        self.cache['ticket_type'] = {}
        self.cache['ticket_status'] = {}
        self.cache['ticket_priority'] = {}
        self.cache['ticket_urgency'] = {}
        self.cache['ticket_impact'] = {}
        self.cache['ticket_source'] = {}

    def make_ticket_call(self, url, action, post_body=None):
        url_string = '/' + str(self.ticket_app_id) + '/tickets'
        if len(url) > 0:
            url_string += '/' + url
        if action == 'get':
            return self.make_get(url_string)
        if action == 'post' and post_body:
            return self.make_post(url_string, post_body)
        if action == 'put' and post_body:
            return self.make_put(url_string, post_body)
        # TODO: need to expand this when we add patch/put/delete
        raise tdx_api_exceptions.TdxApiHTTPRequestError('No method' + action + 'or no post information')

    def make_call(self, url, action, post_body=None):
        return self.make_ticket_call(url, action, post_body)

    def get_all_ticket_custom_attributes(self):
        return self.get_all_custom_attributes(TDXTicketIntegration.component_ids['ticket'], app_id=self.ticket_app_id)

    def get_ticket_custom_attribute_by_name(self, key):
        return self.get_custom_attribute_by_name(key, TDXTicketIntegration.component_ids['ticket'])

    # #### GETTING TICKETS #### #

    def get_ticket_by_id(self, ticket_id) -> tdx_ticket.TdxTicket:
        """
        Gets a ticket, based on its ID 
        :param ticket_id: ticket ID of required ticket
        :return: json format of ticket info
        """
        return tdx_ticket.TdxTicket(self, self.make_call(str(ticket_id), 'get'))

    def search_tickets(self, criteria, max_results=25, closed=False, cancelled=False, other_status=False) -> list:
        """
        Gets a ticket, based on criteria
        :param max_results: maximum number of results to return
        :param criteria: a string, list or dict to search for tickets with
                Common criteria:
                    {
                        'TicketClassification': [List of Int],
                        'SearchText': [String],
                        'Status IDs': [List of Int],
                        'ResponsibilityUids': [List of String (GUID)],
                        'ResponsibilityGroupIDs': [List of String (ID)],
                        'RequestorEmailSearch': [String],
                        'LocationIDs': [List of Int],
                        'LocationRoomIds': [List of Int],
                        'CreatedDateFrom': [DateTime],
                        'CreatedDateTo': [DateTime],
                        'SlaViolationStatus': [Boolean -- true = SLA Violated]
                    }
                    (https://api.teamdynamix.com/TDWebApi/Home/type/TeamDynamix.Api.Tickets.TicketSearch)
        :param cancelled: include cancelled tickets in search if true
        :param closed: include closed tickets in search if true
        :param other_status: Status ID of a custom status
        :return: list of TDXTicket objects
        """
        # Set default statuses
        statuses = list()
        statuses.append(self.get_ticket_status_by_name("New")['ID'])
        statuses.append(self.get_ticket_status_by_name("Open")['ID'])
        statuses.append(self.get_ticket_status_by_name("On Hold")['ID'])

        # Set conditional statuses
        if closed:
            statuses.append(self.get_ticket_status_by_name("Closed")['ID'])
        if cancelled:
            statuses.append(self.get_ticket_status_by_name("Cancelled")['ID'])
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
            ticket_list.append(tdx_ticket.TdxTicket(self, ticket_data))
        return ticket_list

    # #### CHANGING TICKETS #### #

    def edit_tickets(self, ticket_list, changed_attributes, notify=False) -> list:
        """
        Edits one or more tickets, based on:
        :param ticket_list: list of TDXTicket objects, maybe from search_tickets, or a single ticket
        :param changed_attributes: Attributes to alter in selected tickets
        :param notify: If true, will notify newly-responsible resource(s) if changed because of edit
        :return: list of edited tickets, with complete data in json format
        """
        url_string = '{ID}?notifyNewResponsible=' + str(notify)
        edited_tickets = list()
        if isinstance(ticket_list, list) and all(isinstance(elem, tdx_ticket.TdxTicket) for elem in ticket_list):
            for ticket in ticket_list:
                ticket.update(changed_attributes, validate=True)
                post_body = ticket.export(validate=True)
                edited_tickets.append(self.make_call(url_string.format_map(
                    {'ID': str(ticket.get_id())}), 'post', post_body))
        elif isinstance(ticket_list, tdx_ticket.TdxTicket):
            ticket_list.update(changed_attributes, validate=True)
            post_body = ticket_list.export(validate=True)
            edited_tickets.append(self.make_call(url_string.format_map(
                {'ID': str(ticket_list.get_id())}), 'post', post_body))
        else:
            raise tdx_api_exceptions.TdxApiObjectTypeError(
                'edit_tickets() method accepts only TDXTicket objects (or lists of same)\n' +
                'Object found: ' + str(type(ticket_list)))
        
        return edited_tickets

    def edit_ticket_type(self, ticket_list, key) -> list:
        """
        Updates type of ticket, based on:
        :param ticket_list: list of TDXTicket objects, maybe from search_tickets, or a single ticket
        :param key: Desired type. Supports update by ID (int) or Name (str).
        """

        ticket_type = self.get_ticket_type_by_name_id(key)
        changed_attributes = {
            "TypeID": ticket_type['ID']
        }
        return self.edit_tickets(ticket_list, changed_attributes)

    def edit_ticket_status(self, ticket_list, key) -> list:
        """
        Updates status of ticket, based on:
        :param ticket_list: list of TDXTicket objects, maybe from search_tickets, or a single ticket
        :param key: Desired status. Supports search for ID (int) or Name (str).
        """

        if type(key) is int:
            status = self.get_ticket_status_by_id(key)
        else:
            status = self.get_ticket_status_by_name(key)
            
        changed_attributes = {
            "StatusID": status['ID']
        }
        return self.edit_tickets(ticket_list, changed_attributes)

    def edit_ticket_priority(self, ticket_list, key) -> list:
        """
        Updates priority of ticket, based on:
        :param ticket_list: list of TDXTicket objects, maybe from search_tickets, or a single ticket
        :param key: Desired priority. Supports update by ID (int) or Name (str).
        """

        priority = self.get_ticket_priority_by_name_id(key)
        changed_attributes = {
            "PriorityID": priority['ID']
        }
        return self.edit_tickets(ticket_list, changed_attributes)

    def edit_ticket_urgency(self, ticket_list, key) -> list:
        """
        Updates urgency of ticket, based on:
        :param ticket_list: list of TDXTicket objects, maybe from search_tickets, or a single ticket
        :param key: Desired urgency. Supports update by ID (int) or Name (str).
        """

        urgency = self.get_ticket_urgency_by_name_id(key)
        changed_attributes = {
            'UrgencyID': urgency['ID']
        }
        return self.edit_tickets(ticket_list, changed_attributes)

    def edit_ticket_impact(self, ticket_list, key) -> list:
        """
        Updates impact of ticket, based on:
        :param ticket_list: list of TDXTicket objects, maybe from search_tickets, or a single ticket
        :param key: Desired urgency. Supports update by ID (int) or Name (str).
        """

        impact = self.get_ticket_impact_by_name_id(key)
        changed_attributes = {
            'ImpactID': impact['ID']
        }
        return self.edit_tickets(ticket_list, changed_attributes)

    def edit_ticket_source(self, ticket_list, key) -> list:
        """
        Updates source of ticket, based on:
        :param ticket_list: list of TDXTicket objects, maybe from search_tickets, or a single ticket
        :param key: Desired source. Supports update by ID (int) or Name (str).
        """

        source = self.get_ticket_source_by_name_id(key)
        changed_attributes = {
            'SourceID': source['ID']
        }
        return self.edit_tickets(ticket_list, changed_attributes)     

    # TODO: edit ticket service
    # This might involve some work WRT services.
    # If interacting with services is pretty simple, add it to tdx_integration

    # TODO: edit ticket responsible (reassign ticket?) -- for User or Group

    # TODO: edit ticket dates (reschedule ticket?)

    # TODO: edit ticket location (relocate ticket?)

    #

    # #### GETTING TICKET ATTRIBUTES #### #

    def get_all_ticket_types(self):
        """
        Gets a list of all ticket types from TDX
        :return: list of type data
        """
        url_string = "types"
        return self.make_call(url_string, 'get')

    def get_ticket_type_by_name_id(self, key):
        """
        Gets ticket type based on ID or Name
        :param key: Name or ID of attribute to search for
        :return: type data in dict
        """
        if not self.cache['ticket_type']:
            self.cache['ticket_type'] = self.get_all_ticket_types()
        for ticket_type in self.cache['ticket_type']:
            if ticket_type['ID'] == key:
                return ticket_type
            if ticket_type['Name'] == key:
                return ticket_type
        raise tdx_api_exceptions.TdxApiObjectNotFoundError(
                f'No type found with ID or Name {key}')

    def get_all_ticket_statuses(self):
        """
        Gets a list of all ticket statuses from TDX
        :return: list of status data in dict
        """
        url_string = "statuses"
        return self.make_call(url_string, 'get')

    def get_ticket_status_by_id(self, key):
        """
        Gets ticket status based on ID or Name
        :param key: ID of ticket status to search for
        :return: status data in dict
        """
        if key not in self.cache['ticket_status']:
            url_string = f'statuses/{key}'
            self.cache['ticket_status'][key] = self.make_call(url_string, 'get')
        return self.cache['ticket_status'][key]

    def get_ticket_status_by_name(self, key):
        """
        Gets ticket status based on name
        :param key: Name of ticket status to search for
        :return: status data in dict
        """
        if key in self.cache['ticket_status']:
            return self.cache['ticket_status'][key]
        else:
            # Search statuses using API search functionality
            post_body = {
                'SearchText': key
            }
            url_string = 'statuses/search'
            data = self.make_call(url_string, 'post', post_body)
            if data:
                # Add result to cache under searched key
                self.cache['ticket_status'][key] = data[0]
                if key != data[0]['Name']:
                    # Add result to cache under ['Name'] property
                    self.cache['ticket_status'][data[0]['Name']] = data[0]
                return data[0]
        raise tdx_api_exceptions.TdxApiObjectNotFoundError(f"No status found for {key}")

    def get_all_ticket_priorities(self):
        """
        Gets a list of all ticket priorities from TDX
        :return: list of priorities in dict
        """
        url_string = "priorities"
        return self.make_call(url_string, 'get')

    def get_ticket_priority_by_name_id(self, key):
        """
        Gets ticket priority based on ID or Name
        :param key: ID or Name of priority to search for
        :return: priority data in dict
        """
        if not self.cache['ticket_priority']:
            self.cache['ticket_priority'] = self.get_all_ticket_priorities()
        for ticket_priority in self.cache['ticket_priority']:
            if ticket_priority['ID'] == key:
                return ticket_priority
            if ticket_priority['Name'] == key:
                return ticket_priority
        raise tdx_api_exceptions.TdxApiObjectNotFoundError(f'No priority found for {key}')

    def get_all_ticket_urgencies(self):
        """
        Gets all urgencies from the tickets app
        :return: list of priorities in dict
        """
        url_string = "urgencies"
        return self.make_call(url_string, 'get')

    def get_ticket_urgency_by_name_id(self, key):
        """
        Gets ticket urgency based on ID or Name
        :param key: ID or Name of urgency to search for
        :return: urgency data in dict
        """
        if not self.cache['ticket_urgency']:
            self.cache['ticket_urgency'] = self.get_all_ticket_urgencies()
        for ticket_urgency in self.cache['ticket_urgency']:
            if ticket_urgency['ID'] == key:
                return ticket_urgency
            if ticket_urgency['Name'] == key:
                return ticket_urgency
        raise tdx_api_exceptions.TdxApiObjectNotFoundError(f'No urgency found for {key}')
    
    def get_all_ticket_impacts(self):
        """
        Gets a list of all ticket impacts from TDX
        :return: list of impacts in dict
        """
        url_string = "impacts"
        return self.make_call(url_string, 'get')

    def get_ticket_impact_by_name_id(self, key):
        """
        Gets ticket impact based on ID or Name
        :param key: Name or ID of impact to search for
        :return: impact data in dict
        """
        if not self.cache['ticket_impact']:
            self.cache['ticket_impact'] = self.get_all_ticket_impacts()
        for ticket_impact in self.cache['ticket_impact']:
            if ticket_impact['ID'] == key:
                return ticket_impact
            if ticket_impact['Name'] == key:
                return ticket_impact
        raise tdx_api_exceptions.TdxApiObjectNotFoundError(f'No impact found for {key}')

    def get_all_ticket_sources(self):
        """
        Gets a list of all ticket sources from TDX
        :return: list of sources in dict
        """
        url_string = "sources"
        return self.make_call(url_string, 'get')

    def get_ticket_source_by_name_id(self, key):
        """
        Gets ticket source based on ID or Name
        :param key: Name or ID of source to search for. 
        Supports search for exact name ('1. Phone'), or part of name ('Phone').
        :return: source data in dict
        """
        if not self.cache['ticket_source']:
            self.cache['ticket_source'] = self.get_all_ticket_sources()
        for ticket_source in self.cache['ticket_source']:
            if key == ticket_source['ID']:
                return ticket_source
            if key in ticket_source['Name']:
                return ticket_source
        raise tdx_api_exceptions.TdxApiObjectNotFoundError(f'No source found for {key}')

    # #### CREATING/EDITING CUSTOM TICKET STATUSES #### #

    # TODO: create_custom_status(self, name, description, order, status_class, active)
    #   https://api.teamdynamix.com/TDWebApi/Home/type/TeamDynamix.Api.Tickets.TicketStatus
    #   https://api.teamdynamix.com/TDWebApi/Home/section/TicketStatuses
    #   Might need to add a class variable to store the int values of the various status classes.
    #   I don't think you can get them from the API.

    # TODO: edit_custom_status(self, name/id, changed_attributes)'
    #   Need to implement HTTP PUT call for this one. Do this in tdx_integration if possible.
    #   Don't need to write any additional methods to abstract this further -- just assume the user will
    #   be able to craft their own dictionaries to edit statuses
    #   Also, make sure to clear the local status cache if you edit a status.

    # #### TICKET TASKS #### #

    # TODO: Unittest all ticket task methods

    def get_all_tasks_by_ticket_id(self, ticket_id, is_eligible_predecessor=None) -> list:
        """
        Gets a list of tasks currently on an open ticket.
        :param ticket_id: The ticket ID to retrieve ticket tasks for.
        :param is_eligible_predecessor: (optional) If true, will only retrieve tasks that can be assigned as a predecessor for other tasks.
        Note: If the ticket is closed, no tasks will be returned.
        """
        url_string = f'{ticket_id}/tasks?isEligiblePredecessor={is_eligible_predecessor}'
        return self.make_call(url_string, 'get')

    def get_ticket_task_by_id(self, ticket_id, task_id):
        """
        Gets ticket task by ID.
        :param ticket_id: The ticket ID on which the ticket task exists.
        :param task_id: The ticket task ID.
        :return: Task data in dict
        :rtype: dict
        """
        url_string = f'{ticket_id}/tasks/{task_id}'
        return self.make_call(url_string, 'get')

    def create_ticket_task(self, ticket_id, task):
        """
        Adds a ticket task to a ticket.
        :param ticket_id: The ticket ID on which to create the ticket task.
        :param task: dict of task to create, possibly generated from generate_ticket_task
        """
        url_string = f'{ticket_id}/tasks'
        return self.make_call(url_string, 'post', task)

    def edit_ticket_task(self, ticket_id, task_list, changed_attributes):
        """
        Updates ticket task(s) with a set of new values.
        :param ticket_id: The ticket Id on which the ticket task exists.
        :param task_list: list of tasks, maybe from get_all_ticket_tasks,
            or a single ticket task in dict (must include task ID).
        :param changed_attributes: The new values ot set on the ticket task.
        :return: The modified ticket task(s), if the operation was sucessful
        :rtype: dict or list of dict
        """
        if type(task_list) is list:
            edited_tasks = list()
            for task in task_list:
                if task['ID']:
                    task.update(changed_attributes)
                    url_string = f'{ticket_id}/tasks/{task["ID"]}'
                    edited_tasks.append(self.make_call(url_string, 'put', task))
                else:
                    raise tdx_api_exceptions.TdxApiObjectTypeError(
                        "One or more tasks provided does not contain \'ID\'.")
            return edited_tasks
        elif type(task_list) is dict:
            if task_list['ID']:
                task_list.update(changed_attributes)
                url_string = f'{ticket_id}/tasks/{task_list["ID"]}'
                return self.make_call(url_string, 'put', task_list)
            else:
                raise tdx_api_exceptions.TdxApiObjectTypeError(
                    "The task provided does not contain \'ID\'.")
        else:
            raise tdx_api_exceptions.TdxApiObjectTypeError(
                "task_list must be dict or list of dict.")

    # def delete_ticket_task(self, ticket_id, task_id) {

    # }

    # TODO: delete_ticket_task(self, ticket_id, task_id)
    #   Need to implement HTTP DELETE call for this one. Do this in tdx_integration if possible.

    # TODO: change_ticket_task_responsible(self, ticket_id, task_id, responsible)
    #   This should probably call 'edit_ticket_task()'

    # TODO: set_ticket_task_dates(self, ticket_id, task_id, <something datey>)
    #   This should probably call 'edit_ticket_task()'

    # #### TEMPLATING TICKETS #### #

    @classmethod
    def get_ticket_classification_id_by_name(cls, name):
        """
        Gets ticket classification data by searching by the name of the classification
        :param name: the name of the classification to search for
        :return:
        """
        if name in TDXTicketIntegration.ticket_classifications:
            return TDXTicketIntegration.ticket_classifications[name]
        raise tdx_api_exceptions.TdxApiObjectNotFoundError("No classification found for name " + name)

    def generate_ticket(self, title_template, ticket_type, account, responsible, ticket_values=None,
                        body_template=None, attrib_prefix=None, due_date=None, location=None, room=None,
                        active_days=5, priority="Low", status="New", requestor=None,
                        classification="Incident", form_id=0) -> tdx_ticket.TdxTicket:
        """
        Makes a TdxTicket object based on complex information
        :param title_template: a string with {placeholders} that correspond to keys in ticket parameter (REQUIRED)
        :param ticket_type: ticket Type (REQUIRED)
        :param account: Requesting Account for Ticket (REQUIRED)
        :param responsible: Group/email responsible for ticket (REQUIRED)
        :param ticket_values: a dictionary (potentially loaded from google sheet) with substitutions for title/body
        :param body_template: a string with {placeholders} that correspond to keys in ticket parameter
        :param attrib_prefix: the string that prefixes all the custom attribute column names in the ticket dict
        :param due_date: Due Date for ticket, default None (may be included with ticket) (
        :param location: Building name of location (optional)
        :param room: Room name of location (optional)
        :param active_days: number of days before due date to assign start date, default 5
        :param priority: Priority of ticket, default "Low"
        :param status: Status for new ticket, default "New"
        :param requestor: Requester for the ticket, defaults to username of integration (optional)
        :param classification: Classification name for ticket, default "Incident" (optional)
        :param form_id: ID of a form that you'd like to assign to this ticket (Form ID's not accessible via
                        API -- Must be looked up manually in TDAdmin)
        """
        # Required by TDX for a new ticket: Type, Title, Account, Status, Priority, Requestor

        # set defaults
        if not requestor:
            requestor = self.username

        # Required or defaulted parameters
        data = dict()
        data['TypeID'] = self.get_ticket_type_by_name_id(ticket_type)['ID']
        data['Classification'] = self.get_ticket_classification_id_by_name(classification)
        data['AccountID'] = self.get_account_by_name(account)['ID']
        data['StatusID'] = self.get_ticket_status_by_name(status)['ID']
        data['PriorityID'] = self.get_ticket_priority_by_name_id(priority)['ID']
        data['RequestorUid'] = self.search_people(requestor)['UID']
        data['FormID'] = form_id

        # map per-ticket values into title and body
        body = 'Auto-generated Ticket'
        if ticket_values:
            title = title_template.format_map(ticket_values)
            if body_template:
                body = body_template.format_map(ticket_values)
        else:
            title = title_template
        data['Title'] = title
        data['Description'] = body

        # set up attribute values
        if attrib_prefix:
            data['Attributes'] = []
            # attrib_count = 0
            for key, value in ticket_values.items():
                if attrib_prefix in key:
                    attrib_name = key.replace(attrib_prefix, "")
                    attrib = self.get_ticket_custom_attribute_by_name(attrib_name)
                    value = self.get_custom_attribute_value_by_name(attrib, value)
                    new_attrib = dict()
                    new_attrib['ID'] = attrib['ID']
                    new_attrib['Value'] = value['ID']
                    data['Attributes'].append(new_attrib)
        if due_date:
            # Set some date-related properties
            target_date = parse(due_date)
            # Due at 5PM EST (converting from UTC)
            target_date = target_date.replace(hour=21)
            # Create start date object
            start_date = target_date - datetime.timedelta(days=active_days)
            # Set start time to 8 a.m. (9 hours before 5 p.m.)
            start_date = start_date - datetime.timedelta(hours=9)
            # Convert dates to TDX-friendly strings
            data['StartDate'] = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            data['EndDate'] = target_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        if location:
            building = self.get_location_by_name(location)
            data['LocationID'] = building['ID']
            data['LocationRoomID'] = self.get_room_by_name(building, room)['ID']

        if responsible.find("@") == -1:
            data['ResponsibleGroupID'] = self.get_group_by_name(responsible)['ID']
        else:
            data['ResponsibleUid'] = self.search_people(responsible)['UID']

        new_ticket = tdx_ticket.TdxTicket(self, data)
        new_ticket.validate()
        return new_ticket

    # TODO: generate_ticket_task(self, <some sort of ticket info>)
    #   This could be similar to the one above. Obviously less complicated. Make sure it works with dates.

    # #### CREATING TICKETS #### #

    def create_ticket(self, ticket, silent=True) -> tdx_ticket.TdxTicket:
        """
        Creates a ticket using pre-generated data
        :param ticket: TDXTicket Object
        :param silent: Boolean -- if False, no notifications are sent to requestor and responsible, default: True
        :returns: Created ticket, if successful
        """
        if silent:
            request_params = "?EnableNotifyReviewer=False&NotifyRequestor=False&" \
                             "NotifyResponsible=False&AllowRequestorCreation=False"
        else:
            request_params = "?EnableNotifyReviewer=False&NotifyRequestor=True&" \
                             "NotifyResponsible=True&AllowRequestorCreation=False"
        created_ticket_data = self.make_call(request_params, 'post', ticket.export(validate=True))
        return tdx_ticket.TdxTicket(self, created_ticket_data)

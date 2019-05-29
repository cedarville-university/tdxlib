import tdx_api_exceptions
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import tdx_ticket_integration


class TdxTicket:
    valid_attributes = [
        'TypeID', 'AccountID', 'PriorityID', 'RequestorUid', 'Title', 'StatusID', 'Classification', 'Description',
        'FormID', 'Description', 'SourceID', 'ImpactID', 'UrgencyID', 'EstimatedMinutes', 'ResponsibleGroupID',
        'TimeBudget', 'ExpensesBudget', 'LocationID', 'LocationRoomID', 'ServiceID', 'Attributes', 'GoesOffHoldDate',
        'StartDate', 'EndDate', 'ResponsibleUid', 'ID', 'ParentID', 'ParentTitle', 'ParentClass', 'TypeName',
        'TypeCategoryID', 'TypeCategoryName', 'Classification', 'ClassificationName', 'FormName', 'Uri', 'AccountName',
        'SourceName', 'StatusName', 'StatusClass', 'ImpactName', 'UrgencyName', 'PriorityName', 'PriorityOrder',
        'SlaID', 'SlaName', 'IsSlaViolated', 'IsSlaRespondByViolated', 'IsSlaResolveByViolated', 'RespondByDate',
        'ResolveByDate', 'SlaBeginDate', 'IsOnHold', 'PlacedOnHoldDate', 'CreatedDate', 'CreatedUid',
        'CreatedFullName', 'CreatedEmail', 'ModifiedDate', 'ModifiedUid', 'ModifiedFullName', 'RequestorName',
        'RequestorFirstName', 'RequestorLastName', 'RequestorEmail', 'RequestorPhone', 'ActualMinutes', 'DaysOld',
        'ResponsibleFullName', 'ResponsibleEmail', 'ResponsibleGroupName', 'RespondedDate', 'RespondedUid',
        'RespondedFullName', 'CompletedDate', 'CompletedUid', 'CompletedFullName', 'ReviewerUid', 'ReviewerFullName',
        'ReviewerEmail', 'ReviewingGroupID', 'ReviewingGroupName', 'TimeBudgetUsed', 'ExpensesBudgetUsed',
        'IsConvertedToTask', 'ConvertedToTaskDate', 'ConvertedToTaskUid', 'ConvertedToTaskFullName', 'TaskProjectID',
        'TaskProjectName', 'TaskPlanID', 'TaskPlanName', 'TaskID', 'TaskTitle', 'TaskStartDate', 'TaskEndDate',
        'TaskPercentComplete', 'LocationName', 'LocationRoomName', 'RefCode', 'ServiceName', 'ServiceCategoryID',
        'ServiceCategoryName', 'ArticleID', 'ArticleSubject', 'ArticleStatus', 'ArticleCategoryPathNames', 'AppID',
        'Attachments', 'Tasks', 'Notify'
    ]
    valid_int_attributes = [
        'SourceID', 'ImpactID', 'UrgencyID', 'EstimatedMinutes', 'ResponsibleGroupID', 'LocationID', 'LocationRoomID',
        'ServiceID', 'TypeID', 'AccountID', 'PriorityID', 'ParentID', 'TypeCategoryID', 'SlaID', 'ActualMinutes',
        'DaysOld', 'ReviewingGroupID', 'TaskProjectID', 'TaskPlanID', 'TaskID', 'TaskPercentComplete',
        'ServiceCategoryID', 'ArticleID', 'AppID', 'ParentClass', 'Classification', 'StatusClass', 'ArticleStatus'
    ]
    valid_decimal_attributes = ['TimeBudget', 'ExpensesBudget', 'PriorityOrder', 'TimeBudgetUsed', 'ExpensesBudgetUsed']
    valid_bool_attributes = [
        'IsSlaViolated', 'IsSlaRespondByViolated', 'IsSlaResolveByViolated', 'IsOnHold', 'IsConvertedToTask'
    ]
    valid_date_attributes = [
        'GoesOffHoldDate', 'StartDate', 'EndDate', 'RespondByDate', 'ResolveByDate', 'SlaBeginDate', 'IsOnHold',
        'PlacedOnHoldDate', 'CreatedDate', 'ModifiedDate', 'CompletedDate', 'RespondedDate', 'ConvertedToTaskDate',
        'TaskStartDate', 'TaskEndDate'
    ]
    valid_list_attributes = ['Tasks', 'Attachments', 'Notify']
    valid_dict_attributes = ['Attributes']

    editable_attributes = [
        'Description', 'SourceID', 'ImpactID', 'UrgencyID', 'EstimatedMinutes', 'ResponsibleGroupID', 'TimeBudget',
        'ExpensesBudget', 'LocationID', 'LocationRoomID', 'ServiceID', 'Attributes', 'GoesOffHoldDate', 'StartDate',
        'EndDate', 'ResponsibleUid', 'TypeID', 'AccountID', 'PriorityID', 'RequestorUid', 'Title', 'StatusID'
    ]
    editable_int_attributes = [
        'SourceID', 'ImpactID', 'UrgencyID', 'EstimatedMinutes', 'ResponsibleGroupID', 'LocationID', 'LocationRoomID',
        'ServiceID', 'TypeID', 'AccountID', 'PriorityID', 'StatusID'
    ]
    editable_double_attributes = ['ExpensesBudget', 'TimeBudget']
    editable_date_attributes = ['GoesOffHoldDate', 'StartDate', 'EndDate']

    required_attributes = ['TypeID', 'AccountID', 'PriorityID', 'RequestorUid', 'Title']

    # This constructor makes a bare-bones ticket using defaults
    #   that may or may not work in all circumstances.
    def __init__(self, integration: 'tdx_ticket_integration.TDXTicketIntegration', json=None):
        """
        Instantiates a ticket from scratch -- setting some defaults
        :param integration: a valid ticket integration object
        """
        self.tdx_api = integration
        self.ticket_data = dict()
        if json:
            self.import_data(json)
        else:

            # defaults
            requestor = self.tdx_api.username
            priority = "Low"
            ticket_type = "Standard Incident"
            classification = "Incident"
            status = "New"
            account = "Information Technology"

            self.ticket_data['TypeID']: int = (self.tdx_api.get_ticket_type_by_name_id(ticket_type)['ID'])
            self.ticket_data['AccountID']: int = (self.tdx_api.get_account_by_name(account)['ID'])
            self.ticket_data['PriorityID']: int = (self.tdx_api.get_ticket_priority_by_name_id(priority)['ID'])
            self.ticket_data['RequestorUid']: str = (self.tdx_api.get_person_by_email(requestor)['UID'])
            self.ticket_data['Title']: str = "Auto-Generated Ticket"

            # default some helpful stuff
            self.ticket_data['StatusID']: int = (self.tdx_api.get_ticket_status_by_name(status)['ID'])
            self.ticket_data['Classification']: int = (self.tdx_api.get_ticket_classification_id_by_name(
                classification))
            self.ticket_data['Description']: str = "Auto-Generated Ticket from TicketMaster"
            self.ticket_data['FormID']: int = 0  # sets default form

    def __repr__(self):
        return str(self.ticket_data)

    # Print the ticket nicely
    def __str__(self):
        result = ''
        for key, value in self.ticket_data.items():
            # Concatenate result lines, padding 25 chars to align columns
            result += f'{key:25}\t{value}\n'
        return result

    def import_data(self, data):
        self.ticket_data = {}
        for key, value in data.items():
            if key in TdxTicket.valid_attributes:
                if not value or value is '':
                    continue
                if key in TdxTicket.valid_bool_attributes:
                    self.ticket_data[key]: bool = value
                elif key in TdxTicket.valid_int_attributes:
                    self.ticket_data[key]: int = value
                elif key in TdxTicket.valid_decimal_attributes:
                    self.ticket_data[key]: float = value
                elif key in TdxTicket.valid_date_attributes:
                    self.ticket_data[key]: datetime = self.tdx_api.import_tdx_date(value)
                elif key in TdxTicket.valid_dict_attributes:
                    self.ticket_data[key]: dict = value
                elif key in TdxTicket.valid_list_attributes:
                    self.ticket_data[key]: list = value
                else:
                    self.ticket_data[key]: str = value
            else:
                raise tdx_api_exceptions.TdxApiTicketImportError(
                    "Attribute {0} with value {1} not allowed in Ticket".format(key, value))

    def validate(self, data=None, editable_only=False):
        if not data:
            data = self.ticket_data
        # Check for required attributes
        if not editable_only:
            for attrib in TdxTicket.required_attributes:
                if attrib not in data:
                    raise tdx_api_exceptions.TdxApiTicketValidationError(
                        "Value required for {0}".format(attrib))
                if attrib in self.valid_int_attributes:
                    if not isinstance(data[attrib], int):
                        raise tdx_api_exceptions.TdxApiTicketValidationError(
                            "Integer value required for {0}".format(attrib))
                elif not isinstance(data[attrib], str):
                    raise tdx_api_exceptions.TdxApiTicketValidationError(
                        "String value required for {0}".format(attrib))
        for attrib, value in data.items():
            # Check all attributes for validity
            if attrib not in TdxTicket.valid_attributes:
                raise tdx_api_exceptions.TdxApiTicketValidationError(
                        "{0} with value {1} is not a valid ticket attribute".format(attrib, value))
            # Check editable attributes for correct type
            if attrib in TdxTicket.editable_int_attributes:
                try:
                    int(data[attrib])
                except ValueError:
                    raise tdx_api_exceptions.TdxApiTicketValidationError(
                        "Value for {0} cannot be converted to Int".format(attrib))
            if attrib in TdxTicket.editable_double_attributes:
                try:
                    float(data[attrib])
                except ValueError:
                    raise tdx_api_exceptions.TdxApiTicketValidationError(
                        "Value for {0} cannot be converted to decimal number".format(attrib))
            if attrib in TdxTicket.editable_date_attributes:
                if not isinstance(data[attrib], datetime.datetime):
                    try:
                        self.tdx_api.import_tdx_date(data[attrib])
                    except TypeError:
                        raise tdx_api_exceptions.TdxApiTicketValidationError(
                            "Value {1} for {0} cannot be converted to a datetime object".format(attrib,value))
            # Check for editable attributes only
            if editable_only:
                if attrib not in TdxTicket.editable_attributes:
                    raise tdx_api_exceptions.TdxApiTicketValidationError(
                        "Attribute {0} not editable (editable-only validation)".format(attrib))

    def export(self, validate=False):
        # This function exports ticket data as a dict containing a dict called
        #   "ticket" with the attributes of a ticket. This is helpful for creating the JSON
        #   for creating/updating tickets in the TDX API
        # The validate parameter indicates whether or not we should validate
        #   the ticket attributes for the type and presence of required attributes
        exported_ticket_data = dict()
        # We need to strip out non-existent values that TDX won't be able to handle
        for key, value in self.ticket_data.items():
            if value is not None and value is not '':
                if key in TdxTicket.valid_date_attributes:
                    exported_ticket_data[key] = self.tdx_api.export_tdx_date(value)
                else:
                    exported_ticket_data[key] = value
        if validate:
            self.validate(exported_ticket_data)
        return exported_ticket_data

    def get_id(self):
        return self.ticket_data['ID']

    def update(self, updated_values, validate=True):
        if validate:
            self.validate(updated_values, editable_only=True)
        self.ticket_data.update(updated_values)
        return

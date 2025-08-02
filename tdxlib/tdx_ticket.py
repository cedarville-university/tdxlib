import tdxlib.tdx_api_exceptions
import tdxlib.tdx_utils
from tdxlib.tdx_ticket_attribs import *
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import tdxlib.tdx_ticket_integration


class TDXTicket:


    # This constructor makes a bare-bones ticket using defaults
    #   that may or may not work in all circumstances.
    def __init__(self, integration: 'tdxlib.tdx_ticket_integration.TDXTicketIntegration', json=None):
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
            requestor = self.tdx_api.config.username
            priority = "Low"
            ticket_type = "Standard Incident"
            classification = "Incident"
            status = "New"
            account = "Information Technology"

            self.ticket_data['TypeID']: int = (self.tdx_api.get_ticket_type_by_name_id(ticket_type)['ID'])
            self.ticket_data['AccountID']: int = (self.tdx_api.get_account_by_name(account)['ID'])
            self.ticket_data['PriorityID']: int = (self.tdx_api.get_ticket_priority_by_name_id(priority)['ID'])
            self.ticket_data['RequestorUid']: str = (self.tdx_api.get_person_by_name_email(requestor)['UID'])
            self.ticket_data['Title']: str = "Auto-Generated Ticket"

            # default some helpful stuff
            self.ticket_data['StatusID']: int = (self.tdx_api.search_ticket_status(status)['ID'])
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

    def import_data(self, data, strict: bool = False):
        self.ticket_data = {}
        for key, value in data.items():
            if key in valid_attributes:
                if value is False or value == '':
                    continue
                if key in valid_bool_attributes:
                    self.ticket_data[key]: bool = value
                elif key in valid_int_attributes:
                    self.ticket_data[key]: int = value
                elif key in valid_decimal_attributes:
                    self.ticket_data[key]: float = value
                elif key in valid_date_attributes \
                        and value != 0 \
                        and value != '0001-01-01T05:00:00Z'\
                        and value is not None:
                    self.ticket_data[key]: datetime = tdxlib.tdx_utils.import_tdx_date(value)
                elif key in valid_dict_attributes:
                    self.ticket_data[key]: dict = value
                elif key in valid_list_attributes:
                    self.ticket_data[key]: list = value
                else:
                    self.ticket_data[key]: str = value
            else:
                if strict:
                    raise tdxlib.tdx_api_exceptions.TdxApiTicketImportError(
                        "Attribute {0} with value {1} not allowed in Ticket".format(key, value))

    def validate(self, data=None, editable_only=False, strict: bool = False):
        if not data:
            data = self.ticket_data
        # Check for required attributes
        if not editable_only:
            for attrib in required_attributes:
                if attrib not in data:
                    raise tdxlib.tdx_api_exceptions.TdxApiTicketValidationError(
                        "Value required for {0}".format(attrib))
                if attrib in valid_int_attributes:
                    if not isinstance(data[attrib], int):
                        raise tdxlib.tdx_api_exceptions.TdxApiTicketValidationError(
                            "Integer value required for {0}".format(attrib))
                elif not isinstance(data[attrib], str):
                    raise tdxlib.tdx_api_exceptions.TdxApiTicketValidationError(
                        "String value required for {0}".format(attrib))
        for attrib, value in data.items():
            # Check all attributes for validity
            if attrib not in valid_attributes and strict:
                raise tdxlib.tdx_api_exceptions.TdxApiTicketValidationError(
                        "{0} with value {1} is not a valid ticket attribute".format(attrib, value))
            # Check editable attributes for the correct type
            if attrib in editable_int_attributes:
                try:
                    int(data[attrib])
                except ValueError:
                    raise tdxlib.tdx_api_exceptions.TdxApiTicketValidationError(
                        "Value for {0} cannot be converted to Int".format(attrib))
            if attrib in editable_double_attributes:
                try:
                    float(data[attrib])
                except ValueError:
                    raise tdxlib.tdx_api_exceptions.TdxApiTicketValidationError(
                        "Value for {0} cannot be converted to decimal number".format(attrib))
            if attrib in editable_date_attributes:
                if not isinstance(data[attrib], datetime.datetime):
                    try:
                        tdxlib.tdx_utils.import_tdx_date(data[attrib])
                    except TypeError:
                        raise tdxlib.tdx_api_exceptions.TdxApiTicketValidationError(
                            "Value {1} for {0} cannot be converted to a datetime object".format(attrib, value))
            # Check for editable attributes only
            if editable_only:
                if attrib not in editable_attributes:
                    raise tdxlib.tdx_api_exceptions.TdxApiTicketValidationError(
                        "Attribute {0} not editable (editable-only validation)".format(attrib))

    def export(self, validate=False):
        # This function exports ticket data as a dict containing a dict called
        #   "ticket" with the attributes of a ticket. This is helpful for creating the JSON
        #   for creating/updating tickets in the TDX API
        # The validate parameter indicates whether we should validate
        #   the ticket attributes for the type and presence of required attributes
        exported_ticket_data = dict()
        # We need to strip out non-existent values that TDX won't be able to handle
        for key, value in self.ticket_data.items():
            if value is not None and value != '' and value is not False and value != 0:
                if key in valid_date_attributes:
                    if isinstance(value, datetime.datetime) and not value.year == 1:
                        exported_ticket_data[key] = tdxlib.tdx_utils.export_tdx_date(value)
                else:
                    exported_ticket_data[key] = value
        if validate:
            self.validate(exported_ticket_data)
        return exported_ticket_data

    def get_id(self):
        return self.ticket_data['ID']

    def get_attribute(self, attribute: str):
        if attribute in self.ticket_data:
            return self.ticket_data[attribute]
        else:
            return False

    def update(self, updated_values, validate=True):
        if validate:
            self.validate(updated_values, editable_only=True)
        self.ticket_data.update(updated_values)
        return

import tdxlib.tdx_ticket_integration
import gsheet

SHEET_URL = 'https://docs.google.com/spreadsheets/d/<big_long_string>/edit#gid=0'
SHEET_TAB = 'Sheet1'
HEADERS = 1
CONFIGFILE = 'tdxlib.ini'

# Set ticket data from Google Sheets
tickets = gsheet.read(SHEET_URL, SHEET_TAB, HEADERS)

# Set up TDX connection for tickets
tdx = tdxlib.tdx_ticket_integration.TDXTicketIntegration(CONFIGFILE)

# Set up global values for ticket generation

# This is the ID of the form used for these tickets. 
# If not set (or set to 0), the default form will be used.
# WARNING: Form IDs can't currently be looked up via API. They are visible in TDAdmin
form = 0

# By default, this script will use a template for the name and description of the ticket.
# These values will use the str.format_map() format to populate values from the Google
#   sheet into a template (defined here), but they can be overridden with non-templated
#   per-ticket values within the creation loop below.

# This will be the title of the ticket
# Text in {} will be replaced with data from named column in sheet
title_text = 'Test Title Ticket for {Test1}'

# This will be the body of the ticket
# Text in {} will be replaced with data from named column in sheet
body_text = 'Test Body Text for {Test1} or for {Test2}'

# This is the Ticket Type that will be set for these tickets (can be overridden later)
ticket_type = "Accounts and Access"

# This is the Account/Department that will be set for these tickets (can be overridden later)
account = "Admissions"

# This is the Primary Responsible that will be set for these tickets (can be overridden later)
responsible = 'some_poor_person@example.edu'

# This prefix should be on all column names that reference custom attributes
# The prefix will be stripped off before searching for the name of the attribute
#
# e.g. The value for a custom TDX attribute named "My Custom Attribute" should
#    be stored in a Google Sheets column named "attrib_My Custom Attribute"
prefix = 'attrib_'

# The location name for all tickets. This doesn't have to be the full name of the
#   location, but this string should be unique among your TDX Locations.
location = 'Administration Building'

# The room number in the location above. This doesn't have to be exact, but should
#   be unique among all rooms in the location
room = '207'

# Loop through each of the lines in the spreadsheet
created_tickets = list()
for ticket in tickets:
    # Override ticket-specific variables here

    # responsible = ticket['Responsible']
    # account = ticket['Department']
    # ticket_type = ticket['Type']
    # location = ticket['Building']
    # room = ticket['Room']
    # body_text = ticket['Description']
    # title_text = ticket['Title']

    ticket_data = tdx.generate_ticket(title_text, ticket_type, account, responsible, ticket, body_text, prefix,
                                               location=location, room=room, form_id=form)
    created_ticket = tdx.create_ticket(ticket_data)
    created_tickets.append(created_ticket)
print("Created " + str(len(created_tickets)) + " tickets.")
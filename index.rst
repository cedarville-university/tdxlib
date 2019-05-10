# TicketMaster (TeamDynamix Python SDK)

TicketMaster is a suite of Python libraries originally designed to take input from Google Sheets and create tickets in TeamDynamix based on the contents of the sheets. The scope of the project has broadened past its humble beginnings, and continues to do so whenever there's a feature we need that it doesn't currently support.

## Dependencies

* Python 3.6+, with the following pip packages installed:
  * requests
  * python-dateutil
  * gspread (for Google Sheets integration)
  * oauth2client (for Google Sheets integration)

## Components

* **TDXIntegration**: the base class that contains the methods necessary to authenticate to Teamdynamix. This class also contains methods to interact with TeamDyanamix objects that are universal across various Apps (Locations, People, Accounts, etc.)

  Currently Implemented:
  * Authentication (only simple auth, no loginadmin or sso)
  * Locations & Rooms (read-only)
  * People & Groups (read-only) (no group members)
  * Accounts (read-only)
  * Custom attributes for Tickets & Assets (read-only)
  * Import & Export of TDX-Style DateTime objects into python datetime objects
  
  Future Plans:
  * Read-write support for Locations, Rooms, People, Groups, Accounts, and Custom Attributes
  * Support for custom attributes in Projects, CIs
  * Support for manipulating attachments
  * Support for inspecting/manipulating group members
  * Support for inspecting/manipulating roles & user lists
  * Support for mass-importing users from uploaded excel files
  
  Unlikely to be supported:
  * Time entries
  * Time types
  
* **TDXTicketIntegration**: the class (inherited from TDXIntegration) that allows interactions with Ticket objects.

  Currently Implemented:
  * Ticket Priorities
  * Ticket Statuses (including creation of custom statuses) (WIP)
  * Ticket Types
  * Ticket Urgencies
  * Ticket Sources
  * Ticket Impacts
  * Ticket Classifications (not available directly through API)
  * Ticket Forms (not available directly through API)
  * Tickets:
    * Creation (including templated batch-creation from Google Sheets)
    * Editing (including batch-editing of multiple )
    * Manipulating
    * Searching (by any attribute)

  Future Plans:
  * Support for Ticket Tasks
  * More documentation on how to get started with TDXTicketIntegration library
  
  Unlikely to be supported:
  * Blackout Windows
  * Ticket Searches/Reports

* **TDXAssetIntegration**: the class (inherited from TDXIntegration) that allows interactions with Asset objects.

  Currently Implemented:  
  * (Not much)

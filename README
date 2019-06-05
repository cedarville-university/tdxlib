# TDXLib (TeamDynamix Python SDK)

TDXLib is a suite of Python libraries originally designed to take input from Google Sheets and create tickets in TeamDynamix based on the contents of the sheets. The scope of the project has broadened past its humble beginnings, and continues to do so whenever there's a feature we need that it doesn't currently support.

## Dependencies

* Python 3.6+
* requests
* python-dateutil
* gspread (for Google Sheets integration)
* oauth2client (for Google Sheets integration)

## Getting Started

1. [Download](https://www.python.org/) and install Python. If you're new to Python, check out this [setup tutorial](https://realpython.com/installing-python/ "Python 3 Installation & Setup Guide"). For an introduction to basic Python syntax and use, check out the guides on [python.org](https://www.python.org/about/gettingstarted/).

2. Clone or download TDXLib from [GitHub](https://github.com/cedarville-university/tdxlib).

3. Install the required dependencies to your environment using `pip`, which is bundled with Python 3.4+. If you run into issues on Windows, be sure that the location of your Python installation is specified in your system's `PATH` variable.

    The necessary packages are specified in `requirements.txt` and can be installed with one command:

        pip install -r requirements.txt

    Alternatively, install all the packages manually:

        pip install requests python-dateutil gspread oauth2client

4. In order to authenticate to the TeamDynamix API, TDXLib uses a `tdxlib.ini` configuration file. If there is no file set up in your working directory, TDXLib will generate a blank template that can be edited with your organization's information:

        $ python
        Python 3.7.3 (...) [...] on win32
        Type "help", "copyright", "credits" or "license" for more information.
        >>> import tdx_integration
        >>> tdx = tdx_integration.TDXIntegration()
        
        Traceback (most recent call last):
            ...
        FileNotFoundError: No config settings at tdxlib.ini. Writing sample config to ...\tdxlib\tdxlib.ini

    The generated file will look something like this:

        [TDX API Settings]
        'orgname': 'myuniversity',
        'sandbox': True,
        'username': '',
        'password': 'Prompt',
        'ticketAppId': '',
        'assetAppId': '',
        'caching': False

    The `orgname` field is whatever subdomain your organization uses to access TeamDynamix. For example, `https://myuniversity.teamdynamix.com`.

    The `sandbox` field specifies whether TDXLib should interact with a sandbox version of the TDX Environment, which is written over by production monthly. It is recommended to use the sandbox environment when first getting familiar with the API environment.

    The `username` and `password` fields are the login credentials for an account to be used with the TeamDynamix API. Many API endpoints (such as creating objects in TDX) require elevated permissions beyond the average user. You may need to create a user specifically for use with TDXLib and grant permissions based on what you need to do.

    The `ticketAppId` and `assetAppId` fields are the numbers that appear after `Apps` in your TeamDynamix URL, and are specific to your organization. For example: 
    
    Tickets: `https://myuniversity.teamdynamix.com/TDNext/Apps/{ticketAppId}/Tickets/...`  
    Assets: `https://myuniversity.teamdynamix.com/TDNext/Apps/{assetAppId}/Assets/...`

    The `caching` field specifies whether or not TDXLib should cache TeamDynamix objects such as valid ticket types, statuses and priorities. Setting this option to `True` reduces the volume of API calls and allows TDXLib to perform some batch operations much faster.

5. The base class in TDXLib is the `TDXIntegration` object, which provides access to all the base methods in TDX. To make sure your tdxlib.ini file is set up properly, instantiate the class:

        >>> import tdx_integration
        >>> tdx = tdx_integration.TDXIntegration()

    You can optionally specify an alternative configuration file that TDXLib should search for in your working directory. By default, it will look for `tdxlib.ini`.

        >>> tdx = tdx_integration.TDXIntegration("specialconfig.ini")

    Depending on your `tdxlib.ini` settings, you may be prompted for a password to authenticate into the TeamDynamix API. Once everything is working, go ahead and test out a method:

        >>> accounts = tdx.get_all_accounts()

6. To interact with TDX Tickets and Assets, create a `TDXTicketIntegration` and `TDXAssetIntegration` object, respectively:

        >>> import tdx_ticket_integration
        >>> tix = tdx_ticket_integration.TDXTicketIntegration()
        >>> tix.get_ticket_by_id(1234567)

7. Congratulations! You now have the power of the TeamDynamix API at your fingertips. For information on the methods included with TDXLib, check out our documentation on [Read the Docs](http://tdxlib.readthedocs.io).




    
    

## Components

* ### TDXIntegration:

    This base class that contains the methods necessary to authenticate to Teamdynamix. This class also contains methods to interact with TeamDyanamix objects that are universal across various Apps (Locations, People, Accounts, etc.)

    Currently Implemented:
    * Authentication (only simple auth, no loginadmin or SSO)
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

* ### TDXTicketIntegration:

    The class (inherited from TDXIntegration) that allows interactions with Ticket objects.

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

* ### TDXAssetIntegration:

    The class (inherited from TDXIntegration) that allows interactions with Asset objects.

    Currently Implemented:
    * (Not much)

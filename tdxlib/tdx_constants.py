# Hard-coded into TDX
component_ids = {
    'account': 14,
    'asset': 27,
    'configuration_item': 63,
    'contract': 29,
    'file_cabinet': 8,
    'issue': 3,
    'opportunity': 11,
    'person': 31,
    'product': 37,
    'product_model': 30,
    'project': 1,
    'ticket': 9,
    'vendor': 28
}


default_config = {
    # 'org_name': '',
    'sandbox': True,
    'auth_type': 'password',
    # 'username': '',
    # 'password': '',
    # 'ticket_app_id': '',
    # 'asset_app_id': '',
    'caching': False,
    'timezone': '-0500',
    'log_level': 'ERROR',
    # 'full_host': ''

}

config_keys = {
    'org_name': str,
    'orgname': str,
    'sandbox': bool,
    'auth_type': str,
    # backwards compatibility
    'authType': str,
    'password': str,
    'username': str,
    'ticket_app_id': str,
    # backwards compatibility
    'ticketAppId': str,
    'asset_app_id': str,
    # backwards compatibility
    'assetAppId': str,
    'caching': bool,
    'timezone': str,
    'log_level': str,
    # backwards compatibility
    'logLevel': str,
    'full_host': str
}

default_filename = "tdxlib.ini"

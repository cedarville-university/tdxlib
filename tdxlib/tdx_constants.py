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
    'authType': 'password',
    # 'username': '',
    # 'password': '',
    # 'ticketAppId': '',
    # 'assetAppId': '',
    'caching': False,
    'timezone': '-0500',
    'logLevel': 'ERROR',
    # 'full_host': ''

}

config_keys = {
    'org_name': str,
    'sandbox': bool,
    'authType': str,
    'password': str,
    'username': str,
    'ticketAppId': str,
    'assetAppId': str,
    'caching': bool,
    'timezone': str,
    'logLevel': str,
    'full_host': str
}

default_filename = "tdxlib.ini"

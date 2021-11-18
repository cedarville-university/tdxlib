import dateutil.parser
import datetime
import json


# Prints out dict as JSON with indents
def print_nice(myjson):
    print(json.dumps(myjson, indent=4))
    print("")


# Print summary of ticket, or dict of tickets
def print_simple(my_json, attributes=None):
    if isinstance(my_json, list):
        this_json = my_json
    else:
        this_json = list([my_json])
    default_attributes = ['FullName', 'Name', 'Title',  'ID', 'UID', 'Requestor', 'TypeName']
    if not attributes:
        attributes = default_attributes
    for j in this_json:
        for i in attributes:
            if i in j:
                print(i,':\t', j[i])


# Print only ['Name'] attribute of list of objects
def print_names(myjson):
    if isinstance(myjson,list):
        this_json = myjson
    else:
        this_json = list([myjson])
    for i in this_json:
        if 'Name' in i:
            print(i['Name'])


# Imports a string from a TDX Datetime attribute, returns a python datetime object
def import_tdx_date(date_string: str) -> datetime:
    return dateutil.parser.parse(date_string)


# Takes a python datetime object, returns a string compatible with a TDX Datetime attribute
def export_tdx_date(date: datetime, timezone: str = 'Z') -> str:
    """
    Takes a python datetime object, returns a string compatible with a TDX Datetime attribute, including timezone.
    Note: This will not convert a UCT time to the timezone you specify.

    :param date: Datetime object to output as TDX
    :param timezone: A string indicating +/- hours:minutes. For EST this param is '-0500' (Default: Z [UTC])

    :return: A string that TDX will accept

    """
    if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
        date_string = date.strftime('%Y-%m-%dT%H:%M:%S' + timezone)
    else:
        date_string = date.strftime('%Y-%m-%dT%H:%M:%S%z')
    return date_string


def is_id(identifier: str):
    int_id = None
    try:
        int_id = int(identifier)
    except ValueError as e:
        pass
    return int_id

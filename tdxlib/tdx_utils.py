import dateutil.parser
import datetime
import json
import xlrd


# Prints out dict as JSON with indents
def print_nice(myjson):
    print(json.dumps(myjson, indent=4))
    print("")


# Print summary of ticket, or dict of tickets
def print_simple(myjson):
    for i in myjson:
        for j in i:
            if j['Name']:
                print('Name:\t', j['Name'])
            if j['Title']:
                print('Title:\t', j['Title'])
            if j['ID']:
                print('ID:\t', j['ID'])
            if j['UID']:
                print('ID:\t', j['UID'])
            if j['Requestor']:
                print('Requestor:\t', j['Requestor'])
            if j['TypeName']:
                print('Type:\t', j['TypeName'])
            


# Print only ['Name'] attribute of list of objects
def print_names(myjson):
    for i in myjson:
        print(i['Name'])


# Imports a string from an excel date string, returns a python datetime object
def import_excel_date(date_string: str) -> datetime:
    return xlrd.xldate_as_datetime(date_string, 0)


# Imports a string from a TDX Datetime attribute, returns a python datetime object
def import_tdx_date(date_string: str) -> datetime:
    return dateutil.parser.parse(date_string)


# Takes a python datetime object, returns a string compatible with a TDX Datetime attribute
def export_tdx_date(date: datetime) -> str:
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')
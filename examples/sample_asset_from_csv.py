import tdxlib
import csv
from sys import argv

"""
This example script allows you to take a CSV with the columns: 
    "Name", "Serial Number", "Location", "Room", "Model", and  "Tag"
and turn each row into an asset record in TDX. 

Support for custom attributes is provided (commented out). 

See documentation at https://tdxlib.readthedocs.io for more info. 
"""


filename = argv[1]  # Gets the CSV filename from the command line

# Set Global attributes here -- will apply to all created Assets
department_name = 'Information Technology Services'  # Sets the owning department
status = "In Use"

t = tdxlib.tdx_asset_integration.TDXAssetIntegration()  # Starts up a new Asset Integration object
new_asset_list = list()  # Makes a new list to store the new asset records in
with open(filename, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        new_asset_list.append(row)

result = list()
for i in new_asset_list:
    d = dict()  # Empty dict to fill with Custom Attributes if you need them.
    ca_prefix = None  # change this to a string if you want to use custom attributes.
    # ca_prefix = 'custom_'
    # d['custom_My Attribute'] = i['My Attribute']
    # d['custom_My Other Attribute'] = i['My Other Attribute']

    # Here, you can map your CSV's columns to the attributes required:
    name = i['Name']
    sn = i['Serial Number']
    loc = i['Location']
    room = i['Room']
    model = i['Model']
    tag = i['Tag']

    j = t.make_basic_asset_json(d, asset_name=name, serial_number=sn, status_name=status,
                                location_name=loc, room_name=room, product_model=model,
                                asset_tag=tag, owning_dept=department_name, attrib_prefix=ca_prefix)
    a = t.create_asset(j)
    result.append(a)

print ('Completed: \n\n')
tdxlib.tdx_utils.print_nice(result)

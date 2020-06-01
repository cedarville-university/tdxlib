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

# Set Global attributes here -- these will apply to all created Assets'
status = "In Use" # This is required -- must match an existing asset status in TDX exactly
department_name = 'Information Technology Services'  # Optional -- remove "owning_dept=department_name," below if you don't use this
asset_form = 'Computer Form'  # Optional -- remove "form=asset_form," below if you don't use this


t = tdxlib.tdx_asset_integration.TDXAssetIntegration()  # Starts up a new Asset Integration object
new_asset_list = list()  # Makes a new list to store the new asset records in
with open(filename, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        new_asset_list.append(row)

result = list()
for i in new_asset_list:
    d = dict()  # Empty dict to fill with Custom Attributes if you need them. Uncomment below if necessary
    # NOTE: The the name of the attribute on the left side below (in 'd') must match exactly with CA names in TDX.
    # d['TDX Custom Attrib Name'] = i['Some CSV Attribute']
    # d['Other TDX Custom Attrib Name'] = i['Some Other CSV Attribute']

    # Here, you can map your CSV's columns to the available attributes:

    name = i['Name']  # Required
    sn = i['Serial Number']  # Required
    loc = i['Location']  # Optional -- remove "location_name=loc," below if you don't use this
    room = i['Room']  # Optional -- remove "room_name=room," below if you don't use this
    model = i['Model']  # Optional -- remove "product_model=model," below if you don't use this
    tag = i['Tag']  # Optional -- remove "asset_tag=tag," below if you don't use this
    person = i['Owner'] # Optional -- remove "requester=person," below if you don't use this

    # You can get creative with fields, combining attributes from the CSV, if you want to do more complex things:
    #  This sets the name of the asset to <tag>-<sn>
    #    name = f"{i['Tag']}-{i['Serial Number']}"
    #  This sets a custom attribute called "Description" using fields "Type" "Install Date" and "Technician"
    #    d['Description'] = "This {i['Type']} was installed on {i['Install Date']) by {i['Technician']}"

    j = t.build_asset(asset_name=name, serial_number=sn, status_name=status, form=asset_form,
                      location_name=loc, room_name=room, product_model=model, requester=person,
                      asset_tag=tag, owning_dept=department_name, asset_custom_attributes=d)
    a = t.create_asset(j)
    result.append(a)

print ('Completed: \n\n')
tdxlib.tdx_utils.print_nice(result)

import tdx_ticket_integration
from datetime import datetime as dt

# Acquires Bearer token and gets all the libraries for script use.
# tax = tdx_asset_integration.TDXAssetIntegration()
tix = tdx_ticket_integration.TDXTicketIntegration()

# Add your script here

changed_attributes = {
    'Description': f'This task was updated at {dt.now()}.'
}
# result = tix.create_ticket_task(4944908, task)

data = tix.get_ticket_task_by_id(4944908, 1234)
print(bool(data))
tix.print_nice(data)

# tix.edit_ticket_task(4944908, data, changed_attributes)

# data = tix.get_ticket_task_by_id(4944908, 2290947)

# tix.print_nice(data)
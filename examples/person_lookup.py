# TDX test script, prompts for user input, then prints user data from TDX

import tdxlib.tdx_ticket_integration

tix = tdxlib.tdx_ticket_integration.TDXTicketIntegration()

person = input("Please enter your id number: ")

result = tix.get_person_by_name_email(person)

for k,v in result.items:
    print(k + ':', v, sep='\t')
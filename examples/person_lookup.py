# TDX test script, prompts for user input, then prints user data from TDX

import tdxlib.tdx_ticket_integration

tix = tdxlib.tdx_ticket_integration.TDXTicketIntegration()

person = input("Please enter your id number: ")

result = tix.search_people(person)

for a in result:
    print(a, result[a], sep='\t')
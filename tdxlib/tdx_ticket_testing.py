import unittest
from datetime import datetime as dt
from tdxlib import tdx_integration
from tdxlib import tdx_asset_integration
from tdxlib import tdx_ticket_integration


class TdxTicketTesting(unittest.TestCase):

    # Create TDXIntegration object for testing use. Called before testing methods.
    def setUp(self):
        self.tix = tdx_ticket_integration.TDXTicketIntegration()
        right_now = dt.today()
        self.timestamp = right_now.strftime("%d-%B-%Y %H:%M:%S")
    
    def test_authn(self):
        self.assertGreater(len(self.tix.token), 200)

    def test_get_ticket_by_id(self):
        self.assertTrue(self.tix.get_ticket_by_id('5814276'))  # TDX Test Ticket #5814276

    def test_search_tickets(self):
        self.assertTrue(self.tix.search_tickets('test'))

    # #### CHANGING TICKETS #### #

    def test_edit_tickets(self):
        # Protect production from deleting tasks
        if not self.tix.sandbox:
            return
        ticket_list = list()
        ticket_list.append(self.tix.get_ticket_by_id(4944908))
        ticket_list.append(self.tix.get_ticket_by_id(4837287))
        title_string = self.timestamp + ' testing ticket'
        changes = {
            'Title': title_string
        }
        self.assertTrue(all(self.tix.edit_tickets(ticket_list, changes, notify=False)))
   
    def test_edit_type(self):
        # Protect production from deleting tasks
        if not self.tix.sandbox:
            return
        ticket = self.tix.get_ticket_by_id(4944908)
        previous_type = ticket.ticket_data['TypeID']
        desired_type = "IT Internal"
        self.assertTrue(all(self.tix.edit_ticket_type(ticket, desired_type)))

        # revert change to original type
        self.tix.edit_ticket_type(ticket, previous_type)
    
    def test_edit_status(self):
        # Protect production from deleting tasks
        if not self.tix.sandbox:
            return
        ticket = self.tix.get_ticket_by_id(4944908)
        previous_status = ticket.ticket_data['StatusID']
        desired_status = "Open"
        self.assertTrue(all(self.tix.edit_ticket_status(ticket, desired_status)))

        # revert change to original status
        self.tix.edit_ticket_status(ticket, previous_status)

    def test_edit_priority(self):
        # Protect production from deleting tasks
        if not self.tix.sandbox:
            return
        ticket = self.tix.get_ticket_by_id(4944908)
        previous_priority = ticket.ticket_data['PriorityID']
        desired_priority = "Low"
        self.assertTrue(all(self.tix.edit_ticket_priority(ticket, desired_priority)))

        # revert change to original priority
        self.tix.edit_ticket_priority(ticket, previous_priority)

    def test_edit_urgency(self):
        # Protect production from deleting tasks
        if not self.tix.sandbox:
            return
        ticket = self.tix.get_ticket_by_id(4944908)
        previous_urgency = ticket.ticket_data['UrgencyID']
        desired_urgency = "Low"
        self.assertTrue(all(self.tix.edit_ticket_urgency(ticket, desired_urgency)))

        # revert change to original urgency
        self.tix.edit_ticket_urgency(ticket, previous_urgency)

    def test_edit_impact(self):
        # Protect production from deleting tasks
        if not self.tix.sandbox:
            return
        ticket = self.tix.get_ticket_by_id(4944908)
        previous_impact = ticket.ticket_data['ImpactID']
        desired_impact = "Affects Client"
        self.assertTrue(all(self.tix.edit_ticket_impact(ticket, desired_impact)))

        # revert change to original impact
        self.tix.edit_ticket_impact(ticket, previous_impact)

    def test_edit_source(self):
        # Protect production from deleting tasks
        if not self.tix.sandbox:
            return
        ticket = self.tix.get_ticket_by_id(4944908)
        previous_source = ticket.ticket_data['SourceID']
        desired_source = "Phone"
        self.assertTrue(all(self.tix.edit_ticket_source(ticket, desired_source)))

        # revert change to original source
        self.tix.edit_ticket_source(ticket, previous_source)

    # #### GETTING TICKET ATTRIBUTES #### #

    def test_get_all_ticket_types(self):
        types = self.tix.get_all_ticket_types()
        self.assertGreaterEqual(len(types), 40)

    def test_get_ticket_type_by_id(self):
        key = 23286 # IT Internal
        self.assertTrue(self.tix.get_ticket_type_by_name_id(key))

    def test_get_ticket_type_by_name(self):
        key = "IT Internal"
        self.assertTrue(self.tix.get_ticket_type_by_name_id(key))

    def test_get_all_ticket_statuses(self):
        statuses = self.tix.get_all_ticket_statuses()
        self.assertGreaterEqual(len(statuses), 5)

    def test_get_ticket_status_by_id(self):
        key = 30794  # Open
        self.assertTrue(self.tix.get_ticket_status_by_id(key))

    def test_get_ticket_status_by_name(self):
        key = 'New'
        self.assertTrue(self.tix.get_ticket_status_by_name(key))

    def test_get_all_ticket_priorities(self):
        priorities = self.tix.get_all_ticket_priorities()
        self.assertGreaterEqual(len(priorities), 4)

    def test_get_ticket_priority_by_id(self):
        key = 3944  # Low
        self.assertTrue(self.tix.get_ticket_priority_by_name_id(key))

    def test_get_ticket_priority_by_name(self):
        name = 'Low'
        self.assertTrue(self.tix.get_ticket_priority_by_name_id(name))

    def test_get_ticket_classification_id_by_name(self):
        name = 'Incident'
        self.assertTrue(self.tix.get_ticket_classification_id_by_name(name))

    def test_get_all_ticket_urgencies(self):
        urgencies = self.tix.get_all_ticket_urgencies()
        self.assertGreaterEqual(len(urgencies), 3)

    def test_get_ticket_urgency_by_id(self):
        key = 3941  # Low
        self.assertTrue(self.tix.get_ticket_urgency_by_name_id(key))

    def test_get_ticket_urgency_by_name(self):
        key = 'Low'
        self.assertTrue(self.tix.get_ticket_urgency_by_name_id(key))

    def test_get_all_ticket_impacts(self):
        impacts = self.tix.get_all_ticket_impacts()
        self.assertGreaterEqual(len(impacts), 5)

    def test_get_ticket_impact_by_id(self):
        key = 3937 # Affects Client
        self.assertTrue(self.tix.get_ticket_impact_by_name_id(key))

    def test_get_ticket_impact_by_name(self):
        key = 'Affects Client'
        self.assertTrue(self.tix.get_ticket_impact_by_name_id(key))

    def test_get_all_ticket_sources(self):
        sources = self.tix.get_all_ticket_sources()
        self.assertGreaterEqual(len(sources), 7)

    def test_get_ticket_source_by_id(self):
        key = 1318 # Phone
        self.assertTrue(self.tix.get_ticket_source_by_name_id(key))

    def test_get_ticket_source_by_name(self):
        key = 'Phone'
        self.assertTrue(self.tix.get_ticket_source_by_name_id(key))

    def test_create_ticket(self):
        # Protect production from testing tickets
        if not self.tix.sandbox:
            return
        else:
            title_string = "Testing Ticket Created " + self.timestamp
            json_data = self.tix.generate_ticket(title_string, "Accounts and Access", "Information Technology",
                                                 "ticketcreation@cedarville.edu")
            created_ticket = self.tix.create_ticket(json_data)
            self.assertTrue(created_ticket.get_id() > 10000)

    # #### TICKET TASKS #### #

    def test_get_all_tasks_by_ticket_id(self):
        ticket_id = 4944908
        self.assertTrue(self.tix.get_all_tasks_by_ticket_id(ticket_id))

    def test_get_ticket_task_by_id(self):
        ticket_id = 4944908
        task_id = 2290947
        self.assertTrue(self.tix.get_ticket_task_by_id(ticket_id, task_id))

    def test_create_ticket_task(self):
        # Protect production from testing tasks
        if not self.tix.sandbox:
            return
        else:
            ticket_id = 4944908
            task = {
                'Title': f"Test task at {dt.now()}"
            }
            created_task = self.tix.create_ticket_task(ticket_id, task)
            self.assertGreater(created_task['ID'], 10000)

    def test_edit_ticket_task(self):
        # Protect production from deleting tasks
        if not self.tix.sandbox:
            return
        ticket_id = 4944908
        task_id = 2290947
        task = self.tix.get_ticket_task_by_id(ticket_id, task_id)
        changed_attributes = {
            'Description': f'This task was updated at {dt.now()}.'
        }
        edited_task = self.tix.edit_ticket_task(4944908, task, changed_attributes)
        self.assertEqual(edited_task['Description'], changed_attributes['Description'])

    # def test_delete_ticket_task(self):
    #     # NOTE: If create_ticket_task is not working, this test will not work properly.
    #     # Protect production from deleting tasks
    #     if not self.tix.sandbox:
    #         return
    #     else:
    #         ticket_id = 4944908
    #         task = {
    #             'Title': f'Delete this task at {dt.now()}'
    #         }
    #
    #         # Create new task
    #         created_task = self.tix.create_ticket_task(ticket_id, task)
    #
    #         # Delete the task
    #         self.tix.delete_ticket_task(ticket_id, created_task['ID'])
    #
    #         # Make sure the task is deleted
    #         deleted_task = self.tix.get_ticket_task_by_id(ticket_id, created_task['ID'])
    #         self.assertEqual(deleted_task, False)



    # TODO:
    # def test_change_ticket_task_responsible():
    # def test_set_ticket_task_dates():


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TdxTicketTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)

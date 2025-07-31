import unittest
import json
import time
from datetime import datetime as dt
from datetime import timedelta as td
from tdxlib import tdx_ticket_integration
from tdxlib import tdx_utils
import os


class TdxTicketTesting(unittest.TestCase):
    # Create TDXIntegration object for testing use. Called before testing methods.
    def setUp(self):
        # Only run tests that don't require admin
        self.is_admin = False
        testing_vars_file = './ticket_testing_vars.json'
        self.tix = tdx_ticket_integration.TDXTicketIntegration('../tdxlib.ini')
        right_now = dt.today()
        self.timestamp = right_now.strftime("%d-%B-%Y %H:%M:%S")
        if os.path.isfile(testing_vars_file):
            with open(testing_vars_file, 'r') as f:
                self.testing_vars = json.load(f)
        else:
            print('Testing variables need to be populated in file "testing_vars.json" in the working directory.',
                  'A sample file is available in testing/sample_ticket_testing_vars. Any *.json files are ignored by git.')
    
    def test_authn(self):
        if not self.timestamp:
            self.setUp()
        self.assertGreater(len(self.tix.config.token), 200)

    def test_get_ticket_by_id(self):
        if not self.timestamp:
            self.setUp()
        self.assertTrue(self.tix.get_ticket_by_id(self.testing_vars['ticket1']['ID']))  # TDX Test Ticket #5814276

    def test_search_tickets(self):
        if not self.timestamp:
            self.setUp()
        self.assertTrue(self.tix.search_tickets('test'))

    # #### CHANGING TICKETS #### #

    def test_edit_tickets(self):
        if not self.timestamp:
            self.setUp()
        # Protect production from deleting tasks
        if not self.tix.config.sandbox:
            return
        ticket_list = list()
        ticket_list.append(self.tix.get_ticket_by_id(self.testing_vars['ticket2']['ID']))
        ticket_list.append(self.tix.get_ticket_by_id(self.testing_vars['ticket3']['ID']))
        title_string = self.timestamp + ' testing ticket'
        changes = {
            'Title': title_string
        }
        changed_tickets = self.tix.edit_tickets(ticket_list, changes, notify=False)
        self.assertTrue(all(changed_tickets))
        for i in changed_tickets:
            self.assertEqual(i.get_attribute('Title'), changes['Title'])

    # #### GETTING TICKET ATTRIBUTES #### #

    def test_get_all_ticket_types(self):
        if not self.timestamp:
            self.setUp()
        types = self.tix.get_all_ticket_types()
        self.assertGreaterEqual(len(types), 40)

    def test_get_ticket_type_by_id(self):
        if not self.timestamp:
            self.setUp()
        key = self.testing_vars['ticket_type']['ID'] # IT Internal
        self.assertTrue(self.tix.get_ticket_type_by_name_id(key))

    def test_get_ticket_type_by_name(self):
        if not self.timestamp:
            self.setUp()
        key = self.testing_vars['ticket_type']['Name']
        self.assertTrue(self.tix.get_ticket_type_by_name_id(key))

    def test_get_all_ticket_statuses(self):
        if not self.timestamp:
            self.setUp()
        statuses = self.tix.get_all_ticket_statuses()
        self.assertGreaterEqual(len(statuses), 5)

    def test_get_ticket_status_by_id(self):
        if not self.timestamp:
            self.setUp()
        key = self.testing_vars['ticket_status']['ID'] # Open
        self.assertTrue(self.tix.get_ticket_status_by_id(key))

    def test_get_ticket_status_by_name(self):
        if not self.timestamp:
            self.setUp()
        key = self.testing_vars['ticket_status']['Name']
        self.assertTrue(self.tix.search_ticket_status(key))

    def test_get_default_not_closed_ticket_statuses(self):
        if not self.timestamp:
            self.setUp()
        statuses = self.tix.get_default_not_closed_ticket_statuses()
        self.assertGreaterEqual(len(statuses), 1)

    def test_get_default_closed_ticket_statuses(self):
        if not self.timestamp:
            self.setUp()
        statuses = self.tix.get_default_closed_ticket_statuses()
        self.assertGreaterEqual(len(statuses), 1)

    def test_get_default_cancelled_ticket_statuses(self):
        if not self.timestamp:
            self.setUp()
        statuses = self.tix.get_default_cancelled_ticket_statuses()
        self.assertGreaterEqual(len(statuses), 1)

    def test_get_all_ticket_priorities(self):
        if not self.timestamp:
            self.setUp()
        priorities = self.tix.get_all_ticket_priorities()
        self.assertGreaterEqual(len(priorities), 4)

    def test_get_ticket_priority_by_id(self):
        if not self.timestamp:
            self.setUp()
        key = self.testing_vars['ticket_priority']['ID']  # Low
        self.assertTrue(self.tix.get_ticket_priority_by_name_id(key))

    def test_get_ticket_priority_by_name(self):
        if not self.timestamp:
            self.setUp()
        name = self.testing_vars['ticket_priority']['Name']
        self.assertTrue(self.tix.get_ticket_priority_by_name_id(name))

    def test_get_ticket_classification_id_by_name(self):
        if not self.timestamp:
            self.setUp()
        name = self.testing_vars['ticket_classification']['Name']
        self.assertTrue(self.tix.get_ticket_classification_id_by_name(name))

    def test_get_all_ticket_urgencies(self):
        if not self.timestamp:
            self.setUp()
        urgencies = self.tix.get_all_ticket_urgencies()
        self.assertGreaterEqual(len(urgencies), 3)

    def test_get_ticket_urgency_by_id(self):
        if not self.timestamp:
            self.setUp()
        key =  self.testing_vars['ticket_urgency']['ID']
        self.assertTrue(self.tix.get_ticket_urgency_by_name_id(key))

    def test_get_ticket_urgency_by_name(self):
        if not self.timestamp:
            self.setUp()
        key = self.testing_vars['ticket_urgency']['Name']
        self.assertTrue(self.tix.get_ticket_urgency_by_name_id(key))

    def test_get_all_ticket_impacts(self):
        if not self.timestamp:
            self.setUp()
        impacts = self.tix.get_all_ticket_impacts()
        self.assertGreaterEqual(len(impacts), 5)

    def test_get_ticket_impact_by_id(self):
        if not self.timestamp:
            self.setUp()
        key = self.testing_vars['ticket_impact']['ID']
        self.assertTrue(self.tix.get_ticket_impact_by_name_id(key))

    def test_get_ticket_impact_by_name(self):
        if not self.timestamp:
            self.setUp()
        key = self.testing_vars['ticket_impact']['Name']
        self.assertTrue(self.tix.get_ticket_impact_by_name_id(key))

    def test_get_all_ticket_sources(self):
        if not self.timestamp:
            self.setUp()
        sources = self.tix.get_all_ticket_sources()
        self.assertGreaterEqual(len(sources), 7)

    def test_get_ticket_source_by_id(self):
        if not self.timestamp:
            self.setUp()
        key = self.testing_vars['ticket_source']['ID']
        self.assertTrue(self.tix.get_ticket_source_by_name_id(key))

    def test_get_ticket_source_by_name(self):
        if not self.timestamp:
            self.setUp()
        key = self.testing_vars['ticket_source']['Name']
        self.assertTrue(self.tix.get_ticket_source_by_name_id(key))

    def test_create_ticket(self):
        if not self.timestamp:
            self.setUp()
        # Protect production from testing tickets
        if not self.tix.config.sandbox:
            return
        else:
            title_string = "Testing Ticket Created " + self.timestamp
            json_data = self.tix.generate_ticket(title_string,
                                                 self.testing_vars['ticket_type']['Name'],
                                                 self.testing_vars['account']['Name'],
                                                 self.tix.config.username)
            created_ticket = self.tix.create_ticket(json_data)
            self.assertTrue(created_ticket.get_id() > 10000)

    # #### TICKET TASKS #### #

    def test_get_all_tasks_by_ticket_id(self):
        if not self.timestamp:
            self.setUp()
        ticket_id = self.testing_vars['ticket2']['ID']
        self.assertTrue(self.tix.get_all_tasks_by_ticket_id(ticket_id))

    def test_get_ticket_task_by_id(self):
        if not self.timestamp:
            self.setUp()
        ticket_id = self.testing_vars['ticket2']['ID']
        task_id = self.testing_vars['ticket2']['task']['ID']
        self.assertTrue(self.tix.get_ticket_task_by_id(ticket_id, task_id))

    def test_create_ticket_task(self):
        if not self.timestamp:
            self.setUp()
        # Protect production from testing tasks
        if not self.tix.config.sandbox:
            return
        else:
            ticket_id = self.testing_vars['ticket2']['ID']
            task = {
                'Title': f"Test task at {dt.now()}"
            }
            created_task = self.tix.create_ticket_task(ticket_id, task)
            self.assertGreater(created_task['ID'], 10000)

    def test_edit_ticket_task(self):
        if not self.timestamp:
            self.setUp()
        # Protect production from deleting tasks
        if not self.tix.config.sandbox:
            return
        ticket_id = self.testing_vars['ticket2']['ID']
        task_id = self.testing_vars['ticket2']['task']['ID']
        task = self.tix.get_ticket_task_by_id(ticket_id, task_id)
        changed_attributes = {
            'Description': f'This task was updated at {dt.now()}.'
        }
        edited_task = self.tix.edit_ticket_task(ticket_id, task, changed_attributes)
        self.assertTrue(edited_task)
        self.assertEqual(edited_task['Description'], changed_attributes['Description'])

    def test_delete_ticket_task(self):
        if not self.timestamp:
            self.setUp()
        if not self.tix.config.sandbox:
            return
        # Create the task
        ticket_id = self.testing_vars['ticket2']['ID']
        task = {
            'Title': f'Delete this task at {dt.now()}'
        }
        created_task = self.tix.create_ticket_task(ticket_id, task)
        time.sleep(3)
        # Delete the task
        self.tix.delete_ticket_task(ticket_id, created_task['ID'])
        # Make sure the task is deleted
        task_list = self.tix.get_all_tasks_by_ticket_id(ticket_id)
        self.assertFalse(all(i['ID'] == created_task['ID'] for i in task_list))

    def test_reassign_ticket_task(self):
        if not self.timestamp:
            self.setUp()
        if not self.tix.config.sandbox:
            return
        ticket_id = self.testing_vars['ticket2']['ID']
        task_id = self.testing_vars['ticket2']['task']['ID']
        task = self.tix.get_ticket_task_by_id(ticket_id, task_id)
        if task['ResponsibleUid'] == self.testing_vars['person1']['UID']:
            reassign = {'ResponsibleUid': self.testing_vars['person2']['UID']}
        else:
            reassign = {'ResponsibleUid': self.testing_vars['person1']['UID']}
        changed_task = self.tix.edit_ticket_task(ticket_id, task_id, reassign)
        self.assertEqual(changed_task['ResponsibleUid'], reassign['ResponsibleUid'])

    def test_reassign_ticket(self):
        if not self.timestamp:
            self.setUp()
        if not self.tix.config.sandbox:
            return
        ticket_id = self.testing_vars['ticket2']['ID']
        ticket = self.tix.get_ticket_by_id(ticket_id)
        if ticket.get_attribute('ResponsibleUid') == self.testing_vars['person1']['UID']:
            reassign = self.testing_vars['person2']
        else:
            reassign = self.testing_vars['person1']
        changed_ticket = self.tix.reassign_ticket(ticket_id, reassign['PrimaryEmail'])
        self.assertEqual(changed_ticket.get_attribute('ResponsibleUid'), reassign['UID'])

    def test_reschedule_ticket(self):
        if not self.timestamp:
            self.setUp()
        if not self.tix.config.sandbox:
            return
        ticket_id = self.testing_vars['ticket1']['ID']
        start = dt.utcnow()
        end = start + td(days=5)
        changed_ticket = self.tix.reschedule_ticket(ticket_id, start, end)
        self.assertEqual(changed_ticket.get_attribute('StartDate').day, start.day)

    def test_reschedule_ticket_task(self):
        if not self.timestamp:
            self.setUp()
        if not self.tix.config.sandbox:
            return
        ticket_id = self.testing_vars['ticket2']['ID']
        task_id = self.testing_vars['ticket2']['task']['ID']
        start = dt.utcnow()
        end = start + td(days=5)
        changed_ticket_task = self.tix.reschedule_ticket_task(ticket_id, task_id, start, end)
        self.assertEqual(changed_ticket_task['StartDate'][0:8], tdx_utils.export_tdx_date(start)[0:8])

    def test_generate_ticket_task(self):
        if not self.timestamp:
            self.setUp()
        if not self.tix.config.sandbox:
            return
        task = self.tix.generate_ticket_task("Testing Task", description="this is a test",start=dt.utcnow(),
                                             responsible=self.testing_vars['person1']['FullName'])
        self.assertTrue(task)

    def test_create_custom_ticket_status(self):
        if not self.timestamp:
            self.setUp()
        if not self.is_admin:
            return
        if not self.tix.config.sandbox:
            return
        status = self.tix.create_custom_ticket_status('Never Gonna Happen', 1, 'Cancelled')
        get_status = self.tix.get_ticket_status_by_id(status['ID'])
        self.assertTrue(get_status)

    def test_edit_custom_ticket_status(self):
        if not self.timestamp:
            self.setUp()
        if not self.is_admin:
            return
        if not self.tix.config.sandbox:
            return
        self.test_create_custom_ticket_status()
        to_change = {'Name': 'Never Gonna Give You Up'}
        changed = self.tix.edit_custom_ticket_status('Never Gonna Happen', to_change)
        self.assertEqual(to_change['Name'],changed['Name'])

    def test_update_ticket_task(self):
        if not self.timestamp:
            self.setUp()
        if not self.tix.config.sandbox:
            return
        ticket_id = self.testing_vars['ticket2']['ID']
        task_id = self.testing_vars['ticket2']['task']['ID']
        update = self.tix.update_ticket_task(ticket_id, task_id, 99, comments='almost done')
        self.assertTrue(update)

    def test_update_ticket(self):
        if not self.timestamp:
            self.setUp()
        if not self.tix.config.sandbox:
            return
        ticket_id = self.testing_vars['ticket1']['ID']
        update = self.tix.update_ticket(ticket_id, comments=str(self.timestamp), new_status='Open')
        self.assertTrue(self.timestamp in update['Body'])

    def test_upload_attachment(self):
        if not self.timestamp:
            self.setUp()
        if not self.tix.config.sandbox:
            return
        ticket_id = self.testing_vars['ticket1']['ID']
        filename = self.testing_vars['attachment']['Name']
        with open (filename, "rb") as file:
            update = self.tix.upload_attachment(ticket_id, file)
        self.assertEqual(filename.split('/')[-1], update['Name'])

    def test_upload_attachment_filename(self):
        if not self.timestamp:
            self.setUp()
        if not self.tix.config.sandbox:
            return
        ticket_id = self.testing_vars['ticket2']['ID']
        filepath = self.testing_vars['attachment']['Name']
        filename = filepath.split('/')[-1]
        with open (filepath, "rb") as file:
            update = self.tix.upload_attachment(ticket_id, file, filename)
        self.assertEqual(filename, update['Name'])

    def test_get_ticket_task_feed(self):
        if not self.timestamp:
            self.setUp()
        ticket_id = self.testing_vars['ticket2']['ID']
        task_id = self.testing_vars['ticket2']['task']['ID']
        feed = self.tix.get_ticket_task_feed(ticket_id, task_id)
        self.assertGreater(len(feed), 0)

    def test_get_ticket_feed(self):
        if not self.timestamp:
            self.setUp()
        ticket_id = self.testing_vars['ticket2']['ID']
        feed = self.tix.get_ticket_feed(ticket_id)
        self.assertGreater(len(feed), 0)

    def test_build_custom_attribute_value(self):
        if not self.tix:
            self.setUp()
        if not self.tix.config.sandbox:
            return
        new_ca = self.tix.build_ticket_custom_attribute_value(self.testing_vars['ticket_ca']['Name'],
                                                              self.testing_vars['ticket_ca']['choice']['Name'])
        self.assertEqual(new_ca['ID'], self.testing_vars['ticket_ca']['ID'])
        self.assertEqual(new_ca['Value'], self.testing_vars['ticket_ca']['choice']['ID'])

    def test_change_custom_attribute_value(self):
        if not self.tix:
            self.setUp()
        if not self.tix.config.sandbox:
            return
        new_ca = self.tix.build_ticket_custom_attribute_value(self.testing_vars['ticket_ca']['Name'],
                                                              self.testing_vars['ticket_ca']['choice2']['Name'])
        a = self.tix.change_ticket_custom_attribute_value(self.testing_vars['ticket2']['ID'], [new_ca])
        new_ca = self.tix.build_ticket_custom_attribute_value(self.testing_vars['ticket_ca']['Name'],
                                                              self.testing_vars['ticket_ca']['choice']['Name'])
        a2 = self.tix.change_ticket_custom_attribute_value(self.testing_vars['ticket2']['ID'], [new_ca])
        found = False
        found2 = False
        for x in a.ticket_data['Attributes']:
            if x['Name'] == self.testing_vars['ticket_ca']['Name']:
                self.assertEqual(str(x['Value']), str(self.testing_vars['ticket_ca']['choice2']['ID']))
                found = True
        for x in a2.ticket_data['Attributes']:
            if x['Name'] == self.testing_vars['ticket_ca']['Name']:
                self.assertEqual(str(x['Value']), str(self.testing_vars['ticket_ca']['choice']['ID']))
                found2 = True
        self.assertTrue(found)
        self.assertTrue(found2)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TdxTicketTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)

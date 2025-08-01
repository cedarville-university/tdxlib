import unittest
import json
import time
from datetime import datetime as dt
from datetime import timedelta as td
from typing import Dict, Any, List, Optional
from functools import wraps
from tdxlib import tdx_ticket_integration
from tdxlib import tdx_utils
import os


class TdxTicketTesting(unittest.TestCase):
    """Test suite for TDX Ticket Integration functionality."""
    
    # Class constants
    MIN_TICKET_ID = 10000
    MIN_EXPECTED_TYPES = 40
    MIN_EXPECTED_STATUSES = 5
    MIN_EXPECTED_PRIORITIES = 4
    MIN_EXPECTED_URGENCIES = 3
    MIN_EXPECTED_IMPACTS = 5
    MIN_EXPECTED_SOURCES = 7
    
    tix: Optional[tdx_ticket_integration.TDXTicketIntegration] = None
    testing_vars: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    is_admin: bool = False
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test class with TDX integration and test variables."""
        cls.is_admin = False
        testing_vars_file = './ticket_testing_vars.json'
        cls.tix = tdx_ticket_integration.TDXTicketIntegration('../tdxlib.ini')
        right_now = dt.today()
        cls.timestamp = right_now.strftime("%d-%B-%Y %H:%M:%S")
        
        if os.path.isfile(testing_vars_file):
            with open(testing_vars_file, 'r') as f:
                cls.testing_vars = json.load(f)
        else:
            raise FileNotFoundError(
                'Testing variables need to be populated in file "testing_vars.json" '
                'in the working directory. A sample file is available in '
                'testing/sample_ticket_testing_vars. Any *.json files are ignored by git.'
            )
    
    def skip_if_not_sandbox(func):
        """Decorator to skip tests that require sandbox environment."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.tix.config.sandbox:
                self.skipTest("Test requires sandbox environment")
            return func(self, *args, **kwargs)
        return wrapper
    
    def skip_if_not_admin(func):
        """Decorator to skip tests that require admin privileges."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.is_admin:
                self.skipTest("Test requires admin privileges")
            return func(self, *args, **kwargs)
        return wrapper
    

    def test_authn(self) -> None:
        """Test that authentication token is properly configured."""
        self.assertGreater(
            len(self.tix.config.token), 200,
            "Authentication token should be longer than 200 characters"
        )

    def test_get_ticket_by_id(self) -> None:
        """Test retrieving a ticket by its ID."""
        ticket_id = self.testing_vars['ticket1']['ID']
        ticket = self.tix.get_ticket_by_id(ticket_id)
        self.assertIsNotNone(ticket, f"Should retrieve ticket with ID {ticket_id}")

    def test_search_tickets(self) -> None:
        """Test searching for tickets with a query string."""
        search_results = self.tix.search_tickets('test')
        self.assertIsNotNone(search_results, "Search should return results or empty list")

    # #### CHANGING TICKETS #### #

    @skip_if_not_sandbox
    def test_edit_tickets(self) -> None:
        """Test editing multiple tickets with the same changes."""
        ticket_list = [
            self.tix.get_ticket_by_id(self.testing_vars['ticket2']['ID']),
            self.tix.get_ticket_by_id(self.testing_vars['ticket3']['ID'])
        ]
        title_string = f"{self.timestamp} testing ticket"
        changes = {'Title': title_string}
        
        changed_tickets = self.tix.edit_tickets(ticket_list, changes, notify=False)
        
        self.assertTrue(all(changed_tickets), "All tickets should be successfully edited")
        for ticket in changed_tickets:
            self.assertEqual(
                ticket.get_attribute('Title'), changes['Title'],
                f"Ticket title should be updated to '{title_string}'"
            )

    # #### GETTING TICKET ATTRIBUTES #### #

    def test_get_all_ticket_types(self) -> None:
        """Test retrieving all available ticket types."""
        ticket_types = self.tix.get_all_ticket_types()
        self.assertGreaterEqual(
            len(ticket_types), self.MIN_EXPECTED_TYPES,
            f"Should retrieve at least {self.MIN_EXPECTED_TYPES} ticket types"
        )

    def test_get_ticket_type_by_id(self) -> None:
        """Test retrieving a ticket type by its ID."""
        ticket_type_id = self.testing_vars['ticket_type']['ID']
        ticket_type = self.tix.get_ticket_type_by_name_id(ticket_type_id)
        self.assertIsNotNone(ticket_type, f"Should retrieve ticket type with ID {ticket_type_id}")

    def test_get_ticket_type_by_name(self) -> None:
        """Test retrieving a ticket type by its name."""
        ticket_type_name = self.testing_vars['ticket_type']['Name']
        ticket_type = self.tix.get_ticket_type_by_name_id(ticket_type_name)
        self.assertIsNotNone(ticket_type, f"Should retrieve ticket type with name '{ticket_type_name}'")

    def test_get_all_ticket_statuses(self) -> None:
        """Test retrieving all available ticket statuses."""
        ticket_statuses = self.tix.get_all_ticket_statuses()
        self.assertGreaterEqual(
            len(ticket_statuses), self.MIN_EXPECTED_STATUSES,
            f"Should retrieve at least {self.MIN_EXPECTED_STATUSES} ticket statuses"
        )

    def test_get_ticket_status_by_id(self) -> None:
        """Test retrieving a ticket status by its ID."""
        status_id = self.testing_vars['ticket_status']['ID']
        status = self.tix.get_ticket_status_by_id(status_id)
        self.assertIsNotNone(status, f"Should retrieve ticket status with ID {status_id}")

    def test_get_ticket_status_by_name(self) -> None:
        """Test searching for a ticket status by its name."""
        status_name = self.testing_vars['ticket_status']['Name']
        status = self.tix.search_ticket_status(status_name)
        self.assertIsNotNone(status, f"Should find ticket status with name '{status_name}'")

    def test_get_default_not_closed_ticket_statuses(self) -> None:
        """Test retrieving default non-closed ticket statuses."""
        statuses = self.tix.get_default_not_closed_ticket_statuses()
        self.assertGreaterEqual(
            len(statuses), 1,
            "Should have at least one default non-closed status"
        )

    def test_get_default_closed_ticket_statuses(self) -> None:
        """Test retrieving default closed ticket statuses."""
        statuses = self.tix.get_default_closed_ticket_statuses()
        self.assertGreaterEqual(
            len(statuses), 1,
            "Should have at least one default closed status"
        )

    def test_get_default_cancelled_ticket_statuses(self) -> None:
        """Test retrieving default cancelled ticket statuses."""
        statuses = self.tix.get_default_cancelled_ticket_statuses()
        self.assertGreaterEqual(
            len(statuses), 1,
            "Should have at least one default cancelled status"
        )

    def test_get_all_ticket_priorities(self) -> None:
        """Test retrieving all available ticket priorities."""
        priorities = self.tix.get_all_ticket_priorities()
        self.assertGreaterEqual(
            len(priorities), self.MIN_EXPECTED_PRIORITIES,
            f"Should retrieve at least {self.MIN_EXPECTED_PRIORITIES} ticket priorities"
        )

    def test_get_ticket_priority_by_id(self) -> None:
        """Test retrieving a ticket priority by its ID."""
        priority_id = self.testing_vars['ticket_priority']['ID']
        priority = self.tix.get_ticket_priority_by_name_id(priority_id)
        self.assertIsNotNone(priority, f"Should retrieve ticket priority with ID {priority_id}")

    def test_get_ticket_priority_by_name(self) -> None:
        """Test retrieving a ticket priority by its name."""
        priority_name = self.testing_vars['ticket_priority']['Name']
        priority = self.tix.get_ticket_priority_by_name_id(priority_name)
        self.assertIsNotNone(priority, f"Should retrieve ticket priority with name '{priority_name}'")

    def test_get_ticket_classification_id_by_name(self) -> None:
        """Test retrieving a ticket classification ID by its name."""
        classification_name = self.testing_vars['ticket_classification']['Name']
        classification_id = self.tix.get_ticket_classification_id_by_name(classification_name)
        self.assertIsNotNone(
            classification_id, 
            f"Should retrieve classification ID for name '{classification_name}'"
        )

    def test_get_all_ticket_urgencies(self) -> None:
        """Test retrieving all available ticket urgencies."""
        urgencies = self.tix.get_all_ticket_urgencies()
        self.assertGreaterEqual(
            len(urgencies), self.MIN_EXPECTED_URGENCIES,
            f"Should retrieve at least {self.MIN_EXPECTED_URGENCIES} ticket urgencies"
        )

    def test_get_ticket_urgency_by_id(self) -> None:
        """Test retrieving a ticket urgency by its ID."""
        urgency_id = self.testing_vars['ticket_urgency']['ID']
        urgency = self.tix.get_ticket_urgency_by_name_id(urgency_id)
        self.assertIsNotNone(urgency, f"Should retrieve ticket urgency with ID {urgency_id}")

    def test_get_ticket_urgency_by_name(self) -> None:
        """Test retrieving a ticket urgency by its name."""
        urgency_name = self.testing_vars['ticket_urgency']['Name']
        urgency = self.tix.get_ticket_urgency_by_name_id(urgency_name)
        self.assertIsNotNone(urgency, f"Should retrieve ticket urgency with name '{urgency_name}'")

    def test_get_all_ticket_impacts(self) -> None:
        """Test retrieving all available ticket impacts."""
        impacts = self.tix.get_all_ticket_impacts()
        self.assertGreaterEqual(
            len(impacts), self.MIN_EXPECTED_IMPACTS,
            f"Should retrieve at least {self.MIN_EXPECTED_IMPACTS} ticket impacts"
        )

    def test_get_ticket_impact_by_id(self) -> None:
        """Test retrieving a ticket impact by its ID."""
        impact_id = self.testing_vars['ticket_impact']['ID']
        impact = self.tix.get_ticket_impact_by_name_id(impact_id)
        self.assertIsNotNone(impact, f"Should retrieve ticket impact with ID {impact_id}")

    def test_get_ticket_impact_by_name(self) -> None:
        """Test retrieving a ticket impact by its name."""
        impact_name = self.testing_vars['ticket_impact']['Name']
        impact = self.tix.get_ticket_impact_by_name_id(impact_name)
        self.assertIsNotNone(impact, f"Should retrieve ticket impact with name '{impact_name}'")

    def test_get_all_ticket_sources(self) -> None:
        """Test retrieving all available ticket sources."""
        sources = self.tix.get_all_ticket_sources()
        self.assertGreaterEqual(
            len(sources), self.MIN_EXPECTED_SOURCES,
            f"Should retrieve at least {self.MIN_EXPECTED_SOURCES} ticket sources"
        )

    def test_get_ticket_source_by_id(self) -> None:
        """Test retrieving a ticket source by its ID."""
        source_id = self.testing_vars['ticket_source']['ID']
        source = self.tix.get_ticket_source_by_name_id(source_id)
        self.assertIsNotNone(source, f"Should retrieve ticket source with ID {source_id}")

    def test_get_ticket_source_by_name(self) -> None:
        """Test retrieving a ticket source by its name."""
        source_name = self.testing_vars['ticket_source']['Name']
        source = self.tix.get_ticket_source_by_name_id(source_name)
        self.assertIsNotNone(source, f"Should retrieve ticket source with name '{source_name}'")

    @skip_if_not_sandbox
    def test_create_ticket(self) -> None:
        """Test creating a new ticket."""
        title_string = f"Testing Ticket Created {self.timestamp}"
        json_data = self.tix.generate_ticket(
            title_string,
            self.testing_vars['ticket_type']['Name'],
            self.testing_vars['account']['Name'],
            self.tix.config.username
        )
        created_ticket = self.tix.create_ticket(json_data)
        self.assertGreater(
            created_ticket.get_id(), self.MIN_TICKET_ID,
            f"Created ticket ID should be greater than {self.MIN_TICKET_ID}"
        )

    # #### TICKET TASKS #### #

    def test_get_all_tasks_by_ticket_id(self) -> None:
        """Test retrieving all tasks for a specific ticket."""
        ticket_id = self.testing_vars['ticket2']['ID']
        tasks = self.tix.get_all_tasks_by_ticket_id(ticket_id)
        self.assertIsNotNone(tasks, f"Should retrieve tasks for ticket ID {ticket_id}")

    def test_get_ticket_task_by_id(self) -> None:
        """Test retrieving a specific task by ticket and task ID."""
        ticket_id = self.testing_vars['ticket2']['ID']
        task_id = self.testing_vars['ticket2']['task']['ID']
        task = self.tix.get_ticket_task_by_id(ticket_id, task_id)
        self.assertIsNotNone(task, f"Should retrieve task {task_id} from ticket {ticket_id}")

    @skip_if_not_sandbox
    def test_create_ticket_task(self) -> None:
        """Test creating a new task for a ticket."""
        ticket_id = self.testing_vars['ticket2']['ID']
        task = {'Title': f"Test task at {dt.now()}"}
        created_task = self.tix.create_ticket_task(ticket_id, task)
        self.assertGreater(
            created_task['ID'], self.MIN_TICKET_ID,
            f"Created task ID should be greater than {self.MIN_TICKET_ID}"
        )

    @skip_if_not_sandbox
    def test_edit_ticket_task(self) -> None:
        """Test editing an existing ticket task."""
        ticket_id = self.testing_vars['ticket2']['ID']
        task_id = self.testing_vars['ticket2']['task']['ID']
        task = self.tix.get_ticket_task_by_id(ticket_id, task_id)
        
        changed_attributes = {'Description': f'This task was updated at {dt.now()}.'}
        edited_task = self.tix.edit_ticket_task(ticket_id, task, changed_attributes)
        
        self.assertIsNotNone(edited_task, "Task should be successfully edited")
        self.assertEqual(
            edited_task['Description'], changed_attributes['Description'],
            "Task description should be updated to match new value"
        )

    @skip_if_not_sandbox
    def test_delete_ticket_task(self) -> None:
        """Test creating and then deleting a ticket task."""
        ticket_id = self.testing_vars['ticket2']['ID']
        task = {'Title': f'Delete this task at {dt.now()}'}
        
        # Create the task
        created_task = self.tix.create_ticket_task(ticket_id, task)
        time.sleep(3)  # Wait for task creation to propagate
        
        # Delete the task
        self.tix.delete_ticket_task(ticket_id, created_task['ID'])
        
        # Verify the task is deleted
        task_list = self.tix.get_all_tasks_by_ticket_id(ticket_id)
        task_exists = any(t['ID'] == created_task['ID'] for t in task_list)
        self.assertFalse(task_exists, "Task should be deleted from ticket")

    @skip_if_not_sandbox
    def test_reassign_ticket_task(self) -> None:
        """Test reassigning a ticket task to a different person."""
        ticket_id = self.testing_vars['ticket2']['ID']
        task_id = self.testing_vars['ticket2']['task']['ID']
        task = self.tix.get_ticket_task_by_id(ticket_id, task_id)
        
        # Determine who to reassign to
        if task['ResponsibleUid'] == self.testing_vars['person1']['UID']:
            reassign_to = {'ResponsibleUid': self.testing_vars['person2']['UID']}
        else:
            reassign_to = {'ResponsibleUid': self.testing_vars['person1']['UID']}
        
        changed_task = self.tix.edit_ticket_task(ticket_id, task_id, reassign_to)
        self.assertEqual(
            changed_task['ResponsibleUid'], reassign_to['ResponsibleUid'],
            "Task should be reassigned to the specified person"
        )

    @skip_if_not_sandbox
    def test_reassign_ticket(self) -> None:
        """Test reassigning a ticket to a different person."""
        ticket_id = self.testing_vars['ticket2']['ID']
        ticket = self.tix.get_ticket_by_id(ticket_id)
        
        # Determine who to reassign to
        if ticket.get_attribute('ResponsibleUid') == self.testing_vars['person1']['UID']:
            reassign_to = self.testing_vars['person2']
        else:
            reassign_to = self.testing_vars['person1']
        
        changed_ticket = self.tix.reassign_ticket(ticket_id, reassign_to['PrimaryEmail'])
        self.assertEqual(
            changed_ticket.get_attribute('ResponsibleUid'), reassign_to['UID'],
            "Ticket should be reassigned to the specified person"
        )

    @skip_if_not_sandbox
    def test_reschedule_ticket(self) -> None:
        """Test rescheduling a ticket with new start and end dates."""
        ticket_id = self.testing_vars['ticket1']['ID']
        start = dt.utcnow()
        end = start + td(days=5)
        
        changed_ticket = self.tix.reschedule_ticket(ticket_id, start, end)
        self.assertEqual(
            changed_ticket.get_attribute('StartDate').day, start.day,
            "Ticket start date should match the rescheduled date"
        )

    @skip_if_not_sandbox
    def test_reschedule_ticket_task(self) -> None:
        """Test rescheduling a ticket task with new start and end dates."""
        ticket_id = self.testing_vars['ticket2']['ID']
        task_id = self.testing_vars['ticket2']['task']['ID']
        start = dt.utcnow()
        end = start + td(days=5)
        
        changed_ticket_task = self.tix.reschedule_ticket_task(ticket_id, task_id, start, end)
        expected_date = tdx_utils.export_tdx_date(start)[0:8]
        actual_date = changed_ticket_task['StartDate'][0:8]
        self.assertEqual(
            actual_date, expected_date,
            "Task start date should match the rescheduled date"
        )

    @skip_if_not_sandbox
    def test_generate_ticket_task(self) -> None:
        """Test generating a ticket task data structure."""
        task = self.tix.generate_ticket_task(
            "Testing Task", 
            description="this is a test",
            start=dt.utcnow(),
            responsible=self.testing_vars['person1']['FullName']
        )
        self.assertIsNotNone(task, "Should generate valid task data structure")

    @skip_if_not_admin
    @skip_if_not_sandbox
    def test_create_custom_ticket_status(self) -> None:
        """Test creating a custom ticket status (requires admin privileges)."""
        status = self.tix.create_custom_ticket_status('Never Gonna Happen', 1, 'Cancelled')
        retrieved_status = self.tix.get_ticket_status_by_id(status['ID'])
        self.assertIsNotNone(retrieved_status, "Should retrieve the created custom status")

    @skip_if_not_admin
    @skip_if_not_sandbox
    def test_edit_custom_ticket_status(self) -> None:
        """Test editing a custom ticket status (requires admin privileges)."""
        self.test_create_custom_ticket_status()
        to_change = {'Name': 'Never Gonna Give You Up'}
        changed = self.tix.edit_custom_ticket_status('Never Gonna Happen', to_change)
        self.assertEqual(
            changed['Name'], to_change['Name'],
            "Custom status name should be updated to new value"
        )

    @skip_if_not_sandbox
    def test_update_ticket_task(self) -> None:
        """Test updating a ticket task with progress and comments."""
        ticket_id = self.testing_vars['ticket2']['ID']
        task_id = self.testing_vars['ticket2']['task']['ID']
        update = self.tix.update_ticket_task(ticket_id, task_id, 99, comments='almost done')
        self.assertIsNotNone(update, "Task update should be successful")

    @skip_if_not_sandbox
    def test_update_ticket(self) -> None:
        """Test updating a ticket with comments and status change."""
        ticket_id = self.testing_vars['ticket1']['ID']
        update = self.tix.update_ticket(ticket_id, comments=str(self.timestamp), new_status='Open')
        self.assertIn(
            self.timestamp, update['Body'],
            "Update comments should be included in ticket body"
        )

    @skip_if_not_sandbox
    def test_upload_attachment(self) -> None:
        """Test uploading an attachment to a ticket."""
        ticket_id = self.testing_vars['ticket1']['ID']
        filename = self.testing_vars['attachment']['Name']
        
        with open(filename, "rb") as file:
            update = self.tix.upload_attachment(ticket_id, file)
        
        expected_name = filename.split('/')[-1]
        self.assertEqual(
            update['Name'], expected_name,
            f"Uploaded attachment name should be '{expected_name}'"
        )

    @skip_if_not_sandbox
    def test_upload_attachment_filename(self) -> None:
        """Test uploading an attachment with a custom filename."""
        ticket_id = self.testing_vars['ticket2']['ID']
        filepath = self.testing_vars['attachment']['Name']
        filename = filepath.split('/')[-1]
        
        with open(filepath, "rb") as file:
            update = self.tix.upload_attachment(ticket_id, file, filename)
        
        self.assertEqual(
            update['Name'], filename,
            f"Uploaded attachment should have custom filename '{filename}'"
        )

    def test_get_ticket_task_feed(self) -> None:
        """Test retrieving the activity feed for a ticket task."""
        ticket_id = self.testing_vars['ticket2']['ID']
        task_id = self.testing_vars['ticket2']['task']['ID']
        feed = self.tix.get_ticket_task_feed(ticket_id, task_id)
        self.assertGreater(
            len(feed), 0,
            "Task feed should contain at least one activity entry"
        )

    def test_get_ticket_feed(self) -> None:
        """Test retrieving the activity feed for a ticket."""
        ticket_id = self.testing_vars['ticket2']['ID']
        feed = self.tix.get_ticket_feed(ticket_id)
        self.assertGreater(
            len(feed), 0,
            "Ticket feed should contain at least one activity entry"
        )

    @skip_if_not_sandbox
    def test_build_custom_attribute_value(self) -> None:
        """Test building a custom attribute value structure."""
        ca_name = self.testing_vars['ticket_ca']['Name']
        choice_name = self.testing_vars['ticket_ca']['choice']['Name']
        
        new_ca = self.tix.build_ticket_custom_attribute_value(ca_name, choice_name)
        
        self.assertEqual(
            new_ca['ID'], self.testing_vars['ticket_ca']['ID'],
            "Custom attribute ID should match expected value"
        )
        self.assertEqual(
            new_ca['Value'], self.testing_vars['ticket_ca']['choice']['ID'],
            "Custom attribute value should match choice ID"
        )

    @skip_if_not_sandbox
    def test_change_custom_attribute_value(self) -> None:
        """Test changing a custom attribute value on a ticket."""
        ca_name = self.testing_vars['ticket_ca']['Name']
        ticket_id = self.testing_vars['ticket2']['ID']
        
        # Change to choice2
        new_ca_choice2 = self.tix.build_ticket_custom_attribute_value(
            ca_name, self.testing_vars['ticket_ca']['choice2']['Name']
        )
        updated_ticket = self.tix.change_ticket_custom_attribute_value(ticket_id, [new_ca_choice2])
        
        # Change back to choice1
        new_ca_choice1 = self.tix.build_ticket_custom_attribute_value(
            ca_name, self.testing_vars['ticket_ca']['choice']['Name']
        )
        updated_ticket2 = self.tix.change_ticket_custom_attribute_value(ticket_id, [new_ca_choice1])
        
        # Verify choice2 was set
        choice2_found = False
        for attr in updated_ticket.ticket_data['Attributes']:
            if attr['Name'] == ca_name:
                self.assertEqual(
                    str(attr['Value']), str(self.testing_vars['ticket_ca']['choice2']['ID']),
                    "Custom attribute should be set to choice2 value"
                )
                choice2_found = True
        
        # Verify choice1 was set back
        choice1_found = False
        for attr in updated_ticket2.ticket_data['Attributes']:
            if attr['Name'] == ca_name:
                self.assertEqual(
                    str(attr['Value']), str(self.testing_vars['ticket_ca']['choice']['ID']),
                    "Custom attribute should be reset to choice1 value"
                )
                choice1_found = True
        
        self.assertTrue(choice2_found, "Should find custom attribute with choice2 value")
        self.assertTrue(choice1_found, "Should find custom attribute with choice1 value")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TdxTicketTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)

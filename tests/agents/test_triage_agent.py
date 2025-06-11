import pytest
from unittest.mock import patch, ANY
from agents.triage_agent import EmailTriageTool, triage_email, triage_agent as actual_triage_agent
from crewai import Task

class TestEmailTriageTool:
    def test_run_urgent(self):
        assert EmailTriageTool()._run("This is an urgent email") == "Urgent & Important"

    def test_run_important(self):
        assert EmailTriageTool()._run("This is an important email") == "Important"

    def test_run_not_urgent(self):
        assert EmailTriageTool()._run("This is a regular email") == "Not Urgent"

class TestTriageAgent:
    @patch('agents.triage_agent.Task')
    def test_triage_email(self, mock_task_class):
        # Create a mock instance for the Task
        mock_task_instance = mock_task_class.return_value

        # Call the function to be tested
        triage_email("test content")

        # Assert that the Task constructor was called with the correct arguments
        # Assert that the Task constructor was called with the correct arguments
        mock_task_class.assert_called_once_with(
            description="Classify this email: test content",  # Corrected description
            expected_output="A label: 'Urgent & Important', 'Important', or 'Not Urgent'.",
            agent=ANY  # Use ANY to avoid recursion error with complex agent object
        )

        # Optionally, assert that the agent passed was the correct one
        args, kwargs = mock_task_class.call_args
        assert 'agent' in kwargs
        assert kwargs['agent'] is actual_triage_agent

        # Assert that the execute method of the mocked task instance was called
        mock_task_instance.execute.assert_called_once()

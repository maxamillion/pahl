import pytest
from unittest.mock import patch, ANY
from agents.summarization_agent import EmailSummarizationTool, summarize_email, summarization_agent as actual_summarization_agent
from crewai import Task

class TestEmailSummarizationTool:
    def test_run(self):
        tool = EmailSummarizationTool()
        # The actual _run method in summarization_agent.py has a placeholder.
        # We'll test that placeholder behavior. If it were a real summarization,
        # this test would be more complex or mock external calls.
        expected_output = {
            "summary": "Summarized: Test email content",
            "actions": ["Action 1", "Action 2"]
        }
        assert tool._run("Test email content") == expected_output

class TestSummarizationAgent:
    @patch('agents.summarization_agent.Task')
    def test_summarize_email(self, mock_task_class):
        # Create a mock instance for the Task
        mock_task_instance = mock_task_class.return_value

        # Call the function to be tested
        summarize_email("test content")

        # Assert that the Task constructor was called with the correct arguments
        mock_task_class.assert_called_once_with(
            description="Summarize the following email content: test content",
            expected_output="A JSON object with 'summary' and 'actions' keys. 'actions' should be a list of strings.",
            agent=ANY # Use ANY and then check instance if necessary, like in triage tests
        )

        # Check that the agent passed was the correct one
        args, kwargs = mock_task_class.call_args
        assert 'agent' in kwargs
        assert kwargs['agent'] is actual_summarization_agent

        # Assert that the execute method of the mocked task instance was called
        mock_task_instance.execute.assert_called_once()

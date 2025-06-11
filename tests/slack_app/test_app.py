import pytest
from flask import Flask, json
from unittest.mock import patch, MagicMock
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from agents.summarization_agent import summarize_email # This will be mocked
from slack_app.app import app # Import the app instance

@pytest.fixture
def test_client(): # Renamed fixture
    app.config['TESTING'] = True
    # For the /briefme command, SLACK_BOT_TOKEN is needed for WebClient.
    # Since we are mocking WebClient, we don't strictly need a real token for these tests.
    # However, if the app initialization itself required it, we might need to set it.
    # app.config['SLACK_BOT_TOKEN'] = "test_token"
    with app.test_client() as current_client: # Use different internal var name
        yield current_client

class TestBriefmeCommand:

    @patch('slack_app.app.summarize_email')
    @patch('slack_app.app.client') # Patch the global client instance
    def test_briefme_success(self, mock_slack_client_instance, mock_summarize_email, test_client): # Added test_client fixture
        # Setup mock client instance and its methods
        # mock_slack_client_instance is now the direct mock of the client used in app.py
        mock_slack_client_instance.chat_postMessage.return_value = {"ok": True, "ts": "12345.67890"}

        # Setup mock for summarize_email
        mock_summarize_email.side_effect = [
            {"summary": "Summary for email 1: Urgent project update", "actions": ["Follow up with Alice", "Review document"]},
            {"summary": "Summary for email 2: Team lunch invitation", "actions": ["RSVP by EOD"]}
        ]

        # Make a POST request to /briefme
        response = test_client.post('/briefme', data={ # Use renamed fixture
            'user_id': 'U123ABC',
            'channel_id': 'C456DEF',
            'text': '' # Assuming text is not used by /briefme for now
        })

        assert response.status_code == 200
        assert response.data.decode('utf-8') == "" # App returns empty string on success


        # Assert summarize_email was called twice (for two dummy emails)
        assert mock_summarize_email.call_count == 2
        mock_summarize_email.assert_any_call("Dummy email content 1")
        mock_summarize_email.assert_any_call("Dummy email content 2")


        # Assert chat_postMessage was called
        mock_slack_client_instance.chat_postMessage.assert_called_once()

        # Verify the structure and content of the blocks argument
        call_args = mock_slack_client_instance.chat_postMessage.call_args
        assert call_args is not None
        posted_blocks = call_args.kwargs.get('blocks')
        assert posted_blocks is not None

        # Basic structure check
        assert len(posted_blocks) == 3 # Intro section + 2 summary sections
        assert posted_blocks[0]['type'] == 'section' # Corrected from 'header'
        assert posted_blocks[0]['text']['text'] == "Here's a brief summary of your important emails:"

        # Check content for first email
        # The exact structure of summary blocks can be detailed. For now, check for key text.
        # First summary is at index 1, second at index 2
        summary1_text = json.dumps(posted_blocks[1])
        assert "Summary for email 1: Urgent project update" in summary1_text
        assert "Follow up with Alice" in summary1_text
        assert "Review document" in summary1_text

        # Check content for second email
        summary2_text = json.dumps(posted_blocks[2])
        assert "Summary for email 2: Team lunch invitation" in summary2_text
        assert "RSVP by EOD" in summary2_text

        # Check channel_id and user_id (if private message)
        # In the app, it posts to channel_id for now.
        assert call_args.kwargs.get('channel') == 'C456DEF'


    @patch('slack_app.app.summarize_email')
    @patch('slack_app.app.client') # Patch the global client instance
    def test_briefme_slack_api_error(self, mock_slack_client_instance, mock_summarize_email, test_client): # Added test_client fixture
        # Setup mock client instance to raise SlackApiError
        mock_slack_client_instance.chat_postMessage.side_effect = SlackApiError(
            message="API error",
            response={"ok": False, "error": "some_slack_error"} # SlackApiError expects a response dict
        )

        # Setup mock for summarize_email (it will be called, but the error happens after)
        mock_summarize_email.side_effect = [
            {"summary": "Summary 1", "actions": ["Action A"]},
            {"summary": "Summary 2", "actions": ["Action B"]}
        ]

        response = test_client.post('/briefme', data={ # Use renamed fixture
            'user_id': 'U123ABC',
            'channel_id': 'C456DEF',
            'text': ''
        })

        assert response.status_code == 500
        assert response.get_json() == {"error": "Error sending message"} # Use get_json()

        # Check that summarize_email was called
        assert mock_summarize_email.call_count == 2

        # Check that chat_postMessage was called (and raised an error)
        mock_slack_client_instance.chat_postMessage.assert_called_once()

# Removed test_briefme_slack_api_error_sends_user_notification as the app directly returns 500

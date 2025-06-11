import pytest
from flask import Flask, json
from unittest.mock import patch
from slack_sdk import WebClient # For type hinting if needed, not directly used due to mock
from slack_app.app import app # Import the app instance

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    # SLACK_BOT_TOKEN is used by the app.client instance.
    # Even though we mock app.client, if app initialization logic depended on it,
    # it might be an issue. Here, client is initialized globally, so we mock that instance.
    # app.config['SLACK_BOT_TOKEN'] = "test_token_for_integration" # Not strictly needed due to mock
    with app.test_client() as client_instance:
        yield client_instance

class TestBriefmeIntegration:

    @patch('litellm.completion') # Mocking the actual LLM call
    @patch('slack_app.app.client') # Mocking the Slack client instance
    def test_briefme_integration_success(self, mock_slack_client_instance, mock_litellm_completion, test_client):
        # Setup mock for the chat_postMessage method
        mock_slack_client_instance.chat_postMessage.return_value = {"ok": True, "ts": "12345.67890"}

        # Setup mock for litellm.completion
        # It needs to return a ModelResponse object, or something that can be processed into one.
        # The structure of ModelResponse can be complex. Let's find what the agent expects.
        # The agent's _parse_output method will handle the response.
        # For summarization, the agent should format the tool's dict output as a JSON string.

        # Simulate two calls for the two dummy emails
        # The actual content of the choices.message.content is what the agent's _parse_output receives.
        # This string should be a JSON representation of the summary.

        # First summary
        summary_content_1 = {
            "summary": "Summarized: Dummy email content 1", # This comes from EmailSummarizationTool
            "actions": ["Action 1", "Action 2"]
        }
        # The LLM is expected to format this as a JSON string.
        llm_response_string_1 = json.dumps(summary_content_1)

        # Second summary
        summary_content_2 = {
            "summary": "Summarized: Dummy email content 2",
            "actions": ["Action 1", "Action 2"]
        }
        llm_response_string_2 = json.dumps(summary_content_2)

        # Mocking structure based on litellm.ModelResponse and a typical OpenAI-like response
        # This is a simplified mock. A more accurate mock would create a proper ModelResponse object.
        # For now, let's assume the crewai Agent class can handle a dict that looks like part of ModelResponse.
        # Looking at crewai.agent.Agent._parse_output, it expects a string.
        # So, litellm.completion should ultimately result in this string being available.
        # LiteLLM's completion usually returns a ModelResponse object.
        # The relevant part is often ModelResponse.choices[0].message.content.

        # Let's construct mock ModelResponse objects
        from litellm.utils import ModelResponse, Choices, Message

        mock_model_response_1 = ModelResponse(
            id="mock_response_id_1",
            choices=[Choices(index=0, message=Message(content=llm_response_string_1, role="assistant"))],
            created=123,
            model="gpt-mock",
            usage={"total_tokens": 0, "prompt_tokens":0, "completion_tokens":0 }
        )
        mock_model_response_2 = ModelResponse(
            id="mock_response_id_2",
            choices=[Choices(index=0, message=Message(content=llm_response_string_2, role="assistant"))],
            created=124,
            model="gpt-mock",
            usage={"total_tokens": 0, "prompt_tokens":0, "completion_tokens":0 }
        )

        mock_litellm_completion.side_effect = [
            mock_model_response_1,
            mock_model_response_2
        ]

        # Make a POST request to /briefme
        response = test_client.post('/briefme', data={
            'user_id': 'U123INT',
            'channel_id': 'C456INT',
            'text': ''
        })

        # Assert the immediate HTTP response is successful
        assert response.status_code == 200
        assert response.data.decode('utf-8') == "" # App returns empty string on success

        # Assert that chat_postMessage was called (meaning the main flow completed)
        mock_slack_client_instance.chat_postMessage.assert_called_once()

        # Get the 'blocks' argument passed to chat_postMessage
        call_args = mock_slack_client_instance.chat_postMessage.call_args
        assert call_args is not None
        posted_blocks = call_args.kwargs.get('blocks')
        assert posted_blocks is not None

        # Verify the content of the blocks, focusing on agent's output
        # There's an intro block, then two summary blocks
        assert len(posted_blocks) == 3
        assert posted_blocks[0]['type'] == 'section'
        assert posted_blocks[0]['text']['text'] == "Here's a brief summary of your important emails:"

        # --- Check content for the first email (processed by actual summarize_email) ---
        summary1_block_text = posted_blocks[1]['text']['text']
        # Expected summary from EmailSummarizationTool._run("Dummy email content 1")
        assert "*Summary:* Summarized: Dummy email content 1" in summary1_block_text
        # Expected actions from EmailSummarizationTool._run
        assert "*Actions:* Action 1, Action 2" in summary1_block_text
        assert "*From:* Test Sender" in summary1_block_text # Static text from app
        assert "*Subject:* Test Subject" in summary1_block_text # Static text from app

        # --- Check content for the second email (processed by actual summarize_email) ---
        summary2_block_text = posted_blocks[2]['text']['text']
        # Expected summary from EmailSummarizationTool._run("Dummy email content 2")
        assert "*Summary:* Summarized: Dummy email content 2" in summary2_block_text
        # Expected actions from EmailSummarizationTool._run
        assert "*Actions:* Action 1, Action 2" in summary2_block_text
        assert "*From:* Test Sender" in summary2_block_text # Static text from app
        assert "*Subject:* Test Subject" in summary2_block_text # Static text from app

        # Check that the correct channel was used
        assert call_args.kwargs.get('channel') == 'C456INT'

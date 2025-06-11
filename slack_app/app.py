import os
import json
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from agents.summarization_agent import summarize_email

app = Flask(__name__)

# Slack API credentials
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")  # Replace with your actual token
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET") # Replace with your signing secret

# Initialize Slack client
client = WebClient(token=SLACK_BOT_TOKEN)

@app.route('/briefme', methods=['POST'])
def briefme_command():
    # Verify the request signature
    # if not verify_slack_signature(request):
    #     return jsonify({"error": "Invalid request signature"}), 400

    # Get the user ID from the request
    user_id = request.form.get("user_id")
    channel_id = request.form.get("channel_id")

    # Get a list of important emails (replace with your actual logic)
    important_emails = [
        {"id": "123", "content": "Dummy email content 1"},
        {"id": "456", "content": "Dummy email content 2"},
    ]

    # Prepare the response message
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Here's a brief summary of your important emails:"
            }
        }
    ]

    for email in important_emails:
        summary = summarize_email(email["content"])
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"""*From:* Test Sender
*Subject:* Test Subject
*Summary:* {summary['summary']}
*Actions:* {', '.join(summary['actions'])}"""
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Details & Reply",
                        "emoji": True
                    },
                    "value": email["id"]
                }
            }
        )

    try:
        # Call the Slack API to send the message
        result = client.chat_postMessage(
            channel=channel_id,
            blocks=blocks
        )
        return "", 200

    except SlackApiError as e:
        print(f"Error sending message: {e}")
        return jsonify({"error": "Error sending message"}), 500

# def verify_slack_signature(request):
#     # TODO: Implement signature verification
#     return True

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8081)))
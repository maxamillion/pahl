import os
import json
from flask import Flask, request, redirect, url_for
from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import firebase_admin
from firebase_admin import credentials as firebase_credentials
from firebase_admin import firestore

app = Flask(__name__)

# Firebase setup
cred = firebase_credentials.ApplicationDefault()
firebase_admin.initialize_app(cred)
db = firestore.client()

# Gmail API credentials
CLIENT_SECRET_FILE = 'credentials.json'  # Replace with your actual credentials file
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_flow():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True))
    return flow

@app.route('/login')
def login():
    flow = get_flow()
    auth_url, state = flow.authorization_url(access_type='offline', prompt='consent')
    return redirect(auth_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = request.args.get('state')
    flow = get_flow()
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials

    # Store credentials in Firestore (replace 'user_id' with a unique identifier)
    user_id = 'test_user'  # Replace with actual user ID
    doc_ref = db.collection('users').document(user_id)
    doc_ref.set({
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    })

    return 'Credentials stored successfully!'

@app.route('/cloudscheduler')
def cloudscheduler():
    # Retrieve credentials from Firestore
    user_id = 'test_user'  # Replace with actual user ID
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        creds_data = doc.to_dict()
        creds = credentials.Credentials(
            creds_data['token'],
            refresh_token=creds_data['refresh_token'],
            token_uri=creds_data['token_uri'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            scopes=creds_data['scopes']
        )

        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])

        if not messages:
            return 'No messages found.'
        else:
            # Store message IDs in Firestore
            for message in messages:
                message_id = message['id']
                message_ref = db.collection('messages').document(message_id)
                message_ref.set({
                    'user_id': user_id,
                    'message_id': message_id
                })
            return 'Message IDs stored successfully!'
    else:
        return 'No credentials found for user.'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
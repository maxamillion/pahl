# pahl
Productivity Agent Helper Library 
<<<<<<< HEAD
=======

# AI Email Assistant Deployment Guide

This guide provides instructions on how to deploy the AI Email Assistant to Google Cloud and integrate it with Slack.

## Prerequisites

*   A Google Cloud account with billing enabled.
*   The Google Cloud SDK (gcloud CLI) installed and configured.
*   A Slack workspace where you have permissions to create and manage apps.
*   Basic knowledge of command-line operations and environment variables.

## I. Google Cloud Setup

1.  **Create a Google Cloud Project:**
    *   If you don't already have one, create a new Google Cloud project in the Google Cloud Console (<https://console.cloud.google.com/>).
    *   Note the Project ID; you'll need it in subsequent steps.

2.  **Enable APIs:**
    *   Enable the following APIs for your project:
        *   Gmail API
        *   Cloud Functions API
        *   Cloud Build API
        *   Firestore API
        *   Cloud Scheduler API
    *   You can enable these APIs in the Google Cloud Console by searching for them and clicking "Enable."

3.  **Create a Service Account:**
    *   Create a service account in the Google Cloud Console (IAM & Admin > Service Accounts).
    *   Grant the service account the following roles:
        *   Cloud Functions Invoker
        *   Cloud Datastore User
        *   Gmail API
        *   Cloud Scheduler Admin
    *   Download the service account key as a JSON file. Store this file securely. This file will be used as your Firebase credentials.

4.  **Configure Firebase:**
    *   Initialize Firebase for your Google Cloud project:

    *   ```bash
        firebase init
        ```
        *   Select "Firestore" and select the Google Cloud Project.

## II. Slack App Setup

1.  **Create a Slack App:**
    *   Go to the Slack API console (<https://api.slack.com/apps>).
    *   Create a new app.
    *   Note the Client ID, Client Secret, and Signing Secret; you'll need them in subsequent steps.

2.  **Configure OAuth & Permissions:**
    *   In your Slack App settings, go to "OAuth & Permissions."
    *   Add the following OAuth scopes:
        *   `channels:read`
        *   `chat:write`
        *   `commands`
        *   `users:read` (optional, if you need to access user information)
    *   Add a Redirect URI, to the `oauth2callback` of your deployed google cloud app. For example: `https://your-cloud-function.com/oauth2callback`

3.  **Configure Slash Command:**
    *   In your Slack App settings, go to "Slash Commands."
    *   Create a new slash command:
        *   **Command:** `/briefme`
        *   **Request URL:**  (This will be the URL of your deployed `slack_app` Cloud Function)
        *   **Description:** Get a brief summary of your important emails.

4.  **Enable Interactive Components:**
    *   In your Slack App settings, go to "Interactive Components."
    *   Enable interactive components and set the Request URL to the same URL as your slash command (the `slack_app` Cloud Function URL).

## III. Code Deployment

1.  **Deploy Google Cloud Functions:**

*   The files in the `google_cloud` and `slack_app` folders need to be deployed as Google Cloud functions.
*   Navigate to the root of the project on your local machine.
*   Before deploying functions, it is best practice to create unique virtual environments for each function to better manage dependencies

*   Deploy the `google_cloud` function. Replace the variables between <> to match your environment

```bash
cd google_cloud
gcloud functions deploy <YOUR_GCLOUD_FUNCTION_NAME_GOOGLE_CLOUD> \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --region <YOUR_GCLOUD_REGION> \
  --service-account=<YOUR_SERVICE_ACCOUNT_EMAIL>
```

*   Deploy the `slack_app` function. Replace the variables between <> to match your environment

```bash
cd slack_app
gcloud functions deploy <YOUR_GCLOUD_FUNCTION_NAME_SLACK_APP> \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --region <YOUR_GCLOUD_REGION> \
  --service-account=<YOUR_SERVICE_ACCOUNT_EMAIL> \
  --set-env-vars SLACK_BOT_TOKEN=<YOUR_SLACK_BOT_TOKEN>,SLACK_SIGNING_SECRET=<YOUR_SLACK_SIGNING_SECRET>
```

2.  **Set Environment Variables**
    *   In the Google Cloud Console, for both cloud functions (the Gmail interaction and the Slack bot interaction), set the appropriate environment variables:

    *   For the `google_cloud` function:
        *   No environment variables are needed unless you don't want to use firebase.

    *   For the `slack_app` function:
        *   `SLACK_BOT_TOKEN`: Your Slack bot token (xoxb-...).
        *   `SLACK_SIGNING_SECRET`: Your Slack signing secret.

3.  **OAuth Setup for Gmail API**

*   In the Google Cloud console, under "APIs & Services", find "Credentials".
*   Create an OAuth 2.0 Client ID. Configure the consent screen by providing a name for your app. You'll need to set the authorized Javascript origins and redirect URIs. The redirect URI will be the URL for your `google_cloud` cloud function endpoint `/oauth2callback`.

## IV. Final Configuration

1.  **Firestore Rules:**
    *   Configure Firestore rules to secure your data. At a minimum, you should:
        *   Restrict access to the `users` collection to authenticated users only.
        *   Prevent unauthorized access to email content.
    *   Sample Firestore rules (adjust as needed):

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /messages/{messageId} {
      allow read: if request.auth != null;
      allow write: if false;
    }
  }
}
```

2.  **Testing**

*   Access the `/login` URL of your `google_cloud` Cloud Function in a browser. This will initiate the Gmail OAuth flow and store credentials in Firestore.
*   In your Slack workspace, type `/briefme`. The bot should respond with a summary of your emails.

## V. Troubleshooting

*   **Permissions Issues:** Double-check that the service account has the necessary roles and that the Slack App has the correct OAuth scopes.
*   **Code Errors:** Review the Cloud Functions logs for any errors or exceptions.
*   **OAuth Errors:** Ensure that your OAuth client ID and secret are configured correctly and that the redirect URI is accurate.
*   **Slack App Errors:** Check the Slack API console for any errors related to your app.

## Important Considerations

*   **Security:** This deployment guide provides a basic setup. For production environments, you should implement more robust security measures, such as:
    *   Regularly rotating service account keys.
    *   Using a more secure method of storing credentials (e.g., Google Cloud Secret Manager).
    *   Implementing robust input validation to prevent security vulnerabilities.
*   **Cost:** Be aware of the costs associated with using Google Cloud Functions, Firestore, and other Google Cloud services.
*   **Scalability:** Google Cloud Functions can scale automatically to handle increased traffic. However, you should monitor your application's performance and adjust resources as needed.
>>>>>>> b0c07b6 (Initial commit using Goose with Gemini)

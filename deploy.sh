#!/bin/bash

# Install gcloud CLI (if not already installed)
# curl -sSL https://sdk.cloud.google.com | bash

# Authenticate with Google Cloud
# gcloud auth login

# Set the project ID
# gcloud config set project YOUR_PROJECT_ID

# Deploy the Cloud Function
cd google_cloud
gcloud functions deploy email_assistant \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --region us-central1

# Deploy the Slack App (assuming it's also a Cloud Function)
# cd ../slack_app
# gcloud functions deploy slack_app \
#   --runtime python39 \
#   --trigger-http \
#   --allow-unauthenticated \
#   --region us-central1
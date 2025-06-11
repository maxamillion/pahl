# Project: AI Email Assistant for Executive Productivity

## 1. Executive Summary

This document outlines a plan to develop an AI-powered agent system to manage the Gmail inbox of a Distinguished Engineer. The primary goal is to drastically reduce time spent on email by automating the process of identifying important messages, summarizing their content, highlighting action items, and drafting replies. The user will interact with this system through a conversational Slack bot, providing a seamless and efficient interface that integrates directly into their existing workflow.

The system will be built on a modern, secure, and scalable serverless architecture, prioritizing data privacy and reliability.

---

## 2. System Architecture

We will build a system composed of several interoperating microservices and a "team" of specialized AI agents. This decoupled architecture ensures scalability, maintainability, and the ability to upgrade individual components without affecting the entire system.

### Core Components:

* **Slack Bot (The Interface):** This is the user-facing component. It will be a Slack App that provides slash commands (e.g., `/briefme`, `/show <email_id>`), interactive buttons ("Send Reply," "Edit," "Archive"), and modals for editing draft replies.

* **Agent Core Logic (The Backend):** A serverless application (e.g., Google Cloud Run or AWS Lambda) that serves as the central hub. It will host the API endpoints that the Slack bot interacts with and will orchestrate the work of the AI agents.

* **AI Agent "Team" (The Brains):** This is not a single model but a series of focused prompts and logic flows directed at a powerful Large Language Model (like Gemini). Each agent has a specific responsibility:

    * **Triage Agent:**
        * **Job:** Periodically scans the inbox for new, unread emails.
        * **Task:** Performs a rapid classification on each email: `Urgent & Important`, `Important, Not Urgent`, `Newsletter/FYI`, `Spam/Notification`. It also extracts the primary sender and subject.
        * **Output:** Creates a preliminary record in our database with its classification.

    * **Summarization & Action-Item Agent:**
        * **Job:** Processes emails marked as `Important`.
        * **Task:** Generates a concise, one-sentence summary. It then performs a second pass to extract explicit and implicit action items or questions directed at the user.
        * **Output:** A structured object containing the summary and a list of action items (e.g., `{ summary: "...", actions: ["Review the Q3 architecture doc", "Approve the budget request"] }`).

    * **Drafting Agent:**
        * **Job:** Activated when the user requests to reply to an email.
        * **Task:** Analyzes the original email's content, the summary, and the extracted action items to generate a relevant, professional reply. The agent's prompt will be engineered to adopt a tone appropriate for an executive.
        * **Output:** A complete, ready-to-send draft email.

* **Secure Data Store (The Memory):** A Firestore database will be used to maintain the state of the system.
    * **What it stores:**
        * Securely encrypted Google OAuth tokens for the user.
        * A record for each processed email: its ID, classification, summary, action items, and current status (e.g., `briefed`, `reply_sent`).
        * User preferences (e.g., tone of voice for drafts).

* **Google Services Integration:**
    * **Gmail API:** Securely connects to the user's inbox using OAuth 2.0 to read emails, send replies, and apply labels/archive messages.
    * **Google Cloud Scheduler:** A cron job service that triggers the **Triage Agent** to scan the inbox on a regular schedule (e.g., every 5 minutes).

---

## 3. User Workflow

1.  **Onboarding (One-time):** The user adds the Slack bot to their workspace and, through a secure link, is directed to a Google OAuth consent screen to grant the application permission to access their Gmail.
2.  **Background Processing (Continuous):** The Cloud Scheduler triggers the **Triage Agent**. It scans for new mail, classifies it, and updates the Firestore database. Important emails are then picked up by the **Summarization Agent**.
3.  **User Interaction (On-Demand):**
    * The user types `/briefme` in Slack.
    * The Slack bot calls the **Agent Core**.
    * The Core queries Firestore for all emails marked as important that the user hasn't been briefed on yet.
    * It formats this into a clean, scannable list in Slack, with buttons for each item: `Details & Reply` and `Archive`.
    * The user clicks `Details & Reply` for a specific email.
    * The Core retrieves the full summary and action items from Firestore and calls the **Drafting Agent** to generate a reply.
    * A new, detailed message appears in Slack showing:
        * **From:** Sender
        * **Subject:** Subject
        * **Summary:** AI-generated summary.
        * **Action Items:** List of tasks/questions.
        * **Suggested Reply:** The AI-generated draft.
        * **Buttons:** `Send`, `Edit & Send`, `Archive`.
4.  **Taking Action:**
    * **Send:** The Core uses the Gmail API to send the drafted reply immediately.
    * **Edit & Send:** A Slack modal (popup) appears with the draft in a text box. The user edits the text, clicks "Submit," and the Core sends the updated version.
    * **Archive:** The email is marked as read and archived in Gmail.

---

## 4. Implementation Phases

We will develop this system in logical, iterative phases to deliver value quickly and ensure each component is robust before building the next.

### Phase 1: Core Infrastructure & Read-Only MVP

* **Goals:** Establish secure connections and provide initial value.
* **Tasks:**
    1.  Set up Google Cloud and Slack App projects.
    2.  Implement the secure OAuth 2.0 flow for Gmail authentication.
    3.  Build the **Triage** and **Summarization** agents.
    4.  Develop the Cloud Scheduler trigger.
    5.  Implement the `/briefme` command in Slack to display summaries.
* **Outcome:** A working bot that can brief the user on their important emails, without reply functionality.

### Phase 2: Interactive Reply & Action

* **Goals:** Enable the full email management loop.
* **Tasks:**
    1.  Develop the **Drafting Agent**.
    2.  Implement the `Details & Reply` flow.
    3.  Build the "Send," "Edit & Send" (with modal), and "Archive" button functionality.
    4.  Request and handle `gmail.modify` scope for sending and archiving.
* **Outcome:** The user can be briefed *and* can clear their inbox directly from Slack.

### Phase 3: Intelligence & Personalization

* **Goals:** Make the agent smarter and more tailored to the user.
* **Tasks:**
    1.  **Fine-tuning Tone:** Create a system where the user can provide feedback on drafts ("too formal," "more concise"), which is used to refine the prompt for the **Drafting Agent**.
    2.  **Calendar Awareness:** Integrate with Google Calendar API to allow the drafting agent to reference the user's availability when suggesting replies for meeting requests.
    3.  **Contact Importance:** Develop a simple model to weigh email importance based on the sender (e.g., messages from direct reports or leadership are always important).

---

## 5. Security & Data Privacy

This is the highest priority.

* **Authentication:** All access is handled via industry-standard OAuth 2.0. We will never store the user's password.
* **Data Storage:** All sensitive data, particularly OAuth tokens, will be encrypted at rest in Firestore.
* **Principle of Least Privilege:** We will only request the Gmail API permissions absolutely necessary for each phase (e.g., starting with `gmail.readonly`).
* **Data Handling:** Email content is passed to the AI model for processing but is not stored long-term in our logs or used for any purpose other than serving the user's requests. Firestore will only store the metadata, summaries, and action items, not the full email bodies.

---

## 6. Next Steps

1.  Review and confirm this project plan.
2.  Provision the initial Google Cloud and Slack application shells.
3.  Begin development of **Phase 1**.

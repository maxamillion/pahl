from crewai import Agent, Task, Crew
from crewai import Tool

class EmailTriageTool(Tool):
    description = "A tool for classifying the importance and urgency of an email."

    def __init__(self):
        super().__init__(name="Email Triage Tool")

    def _run(self, email_content):
        # Replace with your actual email triage logic
        if "urgent" in email_content.lower():
            return "Urgent & Important"
        elif "important" in email_content.lower():
            return "Important"
        else:
            return "Not Urgent"

triage_agent = Agent(
    role='Executive Email Triage Specialist',
    goal='Efficiently classify incoming emails based on their urgency and importance to enable the executive to focus on critical items. The classification must be accurate and consistent, ensuring that high-priority emails are immediately flagged while low-priority emails are filtered out.',
    backstory='You are a highly organized and detail-oriented email triage specialist with a deep understanding of executive priorities. You have a proven track record of accurately classifying emails, filtering out irrelevant information, and ensuring that urgent matters are promptly addressed. Your expertise allows executives to manage their inbox efficiently and focus on their most important tasks.',
    verbose=True,
    tools=[EmailTriageTool()]
)

def triage_email(email_content):
    task = Task(description=f"Classify this email: {email_content}", agent=triage_agent)
    return task.execute()
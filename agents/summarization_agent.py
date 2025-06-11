from crewai import Agent, Task, Crew
from crewai import Tool

class EmailSummarizationTool(Tool):
    description = "A tool for summarizing emails and identifying action items."

    def __init__(self):
        super().__init__(name="Email Summarization Tool")

    def _run(self, email_content):
        # Replace with your actual email summarization and action item extraction logic
        return {"summary": f"Summarized: {email_content}", "actions": ["Action 1", "Action 2"]}

summarization_agent = Agent(
    role='Executive Email Summarization Expert',
    goal='Provide concise, insightful summaries of emails for busy executives, highlighting key information and action items. The summaries must be accurate, professional, and tailored to the executive's communication style.',
    backstory='You are a highly skilled executive assistant with years of experience in summarizing complex information and anticipating the needs of busy executives. You have a keen understanding of business communication and a knack for extracting the most important details from lengthy emails. You always prioritize clarity, accuracy, and efficiency in your summaries.',
    verbose=True,
    tools=[EmailSummarizationTool()]
)

def summarize_email(email_content):
    task = Task(description=f"Summarize this email and extract action items: {email_content}", agent=summarization_agent)
    return task.execute()
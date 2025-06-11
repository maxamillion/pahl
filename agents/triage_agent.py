from crewai import Agent, Task, Crew
from crewai.tools.base_tool import Tool

from typing import Callable

class EmailTriageTool(Tool):
    def __init__(self):
        super().__init__(
            name="Email Triage Tool",
            description="A tool for classifying the importance and urgency of an email.",
            func=self._run
        )
        # The 'func' attribute is already set by the super().__init__ call
        # if 'Tool' class handles it, or it needs to be set if super is BaseTool
        # and Tool's __init__ is not called.
        # Given Tool(BaseTool) structure, func is a field in Tool.
        # Let's ensure it's set if not by super.
        # However, looking at BaseTool, Tool class takes 'func' as an argument.
        # The super call should correctly pass it to the Tool's model fields.

    def _run(self, email_content: str) -> str:
        # Replace with your actual email triage logic
        if "urgent" in email_content.lower():
            return "Urgent & Important"
        elif "important" in email_content.lower():
            return "Important"
        else:
            return "Not Urgent"

# Instantiate the tool separately
email_triage_tool_instance = EmailTriageTool()

triage_agent = Agent(
    role='Executive Email Triage Specialist',
    goal='Efficiently classify incoming emails based on their urgency and importance to enable the executive to focus on critical items. The classification must be accurate and consistent, ensuring that high-priority emails are immediately flagged while low-priority emails are filtered out.',
    backstory='You are a highly organized and detail-oriented email triage specialist with a deep understanding of executive priorities. You have a proven track record of accurately classifying emails, filtering out irrelevant information, and ensuring that urgent matters are promptly addressed. Your expertise allows executives to manage their inbox efficiently and focus on their most important tasks.',
    verbose=True,
    tools=[email_triage_tool_instance]
)

def triage_email(email_content: str) -> str:
    task = Task(
        description=f"Classify this email: {email_content}",
        agent=triage_agent,
        expected_output="A label: 'Urgent & Important', 'Important', or 'Not Urgent'."
    )
    # execute_sync returns a TaskOutput object. The .raw attribute should contain the string.
    output = task.execute_sync()
    return output.raw if hasattr(output, 'raw') else str(output)
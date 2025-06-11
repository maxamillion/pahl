import json
from crewai import Agent, Task, Crew
from crewai.tools.base_tool import Tool
from typing import Dict, List, Union

class EmailSummarizationTool(Tool):
    def __init__(self):
        super().__init__(
            name="Email Summarization Tool",
            description="A tool for summarizing emails and identifying action items.",
            func=self._run
        )

    def _run(self, email_content: str) -> Dict[str, Union[str, List[str]]]:
        # Replace with your actual email summarization and action item extraction logic
        return {"summary": f"Summarized: {email_content}", "actions": ["Action 1", "Action 2"]}

email_summarization_tool_instance = EmailSummarizationTool()

summarization_agent = Agent(
    role='Executive Email Summarization Expert',
    goal='''Provide concise, insightful summaries of emails for busy executives,
highlighting key information and action items. The summaries must be accurate,
professional, and tailored to the executive's communication style.''',
    backstory='''You are a highly skilled executive assistant with years of experience
in summarizing complex information and anticipating the needs of busy executives.
You have a keen understanding of business communication and a knack for
extracting the most important details from lengthy emails. You always prioritize
clarity, accuracy, and efficiency in your summaries.''',
    verbose=True,
    tools=[email_summarization_tool_instance]
)

def summarize_email(email_content: str) -> Dict[str, Union[str, List[str]]]:
    task = Task(
        description=f"Summarize the following email content: {email_content}",
        expected_output="A JSON object with 'summary' and 'actions' keys. 'actions' should be a list of strings.",
        agent=summarization_agent
    )
    # Assuming the raw output of the task is the dictionary we need.
    # If a TaskOutput object is returned, we might need to access an attribute like .raw or .result
    raw_output = task.execute_sync()
    # The EmailSummarizationTool._run returns a dict. The agent should pass this through.
    # If raw_output is a TaskOutput object, its .raw attribute should be the dict.
    if hasattr(raw_output, 'raw') and isinstance(raw_output.raw, dict):
        return raw_output.raw
    elif isinstance(raw_output, dict): # If execute_sync somehow returns the dict directly
        return raw_output
    # Fallback or error handling if the structure isn't as expected
    # For now, let's assume it's TaskOutput and its .raw is the dict.
    # The actual tool returns a dict, agent.execute_task should return string,
    # TaskOutput then wraps this.
    # The summarize_email function is type hinted to return Dict.
    # The EmailSummarizationTool._run method returns a dict.
    # The agent's LLM would typically convert this dict to a string.
    # Then TaskOutput.raw would be that string.
    # This needs careful checking of how CrewAI handles structured output from tools.
    # For now, let's assume the agent is expected to produce a string representation
    # of the JSON, and we need to parse it.
    # The 'expected_output' for the task is "A JSON object..."
    # This implies the agent's final output (TaskOutput.raw) will be a string that is a JSON object.

    # Given the tool returns a dict, and the agent is instructed for JSON output,
    # let's assume task.execute_sync().raw is a JSON string.
    output_str = raw_output.raw if hasattr(raw_output, 'raw') else str(raw_output)
    try:
        return json.loads(output_str)
    except json.JSONDecodeError:
        # Handle cases where the output isn't a valid JSON string
        # This might indicate a problem with the agent's output or assumptions
        print(f"Warning: Output from summarization task was not valid JSON: {output_str}")
        # Fallback to returning a dict with an error or the raw string in summary
        return {"summary": f"Error parsing summary: {output_str}", "actions": []}
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ToolRetryMiddleware,
    TodoListMiddleware,
    SummarizationMiddleware,
)
from langchain.agents.structured_output import ToolStrategy
from langchain_community.tools.gmail.search import GmailSearch
from langchain_community.tools.gmail.get_message import GmailGetMessage

from .delete import GmailDelete
from .models import get_gemini_chat
from .prompts import SYSTEM_PROMPT
from pydantic import BaseModel, Field
from typing import Optional, List


class GmailAgentResponse(BaseModel):
    """Structured output from Gmail Swarm Agent."""

    message: str = Field(
        ..., description="Cleaned natural language response from the agent."
    )
    deleted_subjects: Optional[List[str]] = Field(
        default=None, description="Subject lines of the emails that were deleted."
    )
    tool_name: Optional[str] = Field(
        None, description="If any tool was called, name of the tool used."
    )
    error_type: Optional[str] = Field(
        None, description="If any error occurred, type of error (e.g. HttpError)."
    )
    error_message: Optional[str] = Field(
        None, description="Detailed error message or diagnostic string."
    )
    success: bool = Field(
        True, description="Whether the operation completed successfully."
    )


def build_swarm():
    model = get_gemini_chat()

    tools = [
        GmailSearch(),
        GmailGetMessage(),
        GmailDelete(),
    ]

    agent = create_agent(
        model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        response_format=ToolStrategy(GmailAgentResponse),
        middleware=[
            ToolRetryMiddleware(
                max_retries=3,
                backoff_factor=2.0,
                initial_delay=1.0,
                max_delay=60.0,
                jitter=True,
            ),
            TodoListMiddleware(),
            SummarizationMiddleware(
                model=model,  # smaller summarizer model
                max_tokens_before_summary=400000,  # when to summarize
                messages_to_keep=200,  # keep latest conversation intact
                summary_prompt=(
                    "Summarize the conversation so far focusing on Gmail inbox triage decisions, "
                    "including which mails were deleted, kept, and why. "
                    "Maintain important context for future decisions."
                ),
            ),
        ],
    )

    return agent

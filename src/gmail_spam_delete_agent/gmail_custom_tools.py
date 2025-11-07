from typing import Annotated, List
import os
import sys

from googleapiclient.discovery import build
from langchain_core.tools import tool

from gmail_auth import ensure_gmail_token


def _gmail_service():
	creds = ensure_gmail_token()
	return build("gmail", "v1", credentials=creds)


def _flags():
	return {
		"DRY_RUN": os.getenv("DRY_RUN", "0") == "1",
		"VERBOSE": os.getenv("VERBOSE", "0") == "1" or os.getenv("DEBUG", "0") == "1",
		"DEBUG": os.getenv("DEBUG", "0") == "1",
	}


@tool
def gmail_delete(
    message_ids: Annotated[List[str], "List of Gmail message ids to permanently delete"],
) -> str:
    """Permanently DELETE a list of Gmail messages by message_id (bypasses Trash)"""
    flags = _flags()
    if flags["VERBOSE"]:
        print(f"[Deleter] delete ids={message_ids} dry_run={flags['DRY_RUN']}", file=sys.stderr)
    if flags["DRY_RUN"]:
        return f"dry_run:deleted:{','.join(message_ids)}"
    service = _gmail_service()
    for message_id in message_ids:
        service.users().messages().delete(userId="me", id=message_id).execute()
    return f"deleted:{','.join(message_ids)}"

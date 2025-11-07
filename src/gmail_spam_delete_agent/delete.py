import time
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_google_community.gmail.base import GmailBaseTool


class DeleteArgsSchema(BaseModel):
    """Input schema for GmailDelete tool."""

    message_ids: Optional[List[str]] = Field(
        default=None,
        description="List of Gmail message IDs to delete directly."
    )
    query: Optional[str] = Field(
        default=None,
        description=(
            "Gmail search query to find messages to delete. "
            "Example: 'from:promotions older_than:30d'"
        )
    )
    dry_run: bool = Field(
        default=False,
        description="If True, simulate deletions without actually removing messages."
    )
    max_results: int = Field(
        default=20,
        description="Maximum number of messages to delete when using query search."
    )


class GmailDelete(GmailBaseTool):
    """Tool that deletes Gmail messages based on ID or query."""

    name: str = "delete_gmail"
    description: str = (
        "Deletes Gmail messages by ID or using a Gmail search query. "
        "Supports dry-run mode for simulation."
    )
    args_schema: Type[DeleteArgsSchema] = DeleteArgsSchema

    def _delete_message(self, message_id: str, dry_run: bool = False) -> Dict[str, Any]:
        """Delete a single Gmail message."""
        if dry_run:
            return {"id": message_id, "status": "simulated"}

        try:
            self.api_resource.users().messages().delete(userId="me", id=message_id).execute()
            return {"id": message_id, "status": "deleted"}
        except Exception as e:
            return {"id": message_id, "status": "error", "error": str(e)}

    def _run(
        self,
        message_ids: Optional[List[str]] = None,
        query: Optional[str] = None,
        dry_run: bool = False,
        max_results: int = 20,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Run the delete Gmail tool."""
        results = []

        if not message_ids and not query:
            return {"success": False, "error": "You must specify message_ids or query."}

        # If query is given, fetch messages first
        if query:
            search_response = (
                self.api_resource.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )
            message_ids = [msg["id"] for msg in search_response.get("messages", [])]

        if not message_ids:
            return {"success": True, "deleted": [], "message": "No messages matched query."}

        for msg_id in message_ids:
            results.append(self._delete_message(msg_id, dry_run))
            time.sleep(0.2)  # tiny throttle to avoid rate limit

        return {
            "success": True,
            "dry_run": dry_run,
            "deleted_count": len([r for r in results if r["status"] == "deleted"]),
            "simulated_count": len([r for r in results if r["status"] == "simulated"]),
            "errors": [r for r in results if r["status"] == "error"],
            "results": results,
        }

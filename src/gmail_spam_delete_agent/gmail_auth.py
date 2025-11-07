import os
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


# Covers read, modify (trash), and basic profile
SCOPES = [
	"https://www.googleapis.com/auth/gmail.modify",
	"https://www.googleapis.com/auth/gmail.readonly",
	"https://www.googleapis.com/auth/gmail.metadata",
]


def ensure_gmail_token(
	client_secrets_file: Optional[str] = None,
	token_file: Optional[str] = None,
) -> Credentials:
	"""Ensure a valid user OAuth token exists; run browser flow if needed.

	client_secrets_file: path to OAuth client secrets JSON
	token_file: path where token.json should be stored
	"""
	client_secrets_file = (
		client_secrets_file
		or os.getenv("GMAIL_CLIENT_SECRETS_FILE")
		or os.path.join("credentials", "client_secret.json")
	)
	token_file = (
		token_file or os.getenv("GMAIL_TOKEN_FILE") or os.path.join("credentials", "token.json")
	)

	Path(os.path.dirname(token_file)).mkdir(parents=True, exist_ok=True)

	creds: Optional[Credentials] = None
	if os.path.exists(token_file):
		creds = Credentials.from_authorized_user_file(token_file, SCOPES)
	# Refresh or run flow
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
			creds = flow.run_local_server(port=0)
		with open(token_file, "w", encoding="utf-8") as f:
			f.write(creds.to_json())
	return creds



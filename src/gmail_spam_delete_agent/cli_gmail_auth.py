import os
import sys
from dotenv import load_dotenv

from .gmail_auth import ensure_gmail_token


def main() -> None:
	load_dotenv()
	client = os.getenv("GMAIL_CLIENT_SECRETS_FILE") or "credentials/client_secret.json"
	token = os.getenv("GMAIL_TOKEN_FILE") or "credentials/token.json"
	try:
		ensure_gmail_token(client, token)
		print(f"OAuth complete. Token saved to {token}")
	except FileNotFoundError:
		print(
			f"Missing client secrets JSON at {client}. Download from Google Cloud Console (OAuth client ID).",
			file=sys.stderr,
		)
		sys.exit(1)


if __name__ == "__main__":
	main()



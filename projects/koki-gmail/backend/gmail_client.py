"""Thin wrapper around the Gmail API: OAuth + fetching recent messages."""
import base64
import json
import os
from email.utils import parsedate_to_datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Read-only: the app can never send, delete, or modify your mail.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

HERE = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(HERE, "credentials.json")
TOKEN_FILE = os.path.join(HERE, "token.json")


def _load_creds():
    """Load cached Gmail credentials from env (for servers) or local file."""
    # On a deployed server there is no browser and the disk is ephemeral, so we
    # read the OAuth token JSON from an env var generated once via auth_setup.py.
    token_json = os.environ.get("GMAIL_TOKEN_JSON")
    if token_json:
        return Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)
    if os.path.exists(TOKEN_FILE):
        return Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return None


def get_service():
    """Return an authenticated Gmail service.

    Locally, the first call opens a browser for consent and caches token.json.
    On a server, credentials come from the GMAIL_TOKEN_JSON env var and are only
    refreshed (never re-prompted, since there is no browser).
    """
    creds = _load_creds()
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.environ.get("GMAIL_TOKEN_JSON"):
            raise RuntimeError(
                "GMAIL_TOKEN_JSON is set but invalid and cannot be refreshed. "
                "Re-run auth_setup.py locally and update the env var."
            )
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def _header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _extract_body(payload):
    """Best-effort plain-text body extraction from a Gmail message payload."""
    if payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", "ignore")
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", "ignore")
    # fall back to recursing into nested parts
    for part in payload.get("parts", []):
        body = _extract_body(part)
        if body:
            return body
    return ""


def fetch_recent(max_results=15, query="in:inbox"):
    """Return a list of simplified message dicts for the most recent inbox mail."""
    service = get_service()
    listing = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )
    messages = []
    for ref in listing.get("messages", []):
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=ref["id"], format="full")
            .execute()
        )
        headers = msg["payload"]["headers"]
        date_raw = _header(headers, "Date")
        try:
            date = parsedate_to_datetime(date_raw).isoformat() if date_raw else ""
        except (TypeError, ValueError):
            date = date_raw
        messages.append(
            {
                "id": msg["id"],
                "thread_id": msg["threadId"],
                "from": _header(headers, "From"),
                "subject": _header(headers, "Subject"),
                "date": date,
                "snippet": msg.get("snippet", ""),
                "body": _extract_body(msg["payload"])[:4000],
            }
        )
    return messages

"""Run ONCE on your own computer to authorize Gmail, then print the token
to paste into your host's GMAIL_TOKEN_JSON environment variable.

Usage:
    pip install -r requirements.txt
    python auth_setup.py        # opens a browser, then prints the token JSON
"""
import os

from google_auth_oauthlib.flow import InstalledAppFlow

from gmail_client import CREDENTIALS_FILE, SCOPES, TOKEN_FILE


def main():
    if not os.path.exists(CREDENTIALS_FILE):
        raise SystemExit(
            f"Missing {CREDENTIALS_FILE}. Download OAuth client (Desktop app) "
            "credentials from Google Cloud Console first (see README)."
        )
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    token_json = creds.to_json()
    with open(TOKEN_FILE, "w") as f:
        f.write(token_json)

    print("\n" + "=" * 60)
    print("SUCCESS. Set this as the GMAIL_TOKEN_JSON env var on your host")
    print("(Render: Environment tab. Paste the entire line below):")
    print("=" * 60)
    print(token_json)


if __name__ == "__main__":
    main()

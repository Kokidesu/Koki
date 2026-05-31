"""Summarize + triage emails with Claude."""
import json
import os

from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-haiku-4-5-20251001"  # fast + cheap; good enough for triage

SYSTEM = """You are an inbox triage assistant. For each email you receive,
produce a tight one-line summary and classify it. Be ruthless about noise:
marketing blasts, automated notifications, and newsletters are 'noise' unless
they clearly need action.

Respond with ONLY a JSON object, no prose:
{
  "summary": "<=15 word plain-language summary of what this email is about",
  "category": "needs_reply" | "fyi" | "noise",
  "urgency": "high" | "medium" | "low",
  "action": "<=10 word suggested next step, or empty string"
}"""


def summarize(email):
    """Return a triage dict for a single email; degrades gracefully on error."""
    user = (
        f"From: {email['from']}\n"
        f"Subject: {email['subject']}\n"
        f"Date: {email['date']}\n\n"
        f"{email['body'] or email['snippet']}"
    )
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=300,
            system=SYSTEM,
            messages=[{"role": "user", "content": user}],
        )
        text = resp.content[0].text.strip()
        # strip ```json fences if the model adds them
        if text.startswith("```"):
            text = text.split("```")[1].lstrip("json").strip()
        return json.loads(text)
    except Exception as exc:  # noqa: BLE001 - never let one bad email break the digest
        return {
            "summary": email["subject"] or "(no subject)",
            "category": "fyi",
            "urgency": "low",
            "action": "",
            "error": str(exc),
        }

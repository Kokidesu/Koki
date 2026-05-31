"""Koki backend: fetch Gmail, summarize with Claude, serve a mobile digest."""
import os

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse

import gmail_client
import summarizer

app = FastAPI(title="Koki Gmail Summarizer")

HERE = os.path.dirname(os.path.abspath(__file__))

# Once deployed, the digest lives on a public URL, so we gate the data behind a
# passcode. Set KOKI_PASSCODE on your host; leave it unset for local use.
PASSCODE = os.environ.get("KOKI_PASSCODE")


def _check_access(passcode):
    if PASSCODE and passcode != PASSCODE:
        raise HTTPException(status_code=401, detail="Bad or missing passcode")


@app.get("/")
def index():
    return FileResponse(os.path.join(HERE, "static", "index.html"))


@app.get("/api/digest")
def digest(limit: int = 15, x_koki_pass: str = Header(default="")):
    """Fetch recent inbox mail and return triaged summaries."""
    _check_access(x_koki_pass)
    emails = gmail_client.fetch_recent(max_results=limit)
    items = []
    for email in emails:
        triage = summarizer.summarize(email)
        items.append(
            {
                "id": email["id"],
                "from": email["from"],
                "subject": email["subject"],
                "date": email["date"],
                **triage,
            }
        )
    # surface what needs attention first
    order = {"needs_reply": 0, "fyi": 1, "noise": 2}
    items.sort(key=lambda x: (order.get(x["category"], 1), x.get("urgency") != "high"))
    counts = {c: sum(1 for i in items if i["category"] == c) for c in order}
    return JSONResponse({"items": items, "counts": counts})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

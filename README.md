# Koki — Gmail Summarizer Agent

An AI agent that pulls your Gmail, summarizes each thread, and flags what
actually needs your attention — so the spam noise collapses into a clean,
scannable digest you open from your iPhone home screen.

## What it is

- **Backend** (`backend/`): a small FastAPI server that
  - logs into Gmail via OAuth (read-only),
  - fetches recent messages,
  - asks Claude to summarize each one + classify it (needs reply / FYI / noise),
  - serves the results as JSON and a mobile web page.
- **Front-end**: a mobile-friendly web app (PWA) you open in iPhone Safari and
  "Add to Home Screen". No Mac and no Apple Developer account required.

This is the **fast local prototype**. Once you like it, the same backend can be
deployed to a free host (Fly.io / Render) to run 24/7 with push notifications.

## One-time setup

### 1. Get a Claude API key
Create one at https://console.anthropic.com → set it as `ANTHROPIC_API_KEY`.

### 2. Create Gmail OAuth credentials
1. Go to https://console.cloud.google.com → create a project.
2. **APIs & Services → Enable APIs** → enable **Gmail API**.
3. **OAuth consent screen** → External → add your own email as a *Test user*.
4. **Credentials → Create credentials → OAuth client ID → Desktop app**.
5. Download the JSON, save it as `backend/credentials.json`.

### 3. Install & run
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python app.py
```
First run opens a browser to grant Gmail access (token is cached in
`backend/token.json`). Then open http://localhost:8000 on your computer, or
visit it from your iPhone on the same network.

## Deploy it to run 24/7 (free, on Render)

A deployed server has no browser and a wipe-on-restart disk, so you authorize
Gmail **once on your own computer** and hand the resulting token to the host.

1. **Authorize Gmail locally** (one time):
   ```bash
   cd backend && pip install -r requirements.txt
   python auth_setup.py        # opens browser, then prints a token JSON line
   ```
   Copy the long token JSON it prints.

2. **Push this repo to GitHub** (already done on your branch).

3. **Create the service on Render** (https://render.com, free, no card):
   - New → **Blueprint** → connect your GitHub repo. It reads `render.yaml`.
   - In the service's **Environment** tab, fill the three secrets:
     - `ANTHROPIC_API_KEY` — your Claude key
     - `GMAIL_TOKEN_JSON` — the token line from step 1
     - `KOKI_PASSCODE` — any password you choose
   - Deploy. You get a public URL like `https://koki.onrender.com`.

4. **Add to your iPhone**: open that URL in Safari → Share → **Add to Home
   Screen**. Enter your passcode once and it's saved.

Notes:
- Render's free tier sleeps after ~15 min idle and cold-starts on the next open
  (a few seconds) — fine for personal use. Upgrade or switch to Fly.io for
  instant-on.
- The same `Dockerfile` deploys to Fly.io (`fly launch`) or any container host.
- When the Gmail token eventually expires, re-run `auth_setup.py` and update the
  `GMAIL_TOKEN_JSON` env var.

## Roadmap
- [x] Local prototype: fetch + summarize + mobile digest
- [x] Deploy to free cloud host (24/7)
- [ ] Persist summaries + read/handled state (SQLite)
- [ ] Real-time Gmail push (watch + Pub/Sub) + iOS web push notifications
- [ ] "Needs reply" smart drafts

## Security note
Your API key and Gmail token live only on the server (never in the app). Never
commit `credentials.json` or `token.json` — they're gitignored.

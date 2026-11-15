# Qwen Chat App

A standalone FastAPI web chat interface that forwards chat messages to a Qwen-compatible API.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Set these environment variables before starting:
# QWEN_API_URL=https://your-cloudflare-tunnel.trycloudflare.com
# QWEN_API_TOKEN=your-secret-token

uvicorn app:app --reload
```

Open http://127.0.0.1:8000

## Render deployment

Create a new Web Service from this repository (or upload these files to a new GitHub repository).

- Runtime: Docker
- Build command: leave blank
- Start command: leave blank (Dockerfile starts the service)
- Environment variables:
  - `QWEN_API_URL`: the Kaggle Cloudflare tunnel base URL, without a trailing slash
  - `QWEN_API_TOKEN`: the bearer token printed by the Kaggle notebook

Health endpoint: `/health`

**Important:** The Kaggle notebook and Cloudflare quick tunnel must remain running. The quick-tunnel URL can change when recreated. Never commit your API token to GitHub.

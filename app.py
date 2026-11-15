import os
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Literal

app = FastAPI(title="Qwen Chat Application")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

QWEN_API_URL = os.getenv("QWEN_API_URL", "").rstrip("/")
QWEN_API_TOKEN = os.getenv("QWEN_API_TOKEN", "")

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health():
    return {
        "status": "online",
        "qwen_configured": bool(QWEN_API_URL and QWEN_API_TOKEN)
    }

@app.post("/api/chat")
def chat(data: ChatRequest):
    if not QWEN_API_URL or not QWEN_API_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="QWEN_API_URL and QWEN_API_TOKEN must be configured"
        )
    if not data.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")

    payload = {
        "model": "qwen2.5",
        "messages": [message.model_dump() for message in data.messages],
        "temperature": 0.3,
        "max_tokens": 1024,
        "stream": False
    }

    try:
        response = requests.post(
            f"{QWEN_API_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {QWEN_API_TOKEN}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=300
        )
        response.raise_for_status()
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        return {"reply": answer, "model": result.get("model", "qwen2.5")}
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Qwen API timed out")
    except requests.exceptions.RequestException as exc:
        # Do not expose request headers or secrets in the error response.
        raise HTTPException(status_code=502, detail="Could not reach the Qwen API") from exc
    except (KeyError, ValueError, IndexError) as exc:
        raise HTTPException(status_code=502, detail="Invalid response from Qwen API") from exc

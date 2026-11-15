
import os
import requests

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Literal

app = FastAPI(title="Qwen Chat App")

# Configuration from Render environment variables
QWEN_API_URL = os.getenv("QWEN_API_URL", "")
QWEN_API_TOKEN = os.getenv("QWEN_API_TOKEN", "").strip()

headers = {
    "Content-Type": "application/json"
}

if QWEN_API_TOKEN:
    headers["Authorization"] = f"Bearer {QWEN_API_TOKEN}"
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen2.5")


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Qwen Chat</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }

        header {
            background: #202123;
            color: white;
            padding: 18px 25px;
            font-size: 20px;
        }

        #chat {
            max-width: 850px;
            margin: 20px auto;
            padding: 15px;
            height: calc(100vh - 155px);
            overflow-y: auto;
        }

        .message {
            padding: 15px 18px;
            margin: 12px 0;
            border-radius: 10px;
            line-height: 1.6;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }

        .user {
            background: #dbeafe;
            margin-left: 15%;
        }

        .bot {
            background: white;
            margin-right: 10%;
        }

        .input-area {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 15px;
            display: flex;
            justify-content: center;
            gap: 10px;
        }

        input {
            width: 70%;
            max-width: 700px;
            padding: 15px;
            border: 1px solid #ccc;
            border-radius: 10px;
            font-size: 16px;
        }

        button {
            padding: 15px 25px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .status {
            text-align: center;
            color: #777;
            padding: 8px;
        }
    </style>
</head>

<body>

<header>Qwen Chat App</header>

<div id="chat">
    <div class="message bot">
        Hello! I am your Qwen assistant. Ask me anything.
    </div>
</div>

<div class="input-area">
    <input
        id="message"
        placeholder="Ask Qwen something..."
        autocomplete="off"
    >
    <button id="send" onclick="sendMessage()">Send</button>
</div>

<script>
const chat = document.getElementById("chat");
const input = document.getElementById("message");
const sendButton = document.getElementById("send");

// Conversation history
const messages = [
    {
        role: "system",
        content: "You are a helpful AI assistant. Give clear, accurate and structured answers."
    }
];

function addMessage(role, content) {
    const div = document.createElement("div");

    div.className = "message " + role;
    div.textContent = content;

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;

    return div;
}

async function sendMessage() {
    const message = input.value.trim();

    if (!message || sendButton.disabled) return;

    input.value = "";

    addMessage("user", message);

    messages.push({
        role: "user",
        content: message
    });

    sendButton.disabled = true;

    const loading = addMessage("bot", "Qwen is thinking...");

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                messages: messages
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Request failed");
        }

        loading.textContent = data.reply;

        messages.push({
            role: "assistant",
            content: data.reply
        });

    } catch (error) {
        loading.textContent = "Error: " + error.message;

        // Remove the failed user message from history
        messages.pop();

    } finally {
        sendButton.disabled = false;
        input.focus();
        chat.scrollTop = chat.scrollHeight;
    }
}

input.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});
</script>

</body>
</html>
    """


@app.post("/chat")
def chat(request: ChatRequest):

    if not QWEN_API_URL:
        raise HTTPException(
            status_code=503,
            detail="QWEN_API_URL is not configured in Render."
        )

    headers = {
        "Content-Type": "application/json"
    }

    if QWEN_API_TOKEN:
        headers["Authorization"] = f"Bearer {QWEN_API_TOKEN}"

    payload = {
        "model": QWEN_MODEL,
        "messages": [
            message.model_dump()
            for message in request.messages
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
        "top_p": 0.9,
        "stream": False
    }

    try:
        response = requests.post(
            QWEN_API_URL,
            headers=headers,
            json=payload,
            timeout=180
        )

        response.raise_for_status()
        result = response.json()

        # Standard OpenAI-compatible response
        if "choices" in result:
            reply = result["choices"][0]["message"]["content"]

        # Alternative response formats
        elif "reply" in result:
            reply = result["reply"]

        elif "response" in result:
            reply = result["response"]

        elif "content" in result:
            reply = result["content"]

        else:
            raise ValueError(
                "Unrecognized Qwen response: " + str(result)[:500]
            )

        return {"reply": reply}

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Qwen model timed out. Please try again."
        )

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Qwen API connection failed: {str(e)}"
        )

    except (ValueError, KeyError, IndexError, TypeError) as e:
        raise HTTPException(
            status_code=502,
            detail=f"Could not process Qwen response: {str(e)}"
        )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": QWEN_MODEL,
        "qwen_configured": bool(QWEN_API_URL)
    }

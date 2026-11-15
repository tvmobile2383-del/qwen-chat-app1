
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Qwen Chat App")

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Qwen Chat</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
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
            margin: 30px auto;
            padding: 20px;
            height: 65vh;
            overflow-y: auto;
        }
        .message {
            padding: 15px 18px;
            margin: 12px 0;
            border-radius: 10px;
            line-height: 1.5;
        }
        .user {
            background: #dbeafe;
            text-align: right;
        }
        .bot {
            background: white;
        }
        .input-area {
            position: fixed;
            bottom: 20px;
            left: 0;
            right: 0;
            display: flex;
            justify-content: center;
            gap: 10px;
            padding: 10px;
        }
        input {
            width: 65%;
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
    </style>
</head>
<body>

<header>Qwen Chat App</header>

<div id="chat">
    <div class="message bot">
        Hello! Welcome to Qwen Chat. How can I help you?
    </div>
</div>

<div class="input-area">
    <input id="message" placeholder="Type your message..."
           onkeydown="if(event.key==='Enter') sendMessage()">
    <button onclick="sendMessage()">Send</button>
</div>

<script>
async function sendMessage() {
    const input = document.getElementById("message");
    const chat = document.getElementById("chat");
    const message = input.value.trim();

    if (!message) return;

    chat.innerHTML +=
        '<div class="message user"></div>';

    chat.lastElementChild.textContent = message;
    input.value = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: message})
        });

        if (!response.ok) {
            throw new Error("Server error: " + response.status);
        }

        const data = await response.json();

        chat.innerHTML +=
            '<div class="message bot"></div>';

        chat.lastElementChild.textContent = data.reply;

    } catch (error) {
        chat.innerHTML +=
            '<div class="message bot"></div>';

        chat.lastElementChild.textContent =
            "Error: " + error.message;
    }

    chat.scrollTop = chat.scrollHeight;
}
</script>

</body>
</html>
    """

@app.post("/chat")
async def chat(request: ChatRequest):
    return {
        "reply": "Your message received successfully: " + request.message
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

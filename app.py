
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Qwen Chat App")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Qwen Chat App</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f6f9;
                text-align: center;
                padding: 100px 20px;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 12px;
                max-width: 600px;
                margin: auto;
            }
            h1 { color: #2563eb; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hello World!</h1>
            <h2>Qwen Chat App</h2>
            <p>Your application is running successfully.</p>
        </div>
    </body>
    </html>
    """

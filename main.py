from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from os import getenv
from fastapi.responses import HTMLResponse
from openai import OpenAI

client = OpenAI(api_key=getenv("DEEP_SEEK_API_KEY"), base_url="https://api.deepseek.com")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

html_content = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>WebSocket Client</h1>
        <button onclick="connectWebSocket()">Connect</button>
        <br><br>
        <input id="messageInput" type="text" placeholder="Type your message" />
        <button onclick="sendMessage()">Send</button>
        <ul id="messages"></ul>
        
        <script>
            let socket;

            function connectWebSocket() {
                socket = new WebSocket("ws://127.0.0.1:8000/chatbot");
                socket.onmessage = function(event) {
                    const messages = document.getElementById('messages');
                    const message = document.createElement('li');
                    message.textContent = `Deep Seek: ${event.data}`;
                    messages.appendChild(message);
                };
            }

            function sendMessage() {
                const input = document.getElementById("messageInput");
                socket.send(input.value);
                input.value = '';
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html_content)

@app.websocket("/chatbot")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        
        # Creamos y enviamos el prompt
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": data},
            ],
            stream=False
        )

        # Respuesta de deep seek
        ia_response = response.choices[0].message.content
        print(f"Mensaje recibido del cliente: {data}")
        await websocket.send_text(f"{ia_response}")



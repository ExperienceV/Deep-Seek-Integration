from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from openai import OpenAI

client = OpenAI(api_key="sk-c6e55ff3e4ca4ac5a040ff4f34d4f459", base_url="https://api.deepseek.com")

app = FastAPI()

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



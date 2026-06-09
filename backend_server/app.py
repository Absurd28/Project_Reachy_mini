from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import json
import asyncio
import os

app = FastAPI()

# Enable CORS for local network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "*"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to the frontend file
FRONTEND_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend_app", "index.html")

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New Dashboard Connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

# --- Data Models ---
class AlertPayload(BaseModel):
    timestamp: str
    robot_id: str
    event_type: str
    severity: str
    message: str
    telemetry: dict = None

class JointCommand(BaseModel):
    joint_name: str
    angle: float

# --- REST Endpoints ---
@app.get("/")
async def get_dashboard():
    """Serves the frontend dashboard from the root URL."""
    return FileResponse(FRONTEND_PATH)

@app.post("/api/alerts")
async def receive_alert(alert: AlertPayload):
    """Receives alerts from the Edge logic and broadcasts to all Dashboards."""
    print(f"Alert Received: {alert.event_type} - {alert.severity}")
    await manager.broadcast(json.dumps({
        "type": "ALERT",
        "data": alert.model_dump()
    }))
    return {"status": "dispatched"}

@app.post("/api/commands")
async def receive_command(request: Request):
    """Receives remote commands from the Dashboard UI."""
    data = await request.json()
    command = data.get("command")
    print(f"REMOTE COMMAND RECEIVED: {command}")
    
    # Broadcast command to any listening robot controllers (if any)
    await manager.broadcast(json.dumps({
        "type": "CMD_TRIGGER",
        "command": command
    }))
    return {"status": "command_received", "cmd": command}

@app.post("/api/commands/joint")
async def receive_joint_command(cmd: JointCommand):
    """Receives specific joint movements from the Dashboard sliders."""
    print(f"JOINT MOVE: {cmd.joint_name} -> {cmd.angle}")
    # In a real setup, this would command the Reachy SDK
    return {"status": "success", "joint": cmd.joint_name, "angle": cmd.angle}

# --- WebSocket Endpoint ---
@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Dashboard Disconnected.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) # Using 8001 to avoid conflict with Reachy Daemon

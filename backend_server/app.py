from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import json
import asyncio
import os
from contextlib import asynccontextmanager

# --- Global State for Real-Time Mirroring ---
global_robot_state = {
    "neck_roll": 0.0, "neck_pitch": 0.0, "neck_yaw": 0.0, "neck_height": 20.0,
    "l_antenna": 0.0, "r_antenna": 0.0,
    "posture": "IDLE", "distance": 0.0
}

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New Dashboard Connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

# --- Async Background Telemetry Task (30 FPS) ---
async def telemetry_broadcast_loop():
    """Non-blocking background loop to sync state to all clients."""
    while True:
        try:
            await manager.broadcast(json.dumps({
                "type": "JOINT_UPDATE",
                "data": global_robot_state
            }))
            # Yield control back to event loop for 33ms (approx 30 FPS)
            await asyncio.sleep(0.03)
        except Exception as e:
            print(f"Telemetry loop error: {e}")
            await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Initializing Robotics Communication Center...")
    telemetry_task = asyncio.create_task(telemetry_broadcast_loop())
    yield
    # Shutdown logic
    print("Shutting down Communication Center...")
    telemetry_task.cancel()
    try:
        await telemetry_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

# Enable CORS for Vite Dev Server
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

@app.get("/api/health")
async def health_check():
    """Lightweight verification endpoint."""
    return {"status": "online", "robot_state": "connected", "port": 8000}

@app.post("/api/alerts")
async def receive_alert(alert: AlertPayload):
    """Receives alerts from the Edge logic and broadcasts to all Dashboards."""
    print(f"Alert Received: {alert.event_type} - {alert.severity}")
    
    # Update global state if telemetry is included
    if alert.telemetry:
        global_robot_state.update(alert.telemetry)

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
    # Update global state for mirroring
    if cmd.joint_name in global_robot_state:
        global_robot_state[cmd.joint_name] = cmd.angle
    
    print(f"JOINT MOVE: {cmd.joint_name} -> {cmd.angle}")
    # In a real setup, this would command the Reachy SDK
    return {"status": "success", "joint": cmd.joint_name, "angle": cmd.angle}

# --- WebSocket Endpoint ---
@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Handle client-to-server messages if any
            data = await websocket.receive_text()
            print(f"Received from dashboard: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Dashboard gracefully disconnected.")
    except Exception as e:
        manager.disconnect(websocket)
        print(f"WebSocket Error: {e}")

if __name__ == "__main__":
    # Standardizing to Port 8000 as per directive
    uvicorn.run(app, host="0.0.0.0", port=8000)

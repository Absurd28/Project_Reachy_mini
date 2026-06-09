from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import json
import asyncio
import os
from contextlib import asynccontextmanager

# --- Global State ---
connected_clients = set()
global_robot_state = {
    "neck_roll": 0.0, "neck_pitch": 0.0, "neck_yaw": 0.0, "neck_height": 20.0,
    "l_antenna": 0.0, "r_antenna": 0.0,
    "posture": "IDLE", "distance": 0.0,
    "x": 0.0, "y": 0.0
}

# --- Data Models ---
class TelemetryData(BaseModel):
    x: float
    y: float
    posture: str
    distance: float

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

# --- App Lifecycle ---
async def telemetry_broadcast_loop():
    """Non-blocking background loop to sync joint state to all clients."""
    while True:
        try:
            payload = {
                "type": "JOINT_UPDATE",
                "data": global_robot_state
            }
            for client in list(connected_clients):
                try:
                    await client.send_json(payload)
                except Exception:
                    connected_clients.remove(client)
            await asyncio.sleep(0.03)
        except Exception as e:
            print(f"Telemetry loop error: {e}")
            await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing Robotics Communication Center...")
    telemetry_task = asyncio.create_task(telemetry_broadcast_loop())
    yield
    print("Shutting down Communication Center...")
    telemetry_task.cancel()
    try:
        await telemetry_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend_app", "index.html")

# --- REST Endpoints ---
@app.get("/api/health")
async def health_check():
    return {"status": "online", "robot_state": "connected", "port": 8000}

@app.post("/api/internal/telemetry")
async def receive_internal_telemetry(data: TelemetryData):
    """
    Bridge endpoint: Receives data from OpenCV loop and broadcasts to WebSockets.
    """
    # Package exactly as requested for the direct broadcast
    payload = data.model_dump()
    
    # Update global state for mirroring
    global_robot_state.update(payload)

    # Broadcast raw payload to all connected clients
    for client in list(connected_clients):
        try:
            await client.send_json(payload)
        except Exception:
            connected_clients.remove(client)
    
    return {"status": "broadcasted"}

@app.post("/api/alerts")
async def receive_alert(alert: AlertPayload):
    """Receives alerts and broadcasts to all Dashboards."""
    print(f"Alert Received: {alert.event_type} - {alert.severity}")
    
    if alert.telemetry:
        global_robot_state.update(alert.telemetry)

    payload = {
        "type": "ALERT",
        "data": alert.model_dump()
    }
    
    for client in list(connected_clients):
        try:
            await client.send_json(payload)
        except Exception:
            connected_clients.remove(client)
            
    return {"status": "dispatched"}

@app.post("/api/commands")
async def receive_command(request: Request):
    data = await request.json()
    command = data.get("command")
    print(f"REMOTE COMMAND RECEIVED: {command}")
    
    payload = {
        "type": "CMD_TRIGGER",
        "command": command
    }
    
    for client in list(connected_clients):
        try:
            await client.send_json(payload)
        except Exception:
            connected_clients.remove(client)
            
    return {"status": "command_received", "cmd": command}

@app.post("/api/commands/joint")
async def receive_joint_command(cmd: JointCommand):
    if cmd.joint_name in global_robot_state:
        global_robot_state[cmd.joint_name] = cmd.angle
    print(f"JOINT MOVE: {cmd.joint_name} -> {cmd.angle}")
    return {"status": "success", "joint": cmd.joint_name, "angle": cmd.angle}

# --- WebSocket Endpoint ---
@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    print(f"New Dashboard Connected. Total: {len(connected_clients)}")
    try:
        while True:
            # Keep-alive and receive messages
            data = await websocket.receive_text()
            print(f"Received from dashboard: {data}")
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("Dashboard gracefully disconnected.")
    except Exception as e:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        print(f"WebSocket Error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

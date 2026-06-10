from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import json
import asyncio
import os
from contextlib import asynccontextmanager
from .robot_controller import RobotController

# --- Global State & Rule 1: Global Instance ---
connected_clients = set()
robot = RobotController(host="127.0.0.1", port=8000)

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
    # Rule 1 Implementation: Startup connection and stiffening
    print("Initializing Robotics Communication Center...")
    robot.connect() 
    telemetry_task = asyncio.create_task(telemetry_broadcast_loop())
    yield
    print("Shutting down Communication Center...")
    robot.disconnect()
    telemetry_task.cancel()
    try:
        await telemetry_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

# --- Rule 2: Permissive CORS for local development ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REST Endpoints ---
@app.get("/api/health")
async def health_check():
    return {"status": "online", "robot_state": "connected" if robot.is_connected else "disconnected", "port": 8001}

@app.post("/api/internal/telemetry")
async def receive_internal_telemetry(data: TelemetryData):
    payload = data.model_dump()
    global_robot_state.update(payload)
    for client in list(connected_clients):
        try:
            await client.send_json(payload)
        except Exception:
            connected_clients.remove(client)
    return {"status": "broadcasted"}

@app.post("/api/alerts")
async def receive_alert(alert: AlertPayload):
    if alert.telemetry:
        global_robot_state.update(alert.telemetry)
    payload = {"type": "ALERT", "data": alert.model_dump()}
    for client in list(connected_clients):
        try:
            await client.send_json(payload)
        except Exception:
            connected_clients.remove(client)
    return {"status": "dispatched"}

# --- Rule 3: Async Background Execution & Verification Logging ---
@app.post("/api/commands")
async def receive_command(request: Request, background_tasks: BackgroundTasks):
    """
    Main command bridge using BackgroundTasks for non-blocking hardware execution.
    """
    try:
        payload = await request.json()
        command = payload.get("command") or payload.get("action")
        
        # Rule 3: High-visibility verification logging
        print(f"🚥 COMMAND RECEIVED: {payload}")
        
        if not command:
            print("⚠️ ERROR: No command specified in payload")
            return JSONResponse(content={"error": "No command specified"}, status_code=400)
            
        print(f"[*] Dispatching to hardware: {command}")
        
        # Rule 3: Execute movement in background
        background_tasks.add_task(robot.handle_macro, command)
        
        # WebSocket feedback
        ws_payload = {"type": "CMD_TRIGGER", "command": command}
        for client in list(connected_clients):
            try:
                await client.send_json(ws_payload)
            except Exception:
                connected_clients.remove(client)
                
        return {"status": "command_received", "cmd": command}
    except Exception as e:
        print(f"❌ COMMAND ENDPOINT ERROR: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

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
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("Dashboard gracefully disconnected.")
    except Exception as e:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        print(f"WebSocket Error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)

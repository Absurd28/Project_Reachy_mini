import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Activity, Radio, AlertTriangle, ShieldCheck } from 'lucide-react';
import TelemetryPanel from './components/TelemetryPanel';
import ControlPanel from './components/ControlPanel';
import EventFeed from './components/EventFeed';
import LiveViewport from './components/LiveViewport';

const ROBOT_HOST = window.location.hostname;
const WS_URL = `ws://${ROBOT_HOST}:8001/ws/telemetry`;
const API_BASE_URL = `http://${ROBOT_HOST}:8001/api`;

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [telemetryState, setTelemetryState] = useState({ posture: '---', distance: null, x: 0, y: 0 });
  const [jointState, setJointState] = useState({});
  const [alerts, setAlerts] = useState([]);
  const wsRef = useRef(null);
  const retryDelayRef = useRef(2000);

  const addAlert = useCallback((msg, severity) => {
    setAlerts(prev => [{
      id: Date.now() + Math.random(),
      time: new Date().toLocaleTimeString(),
      message: msg,
      severity: severity
    }, ...prev].slice(0, 50));
  }, []);

  const sendCommand = async (command) => {
    console.log(`[NETWORK] Sending command: ${command} to ${API_BASE_URL}/commands`);
    try {
      const response = await fetch(`${API_BASE_URL}/commands`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: command })
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      console.log("[NETWORK] Command success:", result);
    } catch (error) {
      console.error("[NETWORK] Command Error:", error);
      addAlert(`Command Failed: ${command}`, "CRITICAL");
    }
  };

  useEffect(() => {
    let reconnectTimeout;
    let connectDelay;

    const connect = () => {
      // Prevent double-connection during React Dev mode rapid remounts
      if (wsRef.current) return;

      console.log(`Attempting connection to: ${WS_URL}`);
      addAlert(`Connecting to ${WS_URL}...`, "INFO");
      
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        retryDelayRef.current = 2000;
        addAlert("System link established.", "INFO");
        console.log("Handshake successful: WebSocket Link Active.");
      };

      ws.onerror = (err) => {
        console.error("WebSocket Error:", err);
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        wsRef.current = null;
        if (!event.wasClean) {
            console.log(`WS Closed: Code=${event.code}. Retrying in ${retryDelayRef.current/1000}s...`);
            addAlert(`Link lost (Code ${event.code}). Retrying...`, "CRITICAL");
            
            reconnectTimeout = setTimeout(() => {
                connect();
                retryDelayRef.current = Math.min(retryDelayRef.current * 2, 30000);
            }, retryDelayRef.current);
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Robust Message Routing
          if (data.posture !== undefined) {
             // Vision Loop Telemetry (Direct Payload)
             setTelemetryState(prev => ({
                ...prev,
                ...data
             }));
          } else if (data.type === "JOINT_UPDATE") {
             setJointState(data.data);
          } else if (data.type === "ALERT") {
             addAlert(data.data.message, data.data.severity);
             if (data.data.telemetry) {
                setTelemetryState(prev => ({
                    ...prev,
                    ...data.data.telemetry
                }));
             }
          }
        } catch (e) {
          console.error("Message parsing error:", e);
        }
      };
    };

    // Slight delay to ensure previous unmounts have fully cleared the socket
    connectDelay = setTimeout(connect, 200);

    return () => {
      clearTimeout(connectDelay);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      clearTimeout(reconnectTimeout);
    };
  }, [addAlert]);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-50 p-6 flex flex-col font-sans">
      {/* Header */}
      <header className="flex justify-between items-center pb-5 border-b border-slate-700 mb-6">
        <div>
          <h1 className="text-2xl font-bold m-0 flex items-center gap-2">
            REACHY<span className="text-sky-400">MINI</span>
            <span className="text-sm font-normal text-slate-400 ml-2 tracking-widest">COMMAND CENTER</span>
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-black/30 rounded-full text-xs font-bold">
            {isConnected ? (
              <><div className="w-2.5 h-2.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)]"></div> <span className="text-green-400">LINK ACTIVE</span></>
            ) : (
              <><div className="w-2.5 h-2.5 rounded-full bg-red-500"></div> <span className="text-red-400">LINK DOWN</span></>
            )}
          </div>
          <button 
            onClick={() => sendCommand('E-STOP')}
            className="bg-red-500 hover:bg-red-400 text-white font-bold py-3 px-6 rounded text-sm tracking-widest uppercase transition-colors flex items-center gap-2"
          >
            <AlertTriangle size={18} />
            E-STOP
          </button>
        </div>
      </header>

      {/* Main Grid */}
      <main className="flex-grow grid grid-cols-1 lg:grid-cols-[350px_1fr_350px] gap-6">
        
        {/* Left Column: Telemetry & Status */}
        <div className="flex flex-col gap-6">
          <TelemetryPanel telemetry={telemetryState} isConnected={isConnected} />
          <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 shadow-lg">
             <h2 className="text-sky-400 text-xs uppercase tracking-wider font-bold mb-4 flex justify-between">
                System Modes <Activity size={14} />
             </h2>
             <div className="flex gap-2 mb-6">
                <button onClick={() => sendCommand('STIFF')} className="flex-1 py-2 bg-slate-600 hover:bg-slate-500 rounded text-sm font-semibold transition-colors">STIFF</button>
                <button onClick={() => sendCommand('COMPLIANT')} className="flex-1 py-2 bg-green-500 hover:bg-green-400 text-slate-900 rounded text-sm font-semibold transition-colors">COMPLIANT</button>
             </div>
          </div>
        </div>

        {/* Center Column: Viewport */}
        <div className="bg-black rounded-xl border border-slate-700 relative overflow-hidden flex flex-col shadow-inner min-h-[400px]">
           <LiveViewport telemetry={telemetryState} isConnected={isConnected} />
        </div>

        {/* Right Column: Controls */}
        <ControlPanel jointState={jointState} addAlert={addAlert} apiUrl={API_BASE_URL} />
        
      </main>

      {/* Bottom Row: Feed */}
      <div className="mt-6 h-48 bg-slate-800 rounded-xl border border-slate-700 p-0 overflow-hidden flex flex-col">
        <div className="px-5 py-3 border-b border-slate-700 flex justify-between items-center bg-slate-800/50">
           <h2 className="text-sky-400 text-xs uppercase tracking-wider font-bold m-0 flex items-center gap-2">
             Event Console
           </h2>
        </div>
        <EventFeed alerts={alerts} />
      </div>
    </div>
  );
}

export default App;

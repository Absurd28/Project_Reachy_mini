import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Radio, AlertTriangle, ShieldCheck } from 'lucide-react';
import TelemetryPanel from './components/TelemetryPanel';
import ControlPanel from './components/ControlPanel';
import EventFeed from './components/EventFeed';

const ROBOT_IP = window.location.hostname || "127.0.0.1";
const WS_URL = `ws://${ROBOT_IP}:8001/ws/telemetry`;

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [telemetry, setTelemetry] = useState({ posture: '---', distance: null });
  const [jointState, setJointState] = useState({});
  const [alerts, setAlerts] = useState([]);

  const addAlert = useCallback((msg, severity) => {
    setAlerts(prev => [{
      id: Date.now() + Math.random(),
      time: new Date().toLocaleTimeString(),
      message: msg,
      severity: severity
    }, ...prev].slice(0, 50));
  }, []);

  useEffect(() => {
    let ws;
    let reconnectTimeout;

    const connect = () => {
      ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        setIsConnected(true);
        addAlert("System link established.", "INFO");
      };

      ws.onclose = () => {
        setIsConnected(false);
        addAlert("Link lost. Retrying...", "CRITICAL");
        reconnectTimeout = setTimeout(connect, 3000);
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          
          if (msg.type === "ALERT") {
            addAlert(msg.data.message, msg.data.severity);
            if (msg.data.telemetry) {
              setTelemetry({
                posture: msg.data.telemetry.posture || '---',
                distance: msg.data.telemetry.distance || null
              });
            }
          } else if (msg.type === "JOINT_UPDATE") {
            setJointState(msg.data);
          }
        } catch (e) {
          console.error("Message parsing error:", e);
        }
      };
    };

    connect();

    return () => {
      if (ws) ws.close();
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
            onClick={() => fetch(`http://${ROBOT_IP}:8001/api/commands`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ command: 'E-STOP' })
            })}
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
          <TelemetryPanel telemetry={telemetry} isConnected={isConnected} />
          <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 shadow-lg">
             <h2 className="text-sky-400 text-xs uppercase tracking-wider font-bold mb-4 flex justify-between">
                System Modes <Activity size={14} />
             </h2>
             <div className="flex gap-2 mb-6">
                <button onClick={() => fetch(`http://${ROBOT_IP}:8001/api/commands`, { method: 'POST', body: JSON.stringify({command: 'STIFF'})})} className="flex-1 py-2 bg-slate-600 hover:bg-slate-500 rounded text-sm font-semibold transition-colors">STIFF</button>
                <button onClick={() => fetch(`http://${ROBOT_IP}:8001/api/commands`, { method: 'POST', body: JSON.stringify({command: 'COMPLIANT'})})} className="flex-1 py-2 bg-green-500 hover:bg-green-400 text-slate-900 rounded text-sm font-semibold transition-colors">COMPLIANT</button>
             </div>
          </div>
        </div>

        {/* Center Column: Viewport */}
        <div className="bg-black rounded-xl border border-slate-700 relative overflow-hidden flex flex-col justify-center items-center shadow-inner">
           <Radio size={48} className="text-slate-600 mb-4" />
           <p className="text-slate-500 text-sm tracking-wide">WAITING FOR MEDIA STREAM...</p>
        </div>

        {/* Right Column: Controls */}
        <ControlPanel jointState={jointState} addAlert={addAlert} apiUrl={`http://${ROBOT_IP}:8001/api`} />
        
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
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Activity, Radio, AlertTriangle, ShieldCheck, X, Bell } from 'lucide-react';
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
  const [activeToast, setActiveToast] = useState(null);
  
  const wsRef = useRef(null);
  const retryDelayRef = useRef(2000);
  const audioRef = useRef(null);

  // Initialize Audio for "bip" sound
  useEffect(() => {
    // Standard system-like beep sound
    audioRef.current = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3');
  }, []);

  const triggerEmergencyAlert = useCallback((message) => {
    // 1. Play "bip" sound
    if (audioRef.current) {
      audioRef.current.play().catch(e => console.log("Audio play failed:", e));
    }

    // 2. Trigger Haptic Feedback (Vibration) if on mobile
    if (navigator.vibrate) {
      navigator.vibrate([200, 100, 200]);
    }

    // 3. Set Active Notification Toast
    setActiveToast({
      id: Date.now(),
      message: message,
      type: "EMERGENCY"
    });

    // Auto-clear toast after 10 seconds
    setTimeout(() => setActiveToast(null), 10000);
  }, []);

  const addAlert = useCallback((msg, severity) => {
    setAlerts(prev => [{
      id: Date.now() + Math.random(),
      time: new Date().toLocaleTimeString(),
      message: msg,
      severity: severity
    }, ...prev].slice(0, 50));

    // If it's a critical voice distress alert, trigger the notification ecosystem
    if (severity === "CRITICAL" && (msg.toLowerCase().includes("distress") || msg.toLowerCase().includes("patient said"))) {
      triggerEmergencyAlert(msg);
    }
  }, [triggerEmergencyAlert]);

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
      if (wsRef.current) return;
      console.log(`Attempting connection to: ${WS_URL}`);
      
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        retryDelayRef.current = 2000;
        addAlert("System link established.", "INFO");
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        wsRef.current = null;
        if (!event.wasClean) {
            reconnectTimeout = setTimeout(() => {
                connect();
                retryDelayRef.current = Math.min(retryDelayRef.current * 2, 30000);
            }, retryDelayRef.current);
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.posture !== undefined) {
             setTelemetryState(prev => ({ ...prev, ...data }));
          } else if (data.type === "JOINT_UPDATE") {
             setJointState(data.data);
          } else if (data.type === "ALERT") {
             addAlert(data.data.message, data.data.severity);
          }
        } catch (e) {
          console.error("Message parsing error:", e);
        }
      };
    };

    connectDelay = setTimeout(connect, 200);
    return () => {
      clearTimeout(connectDelay);
      if (wsRef.current) wsRef.current.close();
      clearTimeout(reconnectTimeout);
    };
  }, [addAlert]);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-50 p-6 flex flex-col font-sans relative overflow-hidden">
      
      {/* Emergency Notification Toast */}
      {activeToast && (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-[100] w-[90%] max-w-md animate-bounce-in">
          <div className="bg-red-600 border-2 border-red-400 rounded-xl shadow-[0_0_30px_rgba(220,38,38,0.5)] p-4 flex items-center gap-4 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-white/30 animate-shrink" style={{animationDuration: '10s'}}></div>
            <div className="p-3 bg-white/20 rounded-full animate-pulse">
              <Bell className="text-white" size={24} />
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-white text-lg leading-tight uppercase tracking-tight">Emergency Detected</h3>
              <p className="text-red-100 text-sm font-medium">{activeToast.message}</p>
            </div>
            <button 
              onClick={() => setActiveToast(null)}
              className="p-1 hover:bg-white/20 rounded-full transition-colors"
            >
              <X size={20} className="text-white" />
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="flex justify-between items-center pb-5 border-b border-slate-700 mb-6">
        <div>
          <h1 className="text-2xl font-bold m-0 flex items-center gap-2">
            REACHY<span className="text-sky-400">MINI</span>
            <span className="text-sm font-normal text-slate-400 ml-2 tracking-widest uppercase">Command Center</span>
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-black/30 rounded-full text-xs font-bold">
            {isConnected ? (
              <><div className="w-2.5 h-2.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)]"></div> <span className="text-green-400 tracking-wider">LINK ACTIVE</span></>
            ) : (
              <><div className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></div> <span className="text-red-400 tracking-wider">LINK DOWN</span></>
            )}
          </div>
          <button 
            onClick={() => sendCommand('E-STOP')}
            className="bg-red-500 hover:bg-red-400 text-white font-bold py-3 px-6 rounded text-sm tracking-widest uppercase transition-all active:scale-95 flex items-center gap-2 shadow-lg shadow-red-900/20"
          >
            <AlertTriangle size={18} />
            E-STOP
          </button>
        </div>
      </header>

      {/* Main Grid */}
      <main className="flex-grow grid grid-cols-1 lg:grid-cols-[350px_1fr_350px] gap-6">
        <div className="flex flex-col gap-6">
          <TelemetryPanel telemetry={telemetryState} isConnected={isConnected} />
          <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 shadow-lg">
             <h2 className="text-sky-400 text-xs uppercase tracking-wider font-bold mb-4 flex justify-between">
                System Modes <Activity size={14} />
             </h2>
             <div className="flex gap-2">
                <button onClick={() => sendCommand('STIFF')} className="flex-1 py-2 bg-slate-600 hover:bg-slate-500 rounded text-sm font-semibold transition-all active:scale-95">STIFF</button>
                <button onClick={() => sendCommand('COMPLIANT')} className="flex-1 py-2 bg-green-500 hover:bg-green-400 text-slate-900 rounded text-sm font-semibold transition-all active:scale-95">COMPLIANT</button>
             </div>
          </div>
        </div>

        <div className="bg-black rounded-xl border border-slate-700 relative overflow-hidden flex flex-col shadow-inner min-h-[400px]">
           <LiveViewport telemetry={telemetryState} isConnected={isConnected} />
        </div>

        <ControlPanel jointState={jointState} addAlert={addAlert} apiUrl={API_BASE_URL} />
      </main>

      {/* Bottom Row: Feed */}
      <div className="mt-6 h-48 bg-slate-800 rounded-xl border border-slate-700 p-0 overflow-hidden flex flex-col shadow-xl">
        <div className="px-5 py-3 border-b border-slate-700 flex justify-between items-center bg-slate-900/50">
           <h2 className="text-sky-400 text-xs uppercase tracking-wider font-bold m-0 flex items-center gap-2">
             Event Console
           </h2>
        </div>
        <EventFeed alerts={alerts} />
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes bounce-in {
          0% { transform: translate(-50%, -100%); opacity: 0; }
          60% { transform: translate(-50%, 20px); opacity: 1; }
          100% { transform: translate(-50%, 0); opacity: 1; }
        }
        @keyframes shrink {
          from { width: 100%; }
          to { width: 0%; }
        }
        .animate-bounce-in { animation: bounce-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
        .animate-shrink { animation: shrink linear forwards; }
      `}} />
    </div>
  );
}

export default App;

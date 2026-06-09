import React from 'react';
import { ShieldCheck } from 'lucide-react';

const TelemetryPanel = ({ telemetry, isConnected }) => {
  return (
    <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 shadow-lg">
      <h2 className="text-sky-400 text-xs uppercase tracking-wider font-bold mb-4 flex justify-between items-center">
        Live Telemetry
        <ShieldCheck size={14} className={telemetry.posture === 'SAFE' ? 'text-green-400' : 'text-slate-500'} />
      </h2>
      
      <div className="space-y-4">
        <div className="bg-slate-900/50 p-3 rounded border-l-2 border-sky-400">
          <div className="text-[10px] text-slate-400 mb-1 uppercase tracking-wider">Recognized Posture</div>
          <div className="text-xl font-mono font-bold">
            {isConnected ? telemetry.posture : '---'}
          </div>
        </div>
        
        <div className="bg-slate-900/50 p-3 rounded border-l-2 border-sky-400">
          <div className="text-[10px] text-slate-400 mb-1 uppercase tracking-wider">Distance Heuristic</div>
          <div className="text-xl font-mono font-bold">
            {isConnected && telemetry.distance !== null ? `${telemetry.distance.toFixed(2)}m` : '0.00m'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TelemetryPanel;
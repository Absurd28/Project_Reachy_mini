import React from 'react';

const EventFeed = ({ alerts }) => {
  return (
    <div className="flex-grow overflow-y-auto p-3 font-mono text-xs flex flex-col gap-1 bg-black">
      {alerts.length === 0 && (
        <div className="text-slate-500 italic p-2">No events to display...</div>
      )}
      
      {alerts.map(alert => {
        let colorClass = "text-slate-400"; // INFO
        let bgClass = "bg-transparent";

        if (alert.severity === "WARNING") {
          colorClass = "text-amber-400";
          bgClass = "bg-amber-500/10";
        } else if (alert.severity === "CRITICAL") {
          colorClass = "text-red-400 font-bold";
          bgClass = "bg-red-500/10";
        }

        return (
          <div key={alert.id} className={`px-3 py-1.5 rounded flex gap-3 ${colorClass} ${bgClass}`}>
            <span className="opacity-60 whitespace-nowrap">[{alert.time}]</span>
            <span className="opacity-80 w-16">[{alert.severity}]</span>
            <span className="flex-grow">{alert.message}</span>
          </div>
        );
      })}
    </div>
  );
};

export default EventFeed;
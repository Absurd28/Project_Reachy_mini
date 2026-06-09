import React, { useRef, useCallback, useState, useEffect } from 'react';
import axios from 'axios';
import { SlidersHorizontal } from 'lucide-react';

const ControlPanel = ({ jointState, addAlert, apiUrl }) => {
  const debounceRef = useRef({});
  const [localJoints, setLocalJoints] = useState({
    neck_roll: 0, neck_pitch: 0, neck_yaw: 0, neck_height: 20,
    l_antenna: 0, r_antenna: 0
  });

  // Sync local UI with incoming remote state when idle
  useEffect(() => {
    if (Object.keys(jointState).length > 0) {
      setLocalJoints(prev => ({ ...prev, ...jointState }));
    }
  }, [jointState]);

  const sendMacro = async (cmd) => {
    try {
      addAlert(`Sending command: ${cmd}`, "INFO");
      await axios.post(`${apiUrl}/commands`, { command: cmd });
    } catch (e) {
      addAlert(`Failed to send command: ${cmd}`, "CRITICAL");
    }
  };

  const handleSliderChange = useCallback((jointName, value) => {
    const numVal = parseFloat(value);
    
    // Update local immediately
    setLocalJoints(prev => ({ ...prev, [jointName]: numVal }));

    // Debounce actual request (50ms)
    if (debounceRef.current[jointName]) {
      clearTimeout(debounceRef.current[jointName]);
    }

    debounceRef.current[jointName] = setTimeout(async () => {
      try {
        await axios.post(`${apiUrl}/commands/joint`, {
          joint_name: jointName,
          angle: numVal
        });
      } catch (e) {
        console.error("Joint command failed", e);
      }
    }, 50);
  }, [apiUrl]);

  const renderSlider = (label, jointKey, min, max, unit = '°') => (
    <div className="mb-4">
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>{label}</span>
        <span>{localJoints[jointKey]}{unit}</span>
      </div>
      <input 
        type="range" 
        min={min} max={max} 
        value={localJoints[jointKey]}
        onChange={(e) => handleSliderChange(jointKey, e.target.value)}
        className="w-full accent-sky-400 cursor-pointer h-1 bg-slate-700 rounded-lg appearance-none"
      />
    </div>
  );

  return (
    <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 shadow-lg flex flex-col h-full overflow-y-auto">
      <h2 className="text-sky-400 text-xs uppercase tracking-wider font-bold mb-4 flex justify-between">
        Manual Control <SlidersHorizontal size={14} />
      </h2>

      <div className="mb-6">
        <h3 className="text-[10px] text-slate-500 uppercase tracking-widest mb-3 border-b border-slate-700 pb-1">Neck Orbita3D</h3>
        {renderSlider('Roll', 'neck_roll', -45, 45)}
        {renderSlider('Pitch', 'neck_pitch', -45, 45)}
        {renderSlider('Yaw', 'neck_yaw', -90, 90)}
      </div>

      <div className="mb-6">
        <h3 className="text-[10px] text-slate-500 uppercase tracking-widest mb-3 border-b border-slate-700 pb-1">Translation</h3>
        {renderSlider('Height', 'neck_height', 0, 100, 'mm')}
      </div>

      <div className="mb-6">
        <h3 className="text-[10px] text-slate-500 uppercase tracking-widest mb-3 border-b border-slate-700 pb-1">Antennas</h3>
        {renderSlider('Left Antenna', 'l_antenna', -30, 90)}
        {renderSlider('Right Antenna', 'r_antenna', -30, 90)}
      </div>

      <div className="mt-auto pt-4 border-t border-slate-700">
        <h3 className="text-[10px] text-slate-500 uppercase tracking-widest mb-3">Macro Gestures</h3>
        <div className="grid grid-cols-2 gap-2">
          <button onClick={() => sendMacro('emerge_wakeup')} className="bg-slate-700 hover:bg-sky-600 hover:text-white text-slate-300 text-xs py-2 rounded transition-colors">Wake Up</button>
          <button onClick={() => sendMacro('retract_hide')} className="bg-slate-700 hover:bg-sky-600 hover:text-white text-slate-300 text-xs py-2 rounded transition-colors">Retract/Hide</button>
          <button onClick={() => sendMacro('curious_tilt')} className="bg-slate-700 hover:bg-sky-600 hover:text-white text-slate-300 text-xs py-2 rounded transition-colors">Curious</button>
          <button onClick={() => sendMacro('scan_room')} className="bg-slate-700 hover:bg-sky-600 hover:text-white text-slate-300 text-xs py-2 rounded transition-colors">Scan</button>
        </div>
      </div>
    </div>
  );
};

export default ControlPanel;
'use client';

import React, { useEffect, useState, useRef } from 'react';
import { Terminal, Shield, Cpu, Activity } from 'lucide-react';
import { EventStore } from '@/lib/event-store';

export default function TelemetryStream({ store }: { store: EventStore }) {
  const [telemetry, setTelemetry] = useState<any[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const updateTelemetry = () => {
      const newTelemetry = store.getTelemetry();
      console.log("[TelemetryStream] Updating telemetry array, size:", newTelemetry.length);
      setTelemetry(newTelemetry);
    };

    updateTelemetry();
    const unsubscribe = store.subscribe(updateTelemetry);
    return () => unsubscribe();
  }, [store]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [telemetry]);

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-300 rounded-2xl overflow-hidden shadow-2xl border border-slate-800 font-mono">
      {/* Terminal Header */}
      <div className="px-4 py-2 bg-slate-900 border-b border-slate-800 flex items-center justify-between shrink-0">
        <div className="flex gap-2">
          <div className="w-3 h-3 rounded-full bg-slate-700" />
          <div className="w-3 h-3 rounded-full bg-slate-700" />
          <div className="w-3 h-3 rounded-full bg-slate-700" />
        </div>
        <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest font-bold text-slate-500">
          <Terminal className="w-3 h-3" />
          Vultr VPS Telemetry Stream
        </div>
        <div className="text-[10px] text-emerald-500/80 font-bold uppercase tracking-wider">
          Live · SSH:155.138.218.106
        </div>
      </div>

      {/* Terminal Body */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-2 text-[11px] leading-relaxed selection:bg-gold/30 selection:text-white"
      >
        {telemetry.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-4 text-slate-700">
            <Activity className="w-8 h-8 opacity-20" />
            <p className="tracking-widest uppercase text-[10px]">Awaiting encrypted I/O...</p>
          </div>
        ) : (
          telemetry.map((entry, i) => (
            <div key={i} className="animate-in fade-in slide-in-from-left-1 duration-200">
              {entry.command && (
                <div className="flex gap-2 text-gold/80">
                  <span className="text-gold opacity-50">root@vps:~$</span>
                  <span className="font-bold">{entry.command}</span>
                </div>
              )}
              {entry.output && (
                <div className={`whitespace-pre-wrap ml-2 p-2 rounded-lg ${entry.stream === 'stderr' ? 'text-red-400 bg-red-400/5' : 'text-slate-400 opacity-90'}`}>
                  {entry.output}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Terminal Footer */}
      <div className="px-4 py-2 bg-slate-900/50 text-[9px] text-slate-600 flex justify-between shrink-0">
        <div className="flex gap-4">
          <span className="flex items-center gap-1"><Shield className="w-3 h-3" /> Secure: AES-256</span>
          <span className="flex items-center gap-1"><Cpu className="w-3 h-3" /> ADK Mastery active</span>
        </div>
        <div>
          UTF-8 · ZSH · 80x24
        </div>
      </div>
    </div>
  );
}

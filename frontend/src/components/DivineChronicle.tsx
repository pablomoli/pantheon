'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { EventStore, PantheonEvent } from '@/lib/event-store';

export default function DivineChronicle({ store }: { store: EventStore }) {
  const [events, setEvents] = useState<PantheonEvent[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const updateEvents = () => {
      setEvents(store.getRecentEvents(100));
    };

    updateEvents();
    const unsubscribe = store.subscribe(updateEvents);
    return () => unsubscribe();
  }, [store]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [events]);

  return (
    <div className="flex flex-col h-full bg-[#1c1c1e] rounded-xl border border-white/10 shadow-2xl overflow-hidden font-mono text-green-400 m-4 relative group">
      {/* Ambient Glow */}
      <div className="absolute inset-0 bg-green-500/5 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

      {/* macOS Terminal Title Bar */}
      <div className="flex items-center px-4 py-2.5 bg-[#2d2d30] border-b border-black/40 shrink-0 z-10">
        <div className="flex gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f56] shadow-sm shadow-red-900/20" />
          <div className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e] shadow-sm shadow-yellow-900/20" />
          <div className="w-2.5 h-2.5 rounded-full bg-[#27c93f] shadow-sm shadow-green-900/20" />
        </div>
        <div className="flex-1 text-center text-[10px] text-white/30 font-mono tracking-[0.2em] font-bold uppercase">
          root@pantheon — TELEMETRY
        </div>
        <div className="w-12 text-[9px] text-white/20 text-right font-bold">SSH</div>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-5 space-y-2 bg-[#1e1e1e] custom-scrollbar scroll-smooth"
      >
        <AnimatePresence initial={false}>
          {events.length === 0 ? (
            <div className="h-full flex flex-col items-start justify-start p-2 text-green-400/50">
              <div className="flex items-center gap-2">
                <span className="w-2 h-4 bg-green-500/80 animate-pulse" />
                <span className="text-[11px] uppercase tracking-widest opacity-40">Awaiting transmission...</span>
              </div>
            </div>
          ) : (
            <>
              {events.map((event, i) => {
                const timeString = new Date(event.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
                const agentString = (event.agent || 'SYSTEM').toUpperCase();
                
                let message = '';
                let detail = '';

                if (event.type === 'TOOL_CALLED') {
                  message = `Invoking tool: ${event.tool}`;
                  detail = JSON.stringify(event.payload, null, 2);
                } else if (event.type === 'TOOL_RESULT') {
                  message = `Tool completed: ${event.tool}`;
                  detail = JSON.stringify(event.payload, null, 2);
                } else if (event.type === 'IOC_DISCOVERED') {
                  message = `Extracted ${event.payload.ioc_type as string}: ${event.payload.value as string}`;
                  const { ioc_type, value, ...rest } = event.payload;
                  if (Object.keys(rest).length > 0) detail = JSON.stringify(rest, null, 2);
                } else if (event.type === 'HANDOFF') {
                  message = `A2A Handshake: Dispatched ${event.payload.to as string}`;
                } else if (event.type === 'AGENT_ACTIVATED' || event.type === 'AGENT_COMPLETED') {
                  message = String(event.payload.message || event.type);
                  const { message: _, ...rest } = event.payload;
                  if (Object.keys(rest).length > 0) detail = JSON.stringify(rest, null, 2);
                } else if (event.type === 'ERROR') {
                  message = String(event.payload.error || event.payload.message || 'Error occurred');
                } else {
                  message = String(event.payload.message || event.type);
                  if (Object.keys(event.payload).length > 1 || (Object.keys(event.payload).length === 1 && !event.payload.message)) {
                    const { message: _, ...rest } = event.payload;
                    detail = JSON.stringify(rest, null, 2);
                  }
                }

                let prefixColor = 'text-green-500';
                if (event.type === 'ERROR') prefixColor = 'text-red-500';
                if (event.type === 'IOC_DISCOVERED') prefixColor = 'text-amber-500';
                if (event.type === 'HANDOFF') prefixColor = 'text-fuchsia-400';
                if (event.type === 'TOOL_CALLED' || event.type === 'TOOL_RESULT') prefixColor = 'text-blue-400';
                if (event.type === 'PROCESS_EVENT') prefixColor = 'text-yellow-400';
                if (event.type === 'NETWORK_EVENT') prefixColor = 'text-rose-500';
                
                // Muse specific coloring
                if (event.agent === 'muse') prefixColor = 'text-pink-400';

                return (
                  <motion.div
                    key={event.id || i}
                    initial={{ opacity: 0, x: -5 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex flex-col hover:bg-white/5 py-1.5 px-3 rounded-lg border border-transparent hover:border-white/5 transition-all text-[11px]"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-start gap-x-3">
                      <div className="flex items-center shrink-0">
                        <span className="text-white/20 mr-2 tabular-nums font-light">[{timeString}]</span>
                        <span className={`min-w-[70px] ${prefixColor} font-black tracking-tight`}>[{agentString}]</span>
                      </div>
                      <span className="text-green-400/80 leading-relaxed break-words flex-1">
                        <span className="text-white/20 mr-2 hidden sm:inline">❯</span>
                        {message}
                      </span>
                    </div>
                    {detail && detail !== '{}' && (
                      <div className="mt-2 ml-4 sm:ml-[110px] pl-4 border-l border-white/10 text-white/40 whitespace-pre-wrap break-all overflow-hidden text-[10px] bg-black/10 rounded py-2 pr-2">
                        {detail}
                      </div>
                    )}
                  </motion.div>
                );
              })}
              <div className="flex items-center gap-2 pt-2 opacity-50">
                <span className="w-1.5 h-3 bg-green-500 animate-[pulse_1s_infinite]" />
              </div>
            </>
          )}
        </AnimatePresence>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 5px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.1);
        }
      `}</style>
    </div>
  );
}

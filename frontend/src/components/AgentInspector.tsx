'use client';

import React, { useState } from 'react';
import { 
  Pause, 
  Play, 
  Square, 
  RotateCcw, 
  Shield, 
  Zap, 
  Activity, 
  Clock, 
  Terminal 
} from 'lucide-react';
import { AgentName, AgentStatus } from '@/lib/event-store';

const AGENT_META: Record<AgentName, { icon: string; color: string; label: string; role: string }> = {
  zeus: { icon: '⚡', color: '#C9A227', label: 'Zeus', role: 'Root Orchestrator' },
  athena: { icon: '🦉', color: '#60A5FA', label: 'Athena', role: 'Static Analysis' },
  hades: { icon: '💀', color: '#F87171', label: 'Hades', role: 'Dynamic Execution' },
  apollo: { icon: '☀️', color: '#FBBF24', label: 'Apollo', role: 'IOC Enrichment' },
  ares: { icon: '⚔️', color: '#A78BFA', label: 'Ares', role: 'Containment & IR' },
  hermes: { icon: '🌊', color: '#34D399', label: 'Hermes', role: 'Gateway & Voice' },
  artemis: { icon: '🏹', color: '#F472B6', label: 'Artemis', role: 'Sentinel Daemon' },
  hephaestus: { icon: '⚙️', color: '#94A3B8', label: 'Hephaestus', role: 'Sandbox Forge' },
};

export default function AgentInspector({ agent }: { agent: AgentStatus | null }) {
  const [isPaused, setIsPaused] = useState(false);

  if (!agent) {
    return (
      <div className="h-full glass-panel rounded-2xl flex flex-col items-center justify-center p-8 text-center text-muted/40 gap-4">
        <div className="w-16 h-16 rounded-full border border-dashed border-gold/30 flex items-center justify-center opacity-30">
          🏛️
        </div>
        <div className="space-y-1">
          <p className="text-[10px] uppercase tracking-widest font-bold">No Agent Selected</p>
          <p className="text-[9px]">Select a deity from the map to view detailed telemetry</p>
        </div>
      </div>
    );
  }

  const meta = AGENT_META[agent.name];
  const sandboxUrl = process.env.NEXT_PUBLIC_SANDBOX_URL || 'http://localhost:9000';

  const sendCommand = async (command: string) => {
    try {
      await fetch(`${sandboxUrl}/sandbox/agents/${agent.name}/command?command=${command}`, {
        method: 'POST',
      });
      console.log(`Command '${command}' sent to ${agent.name}`);
      if (command === 'pause') setIsPaused(true);
      if (command === 'resume') setIsPaused(false);
    } catch (error) {
      console.error('Failed to send agent command:', error);
    }
  };

  return (
    <div className="h-full flex flex-col glass-panel rounded-2xl overflow-hidden border-gold/20 shadow-warm bg-white/40">
      {/* Header */}
      <div className="px-6 py-8 border-b border-gold/10 bg-gradient-to-br from-gold/5 via-white/50 to-transparent relative overflow-hidden">
        {/* Decorative corner */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-gold/5 rounded-full -mr-16 -mt-16 blur-3xl" />
        
        <div className="relative flex items-start justify-between">
          <div className="flex gap-4">
            <div 
              className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl shadow-warm border-2"
              style={{ backgroundColor: 'white', borderColor: meta.color }}
            >
              {meta.icon}
            </div>
            <div className="pt-1">
              <h2 className="text-xl font-serif font-bold text-ink italic leading-tight">{meta.label}</h2>
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-gold-dark/60 mt-0.5">{meta.role}</p>
            </div>
          </div>
          
          <div className={`px-2 py-1 rounded-full text-[9px] font-bold uppercase tracking-wider border
            ${agent.state === 'active' ? 'bg-amber-100/50 text-amber-600 border-amber-200' : 
              agent.state === 'complete' ? 'bg-green-100/50 text-green-600 border-green-200' : 
              'bg-slate-100/50 text-slate-500 border-slate-200'}
          `}>
            {agent.state}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="p-6 grid grid-cols-2 gap-3 shrink-0">
        <StatItem icon={<Activity />} label="Event Count" value={agent.event_count} />
        <StatItem icon={<Clock />} label="Latency" value="12ms" />
        <StatItem icon={<Shield />} label="Precision" value="99.4%" />
        <StatItem icon={<Terminal />} label="I/O Throughput" value="1.2 KB/s" />
      </div>

      {/* Task Description */}
      <div className="px-6 py-4 flex-1 overflow-y-auto">
        <label className="text-[9px] font-bold uppercase tracking-widest text-muted/60 mb-2 block">Current Divine Objective</label>
        <div className="p-4 rounded-xl bg-gold/5 border border-gold/10 italic text-[11px] text-ink/80 leading-relaxed shadow-inner">
          {agent.current_task || `Consulting the protocols for high-fidelity ${meta.role.toLowerCase()}...`}
        </div>
        
        <label className="text-[9px] font-bold uppercase tracking-widest text-muted/60 mt-6 mb-2 block">Last Reasoned Thought</label>
        <p className="text-[10px] text-muted leading-relaxed pl-1">
          {agent.last_thought || "Processing raw bytes. Establishing grounding context via MCP..."}
        </p>
      </div>

      {/* Controls */}
      <div className="p-6 border-t border-gold/10 bg-white/50 space-y-3 shrink-0">
        <div className="flex gap-2">
          {isPaused ? (
            <ControlButton 
              icon={<Play fill="currentColor" />} 
              label="Resume" 
              onClick={() => sendCommand('resume')} 
              className="flex-1 bg-gold text-white hover:bg-gold-dark"
            />
          ) : (
            <ControlButton 
              icon={<Pause fill="currentColor" />} 
              label="Pause" 
              onClick={() => sendCommand('pause')} 
              className="flex-1 border-gold/40 text-gold hover:bg-gold/5"
            />
          )}
          <ControlButton 
            icon={<Square fill="currentColor" />} 
            label="Stop" 
            onClick={() => sendCommand('stop')} 
            className="flex-1 border-rose/30 text-rose-500 hover:bg-rose/5"
          />
        </div>
        <ControlButton 
          icon={<RotateCcw />} 
          label="Reset Agent Memory" 
          onClick={() => sendCommand('reset')} 
          className="w-full border-gold/40 text-gold hover:bg-gold/5"
        />
      </div>
    </div>
  );
}

function StatItem({ icon, label, value }: { icon: React.ReactNode, label: string, value: string | number }) {
  return (
    <div className="p-3 rounded-xl bg-white/50 border border-gold/10 flex flex-col gap-1 shadow-sm">
      <div className="text-gold-dark/40 flex items-center gap-2 scale-[0.8] origin-left">
        {icon}
        <span className="text-[10px] font-bold uppercase tracking-widest">{label}</span>
      </div>
      <div className="text-sm font- serif font-bold text-ink pl-1">{value}</div>
    </div>
  );
}

function ControlButton({ 
  icon, 
  label, 
  onClick, 
  className = "" 
}: { 
  icon: React.ReactNode, 
  label: string, 
  onClick: () => void,
  className?: string
}) {
  return (
    <button 
      onClick={onClick}
      className={`flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all active:scale-95 border ${className}`}
    >
      <span className="scale-[0.8]">{icon}</span>
      {label}
    </button>
  );
}

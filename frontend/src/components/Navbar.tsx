import { useState } from 'react';
import { Bot, RefreshCw, Copy, Check, ShieldAlert, Cpu, Database } from 'lucide-react';
import { HealthResponse } from '../types';

interface NavbarProps {
  sessionId: string;
  onNewSession: () => void;
  health: HealthResponse | null;
  healthLoading: boolean;
  isSimulating: boolean;
  onToggleSimulation: () => void;
}

export function Navbar({
  sessionId,
  onNewSession,
  health,
  healthLoading,
  isSimulating,
  onToggleSimulation,
}: NavbarProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(sessionId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <header className="sticky top-0 z-30 border-b border-slate-800/80 bg-[#090d16]/90 backdrop-blur-md px-4 py-3">
      <div className="max-w-6xl mx-auto flex flex-wrap items-center justify-between gap-3">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-slate-100 tracking-tight text-base">Nexus Gateway</span>
              <span className="text-[11px] font-mono uppercase px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                Resilient LLM
              </span>
            </div>
            <p className="text-xs text-slate-400">Multi-Key Failover & Request Caching</p>
          </div>
        </div>

        {/* Right Controls */}
        <div className="flex items-center flex-wrap gap-2.5">
          {/* Health indicator */}
          <div className="hidden sm:flex items-center space-x-2 text-xs bg-slate-900/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-300">
            <span
              className={`h-2 w-2 rounded-full ${
                health?.status === 'ok'
                  ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50 animate-pulse'
                  : healthLoading
                  ? 'bg-amber-400 animate-ping'
                  : 'bg-rose-400'
              }`}
            />
            <span className="font-medium">
              {health?.status === 'ok' ? 'Gateway Ready' : healthLoading ? 'Connecting...' : 'Offline'}
            </span>
            {health?.status === 'ok' && (
              <>
                <span className="text-slate-600">|</span>
                <span className="flex items-center text-slate-400 gap-1" title="Configured provider keys in pool">
                  <Cpu className="h-3.5 w-3.5 text-slate-400" />
                  {health.keys_configured} Keys
                </span>
                <span className="text-slate-600">|</span>
                <span className="flex items-center text-slate-400 gap-1" title="LiteLLM Disk/Memory Caching Active">
                  <Database className="h-3.5 w-3.5 text-indigo-400" />
                  Cache Active
                </span>
              </>
            )}
          </div>

          {/* Simulation Toggle Button */}
          <button
            onClick={onToggleSimulation}
            className={`text-xs font-medium px-3 py-1.5 rounded-lg border flex items-center gap-1.5 transition-colors ${
              isSimulating
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 shadow-sm shadow-amber-500/20'
                : 'bg-slate-900 text-slate-300 border-slate-800 hover:bg-slate-800/80 hover:text-slate-100'
            }`}
            title="Open Failover & Chaos Testing Panel"
          >
            <ShieldAlert className={`h-3.5 w-3.5 ${isSimulating ? 'text-amber-400 animate-pulse' : 'text-slate-400'}`} />
            <span>Simulate Failover</span>
            {isSimulating && (
              <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />
            )}
          </button>

          {/* Session ID Pill */}
          <div className="flex items-center space-x-1 bg-slate-900/90 border border-slate-800 rounded-lg px-2.5 py-1 text-xs">
            <span className="text-slate-400 font-mono text-[11px]">Session:</span>
            <span className="text-slate-200 font-mono font-medium">{sessionId}</span>
            <button
              onClick={handleCopy}
              className="text-slate-400 hover:text-slate-200 transition-colors p-1"
              title="Copy session ID"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            </button>
          </div>

          {/* New Chat Button */}
          <button
            onClick={onNewSession}
            className="text-xs font-medium px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1.5 shadow-sm shadow-blue-500/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
            title="Start fresh conversation with a new session_id"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>New Chat</span>
          </button>
        </div>
      </div>
    </header>
  );
}

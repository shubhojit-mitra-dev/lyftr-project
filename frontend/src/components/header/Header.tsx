import { useState } from 'react';
import { Copy, Check, ShieldAlert, SlidersHorizontal, PanelLeft, Plus } from 'lucide-react';
import { HealthResponse } from '../../types';

interface HeaderProps {
  sessionId: string;
  health: HealthResponse | null;
  healthLoading: boolean;
  isSimulating: boolean;
  onToggleSimulation: () => void;
  onOpenSystemPrompt: () => void;
  onToggleSidebar: () => void;
  isSidebarOpen: boolean;
  onNewSession?: () => void;
}

export function Header({
  sessionId,
  health,
  healthLoading,
  isSimulating,
  onToggleSimulation,
  onOpenSystemPrompt,
  onToggleSidebar,
  isSidebarOpen,
  onNewSession,
}: HeaderProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(sessionId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <header className="h-14 border-b border-[#262626] bg-[#000000] px-4 flex items-center justify-between gap-3 shrink-0 z-20">
      {/* Left side: sidebar toggle and model selector */}
      <div className="flex items-center gap-2.5">
        {!isSidebarOpen && (
          <button
            onClick={onToggleSidebar}
            className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-[#171717] transition-colors"
            title="Open Sidebar"
          >
            <PanelLeft className="h-4 w-4" />
          </button>
        )}

        {onNewSession && !isSidebarOpen && (
          <button
            onClick={onNewSession}
            title="Start fresh conversation session"
            className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-[#171717] transition-colors flex items-center gap-1.5 text-xs font-medium"
          >
            <Plus className="h-3.5 w-3.5 text-[#10a37f]" />
            <span>New Session</span>
          </button>
        )}

        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm text-neutral-100 tracking-tight">
            Nexus Gateway
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#10a37f]/10 text-[#10a37f] border border-[#10a37f]/20">
            nvidia/nemotron
          </span>
        </div>
      </div>

      {/* Right side controls */}
      <div className="flex items-center gap-2">
        {/* System Prompt configuration button */}
        <button
          onClick={onOpenSystemPrompt}
          className="text-xs font-medium px-2.5 py-1.5 rounded-lg bg-[#171717] hover:bg-[#212121] text-neutral-300 hover:text-white border border-[#262626] flex items-center gap-1.5 transition-colors"
          title="Configure system prompt"
        >
          <SlidersHorizontal className="h-3.5 w-3.5 text-neutral-400" />
          <span>System Prompt Configuration</span>
        </button>

        {/* Simulation toggle button */}
        <button
          onClick={onToggleSimulation}
          className={`text-xs font-medium px-2.5 py-1.5 rounded-lg border flex items-center gap-1.5 transition-colors ${
            isSimulating
              ? 'bg-amber-950/40 text-amber-300 border-amber-500/40 shadow-sm'
              : 'bg-[#171717] text-neutral-300 border-[#262626] hover:bg-[#212121] hover:text-white'
          }`}
          title="Open Failover & Chaos Testing Panel"
        >
          <ShieldAlert className={`h-3.5 w-3.5 ${isSimulating ? 'text-amber-400 animate-pulse' : 'text-neutral-400'}`} />
          <span>Simulate Failover</span>
          {isSimulating && <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />}
        </button>

        {/* Gateway health badge */}
        <div className="hidden sm:flex items-center gap-1.5 bg-[#171717] border border-[#262626] rounded-lg px-2.5 py-1.5 text-xs text-neutral-400">
          <span
            className={`h-2 w-2 rounded-full ${
              health?.status === 'ok'
                ? 'bg-[#10a37f]'
                : healthLoading
                ? 'bg-amber-400 animate-ping'
                : 'bg-rose-400'
            }`}
          />
          <span className="text-[11px] font-medium text-neutral-300">
            {health?.status === 'ok' ? 'Ready' : healthLoading ? 'Checking...' : 'Offline'}
          </span>
          {health?.status === 'ok' && (
            <span className="text-[10px] text-neutral-500">
              ({health.keys_configured} keys)
            </span>
          )}
        </div>

        {/* Session ID Pill */}
        <div className="hidden md:flex items-center gap-1 bg-[#171717] border border-[#262626] rounded-lg px-2.5 py-1 text-xs">
          <span className="text-neutral-500 font-mono text-[10px]">Session:</span>
          <span className="font-mono text-neutral-300 text-[10px]">{sessionId.slice(0, 10)}...</span>
          <button
            onClick={handleCopy}
            className="p-1 hover:text-white text-neutral-500 rounded transition-colors"
            title="Copy Session ID"
          >
            {copied ? <Check className="h-3 w-3 text-[#10a37f]" /> : <Copy className="h-3 w-3" />}
          </button>
        </div>
      </div>
    </header>
  );
}

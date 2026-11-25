import { Plus, PanelLeftClose, PanelLeft, Bot } from 'lucide-react';
import { SessionSummary } from '../../types';
import { SessionListItem } from './SessionListItem';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  sessions: SessionSummary[];
  activeSessionId: string;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
}

export function Sidebar({
  isOpen,
  onToggle,
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
}: SidebarProps) {
  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        className="fixed top-3 left-3 z-40 p-2 rounded-lg bg-[#171717] hover:bg-[#212121] text-neutral-400 hover:text-white border border-[#262626] transition-colors"
        title="Open Sidebar"
      >
        <PanelLeft className="h-4 w-4" />
      </button>
    );
  }

  return (
    <aside className="w-64 bg-[#0d0d0d] border-r border-[#262626] flex flex-col h-screen shrink-0 select-none z-30 transition-all">
      {/* Top action row */}
      <div className="p-3 flex items-center justify-between border-b border-[#1f1f1f]">
        <button
          onClick={onNewSession}
          title="Start fresh conversation session"
          className="flex-1 flex items-center justify-between px-3 py-2 rounded-lg bg-[#171717] hover:bg-[#212121] text-white text-xs font-medium border border-[#262626] transition-colors mr-2 cursor-pointer"
        >
          <span className="flex items-center gap-2">
            <Plus className="h-3.5 w-3.5 text-[#10a37f]" />
            New chat
          </span>
          <span className="text-[10px] text-neutral-500 font-mono">New Session</span>
        </button>

        <button
          onClick={onToggle}
          className="p-2 rounded-lg text-neutral-400 hover:text-white hover:bg-[#171717] transition-colors"
          title="Close Sidebar"
        >
          <PanelLeftClose className="h-4 w-4" />
        </button>
      </div>

      {/* History section */}
      <div className="flex-1 overflow-y-auto px-2 py-3 space-y-1">
        <div className="px-2 pb-1 text-[10px] font-semibold text-neutral-500 tracking-wider uppercase">
          Conversations
        </div>

        {sessions.length === 0 ? (
          <div className="text-center py-8 text-neutral-600 text-xs">
            No previous conversations
          </div>
        ) : (
          sessions.map((session) => (
            <SessionListItem
              key={session.id}
              session={session}
              isActive={session.id === activeSessionId}
              onSelect={onSelectSession}
              onDelete={onDeleteSession}
            />
          ))
        )}
      </div>

      {/* Footer Branding */}
      <div className="p-3 border-t border-[#1f1f1f] flex items-center gap-2 text-xs text-neutral-400">
        <div className="h-6 w-6 rounded-md bg-[#171717] border border-[#262626] flex items-center justify-center text-[#10a37f]">
          <Bot className="h-3.5 w-3.5" />
        </div>
        <div className="flex-1 truncate">
          <p className="text-[11px] font-medium text-neutral-200">Nexus Gateway</p>
          <p className="text-[10px] text-neutral-500">Resilient LLM Chat</p>
        </div>
      </div>
    </aside>
  );
}

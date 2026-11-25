import { MessageSquare, Trash2 } from 'lucide-react';
import { SessionSummary } from '../../types';

interface SessionListItemProps {
  session: SessionSummary;
  isActive: boolean;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
}

export function SessionListItem({
  session,
  isActive,
  onSelect,
  onDelete,
}: SessionListItemProps) {
  return (
    <div
      onClick={() => onSelect(session.id)}
      className={`group relative flex items-center justify-between gap-2.5 px-3 py-2 rounded-lg text-xs cursor-pointer transition-all ${
        isActive
          ? 'bg-[#212121] text-white font-medium'
          : 'text-neutral-400 hover:bg-[#171717] hover:text-neutral-200'
      }`}
    >
      <div className="flex items-center gap-2.5 truncate min-w-0">
        <MessageSquare
          className={`h-3.5 w-3.5 shrink-0 ${
            isActive ? 'text-[#10a37f]' : 'text-neutral-500 group-hover:text-neutral-400'
          }`}
        />
        <span className="truncate">{session.title}</span>
      </div>

      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete(session.id);
        }}
        className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 text-neutral-500 rounded transition-opacity"
        title="Delete conversation"
      >
        <Trash2 className="h-3 w-3" />
      </button>
    </div>
  );
}

import { X } from 'lucide-react';

interface SystemPromptModalProps {
  isOpen: boolean;
  systemPrompt: string;
  onSystemPromptChange: (val: string) => void;
  onClose: () => void;
}

export function SystemPromptModal({
  isOpen,
  systemPrompt,
  onSystemPromptChange,
  onClose,
}: SystemPromptModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-[#171717] border border-[#262626] rounded-2xl p-5 shadow-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-[#262626] pb-3">
          <div>
            <h3 className="text-sm font-semibold text-white">System Prompt Configuration</h3>
            <p className="text-xs text-neutral-400">
              Overrides default session behavior sent to the primary LLM model.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-[#212121] transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div>
          <textarea
            data-testid="system-prompt-input"
            value={systemPrompt}
            onChange={(e) => onSystemPromptChange(e.target.value)}
            placeholder="e.g. You are a senior software architect specializing in distributed systems. Answer concisely."
            rows={4}
            className="w-full bg-[#0d0d0d] border border-[#262626] rounded-xl p-3 text-xs text-neutral-200 placeholder:text-neutral-500 focus:outline-none focus:border-[#4f4f4f] leading-relaxed resize-none"
          />
        </div>

        <div className="flex items-center justify-end gap-2 pt-2">
          <button
            onClick={() => onSystemPromptChange('')}
            className="px-3 py-1.5 text-xs text-neutral-400 hover:text-white transition-colors"
          >
            Clear
          </button>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-white text-black hover:bg-neutral-200 text-xs font-medium transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}

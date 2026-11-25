import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { ArrowUp } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSendMessage, isLoading, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-focus on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading || disabled) return;

    // MANDATORY REQUIREMENT: data-testid="chat-input" MUST be cleared immediately after sending
    setInput('');

    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    onSendMessage(trimmed);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const target = e.target;
    target.style.height = 'auto';
    target.style.height = `${Math.min(target.scrollHeight, 180)}px`;
  };

  const canSend = input.trim().length > 0 && !isLoading && !disabled;

  return (
    <div className="w-full bg-[#000000] border-t border-[#1f1f1f] p-4">
      <div className="max-w-3xl mx-auto">
        <div className="relative flex items-end bg-[#212121] border border-[#2f2f2f] rounded-3xl p-2.5 focus-within:border-[#4f4f4f] transition-all">
          <textarea
            ref={textareaRef}
            data-testid="chat-input"
            value={input}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            placeholder="Message Nexus Gateway..."
            rows={1}
            disabled={disabled}
            className="w-full resize-none bg-transparent px-3 py-1.5 text-sm text-neutral-100 placeholder:text-neutral-500 focus:outline-none max-h-44 leading-relaxed"
          />

          <button
            data-testid="send-button"
            onClick={handleSend}
            disabled={!canSend}
            className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 transition-all ${
              canSend
                ? 'bg-white text-black hover:bg-neutral-200 cursor-pointer active:scale-95'
                : 'bg-[#2f2f2f] text-neutral-600 cursor-not-allowed'
            }`}
            title="Send message (Enter)"
          >
            <ArrowUp className="h-4 w-4 stroke-[2.5]" />
          </button>
        </div>
        <div className="text-[11px] text-center text-neutral-500 mt-2">
          Nexus LLM Gateway can make mistakes. Verify important failover and token telemetry.
        </div>
      </div>
    </div>
  );
}

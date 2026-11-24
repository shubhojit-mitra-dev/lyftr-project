import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Send, CornerDownLeft, Sparkles } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSendMessage, isLoading, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-focus input on mount
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
    // Enter without Shift sends
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    // Auto-grow height up to 160px
    const target = e.target;
    target.style.height = 'auto';
    target.style.height = `${Math.min(target.scrollHeight, 160)}px`;
  };

  const quickPrompts = [
    'What is the capital of France?',
    'Explain how multi-key failover works in LiteLLM.',
    'Write a concise Python function to calculate fibonacci numbers.',
  ];

  return (
    <div className="border-t border-slate-800/80 bg-[#090d16]/95 backdrop-blur-md px-4 pt-3 pb-4">
      <div className="max-w-4xl mx-auto space-y-2.5">
        {/* Quick prompt suggestions */}
        <div className="hidden sm:flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px] text-slate-400">
          <span className="flex items-center gap-1 text-slate-500 shrink-0">
            <Sparkles className="h-3 w-3 text-blue-400" />
            Quick Test:
          </span>
          {quickPrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => {
                setInput(prompt);
                textareaRef.current?.focus();
              }}
              className="truncate max-w-[260px] bg-slate-900 hover:bg-slate-800 border border-slate-800/80 hover:border-slate-700 px-2.5 py-1 rounded-full text-slate-300 hover:text-white transition-colors"
              title={prompt}
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input box */}
        <div className="relative flex items-end bg-slate-900 border border-slate-800 rounded-2xl focus-within:border-blue-500/70 focus-within:ring-1 focus-within:ring-blue-500/20 shadow-lg shadow-black/40 transition-all p-2">
          <textarea
            ref={textareaRef}
            data-testid="chat-input"
            value={input}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
            rows={1}
            disabled={disabled}
            className="w-full resize-none bg-transparent px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none max-h-40 leading-relaxed"
          />

          <button
            data-testid="send-button"
            onClick={handleSend}
            disabled={!input.trim() || isLoading || disabled}
            className={`h-10 w-10 rounded-xl flex items-center justify-center shrink-0 transition-all ${
              input.trim() && !isLoading && !disabled
                ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/30 cursor-pointer active:scale-95'
                : 'bg-slate-800/80 text-slate-600 cursor-not-allowed'
            }`}
            title="Send Message"
          >
            {isLoading ? (
              <div className="h-4 w-4 border-2 border-slate-400 border-t-white rounded-full animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </button>
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-500 px-1">
          <div className="flex items-center gap-1">
            <CornerDownLeft className="h-3 w-3" />
            <span>Press Enter to send, Shift+Enter for newline</span>
          </div>
          <span>Max 4000 characters</span>
        </div>
      </div>
    </div>
  );
}

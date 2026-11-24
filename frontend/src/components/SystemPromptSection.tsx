import { useState } from 'react';
import { Sliders, ChevronDown, ChevronUp } from 'lucide-react';

interface SystemPromptSectionProps {
  systemPrompt: string;
  onSystemPromptChange: (val: string) => void;
}

export function SystemPromptSection({
  systemPrompt,
  onSystemPromptChange,
}: SystemPromptSectionProps) {
  const [isOpen, setIsOpen] = useState(false);

  const presets = [
    { label: 'Concise Expert', prompt: 'You are a concise, highly knowledgeable technical assistant. Answer directly and precisely.' },
    { label: 'Senior Architect', prompt: 'You are a Staff Principal Systems Architect. Provide comprehensive architectural insights, resilience patterns, and clean code examples.' },
    { label: 'Creative Writer', prompt: 'You are an engaging creative writer. Express responses with vivid imagery and storytelling.' },
  ];

  return (
    <div className="border-b border-slate-800/80 bg-slate-950/40">
      <div className="max-w-4xl mx-auto px-4 py-2">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center justify-between w-full text-xs text-slate-400 hover:text-slate-200 transition-colors py-1"
        >
          <div className="flex items-center space-x-2">
            <Sliders className="h-3.5 w-3.5 text-blue-400" />
            <span className="font-medium">System Prompt Configuration</span>
            {systemPrompt.trim() && (
              <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[10px] px-2 py-0.5 rounded-full">
                Custom Prompt Active ({systemPrompt.length} chars)
              </span>
            )}
          </div>
          <div className="flex items-center space-x-1 text-slate-500">
            <span>{isOpen ? 'Collapse' : 'Expand'}</span>
            {isOpen ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
          </div>
        </button>

        {isOpen && (
          <div className="mt-2 pb-3 space-y-2.5 animate-in fade-in duration-150">
            <div>
              <textarea
                data-testid="system-prompt-input"
                value={systemPrompt}
                onChange={(e) => onSystemPromptChange(e.target.value)}
                placeholder="Optional: Set a custom system prompt to guide the assistant's persona or instructions for this session..."
                rows={3}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-blue-500/60 transition-colors font-sans"
              />
            </div>

            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-[11px] text-slate-500">Presets:</span>
                {presets.map((p) => (
                  <button
                    key={p.label}
                    onClick={() => onSystemPromptChange(p.prompt)}
                    className="text-[11px] px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800 hover:text-slate-100 transition-colors"
                  >
                    {p.label}
                  </button>
                ))}
              </div>

              {systemPrompt && (
                <button
                  onClick={() => onSystemPromptChange('')}
                  className="text-[11px] text-rose-400 hover:text-rose-300 transition-colors"
                >
                  Clear prompt
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

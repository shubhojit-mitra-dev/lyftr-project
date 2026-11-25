import { Sparkles } from 'lucide-react';

interface WelcomeHeroProps {
  onSelectPrompt: (prompt: string) => void;
}

export function WelcomeHero({ onSelectPrompt }: WelcomeHeroProps) {
  const suggestions = [
    {
      title: 'General Knowledge',
      prompt: 'What is the capital of France?',
    },
    {
      title: 'System Architecture',
      prompt: 'Explain how multi-key failover works in LiteLLM.',
    },
    {
      title: 'Python Function',
      prompt: 'Write a concise Python function to calculate fibonacci numbers.',
    },
    {
      title: 'Quantum Computing',
      prompt: 'Explain quantum computing in one simple sentence.',
    },
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] max-w-2xl mx-auto text-center px-4 py-8">
      {/* OpenAI minimal circular emblem */}
      <div className="h-12 w-12 rounded-full bg-[#171717] border border-[#262626] flex items-center justify-center mb-6 shadow-sm">
        <Sparkles className="h-6 w-6 text-[#10a37f]" />
      </div>

      <h1 className="text-2xl font-semibold tracking-tight text-white mb-2">
        What can I help you with today?
      </h1>
      <p className="text-xs text-neutral-400 max-w-md leading-relaxed mb-8">
        Dual-provider failover with NVIDIA NIM & Google Gemini, powered by LiteLLM response caching and SQLite session persistence.
      </p>

      {/* Suggestion cards in OpenAI style */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full text-left">
        {suggestions.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPrompt(item.prompt)}
            className="p-3.5 rounded-xl bg-[#171717] hover:bg-[#212121] border border-[#262626] hover:border-[#383838] transition-all group"
          >
            <div className="text-[11px] font-medium text-neutral-300 group-hover:text-white mb-1">
              {item.title}
            </div>
            <div className="text-xs text-neutral-500 group-hover:text-neutral-400 line-clamp-1">
              {item.prompt}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

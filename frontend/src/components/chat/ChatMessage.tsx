import ReactMarkdown from 'react-markdown';
import { AlertTriangle, Zap, Sparkles, Clock, ShieldCheck } from 'lucide-react';
import { MessageItem } from '../../types';

interface ChatMessageProps {
  message: MessageItem;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isError = message.role === 'error' || message.isError;

  if (isUser) {
    return (
      <div className="flex justify-end mb-6">
        <div className="max-w-[85%] md:max-w-[70%] rounded-2xl bg-[#212121] text-neutral-100 px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap border border-[#2f2f2f]">
          {message.content}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex justify-start mb-6">
        <div className="max-w-[90%] md:max-w-[80%] flex items-start gap-3">
          <div className="h-7 w-7 rounded-full bg-rose-950/80 border border-rose-500/40 flex items-center justify-center shrink-0 text-rose-400 mt-0.5">
            <AlertTriangle className="h-3.5 w-3.5" />
          </div>
          <div className="rounded-2xl bg-[#1f1215] border border-rose-900/60 text-rose-200 px-4 py-3 text-xs leading-relaxed space-y-1">
            <div className="font-semibold text-rose-300">Service Alert</div>
            <p className="text-neutral-300">{message.content}</p>
          </div>
        </div>
      </div>
    );
  }

  // Assistant Message (MUST contain data-testid="assistant-message" and the 5 exact child test-ids)
  const meta = message.metadata;
  const isCache = meta?.resolution_source === 'LLM_CACHE';

  return (
    <div data-testid="assistant-message" className="flex justify-start mb-6">
      <div className="flex items-start max-w-[95%] md:max-w-[85%] gap-3">
        {/* OpenAI emblem avatar */}
        <div className="h-7 w-7 rounded-full bg-[#171717] border border-[#262626] flex items-center justify-center shrink-0 text-[#10a37f] shadow-sm mt-0.5">
          <Sparkles className="h-3.5 w-3.5" />
        </div>

        <div className="flex-1 space-y-2 overflow-hidden">
          {/* Main content markdown */}
          <div className="text-neutral-200 text-sm leading-relaxed prose prose-invert max-w-none prose-p:my-1.5 prose-pre:my-2 prose-pre:bg-[#121212] prose-pre:border prose-pre:border-[#262626]">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>

          {/* Telemetry metadata bar */}
          {meta && (
            <div className="flex flex-wrap items-center gap-1.5 pt-1 text-xs">
              {/* Resolution source badge */}
              <div
                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold tracking-wide border ${
                  isCache
                    ? 'bg-purple-950/30 border-purple-500/40 text-purple-300'
                    : 'bg-[#10a37f]/10 border-[#10a37f]/30 text-[#10a37f]'
                }`}
              >
                {isCache ? (
                  <Zap className="h-3 w-3 text-purple-400" />
                ) : (
                  <Sparkles className="h-3 w-3 text-[#10a37f]" />
                )}
                <span data-testid="meta-source">{meta.resolution_source}</span>
              </div>

              {/* Model */}
              <div className="inline-flex items-center gap-1 bg-[#171717] border border-[#262626] px-2 py-0.5 rounded-md text-[10px] text-neutral-400">
                <span className="text-neutral-500">model:</span>
                <span data-testid="meta-model" className="font-mono text-neutral-200">
                  {meta.model}
                </span>
              </div>

              {/* Latency */}
              <div className="inline-flex items-center gap-1 bg-[#171717] border border-[#262626] px-2 py-0.5 rounded-md text-[10px] text-neutral-400">
                <Clock className="h-3 w-3 text-neutral-500" />
                <span data-testid="meta-latency" className="font-mono text-neutral-200">
                  {meta.latency_ms} ms
                </span>
              </div>

              {/* Tokens: Input & Output */}
              <div className="inline-flex items-center gap-1 bg-[#171717] border border-[#262626] px-2 py-0.5 rounded-md text-[10px] text-neutral-400">
                <span className="text-neutral-500">in:</span>
                <span data-testid="meta-input-tokens" className="font-mono text-neutral-200">
                  {meta.input_tokens}
                </span>
                <span className="text-neutral-600">|</span>
                <span className="text-neutral-500">out:</span>
                <span data-testid="meta-output-tokens" className="font-mono text-neutral-200">
                  {meta.output_tokens}
                </span>
              </div>

              {/* Key ID badge */}
              {meta.key_id && (
                <div className="inline-flex items-center gap-1 bg-[#171717] border border-[#262626] px-2 py-0.5 rounded-md text-[10px] text-neutral-400">
                  <span className="text-neutral-500">key:</span>
                  <span className="font-mono text-neutral-300">{meta.key_id}</span>
                </div>
              )}

              {/* Failover notice if fallback attempts occurred */}
              {meta.fallback_attempts > 0 && (
                <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] bg-amber-950/30 border border-amber-500/40 text-amber-300">
                  <ShieldCheck className="h-3 w-3 text-amber-400" />
                  <span>Failover succeeded ({meta.fallback_attempts} fallback)</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

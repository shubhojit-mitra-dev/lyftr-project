import ReactMarkdown from 'react-markdown';
import { User, Bot, AlertTriangle, Zap, CheckCircle2, Clock, Sparkles } from 'lucide-react';
import { MessageItem } from '../types';

interface ChatMessageProps {
  message: MessageItem;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isError = message.role === 'error' || message.isError;

  if (isUser) {
    return (
      <div className="flex justify-end mb-4 group">
        <div className="flex items-start max-w-[85%] md:max-w-[75%] gap-2.5 flex-row-reverse">
          <div className="h-8 w-8 rounded-full bg-blue-600/30 border border-blue-500/40 flex items-center justify-center shrink-0 text-blue-300">
            <User className="h-4 w-4" />
          </div>
          <div className="rounded-2xl rounded-tr-sm bg-gradient-to-br from-blue-600 to-indigo-600 text-white px-4 py-2.5 shadow-md shadow-blue-900/10 text-sm whitespace-pre-wrap leading-relaxed">
            {message.content}
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex justify-start mb-4">
        <div className="flex items-start max-w-[90%] md:max-w-[80%] gap-2.5">
          <div className="h-8 w-8 rounded-full bg-rose-950/80 border border-rose-500/40 flex items-center justify-center shrink-0 text-rose-400">
            <AlertTriangle className="h-4 w-4" />
          </div>
          <div className="rounded-2xl rounded-tl-sm bg-rose-950/40 border border-rose-900/60 text-rose-200 px-4 py-3 shadow-lg shadow-rose-950/20 text-sm space-y-1">
            <div className="font-semibold text-rose-300 text-xs flex items-center gap-1.5">
              <span>Service Alert</span>
            </div>
            <p className="text-slate-300 text-xs leading-relaxed">{message.content}</p>
          </div>
        </div>
      </div>
    );
  }

  // Assistant Message (MUST contain data-testid="assistant-message" container and the 5 exact child test-ids)
  const meta = message.metadata;
  const isCache = meta?.resolution_source === 'LLM_CACHE';

  return (
    <div data-testid="assistant-message" className="flex justify-start mb-6 group">
      <div className="flex items-start max-w-[95%] md:max-w-[85%] gap-2.5">
        <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 text-slate-300 shadow-sm mt-0.5">
          <Bot className="h-4 w-4" />
        </div>

        <div className="flex-1 space-y-2">
          {/* Main message bubble */}
          <div className="rounded-2xl rounded-tl-sm bg-slate-900/90 border border-slate-800/80 px-4 py-3 text-slate-200 shadow-md text-sm leading-relaxed prose prose-invert max-w-none prose-p:my-1.5 prose-pre:my-2 prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>

          {/* Telemetry and Metadata Strip */}
          {meta && (
            <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
              {/* Resolution source badge */}
              <div
                className={`flex items-center gap-1 px-2.5 py-0.5 rounded-full border text-[11px] font-semibold tracking-wide ${
                  isCache
                    ? 'bg-purple-950/40 border-purple-500/40 text-purple-300 shadow-sm shadow-purple-950/30'
                    : 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300 shadow-sm shadow-emerald-950/30'
                }`}
              >
                {isCache ? (
                  <Zap className="h-3 w-3 text-purple-400" />
                ) : (
                  <Sparkles className="h-3 w-3 text-emerald-400" />
                )}
                {/* Contract requirement: exactly LIVE_INFERENCE or LLM_CACHE */}
                <span data-testid="meta-source">{meta.resolution_source}</span>
              </div>

              {/* Model */}
              <div className="flex items-center gap-1 bg-slate-900 border border-slate-800/80 px-2 py-0.5 rounded-md text-[11px] text-slate-300">
                <span className="text-slate-500">model:</span>
                <span data-testid="meta-model" className="font-mono text-slate-200">
                  {meta.model}
                </span>
              </div>

              {/* Latency */}
              <div className="flex items-center gap-1 bg-slate-900 border border-slate-800/80 px-2 py-0.5 rounded-md text-[11px] text-slate-300">
                <Clock className="h-3 w-3 text-slate-500" />
                {/* Contract requirement: latency, e.g. 812 ms */}
                <span data-testid="meta-latency" className="font-mono text-slate-200">
                  {meta.latency_ms} ms
                </span>
              </div>

              {/* Tokens: Input & Output */}
              <div className="flex items-center gap-1 bg-slate-900 border border-slate-800/80 px-2 py-0.5 rounded-md text-[11px] text-slate-300">
                <span className="text-slate-500">in:</span>
                <span data-testid="meta-input-tokens" className="font-mono text-slate-200">
                  {meta.input_tokens}
                </span>
                <span className="text-slate-600">/</span>
                <span className="text-slate-500">out:</span>
                <span data-testid="meta-output-tokens" className="font-mono text-slate-200">
                  {meta.output_tokens}
                </span>
              </div>

              {/* Key ID info */}
              {meta.key_id ? (
                <div className="flex items-center gap-1 bg-slate-900/60 border border-slate-800/60 px-2 py-0.5 rounded-md text-[10px] text-slate-400 font-mono">
                  <span>key: {meta.key_id}</span>
                </div>
              ) : isCache ? (
                <div className="flex items-center gap-1 bg-purple-950/20 border border-purple-800/30 px-2 py-0.5 rounded-md text-[10px] text-purple-300 font-mono">
                  <span>zero key cost</span>
                </div>
              ) : null}

              {/* Fallback Attempts Indicator if > 0 */}
              {meta.fallback_attempts > 0 && (
                <div className="flex items-center gap-1 bg-amber-950/40 border border-amber-500/40 px-2 py-0.5 rounded-md text-[11px] text-amber-300 font-medium">
                  <CheckCircle2 className="h-3 w-3 text-amber-400" />
                  <span>Failover succeeded ({meta.fallback_attempts} fallback{meta.fallback_attempts > 1 ? 's' : ''})</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

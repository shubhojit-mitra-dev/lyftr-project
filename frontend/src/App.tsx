import { useState, useEffect, useRef } from 'react';
import { Navbar } from './components/Navbar';
import { SimulationPanel } from './components/SimulationPanel';
import { SystemPromptSection } from './components/SystemPromptSection';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { ErrorBoundary } from './components/ErrorBoundary';
import { MessageItem, HealthResponse } from './types';
import { getHealth, sendChatMessage, ApiError } from './api';
import { generateSessionId } from './utils';
import { Bot, ShieldCheck, Zap } from 'lucide-react';

export default function App() {
  // Session lifecycle: PRD requires client to generate a new session_id on initial page load
  const [sessionId, setSessionId] = useState<string>(() => generateSessionId());
  const [systemPrompt, setSystemPrompt] = useState<string>('');
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Simulation header state (X-Simulate-Failure)
  const [simulationHeader, setSimulationHeader] = useState<string | null>(null);
  const [isSimPanelOpen, setIsSimPanelOpen] = useState<boolean>(false);

  // Health status
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState<boolean>(true);

  // Scroll anchor
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on messages or loading update
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Initial health check
  useEffect(() => {
    let isMounted = true;
    async function checkHealth() {
      try {
        setHealthLoading(true);
        const data = await getHealth();
        if (isMounted) {
          setHealth(data);
        }
      } catch (err) {
        console.warn('Backend gateway health check pending/failed:', err);
      } finally {
        if (isMounted) setHealthLoading(false);
      }
    }

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // New Chat handler
  const handleNewSession = () => {
    const nextSessionId = generateSessionId();
    setSessionId(nextSessionId);
    setMessages([]);
  };

  // Send message handler
  const handleSendMessage = async (userText: string) => {
    if (!userText.trim() || isLoading) return;

    const userMessage: MessageItem = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
      role: 'user',
      content: userText,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(
        {
          session_id: sessionId,
          message: userText,
          system_prompt: systemPrompt.trim() ? systemPrompt.trim() : undefined,
        },
        simulationHeader
      );

      const assistantMessage: MessageItem = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
        role: 'assistant',
        content: response.reply,
        metadata: response.metadata,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: unknown) {
      let errorMessage = 'An unexpected error occurred while communicating with the gateway.';
      if (err instanceof ApiError) {
        errorMessage = `HTTP ${err.status}: ${err.detail}`;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }

      const errorTurn: MessageItem = {
        id: `err-${Date.now()}`,
        role: 'error',
        content: errorMessage,
        isError: true,
        timestamp: new Date().toISOString(),
      };

      // PRD requirement: Errors (422, 503) show as a readable message in the chat, never a blank screen
      setMessages((prev) => [...prev, errorTurn]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ErrorBoundary>
      <div className="flex flex-col h-screen bg-[#090d16] text-slate-100 overflow-hidden font-sans">
        {/* Navigation Bar */}
        <Navbar
          sessionId={sessionId}
          onNewSession={handleNewSession}
          health={health}
          healthLoading={healthLoading}
          isSimulating={Boolean(simulationHeader)}
          onToggleSimulation={() => setIsSimPanelOpen((prev) => !prev)}
        />

        {/* Global Armed Simulation Banner when panel is closed */}
        {!isSimPanelOpen && simulationHeader && (
          <div className="bg-amber-950/80 border-b border-amber-500/40 px-4 py-2 text-xs text-amber-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-amber-400 animate-pulse" />
              <span>
                <strong>Failover Simulation Active:</strong> Header{' '}
                <code className="font-mono bg-amber-900/60 px-1.5 py-0.5 rounded text-amber-100 border border-amber-500/30">
                  X-Simulate-Failure: {simulationHeader}
                </code>{' '}
                armed on outgoing requests.
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsSimPanelOpen(true)}
                className="underline hover:text-white"
              >
                Change
              </button>
              <span className="text-amber-500">|</span>
              <button
                onClick={() => setSimulationHeader(null)}
                className="hover:text-white font-medium"
              >
                Disarm
              </button>
            </div>
          </div>
        )}

        {/* Failover / Chaos Testing Panel */}
        {isSimPanelOpen && (
          <SimulationPanel
            simulationHeader={simulationHeader}
            onSetSimulationHeader={setSimulationHeader}
            onClose={() => setIsSimPanelOpen(false)}
          />
        )}

        {/* System Prompt Bar */}
        <SystemPromptSection
          systemPrompt={systemPrompt}
          onSystemPromptChange={setSystemPrompt}
        />

        {/* Main Chat Stream Container */}
        <main className="flex-1 overflow-y-auto px-4 py-6 scroll-smooth">
          <div className="max-w-4xl mx-auto">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center min-h-[50vh] text-center px-4 py-12">
                <div className="h-16 w-16 rounded-2xl bg-gradient-to-tr from-blue-600/20 via-indigo-600/30 to-purple-600/20 border border-blue-500/30 flex items-center justify-center mb-5 shadow-xl shadow-blue-900/10">
                  <Bot className="h-8 w-8 text-blue-400" />
                </div>
                <h2 className="text-xl font-bold tracking-tight text-slate-100 mb-2">
                  Resilient AI Gateway
                </h2>
                <p className="text-sm text-slate-400 max-w-md leading-relaxed mb-6">
                  Experience multi-key failover across NVIDIA NIM and Google Gemini with sub-millisecond response caching.
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full text-left">
                  <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                    <div className="flex items-center space-x-2 text-xs font-semibold text-emerald-400">
                      <Zap className="h-4 w-4" />
                      <span>Request Caching</span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      Subsequent identical prompts resolve instantly with <code className="text-purple-300">LLM_CACHE</code> telemetry and zero token cost.
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                    <div className="flex items-center space-x-2 text-xs font-semibold text-amber-400">
                      <ShieldCheck className="h-4 w-4" />
                      <span>Automatic Failover</span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      Primary key 429/5xx errors automatically failover to secondary backup models seamlessly.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((msg) => (
                  <ChatMessage key={msg.id} message={msg} />
                ))}
              </div>
            )}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex justify-start mb-6 animate-pulse">
                <div className="flex items-center space-x-3 bg-slate-900/80 border border-slate-800/80 rounded-2xl px-4 py-3 shadow-md">
                  <div className="h-2 w-2 rounded-full bg-blue-500 animate-bounce" />
                  <div className="h-2 w-2 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.2s]" />
                  <div className="h-2 w-2 rounded-full bg-purple-500 animate-bounce [animation-delay:0.4s]" />
                  <span className="text-xs text-slate-400 font-medium pl-1">
                    {simulationHeader ? 'Executing resilient failover query...' : 'Querying model...'}
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </main>

        {/* Input Bar */}
        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
    </ErrorBoundary>
  );
}

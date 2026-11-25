import { useState } from 'react';
import { Sidebar } from './components/sidebar/Sidebar';
import { Header } from './components/header/Header';
import { ChatStream } from './components/chat/ChatStream';
import { ChatInput } from './components/chat/ChatInput';
import { SystemPromptModal } from './components/header/SystemPromptModal';
import { SimulationPanel } from './components/simulation/SimulationPanel';
import { SimulationBanner } from './components/simulation/SimulationBanner';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { useHealth } from './hooks/useHealth';
import { useSessions } from './hooks/useSessions';
import { useChat } from './hooks/useChat';

export default function App() {
  const [systemPrompt, setSystemPrompt] = useState<string>('');
  const [isSystemPromptOpen, setIsSystemPromptOpen] = useState<boolean>(false);
  const [simulationHeader, setSimulationHeader] = useState<string | null>(null);
  const [isSimPanelOpen, setIsSimPanelOpen] = useState<boolean>(false);

  const { health, healthLoading } = useHealth();
  const {
    sessionId,
    sessions,
    isSidebarOpen,
    startNewSession,
    registerSessionActivity,
    loadSessionHistory,
    deleteSession,
    toggleSidebar,
  } = useSessions();

  const {
    messages,
    isLoading,
    messagesEndRef,
    sendMessage,
    clearMessages,
    replaceMessages,
  } = useChat({
    sessionId,
    systemPrompt,
    simulationHeader,
    onMessageSent: (text) => registerSessionActivity(sessionId, text),
  });

  const handleNewSession = () => {
    startNewSession();
    clearMessages();
  };

  const handleSelectSession = async (targetId: string) => {
    if (targetId === sessionId) return;
    const history = await loadSessionHistory(targetId);
    replaceMessages(history);
  };

  return (
    <ErrorBoundary>
      <div className="flex h-screen bg-[#000000] text-neutral-100 overflow-hidden font-sans">
        {/* Collapsible conversation history sidebar */}
        <Sidebar
          isOpen={isSidebarOpen}
          onToggle={toggleSidebar}
          sessions={sessions}
          activeSessionId={sessionId}
          onSelectSession={handleSelectSession}
          onNewSession={handleNewSession}
          onDeleteSession={deleteSession}
        />

        {/* Main conversational workspace */}
        <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#000000]">
          <Header
            sessionId={sessionId}
            health={health}
            healthLoading={healthLoading}
            isSimulating={Boolean(simulationHeader)}
            onToggleSimulation={() => setIsSimPanelOpen((prev) => !prev)}
            onOpenSystemPrompt={() => setIsSystemPromptOpen(true)}
            onToggleSidebar={toggleSidebar}
            isSidebarOpen={isSidebarOpen}
            onNewSession={handleNewSession}
          />

          {/* Banner when failure simulation is armed */}
          {simulationHeader && !isSimPanelOpen && (
            <SimulationBanner
              simulationHeader={simulationHeader}
              onOpenPanel={() => setIsSimPanelOpen(true)}
              onDisarm={() => setSimulationHeader(null)}
            />
          )}

          {/* Interactive message stream */}
          <ChatStream
            messages={messages}
            isLoading={isLoading}
            messagesEndRef={messagesEndRef}
            onSelectPrompt={(prompt) => sendMessage(prompt)}
          />

          {/* Fixed bottom input */}
          <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />

          {/* System Prompt configuration drawer/modal */}
          <SystemPromptModal
            isOpen={isSystemPromptOpen}
            systemPrompt={systemPrompt}
            onSystemPromptChange={setSystemPrompt}
            onClose={() => setIsSystemPromptOpen(false)}
          />

          {/* Failover chaos testing modal */}
          {isSimPanelOpen && (
            <SimulationPanel
              simulationHeader={simulationHeader}
              onSetSimulationHeader={setSimulationHeader}
              onClose={() => setIsSimPanelOpen(false)}
            />
          )}
        </div>
      </div>
    </ErrorBoundary>
  );
}

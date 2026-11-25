import { RefObject } from 'react';
import { MessageItem } from '../../types';
import { ChatMessage } from './ChatMessage';
import { WelcomeHero } from './WelcomeHero';
import { Loader2 } from 'lucide-react';

interface ChatStreamProps {
  messages: MessageItem[];
  isLoading: boolean;
  messagesEndRef: RefObject<HTMLDivElement | null>;
  onSelectPrompt: (prompt: string) => void;
}

export function ChatStream({
  messages,
  isLoading,
  messagesEndRef,
  onSelectPrompt,
}: ChatStreamProps) {
  if (messages.length === 0) {
    return (
      <div className="flex-1 overflow-y-auto">
        <WelcomeHero onSelectPrompt={onSelectPrompt} />
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="max-w-3xl mx-auto space-y-2">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="flex items-center gap-2.5 text-xs text-neutral-400 py-3">
            <Loader2 className="h-4 w-4 animate-spin text-[#10a37f]" />
            <span>Generating response...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

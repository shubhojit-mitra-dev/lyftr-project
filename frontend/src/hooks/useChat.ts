import { useState, useRef, useEffect, useCallback } from 'react';
import { MessageItem } from '../types';
import { sendChatMessage, ApiError } from '../services/api';

interface UseChatProps {
  sessionId: string;
  systemPrompt: string;
  simulationHeader: string | null;
  onMessageSent?: (text: string) => void;
}

export function useChat({
  sessionId,
  systemPrompt,
  simulationHeader,
  onMessageSent,
}: UseChatProps) {
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isLoading) return;

      const userMessage: MessageItem = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
        role: 'user',
        content: trimmed,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      if (onMessageSent) {
        onMessageSent(trimmed);
      }

      try {
        const response = await sendChatMessage(
          {
            session_id: sessionId,
            message: trimmed,
            system_prompt: systemPrompt.trim() ? systemPrompt.trim() : undefined,
          },
          simulationHeader
        );

        const assistantMessage: MessageItem = {
          id: `msg-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
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

        // PRD requirement: Errors show as readable message in the chat, never blank screen
        setMessages((prev) => [...prev, errorTurn]);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, systemPrompt, simulationHeader, isLoading, onMessageSent]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const replaceMessages = useCallback((newMessages: MessageItem[]) => {
    setMessages(newMessages);
  }, []);

  return {
    messages,
    isLoading,
    messagesEndRef,
    sendMessage,
    clearMessages,
    replaceMessages,
  };
}

import { useState, useCallback, useEffect } from 'react';
import { SessionSummary, MessageItem } from '../types';
import { generateSessionId } from '../utils';
import { getSessionMessages } from '../services/api';
import {
  loadSavedSessions,
  upsertSession,
  deleteSessionFromStorage,
} from '../services/sessionStorage';

export function useSessions() {
  const [sessionId, setSessionId] = useState<string>(() => generateSessionId());
  const [sessions, setSessions] = useState<SessionSummary[]>(() => loadSavedSessions());
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);

  // Sync sessions list
  useEffect(() => {
    setSessions(loadSavedSessions());
  }, []);

  const startNewSession = useCallback(() => {
    const nextId = generateSessionId();
    setSessionId(nextId);
    return nextId;
  }, []);

  const registerSessionActivity = useCallback((id: string, firstMessageText: string) => {
    const title = firstMessageText.length > 32 ? `${firstMessageText.slice(0, 32)}...` : firstMessageText;
    const summary: SessionSummary = {
      id,
      title: title || 'New Conversation',
      lastActive: new Date().toISOString(),
      messageCount: 1,
    };
    const updated = upsertSession(summary);
    setSessions(updated);
  }, []);

  const loadSessionHistory = useCallback(async (targetId: string): Promise<MessageItem[]> => {
    try {
      const response = await getSessionMessages(targetId);
      const reconstructed: MessageItem[] = response.messages.map((m, idx) => ({
        id: `hist-${targetId}-${idx}`,
        role: m.role,
        content: m.content,
        metadata: m.metadata as any,
        timestamp: new Date().toISOString(),
      }));
      setSessionId(targetId);
      return reconstructed;
    } catch (err) {
      console.warn(`Could not load history for session ${targetId}:`, err);
      setSessionId(targetId);
      return [];
    }
  }, []);

  const deleteSession = useCallback((targetId: string) => {
    const updated = deleteSessionFromStorage(targetId);
    setSessions(updated);
    if (targetId === sessionId) {
      const nextId = generateSessionId();
      setSessionId(nextId);
    }
  }, [sessionId]);

  const toggleSidebar = useCallback(() => {
    setIsSidebarOpen((prev) => !prev);
  }, []);

  return {
    sessionId,
    sessions,
    isSidebarOpen,
    startNewSession,
    registerSessionActivity,
    loadSessionHistory,
    deleteSession,
    toggleSidebar,
    setIsSidebarOpen,
  };
}

import { SessionSummary } from '../types';

const STORAGE_KEY = 'chat_sessions_index';

/**
 * Load list of saved sessions from localStorage.
 */
export function loadSavedSessions(): SessionSummary[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    console.warn('Failed to load sessions from storage:', e);
    return [];
  }
}

/**
 * Save list of sessions to localStorage.
 */
export function saveSessions(sessions: SessionSummary[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
  } catch (e) {
    console.warn('Failed to persist sessions to storage:', e);
  }
}

/**
 * Insert or update a session summary in the index.
 */
export function upsertSession(session: SessionSummary): SessionSummary[] {
  const current = loadSavedSessions();
  const existingIdx = current.findIndex((s) => s.id === session.id);
  let updated: SessionSummary[];

  if (existingIdx >= 0) {
    updated = [...current];
    updated[existingIdx] = {
      ...updated[existingIdx],
      ...session,
      lastActive: new Date().toISOString(),
    };
  } else {
    updated = [session, ...current];
  }

  saveSessions(updated);
  return updated;
}

/**
 * Delete a session from local index.
 */
export function deleteSessionFromStorage(sessionId: string): SessionSummary[] {
  const current = loadSavedSessions();
  const filtered = current.filter((s) => s.id !== sessionId);
  saveSessions(filtered);
  return filtered;
}

import { ChatMetadata } from './chat';

export interface SessionHistoryItem {
  role: 'user' | 'assistant';
  content: string;
  metadata?: Partial<ChatMetadata>;
}

export interface SessionHistoryResponse {
  session_id: string;
  messages: SessionHistoryItem[];
}

export interface SessionSummary {
  id: string;
  title: string;
  lastActive: string;
  messageCount: number;
}

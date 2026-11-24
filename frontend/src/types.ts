/**
 * Type definitions matching PRD Section 3 & Section 5 contracts.
 */

export interface ChatMetadata {
  resolution_source: 'LIVE_INFERENCE' | 'LLM_CACHE';
  model: string;
  latency_ms: number;
  input_tokens: number;
  output_tokens: number;
  key_id: string | null;
  fallback_attempts: number;
}

export interface ChatRequestPayload {
  session_id: string;
  message: string;
  system_prompt?: string;
}

export interface ChatResponsePayload {
  session_id: string;
  reply: string;
  metadata: ChatMetadata;
}

export interface MessageItem {
  id: string;
  role: 'user' | 'assistant' | 'error';
  content: string;
  metadata?: ChatMetadata;
  timestamp?: string;
  isError?: boolean;
}

export interface SessionHistoryResponse {
  session_id: string;
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    metadata?: Partial<ChatMetadata>;
  }>;
}

export interface HealthResponse {
  status: string;
  keys_configured: number;
  cache_enabled: boolean;
}

export type FailureSimulationPreset =
  | 'none'
  | 'key_1=429'
  | 'key_1=429,key_2=500'
  | '*=429'
  | 'custom';

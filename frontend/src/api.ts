import {
  ChatRequestPayload,
  ChatResponsePayload,
  HealthResponse,
  SessionHistoryResponse,
} from './types';

export const API_BASE_URL =
  import.meta.env.VITE_API_URL !== undefined && import.meta.env.VITE_API_URL !== ''
    ? import.meta.env.VITE_API_URL.replace(/\/$/, '')
    : 'http://localhost:8000';

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(`API Error ${status}: ${detail}`);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

/**
 * Fetch health status of the backend LLM gateway.
 */
export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE_URL}/health`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!res.ok) {
    let detail = 'Health check failed';
    try {
      const errJson = await res.json();
      detail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
    } catch {
      detail = res.statusText;
    }
    throw new ApiError(res.status, detail);
  }

  return res.json();
}

/**
 * Send chat message to POST /chat with optional X-Simulate-Failure header.
 */
export async function sendChatMessage(
  payload: ChatRequestPayload,
  simulateFailureHeader?: string | null
): Promise<ChatResponsePayload> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  };

  if (simulateFailureHeader && simulateFailureHeader.trim() !== '') {
    headers['X-Simulate-Failure'] = simulateFailureHeader.trim();
  }

  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    let detail = 'Request failed';
    try {
      const errJson = await res.json();
      if (typeof errJson.detail === 'string') {
        detail = errJson.detail;
      } else if (Array.isArray(errJson.detail)) {
        detail = errJson.detail.map((e: { msg?: string; loc?: string[] }) => e.msg || JSON.stringify(e)).join(', ');
      } else if (errJson.detail) {
        detail = JSON.stringify(errJson.detail);
      }
    } catch {
      detail = res.statusText || `HTTP ${res.status}`;
    }
    throw new ApiError(res.status, detail);
  }

  return res.json();
}

/**
 * Fetch stored conversation history from GET /sessions/{session_id}/messages.
 */
export async function getSessionMessages(sessionId: string): Promise<SessionHistoryResponse> {
  const res = await fetch(`${API_BASE_URL}/sessions/${encodeURIComponent(sessionId)}/messages`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!res.ok) {
    let detail = 'Failed to load session history';
    try {
      const errJson = await res.json();
      detail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
    } catch {
      detail = res.statusText;
    }
    throw new ApiError(res.status, detail);
  }

  return res.json();
}

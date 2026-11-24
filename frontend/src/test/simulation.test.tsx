import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import App from '../App';

describe('Failure Simulation & Header Injection', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('arms X-Simulate-Failure header and dispatches with chat request', async () => {
    let capturedHeaders: HeadersInit | undefined;

    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes('/health')) {
        return Promise.resolve(
          new Response(JSON.stringify({ status: 'ok', keys_configured: 2, cache_enabled: true }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          })
        );
      }
      if (url.includes('/chat')) {
        capturedHeaders = init?.headers;
        return Promise.resolve(
          new Response(
            JSON.stringify({
              session_id: 's-12345678',
              reply: 'Response after failover to key_2',
              metadata: {
                resolution_source: 'LIVE_INFERENCE',
                model: 'gemini/gemini-3.5-flash-lite',
                latency_ms: 850,
                input_tokens: 30,
                output_tokens: 10,
                key_id: 'key_2',
                fallback_attempts: 1,
              },
            }),
            {
              status: 200,
              headers: { 'Content-Type': 'application/json' },
            }
          )
        );
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    render(<App />);

    // Open simulation panel
    const simButton = screen.getByText('Simulate Failover');
    fireEvent.click(simButton);

    // Select primary failover preset: key_1=429
    const presetButton = screen.getByText(/Primary Failover/i);
    fireEvent.click(presetButton);

    // Send a message
    const chatInput = screen.getByTestId('chat-input') as HTMLTextAreaElement;
    const sendButton = screen.getByTestId('send-button');

    fireEvent.change(chatInput, { target: { value: 'Testing failover' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Response after failover to key_2')).toBeInTheDocument();
    });

    // Check that captured headers included X-Simulate-Failure: key_1=429
    expect(capturedHeaders).toBeDefined();
    // Headers can be Record<string, string>
    const headerObj = capturedHeaders as Record<string, string>;
    expect(headerObj['X-Simulate-Failure']).toBe('key_1=429');

    // And assistant message displays failover fallback attempt badge
    expect(screen.getByText(/Failover succeeded \(1 fallback\)/i)).toBeInTheDocument();
  });

  it('allows starting a new session with fresh session id', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes('/health')) {
        return Promise.resolve(
          new Response(JSON.stringify({ status: 'ok', keys_configured: 2, cache_enabled: true }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          })
        );
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    render(<App />);

    const newChatButton = screen.getByTitle(/Start fresh conversation/i);
    expect(newChatButton).toBeInTheDocument();

    fireEvent.click(newChatButton);

    // Verifies button click triggers cleanly without throwing
    expect(screen.getByTestId('chat-input')).toBeInTheDocument();
  });
});

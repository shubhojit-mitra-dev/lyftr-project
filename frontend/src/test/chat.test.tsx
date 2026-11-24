import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import App from '../App';

describe('Chat UI & PRD Section 5 Contract Conformance', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders all primary elements on initial page load', async () => {
    // Mock health endpoint
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

    // Check mandatory inputs
    expect(screen.getByTestId('chat-input')).toBeInTheDocument();
    expect(screen.getByTestId('send-button')).toBeInTheDocument();

    // System prompt section is expandable and contains data-testid="system-prompt-input"
    const toggleButton = screen.getByText('System Prompt Configuration');
    fireEvent.click(toggleButton);

    const systemPromptInput = await screen.findByTestId('system-prompt-input');
    expect(systemPromptInput).toBeInTheDocument();
  });

  it('clears chat-input immediately after sending and renders assistant message with exact test-ids', async () => {
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
      if (url.includes('/chat')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              session_id: 's-12345678',
              reply: 'The capital of France is Paris.',
              metadata: {
                resolution_source: 'LIVE_INFERENCE',
                model: 'nvidia/nemotron-3.5-lightning-30b-a3b',
                latency_ms: 780,
                input_tokens: 35,
                output_tokens: 8,
                key_id: 'key_1',
                fallback_attempts: 0,
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

    const chatInput = screen.getByTestId('chat-input') as HTMLTextAreaElement;
    const sendButton = screen.getByTestId('send-button');

    // Type a message
    fireEvent.change(chatInput, { target: { value: 'What is the capital of France?' } });
    expect(chatInput.value).toBe('What is the capital of France?');

    // Click send
    fireEvent.click(sendButton);

    // CRITICAL PRD REQUIREMENT: chat-input MUST be empty immediately after sending
    expect(chatInput.value).toBe('');

    // Wait for assistant response to render
    const assistantMessage = await screen.findByTestId('assistant-message');
    expect(assistantMessage).toBeInTheDocument();
    expect(screen.getByText('The capital of France is Paris.')).toBeInTheDocument();

    // Verify all 5 nested metadata elements have exact values
    const metaSource = screen.getByTestId('meta-source');
    expect(metaSource).toHaveTextContent('LIVE_INFERENCE');

    const metaModel = screen.getByTestId('meta-model');
    expect(metaModel).toHaveTextContent('nvidia/nemotron-3.5-lightning-30b-a3b');

    const metaLatency = screen.getByTestId('meta-latency');
    expect(metaLatency).toHaveTextContent('780 ms');

    const metaInputTokens = screen.getByTestId('meta-input-tokens');
    expect(metaInputTokens).toHaveTextContent('35');

    const metaOutputTokens = screen.getByTestId('meta-output-tokens');
    expect(metaOutputTokens).toHaveTextContent('8');
  });

  it('renders LLM_CACHE response with exact test-ids and zero-latency caching badge', async () => {
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
      if (url.includes('/chat')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              session_id: 's-12345678',
              reply: 'The capital of France is Paris.',
              metadata: {
                resolution_source: 'LLM_CACHE',
                model: 'nvidia/nemotron-3.5-lightning-30b-a3b',
                latency_ms: 12,
                input_tokens: 35,
                output_tokens: 8,
                key_id: null,
                fallback_attempts: 0,
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

    const chatInput = screen.getByTestId('chat-input') as HTMLTextAreaElement;
    const sendButton = screen.getByTestId('send-button');

    fireEvent.change(chatInput, { target: { value: 'What is the capital of France?' } });
    fireEvent.click(sendButton);

    const assistantMessage = await screen.findByTestId('assistant-message');
    expect(assistantMessage).toBeInTheDocument();

    const metaSource = screen.getByTestId('meta-source');
    expect(metaSource).toHaveTextContent('LLM_CACHE');

    const metaLatency = screen.getByTestId('meta-latency');
    expect(metaLatency).toHaveTextContent('12 ms');
  });

  it('handles non-200 HTTP 503 error gracefully without crashing or blank screen', async () => {
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
      if (url.includes('/chat')) {
        return Promise.resolve(
          new Response(JSON.stringify({ detail: 'all providers unavailable' }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' },
          })
        );
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    render(<App />);

    const chatInput = screen.getByTestId('chat-input') as HTMLTextAreaElement;
    const sendButton = screen.getByTestId('send-button');

    fireEvent.change(chatInput, { target: { value: 'Crash test message' } });
    fireEvent.click(sendButton);

    // Readable error message must appear in the chat
    await waitFor(() => {
      expect(screen.getByText(/all providers unavailable/i)).toBeInTheDocument();
      expect(screen.getByText(/HTTP 503/i)).toBeInTheDocument();
    });

    // Chat input remains interactive and ready
    expect(chatInput).toBeInTheDocument();
    expect(chatInput.disabled).toBe(false);
  });
});

# Architecture Decision Records (ADRs)

## ADR 001: Selection of Dual-Provider LLM Fallback Pool (NVIDIA NIM + Google AI Studio)

### Status
Accepted

### Context
Section 2 of the PRD requires LiteLLM to be configured with at least two API keys across one or more models, providing automatic failover on HTTP 429, quota exhaustion, or 5xx server errors without ever presenting a broken screen to the user.
The project requires real-world providers capable of production-level speed, reasoning, and adherence to OpenAI-compatible formats.

Empirical verification of Google AI Studio models documented in `gemini_interactions_report.json` indicates that while models like `gemini-3.8-flash` and `gemini-3.7-flash` occasionally experience temporary 503 high-demand surges, `gemini-3.5-flash-lite` and `gemini-3.1-flash-lite` demonstrated 100% pass rates on text and structured benchmarks with sub-4s latencies. Simultaneously, NVIDIA NIM provides access to Nemotron-3.5 via its OpenAI-compatible endpoint (`https://integrate.api.nvidia.com/v1`).

### Decision
1. **Primary Provider (`key_1`)**: NVIDIA NIM (`openai/nvidia/nemotron-3.5-lightning-30b-a3b`) configured with the user's NVIDIA API key and custom `api_base`.
2. **Secondary Provider (`key_2`)**: Google Gemini (`gemini/gemini-3.5-flash-lite` or `gemini/gemini-3.1-flash-lite`) configured with Google AI Studio API key.
3. Both keys are registered in LiteLLM's routing engine in strict ordered sequence.

### Consequences
- True multi-provider redundancy: an outage or rate-limit at NVIDIA seamlessly falls back to Google AI Studio.
- Full compliance with PRD Section 2 and Section 4 failover simulation tests.

---

## ADR 002: Request-Scoped Failure Simulation via Custom Interceptor

### Status
Accepted

### Context
Section 4 of the PRD dictates support for the `X-Simulate-Failure` header (e.g. `key_1=429`, `key_1=429,key_2=500`, `*=429`) to trigger realistic failover without expending actual provider quotas. This hook must only operate when `ENABLE_FAILURE_SIMULATION=true`. When triggered, the mock failure must cause the router to advance to the next configured key, returning a valid 200 with `key_id = key_2` (or 503 if all keys fail).

### Decision
Implement an application-level LiteLLM pre-call interceptor/wrapper:
- Parse `X-Simulate-Failure` into a mapped status lookup per `key_id`.
- If simulation is enabled and a key is targeted, raise the corresponding provider exception (`RateLimitError(429)`, `InternalServerError(500)`, `ServiceUnavailableError(503)`).
- Allow LiteLLM's fallback logic to catch the simulated exception and cleanly try the next candidate key.
- Never wrap simulated errors into a 200 message body.

### Consequences
- Complete determinism during automated testing and live video evaluation.
- Clean isolation: zero impact when simulation header is omitted or flag is disabled.

---

## ADR 003: Response Caching with LiteLLM & Wall-Clock Telemetry

### Status
Accepted

### Context
The PRD requires:
1. Cache key: `model + full message list (system prompt + history + new message)`.
2. Resolution source: exactly `"LLM_CACHE"` or `"LIVE_INFERENCE"`.
3. Cache hit returns identical reply text, original token usage, `key_id = null`, and `fallback_attempts = 0`.
4. Cache latency must be strictly lower than live inference.

### Decision
- Enable LiteLLM's built-in disk cache (`litellm.cache = Cache(type="disk")` or `Cache(type="local")`).
- Intercept cache metadata from LiteLLM's response wrapper (`_hidden_params.get("cache_hit")`).
- Compute request execution time using Python's `time.perf_counter()` to guarantee accurate millisecond latency reporting.
- On cache hit, explicitly set `metadata.key_id = None` and `metadata.fallback_attempts = 0` as required by Section 3.

### Consequences
- Transparent caching compliant with Section 3 and 8 of the PRD.
- Sub-10ms response times for repeated prompt sequences across new sessions.

---

## ADR 004: Atomic Transactional Storage with SQLite

### Status
Accepted

### Context
Per Section 2, SQLite is the sole storage engine (`sqlite:////data/app.db`), with no Redis or Postgres permitted.
Failed requests (422 or 503) must not leave orphaned records in session history.

### Decision
- Database access encapsulated in a dedicated SQLite repository layer.
- SQLite database location governed strictly by `DATABASE_URL`.
- Write operations for user message and assistant reply wrapped in an atomic transaction; records are committed only after successful model generation.
- Startup hook initializes schema and composite indexes (`session_id`, `created_at`) automatically.

### Consequences
- Zero state pollution on failed or aborted queries.
- Clean persistence across container restarts when mounted to Docker volume `/data`.

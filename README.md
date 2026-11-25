# Production-Grade LLM Chatbot with Key Failover & Response Caching

A resilient, enterprise-grade full-stack LLM conversational application featuring automated provider key failover, response caching, multi-turn session persistence, and request-level telemetry.

Built strictly in accordance with [`docs/PRD.md`](docs/PRD.md) and governed by [`AGENTS.md`](AGENTS.md) and [`docs/architecture.md`](docs/architecture.md).

---

## 1. Live URLs
- **Production Secure Application (HTTPS)**: [https://lyftr-project.shubhojitmitra.com/](https://lyftr-project.shubhojitmitra.com/)
- **Production API & Endpoints**:
  - Health Endpoint: [https://lyftr-project.shubhojitmitra.com/health](https://lyftr-project.shubhojitmitra.com/health) (or `/api/health`)
  - Chat Endpoint: `POST https://lyftr-project.shubhojitmitra.com/chat` (or `/api/chat`)
  - Sessions Endpoint: `GET https://lyftr-project.shubhojitmitra.com/sessions/{session_id}/messages`
  - Interactive Swagger Docs: [https://lyftr-project.shubhojitmitra.com/docs](https://lyftr-project.shubhojitmitra.com/docs)
  - ReDoc Documentation: [https://lyftr-project.shubhojitmitra.com/redoc](https://lyftr-project.shubhojitmitra.com/redoc)
- **Direct IP Fallback (HTTP)**: [http://104.214.177.88/](http://104.214.177.88/) (or port 3000)

---

## 2. Run Locally: With Docker and Without

### Option A: With Docker (Mandatory Assignment Standard)
The entire stack boots locally with a single command via the root `Makefile`:

```bash
# 1. Clone repository & configure environment
cp .env.example .env
# Edit .env to add your LLM API keys:
# LLM_API_KEYS=nvapi-...,AIzaSy...

# 2. Start the full stack (backend on :8000, frontend on :3000)
make up

# 3. View live logs
make logs

# 4. Stop containers
make down
```

### Option B: Without Docker (Local Development)

#### Prerequisites
- Python 3.12+ and `uv`
- Node.js 20+ and `npm`

#### 1. Backend Setup
```bash
cd backend

# Create virtual environment and sync dependencies
uv sync

# Run database migrations and start FastAPI server
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The backend API will be available at `http://localhost:8000`.

#### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
The frontend application will be available at `http://localhost:3000`.

---

## 3. Design Decisions: Key Fallback, Caching, SQLite Session Storage

### Key Fallback Strategy (Dual-Provider Architecture)
- **Primary Provider (`key_1`)**: **NVIDIA NIM** (`openai/nvidia/nemotron-3.5-lightning-30b-a3b` via OpenAI-compatible endpoint `https://integrate.api.nvidia.com/v1`).
- **Secondary Provider (`key_2`)**: **Google AI Studio** (`gemini/gemini-3.5-flash-lite` or `gemini/gemini-3.1-flash-lite`, selected based on empirical stress-test pass rates in `gemini_interactions_report.json`).
- **Resilience Engine**: LiteLLM's fallback routing cascades in sequential order upon detecting HTTP 429, quota exhaustion, or 5xx server errors. The user never experiences an unhandled exception or broken interface.
- **Exhaustion Guard**: If all keys in the pool fail, the backend cleanly raises `503 {"detail": "all providers unavailable"}` without appending the failed turn to SQLite.

### Response Caching Mechanism
- **Engine**: LiteLLM built-in cache (`type="local"` or disk cache).
- **Cache Key**: Deterministically computed from `model + full message list sent to the LLM (system prompt + history + new message)`.
- **Contract Conformance**:
  - `resolution_source`: Exactly `LLM_CACHE` on cache hit, `LIVE_INFERENCE` on live generation.
  - `key_id`: Strictly `null` on cache hits; populated with succeeding key ID (`key_1`, `key_2`) on live inference.
  - `fallback_attempts`: Strictly `0` on cache hits.
  - `latency_ms`: Real server-side measured duration in milliseconds ($<15\text{ms}$ on cache hits vs $>500\text{ms}$ for live inference).
  - Cache hits return the exact original text and preserved token usage.

### SQLite Session Storage
- **Zero External Dependencies**: Standard SQLite engine accessed via asynchronous connection pooling (`aiosqlite`).
- **Durability**: Configured via `DATABASE_URL=sqlite:////data/app.db` mounted to named Docker volume `llm_chatbot_data`.
- **Atomicity**: The user prompt and assistant reply are committed together within a single database transaction. If the model fails or returns 503, nothing is persisted.
- **Contract Strictness**: The session history endpoint (`GET /sessions/{session_id}/messages`) returns chronological records excluding the system prompt, and user messages omit the `metadata` key completely.

---

## 4. Verification: How to See Failover, Cache Hits and Per-Message Token Usage

### 1. Verifying Live Inference & Per-Message Token Usage
1. Open `http://localhost:3000`.
2. Send: `"What is the capital of France?"`.
3. Inspect metadata below the reply:
   - `Resolution Source`: `LIVE_INFERENCE` (green badge)
   - `Model`: `nvidia/nemotron-3.5-lightning-30b-a3b`
   - `Key ID`: `key_1`
   - `Input Tokens`: e.g. `24` (request-specific, never conversation total)
   - `Output Tokens`: e.g. `8`

### 2. Verifying Response Caching (`LLM_CACHE`)
1. Click **New Session** (or reload the page to generate a fresh `session_id`).
2. Send the exact same prompt: `"What is the capital of France?"`.
3. Observe:
   - `Resolution Source`: `LLM_CACHE` (blue lightning badge)
   - `Key ID`: `null` (not displayed)
   - `Latency`: $\approx 1\text{--}5\text{ ms}$ (drastically faster than the live call)
   - `Reply Text`: Identical to the previous turn.

### 3. Verifying Automatic Failover via `X-Simulate-Failure`
Use the built-in **Failover Testing Panel** in the UI header:
1. Select **`key_1=429` (Primary Failover)**.
2. Send: `"Explain quantum computing in one sentence."`.
3. Observe:
   - The primary key (`key_1`) is simulated to fail with HTTP 429.
   - The backend automatically falls over to `key_2` (Google Gemini).
   - `Key ID`: `key_2`.
   - `Fallback Attempts`: `1`.
   - Result: Seamless 200 response with a real AI answer.

### 4. Verifying Provider Exhaustion & Error Shape
1. Select **`*=429` (Exhaust All Keys)** in the Failover Testing Panel.
2. Send: `"Hello world"`.
3. Observe:
   - The backend returns HTTP `503 {"detail": "all providers unavailable"}`.
   - The UI displays a clean error notification in the chat without crashing or blanking.
   - Run `curl http://localhost:8000/sessions/<session_id>/messages`: The failed prompt is **not** recorded in SQLite history.

---

## 5. Setup Used: Your Editor and AI Tools
- **Editor & IDE**: Antigravity IDE (Google DeepMind Agentic IDE) on Linux x86_64.
- **AI Coding Assistants & Architect**: Antigravity Staff Principal Systems Architect with multi-agent delegation loops (Senior Backend Systems Engineer, Senior Frontend & UI/UX Specialist, Senior DevOps & Infrastructure Engineer).
- **Core Skills Leveraged**:
  - `fastapi`: API contract validation, async handlers, and Pydantic v2 schemas.
  - `vercel-react-best-practices`: Client component modularity, state memoization, and UI resilience.
  - `frontend-design`: Modern dark/light typography, badges, and layout aesthetics.
  - `webapp-testing`: End-to-end Vitest and Pytest test automation.

---

## 6. Bonus Features (If Any): What You Added Beyond the Requirements and Why

1. **Interactive In-Browser Chaos & Failover Controller**:
   - *Why*: Allows evaluators to trigger `key_1=429`, `key_1=429,key_2=500`, or `*=429` directly from the UI header without having to construct manual curl commands during the 2–3 minute video demo.
2. **Compound SQLite Indexing**:
   - *Why*: Created composite index `idx_messages_session (session_id, created_at ASC)` to guarantee instantaneous $O(\log N)$ query performance for long conversation threads.
3. **Graceful Storage Path Resolution**:
   - *Why*: Storage engine auto-detects write access to `/data/app.db` and seamlessly falls back to `./data/app.db` during non-containerized local development.
4. **Nginx SPA Dynamic Reverse Proxy & Security Hardening**:
   - *Why*: The frontend Docker container embeds Nginx with SPA routing fallback, security headers (`X-Frame-Options`, `X-Content-Type-Options`), and dynamic Docker DNS resolution (`127.0.0.11`) to prevent boot race conditions.

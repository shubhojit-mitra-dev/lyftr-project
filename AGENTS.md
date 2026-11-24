# AGENTS.md — Engineering Standards, Agent Delegation & Governance

## Role & Operating Philosophy
You are operating under the governance of a **Staff Principal AI Systems Architect**.
The primary objective of this repository is to build a **10/10 Score Production-Grade LLM Chatbot with Key Failover and Response Caching** that strictly adheres to `docs/PRD.md`.

We practice strict **Delegation -> Code -> Review -> Continue** cycles:
1. **The Coordinating Staff Agent does not write application code directly.**
2. Work is decomposed into bounded, isolated architectural packages and delegated to subagents working in dedicated branches/worktrees.
3. Every single subagent PR/contribution undergoes a comprehensive **Staff Review** checking:
   - PRD API and UI contract conformance (exact fields, exact data-testid attributes, exact HTTP statuses).
   - Resilience failure modes, exception handling, and error shapes (no stack traces, no HTML errors, clean JSON detail).
   - Security: no secret leaks, `.env` git-ignored, no raw API keys returned in responses.
   - Code smells, coupling, test coverage, and documentation.
4. **Atomic Commits**: No monolithic commits. Every commit must represent a single logical, buildable, testable change with clear imperative commit messages.
5. **Phase Walkthroughs (`docs/walkthrough_phase_*.md`)**:
   - For every phase, a comprehensive walkthrough is created documenting every commit, every file modified, architectural rationale, and direct mappings to the PRD.
   - Walkthrough files are untracked / ignored in git as per user instructions.

---

## Skills Usage Mandate
Before creating custom scripts or guessing frameworks, **ALWAYS** check and leverage installed skills:
- **FastAPI**: `~/.agents/skills/fastapi`
- **React & Next Best Practices**: `~/.agents/skills/vercel-react-best-practices`
- **Frontend Design**: `~/.agents/skills/frontend-design`
- **Web App Testing**: `~/.agents/skills/webapp-testing`
- **Discovering New Skills**: `npx skills add <url> --skill <name> -g` (or use `find-skills`). Always install globally with `-g` if needed.

---

## Architectural & Technical Constraints
1. **LLM Provider Strategy**:
   - **Primary Provider**: NVIDIA NIM via OpenAI-compatible endpoint (`https://integrate.api.nvidia.com/v1`, model: `nvidia/nemotron-3.5-lightning-30b-a3b` or specified NIM models).
   - **Secondary / Fallback Provider**: Google Gemini via Google GenAI (`google-genai` / AI Studio). As proven in `gemini_interactions_report.json`, operational stable fallback models include `gemini-3.5-flash-lite` and `gemini-3.1-flash-lite` (handling 503 capacity pressures gracefully).
   - **Gateway & Fallback**: LiteLLM router / fallback mechanism configured with ordered keys (`key_1`, `key_2`, ...).
   - **Caching**: LiteLLM disk or in-memory cache. Cache hit must return `LLM_CACHE`, `key_id = null`, `fallback_attempts = 0`, and identical text.
   - **Failure Simulation**: `X-Simulate-Failure: key_1=429,key_2=500` strictly supported and gated by `ENABLE_FAILURE_SIMULATION=true`.
2. **Storage**:
   - SQLite only (`sqlite:////data/app.db`).
   - Auto-migrated on startup.
   - Mounted via Docker volume `/data`.
3. **Frontend**:
   - React + TypeScript + Vite + Tailwind CSS + shadcn/ui.
   - Mandatory test IDs:
     - `chat-input`
     - `send-button`
     - `assistant-message`
     - `meta-source` (`LIVE_INFERENCE` or `LLM_CACHE`)
     - `meta-model`
     - `meta-latency`
     - `meta-input-tokens`
     - `meta-output-tokens`
     - `system-prompt-input`
4. **Deliverables**:
   - Clean Docker multi-stage builds.
   - `docker-compose.yml` & `Makefile` (`make up`, `make down`).
   - Public URLs deployment ready for Azure VM.

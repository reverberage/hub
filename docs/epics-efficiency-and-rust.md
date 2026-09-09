# Epics & User Stories: Efficiency + Rust Path

**Plan:** [`plan-efficiency-and-rust-path.md`](./plan-efficiency-and-rust-path.md)
**ADR:** ADR-001 (Engine-Layer Efficiency over Full C Migration)
**Status:** Backlog | **Owner:** reverberage

---

## Epic A — Engine-Layer Efficiency (recommended, no rewrite)

**Goal:** Capture the real compute/token savings the "go low-level" premise points at — at the
engine layer, keeping Python glue. No rewrite. Unblocks nothing; improves everything.

### A-US-1 Faster local transcription engine

> **As a** transcriber user,
> **I want** local transcription to run on `faster-whisper` (CTranslate2) or `whisper.cpp` instead of PyTorch `openai-whisper`,
> **so that** CPU transcription is several× faster, install is lighter, and RAM is lower.

- [ ] Add `FasterWhisperEngine` (± `WhisperCppEngine`) behind `TranscriptionEngine` in
  `rvrb-transcriber/src/rvrb_transcriber/engine.py` (lazy import).
- [ ] Add `faster` extra to `rvrb-transcriber/pyproject.toml`; keep `local` for compat.
- [ ] Map `--engine faster` in `cli.py`; document in README engine table.
- [ ] Unit tests with fake model object (no real inference in tests).
- **Acceptance:** `rvrb-transcribe x.wav --engine faster` produces an equivalent `Transcript`;
  cold CPU transcribe (same file, same model) measurably faster than `--engine local`.

### A-US-2 Fast CLI startup (kill cold-start imports)

> **As a** CLI user (and an agent invoking satellites repeatedly),
> **I want** the CLI to start in <300 ms,
> **so that** I don't pay a ~2.5 s `import openai` tax on every invocation.

- [ ] Audit every satellite `provider.py` / `cli.py` / `mcp.py` for top-level heavy imports.
- [ ] Convert eager `openai` imports to function-local lazy imports (pattern already used in
  `engine.py` and `_GenericProvider._client()`).
- [ ] Add a CI check (or test) asserting `--help` exits <300 ms.
- **Acceptance:** `time rvrb-* --help` < 300 ms warm; no heavy import at module load.

### A-US-3 Reduce server-side token spend

> **As a** satellite operator paying the API bill,
> **I want** deterministic caching and model tiering,
> **so that** repeat work costs 0 tokens and cheap tasks use cheap models.

- [ ] Response cache for `rvrb-verify` / `rvrb-transform`: key = (model, system, user) hash;
  store via n3rverberage memory/ChromaDB layer or simple disk cache; `--no-cache` to bypass.
- [ ] Route cheap tasks to flash/mini tiers via `N3RVERBERAGE_DEFAULT_MODEL` fallback; document tier matrix.
- [ ] Audit system-prompt dedup + max-token caps across satellites.
- **Acceptance:** identical repeat call returns from cache (no API hit); cheap-task config exposed via env/flag.

### A-US-4 Standardized agent/dev harness

> **As a** maintainer (and AI agent),
> **I want** one canonical `make verify` (ruff + format-check + mypy + pytest in one call) plus
> committed `uv.lock` and pinned `.python-version`,
> **so that** agents stop burning tokens on ad-hoc env-debug loops (measured 23–33% savings).

- [ ] Add `Makefile`/`scripts/verify.sh` canonical target in `hub` + each satellite.
- [ ] Commit `uv.lock` (transcriber has one; extend) and `.python-version` everywhere.
- [ ] Reference the canonical command in each repo's `AGENTS.md`.
- **Acceptance:** agent session on a satellite uses `make verify`; no manual uv/python resolution loops.

### A-US-5 Profile n3rverberage before any compiled port

> **As a** decision-maker,
> **I want** `py-spy`/`cProfile` data on the daemon + memory search + code-graph traversal under realistic load,
> **so that** Track B only activates on a measured CPU-bound hotspot.

- [ ] Profile `mcp/memory_service.py`, `a2a/hub.py`, `mcp/code_graph_service.py`, BM25/vector rerank.
- [ ] Write hotspot report; record decision (activate B1 vs. stop) in ADR-001.
- **Acceptance:** a documented hotspot report exists; B1 is gated on its findings.

---

## Epic B — Optional Rust Migration (staged, reversible)

**Goal:** If (and only if) profiling/hard requirements justify it, a compiled path in Rust —
the only compiled language whose efficiency (≈ C, Pereira #2) honors the original goal.
Strangler-fig; each stage gated and independently reversible.

### B-US-0 Gate decision

> **As a** maintainer,
> **I want** an explicit gate,
> **so that** we never start a rewrite without a measured justification.

- [ ] Blocked on A-US-5 outcome and/or a hard requirement (static binary, embedded, memory-safety).
- **Acceptance:** documented go/no-go in ADR-001 with evidence.

### B-US-1 Hybrid PyO3 hotspot

> **As a** n3rverberage user,
> **I want** the profiled hotspot reimplemented as a Rust extension (PyO3/maturin) behind the same Python API,
> **so that** I get native speed without a rewrite.

- [ ] `n3rverberage/_native` Rust crate for the profiled module only.
- [ ] Python API unchanged; optional feature flag.
- **Acceptance:** same API, measured speedup on the hotspot; tests pass.

### B-US-2 Rust pilot satellite: `rvrb-transform`

> **As a** maintainer,
> **I want** the smallest satellite ported to a Rust binary as a pilot,
> **so that** we measure real port cost (tokens, time) and validate the CLI/pipe contract before committing further.

- [ ] Rust binary: `reqwest` + `serde/serde_json` + `clap` (+ `tokio` if async).
- [ ] Preserve exact CLI (incl. `--json`) and stdin/stdout composition contract.
- [ ] Ship `rvrb-transform-mcp` via official MCP Rust SDK.
- [ ] Equivalent test suite; publish effort data.
- **Acceptance:** drop-in replacement passing the existing contract + tests; documented port cost.

### B-US-3 Remaining satellites (ascending complexity)

> **As a** maintainer,
> **I want** remaining satellites ported only as justified,
> **so that** effort tracks value.

- [ ] Order: verify → see → speak → hear → transcriber (whisper-rs) → n3rverberage last.
- [ ] Per-satellite go/no-go before starting.
- **Acceptance:** each port passes contract parity + tests + measured win or is not started.

### B-US-4 Permanent non-goals

- [ ] `hub/` (governance/docs/scripts) — no runtime code, never ported.
- [ ] Satellite-protocol / MCP glue contract stays byte-compatible regardless of language.

---

## Legend

`[ ]` = backlog, `[x]` = done. Each user story is independently shippable. Epics map to the
plan sections: Track A = plan §1, Track B = plan §2. Decisions recorded in ADR-001.
# Plan: Engine-Layer Efficiency + Optional Rust Migration Path

**Status:** proposal
**Date:** 2026-09-09
**Scope:** all reverberage satellites + n3rverberage runtime

---

## 0. Context and motivation

The motivation: *"in the AI era we spend tokens and compute; we should program in a cheaper,
lower-level way."* This plan captures what the evidence actually supports, and turns it into
two executable tracks:

- **Track A — Engine-layer efficiency (do this).** Keep Python glue. Push real compute savings
  into the engine layer (whisper.cpp / faster-whisper), cut client overhead, reduce agent-token
  spend, standardize the dev harness. No rewrite.
- **Track B — Rust migration path (optional, staged).** For the satellite layer, a phased Rust
  port is documented as an *option*, because Rust — not C — is the compiled language that
  actually honors the efficiency goal and matches the industry trend.

### 0.1 Why not a full C migration

The original premise ("migrate everything to C") was validated against evidence and **rejected**:

| Claim | Evidence | Verdict |
|-------|----------|---------|
| C is fastest to *run* | Pereira et al., *Energy Efficiency across Programming Languages* (SLE'17 / SCP 2021): C ranks #1 (57 J), Python ~45–76× worse on CPU-bound benchmarks | ✅ true — **but** reverberage is network-bound; 99%+ of wall time is OpenAI/Whisper API wait, server-side, language-independent |
| C is cheapest to *run* (tokens) | The token bill is server-side and language-independent | ❌ no effect |
| C is cheapest to *build with AI agents* | arXiv 2607.22807 ("Tokenmaxxing", ~2,000 agent sessions): **Python is the cheapest language for coding agents**; cost is dominated by iteration/debug loops, not verbosity. Alderson 2026: **C is the *least* token-efficient language** (2.6× gap). Token-economy analyses: C ≈ **2.2×** Python agentic token cost | ❌ C *doubles* agent-token spend |
| C is cheapest to *test/maintain* | No std test framework, UB/heisenbugs, sanitizers needed, manual memory | ❌ most expensive of mainstream languages |
| The low-level AI trend is real | llama.cpp / whisper.cpp (Gerganov), 109K+ stars, de-facto core of Ollama/LM Studio | ✅ **but it lives at the model-runtime layer, not application code** |

**Conclusion:** The C trend is real but lives at the *engine* layer. The migration trend in
industry is the *opposite* direction — **C → Rust** (SACTOR, C2SaferRust; NVIDIA CUDA Rust,
announced 2026-09-08; State of Rust 2025: 48.8% of orgs use Rust in production).

### 0.2 Why Rust, not Go, for the optional compiled path

Go was considered and is documented here for completeness. For *this* codebase and goal:

| Criterion | Rust | Go |
|-----------|------|----|
| Energy/runtime efficiency (Pereira) | **#2 (59 J), ≈ C** | ~11× C (GC + runtime); poor on CPU-bound |
| Compile speed | Slow (top Rust-survey concern) | **Fastest in class** |
| Agent-token cost | 1.57× Python | 1.38× Python |
| Maintenance effort | Steeper (ownership, lifetimes) | **Simplest** |
| ML/audio ecosystem fit | `whisper-rs`, `ort` (ONNX), `rust-bert`, official MCP Rust SDK | thinner ML-native ecosystem |
| AI-systems-layer trend | **Where the momentum is** | not part of that story |

Since the *entire motivation* is compute efficiency, Rust is the only compiled language whose
efficiency actually justifies a migration effort. Go optimizes for agent-token cost and
simplicity; Rust optimizes for runtime efficiency and matches the trend. **Go remains a valid
fallback if team/agent ergonomics outrank runtime efficiency.**

---

## 1. Track A — Engine-layer efficiency (recommended, no rewrite)

Ordered by (savings ÷ effort). All changes keep Python; none break the satellite protocol.

### A1. Swap the transcription engine to whisper.cpp / faster-whisper  *(highest impact)*

**File:** `rvrb-transcriber/src/rvrb_transcriber/engine.py`

Today `LocalWhisperEngine` uses `openai-whisper` (PyTorch) — heavy install, slow on CPU,
large RAM footprint. This is exactly the layer where the llama.cpp/whisper.cpp trend applies.

**Change:** add a new engine class behind the existing `TranscriptionEngine` interface; do not
remove the OpenAI engine.

```python
class FasterWhisperEngine(TranscriptionEngine):
    """Local transcription via faster-whisper (CTranslate2) or whisper.cpp.

    Same model weights, C-native runtime: faster on CPU, lower RAM, no PyTorch.
    """
    def __init__(self, model: str = "base", device: str = "auto"):
        self.model_name = model
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from faster_whisper import WhisperModel  # lazy import
            self._model = WhisperModel(self.model_name, device=self.device)
        return self._model

    def transcribe(self, file_path, language=None) -> Transcript:
        segments_iter, info = self.model.transcribe(str(file_path), language=language)
        segments = [Segment(start=s.start, end=s.end, text=s.text.strip())
                    for s in segments_iter]
        return Transcript(text="".join(s.text for s in segments).strip(),
                          segments=segments,
                          language=getattr(info, "language", "unknown"),
                          duration_seconds=getattr(info, "duration", 0.0))
```

**pyproject:** add optional extra `faster = ["faster-whisper"]` (and/or `wcpp` for whisper.cpp
bindings). Keep `local` extra for backward compatibility. Map `--engine faster` in `cli.py`.

**Expected gain:** several-fold faster local CPU transcription, far smaller install, lower RAM.
The one change with *real, measured* compute savings. **Effort: low.**

### A2. Kill the cold-start import cost

Measured on a mid-range laptop: bare `python3` = 45 ms; `typer+pydantic` = 260 ms;
`import openai` ≈ **2.5 s**. The SDK is imported eagerly in several providers.

**Change:** make every `openai` (and other heavy) import lazy — move it inside the function
that uses it, exactly as `engine.py` already does for `whisper` and the fallback provider does
in `_client()`. Audit all `*/provider.py` and `*/cli.py` for top-level heavy imports.

**Expected gain:** CLI startup from ~2.5 s → <300 ms for `--help` and non-network paths.
**Effort: trivial.**

### A3. Reduce server-side token spend (the real "token savings")

Language choice does nothing for the API bill. These do:

- **Response caching** for `rvrb-verify` / `rvrb-transform`: hash (model, system, input) →
  on-disk cache (reuse n3rverberage's existing memory/ChromaDB layer). Repeat calls = 0 tokens.
- **Model tiering:** route cheap tasks to flash/mini models via the existing
  `N3RVERBERAGE_DEFAULT_MODEL` provider fallback instead of always using plus-tier.
- **Prompt/system-prompt dedup** and max-token caps already partially present; audit defaults.
- **Batching** where the API supports it.

**Effort: low-medium. Gain: directly lowers the invoice — the thing the premise aimed at.**

### A4. Standardize the dev/agent harness (evidence-backed 23–33% agent-token saver)

Carroll's controlled experiment: pinning the environment and exposing one canonical verify
command cut Python agent-session tokens 23–33% — larger than any language effect.

**Change (hub + each satellite):**
- one canonical target, e.g. `make verify` (or `scripts/verify.sh`) running `ruff check`,
  `ruff format --check`, `mypy`, `pytest` in a single invocation;
- commit `uv.lock` (transcriber already has one; extend to all) and a pinned `.python-version`;
- document the canonical command in `AGENTS.md` so agents use it instead of ad-hoc debug loops.

**Effort: trivial. Gain: measurable agent-token reduction, more reproducible CI.**

### A5. Profile n3rverberage's genuine hotspots before touching anything

n3rverberage is the only package with real local compute (memory/ChromaDB/ONNX embeddings,
daemon). Heaviest modules: `init/update.py` (729 LOC), `mcp/memory_service.py` (625),
`a2a/hub.py` (535), `mcp/code_graph_service.py` (370).

**Change:** profile the daemon and memory search with `py-spy`/`cProfile` under realistic load.
Only if a CPU-bound hotspot emerges, consider Track B for that specific module (hybrid).
**Effort: low. Output: data that decides whether any compiled port is warranted at all.**

---

## 2. Track B — Optional Rust migration path (staged, reversible)

A full port is *not* recommended on cost grounds (Rust ≈ 1.57× Python agent-token cost and a
steeper maintenance curve), but it is documented so the option is real and scoped. The strategy
is **strangler-fig**: no big-bang rewrite; each stage is independently shippable and reversible.

### Stage B0 — Gate (must pass first)

Complete Track A1–A5. Proceed only if **A5 profiling shows a CPU-bound hotspot** that the Python
engine layer cannot fix, **or** a hard requirement emerges (single static binary, embedded
target, memory-safety guarantee). If neither happens, stop — Track A already captured the value.

### Stage B1 — Rust for the engine layer only (hybrid)

Port *only* the profiled hotspot to a Rust extension called from Python via **PyO3/maturin**.

- Candidates (only if A5 implicates them): ONNX-embedding hot loop, BM25/vector reranking,
  code-graph traversal in n3rverberage.
- Everything else stays Python. This is precisely how the broader ecosystem already works
  (Python over native engines) and keeps agent-token cost near-Python.

**Deliverable:** `n3rverberage` gains an optional `_native` Rust module; Python API unchanged.
**Effort: medium. Risk: low (isolated, behind a stable Python API).**

### Stage B2 — One leaf satellite as a Rust pilot

Pick the *smallest, most self-contained, I/O-thin* satellite as a pilot to validate the
workflow and measure the true port cost before committing further.

- Best pilot candidate: **`rvrb-transform`** (~1,052 LOC, TEXT→TEXT, pure LLM-API client).
- Rewrite as a Rust binary using `reqwest` + `serde` + `serde_json` + `clap` (+ `tokio` if async
  is needed). Preserve the exact CLI contract (`rvrb-transform "instruction" [text] --json`)
  and stdin/stdout composition from the satellite protocol — satellites compose via Unix pipes,
  so a Rust binary is a drop-in replacement *as long as the CLI and I/O contract hold*.
- MCP exposure: use the official MCP Rust SDK to ship `rvrb-transform-mcp`.

**Gate to proceed:** pilot must (a) match the Python CLI/IO contract, (b) pass an equivalent
test suite, (c) show a *measured* efficiency win that justifies continuing. Publish the real
port effort (tokens, time) as data for the remaining stages.

### Stage B3 — Remaining satellites, by ascending complexity

Only after a successful B2, and only per-satellite when justified:

| Order | Satellite | Rust difficulty | Notes |
|-------|-----------|-----------------|-------|
| 1 | `rvrb-transform` | low | pilot (B2) |
| 2 | `rvrb-verify` | low | TEXT→TEXT, structured output → `serde` JSON-schema |
| 3 | `rvrb-see` | med | IMAGE→TEXT; base64 + vision API client |
| 4 | `rvrb-speak` | med | TEXT→AUDIO; bytes out |
| 5 | `rvrb-hear` | med | AUDIO→TEXT multimodal |
| 6 | `rvrb-transcriber` | med | bind whisper.cpp via `whisper-rs` natively — the clean Rust win |
| 7 | `n3rverberage` | **high** | 16.5K LOC, ChromaDB/ONNX/daemon/MCP servers — port last, only if B1 proves out |

### Stage B4 — What never gets ported

- `hub/` is governance/docs/scripts with **no runtime code** — nothing to port.
- MCP protocol glue, provider fallback chains, and the satellite-protocol contract stay
  byte-compatible regardless of implementation language.

### Rust crate mapping (reference)

| Python dep | Rust equivalent |
|------------|-----------------|
| `openai` SDK | `reqwest` + `serde` (OpenAI-compatible REST) or `async-openai` |
| `pydantic` | `serde` + `serde_json` + `schemars` (JSON-schema) + `validator` |
| `typer` | `clap` |
| `mcp` | official MCP Rust SDK |
| `openai-whisper` | `whisper-rs` (whisper.cpp bindings) |
| `onnxruntime` | `ort` |
| `chromadb` | `qdrant` client / `lancedb` / `tantivy` (re-evaluate) |
| `rank-bm25` | `bm25` crate |
| `aiohttp`/`httpx` | `reqwest` + `tokio` |
| `pyyaml` / `jinja2` | `serde_yaml` / `minijinja` |

---

## 3. Decision summary

| Path | Agent-token cost | Runtime/energy | Maintenance | Recommendation |
|------|------------------|----------------|-------------|----------------|
| Stay Python + Track A | **lowest** | already native engines | **lowest** | **Do this (Track A)** |
| Rust hybrid (B1) | low | best where hot | low-med | If A5 shows a hotspot |
| Full Rust port (B2–B3) | +57% | best overall | higher | Optional, staged, gated |
| Go port | +38% | mediocre (GC) | lowest compiled | Fallback if ergonomics > efficiency |
| Full C port | +120% (worst) | best | **worst + memory-unsafe** | ❌ rejected |

**Next action:** implement Track A1 (faster-whisper engine) and A4 (canonical `make verify`),
then A5 (profile n3rverberage). Let A5's data decide whether Track B ever activates.

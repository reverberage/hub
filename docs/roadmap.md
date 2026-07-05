# Roadmap

## Shipped

| Satellite | Package | Status | Description |
|-----------|---------|--------|-------------|
| **transcriber** | `rvrb-transcriber` | alpha | AI-powered audio transcription (audio → text) |

## Planned (priority order)

### 1. verify — claim verification engine

`rvrb-verify` | **Priority: HIGH** | Target: Q4 2026

Claim in, verdict out. Pluggable backends for fact-checking, legal review,
research validation, and content moderation.

**Why first**: Broadest market surface. Useful for journalism, legal, research,
education, and any domain where claims need verification. No crawler infrastructure required.

### 2. transform — format conversion & restructuring

`rvrb-transform` | **Priority: MEDIUM** | Target: Q1 2027

Text → text pipelines. Format conversion (Markdown ↔ reStructuredText ↔ HTML),
summarization, style normalization, content restructuring.

**Why second**: Fast to ship — pure text I/O, no external dependencies. Unlocks
"workshop" pipeline metaphors: transcribe → transform → verify.

### 3. scout — source discovery

`rvrb-scout` | **Priority: LOW** | Target: Q2 2027

Source discovery and crawling. Feed a topic, get ranked sources.

**Why last**: Requires crawler infrastructure and ongoing maintenance. Lower
time-to-value than verify and transform.

## North Star

Every satellite is a composable, MCP-native Python package. No monolith.
Each does one thing well. Together they form a natural language workshop
for ingest, generate, verify, and transform across audio, video, and text.

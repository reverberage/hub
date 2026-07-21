# FAQ

Common questions about rvrb-verify.

## Provider setup

### Which provider should I use?

**Qwen (default)** — Best for Qwen models, free tier available via Alibaba Cloud.

**OpenAI** — Use if you have an OpenAI API key and prefer GPT models.

**Local** — Use Ollama or vLLM for offline operation. No API key needed.

### How do I get a Qwen API key?

1. Go to [Alibaba Cloud Model Studio](https://dashscope.console.aliyun.com/)
2. Sign up for a free account (Singapore region)
3. Activate Model Studio
4. Generate an API key
5. Set `export DASHSCOPE_API_KEY="sk-..."`

Free tier: 1M tokens per model, 90-day validity.

### Can I use different models for search and judge?

Yes:

```python
from rvrb_verify import verify, get_provider

search = get_provider(model="qwen3-coder-plus")  # Fast model for search
judge = get_provider(model="qwen3.7-plus")       # Smart model for judge

verdict = verify("Claim", search_provider=search, judge_provider=judge)
```

## Strategy selection

### Which strategy should I use?

| Claim type | Strategy |
|------------|----------|
| General facts, news | `fact-check` |
| Legal, regulatory | `legal` |
| Scientific, academic | `research` |

### Can I create custom strategies?

Yes. See [Development](Development) for details on adding custom strategies.

### What tools does each strategy use?

- **fact-check**: web search, news search
- **legal**: statute search, case law search
- **research**: paper search, arXiv search

## Confidence scores

### What does confidence mean?

Confidence is a float from 0.0 to 1.0 representing the judge model's certainty in the verdict.

- **0.9+**: High confidence
- **0.7-0.9**: Medium confidence
- **<0.7**: Low confidence, may be inconclusive

### Why is confidence low?

Low confidence can indicate:
- Ambiguous or subjective claim
- Insufficient evidence found
- Conflicting sources
- Complex or nuanced topic

### Can I set a confidence threshold?

Not currently. You can filter results programmatically:

```python
verdict = verify("Claim")
if verdict.confidence < 0.7:
    print("Low confidence, manual review needed")
```

## Offline usage

### Can I use rvrb-verify offline?

Yes, with a local provider:

```bash
# Install Ollama
# Pull a model
ollama pull llama3

# Use local provider
rvrb-verify "Claim" --provider local
```

### Do the tools work offline?

No. The tools (web search, news search, etc.) require internet access. For offline use, implement a custom `ToolGateway` with local data sources.

## Token costs

### How many tokens does verification use?

Approximate usage per verification:
- **Search phase**: 500-2000 tokens (depends on tools used)
- **Judge phase**: 500-1000 tokens
- **Total**: 1000-3000 tokens per verification

### How can I reduce costs?

- Use faster/cheaper models for search phase
- Limit evidence collection
- Use local provider (no API costs)

## Integration

### Can I use rvrb-verify with other satellites?

Yes. Common pipelines:

```bash
# Transcribe audio → verify claims
rvrb-transcribe meeting.mp3 | rvrb-verify

# Verify → format results
rvrb-verify "Claim" --json | rvrb-transform "Format as markdown table"
```

### Can I use rvrb-verify in my application?

Yes. Install via pip and use the Python API:

```python
from rvrb_verify import verify

verdict = verify("Claim")
```

## Troubleshooting

### Error: "DASHSCOPE_API_KEY is not set"

Set the environment variable:

```bash
export DASHSCOPE_API_KEY="sk-..."
```

Or use a different provider:

```bash
rvrb-verify "Claim" --provider openai
```

### Error: "Unknown strategy: xyz"

Check available strategies:

```bash
python -c "from rvrb_verify import list_strategies; print(list_strategies())"
```

Available: `fact-check`, `legal`, `research`.

### Error: "Model not found"

Check that the model ID is correct:

```bash
rvrb-verify "Claim" --model qwen3-coder-plus
```

For Qwen models, see the [model catalog](https://github.com/reverberage/hub/blob/main/docs/qwen-model-catalog.md).

### Verification returns "inconclusive"

The judge model couldn't determine the verdict with high confidence. This can happen with:
- Ambiguous claims
- Insufficient evidence
- Conflicting sources

Try:
- Rephrasing the claim
- Using a different strategy
- Using a more capable model

### Tools return empty results

The `MockToolGateway` returns mock data. For real tool execution, implement a `RealToolGateway` (see [Development](Development)).

## Performance

### How long does verification take?

Typical verification time:
- **Search phase**: 2-10 seconds (depends on tools)
- **Judge phase**: 1-3 seconds
- **Total**: 3-13 seconds

### Can I speed up verification?

- Use faster models (e.g., `qwen3-coder-flash` for search)
- Reduce evidence collection
- Use local provider (no network latency)

## License

Apache-2.0 — same as the reverberage ecosystem.

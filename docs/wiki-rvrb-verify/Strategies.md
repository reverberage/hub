# Strategies

rvrb-verify uses a strategy pattern to support different types of claim verification. Each strategy defines:
- Which tools to use for searching evidence
- Which models to use for search and judge phases
- How to structure the verification pipeline

## Available strategies

| Strategy | Description | Tools | When to use |
|----------|-------------|-------|-------------|
| `fact-check` | General factual verification | Web search, news search | Everyday claims, news, general knowledge |
| `legal` | Legal/statutory analysis | Statute search, case law search | Legal claims, regulatory compliance |
| `research` | Academic/scientific validation | Paper search, arXiv search | Scientific claims, academic research |

## `fact-check` strategy

General-purpose verification for everyday claims.

**Tools:**
- Web search (Google, Bing)
- News search (recent articles)

**Example claims:**
- "The sky is blue"
- "Water boils at 100°C"
- "Python was created in 1991"
- "The Earth orbits the Sun"

**Usage:**
```bash
rvrb-verify "The sky is blue" --strategy fact-check
```

```python
verdict = verify("The sky is blue", strategy="fact-check")
```

## `legal` strategy

Verification for legal and regulatory claims.

**Tools:**
- Statute search (laws, regulations)
- Case law search (court decisions)

**Example claims:**
- "GDPR requires consent for cookies"
- "The First Amendment protects free speech"
- "Employers must provide health insurance"
- "Copyright lasts 70 years after the author's death"

**Usage:**
```bash
rvrb-verify "GDPR requires consent for cookies" --strategy legal
```

```python
verdict = verify("GDPR requires consent for cookies", strategy="legal")
```

## `research` strategy

Verification for academic and scientific claims.

**Tools:**
- Paper search (academic databases)
- arXiv search (preprints)

**Example claims:**
- "Quantum computing breaks Moore's law"
- "CRISPR can edit human genes"
- "Climate change is caused by human activity"
- "Vaccines do not cause autism"

**Usage:**
```bash
rvrb-verify "Quantum computing breaks Moore's law" --strategy research
```

```python
verdict = verify("Quantum computing breaks Moore's law", strategy="research")
```

## Adding custom strategies

You can create custom strategies by implementing the `VerificationStrategy` interface:

```python
from rvrb_verify.strategies import VerificationStrategy, ToolSpec

class MyStrategy(VerificationStrategy):
    name = "my-strategy"
    description = "Custom verification strategy"
    
    # Tools for search phase
    tools = [
        ToolSpec(name="my_search", description="Search my database"),
    ]
    
    # Model preferences
    model_search = "qwen3-coder-plus"
    model_judge = "qwen3.7-plus"
    
    def search_prompt(self, claim: str) -> list[dict]:
        """Generate messages for search phase."""
        return [
            {"role": "system", "content": "Search for evidence..."},
            {"role": "user", "content": claim},
        ]
    
    def judge_prompt(self, claim: str, evidence: list) -> list[dict]:
        """Generate messages for judge phase."""
        return [
            {"role": "system", "content": "Judge the claim based on evidence..."},
            {"role": "user", "content": f"Claim: {claim}\nEvidence: {evidence}"},
        ]
```

Register the strategy:

```python
from rvrb_verify.strategies import REGISTRY

REGISTRY.register(MyStrategy())
```

## Strategy selection guide

| Claim type | Recommended strategy |
|------------|---------------------|
| "The sky is blue" | `fact-check` |
| "GDPR requires..." | `legal` |
| "Studies show..." | `research` |
| News headlines | `fact-check` |
| Scientific papers | `research` |
| Court rulings | `legal` |
| Product specs | `fact-check` |

## Tool gateways

Strategies use tools to search for evidence. By default, rvrb-verify uses `MockToolGateway` (returns mock data). For real tool execution, implement a `ToolGateway`:

```python
from rvrb_verify.tools import ToolGateway

class RealToolGateway(ToolGateway):
    def execute(self, tool_name: str, arguments: dict) -> str:
        """Execute a real tool call."""
        if tool_name == "web_search":
            # Call real search API
            return search_web(arguments["query"])
        # ...
```

Pass to verify:

```python
verdict = verify("Claim", tool_gateway=RealToolGateway())
```

# Development

Hub development setup and workflows.

## Setup

```bash
# Clone the repository
git clone https://github.com/reverberage/hub.git
cd hub

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

## Commands

| Command | Purpose |
|---------|---------|
| `pytest` | Run tests |
| `ruff check .` | Lint code |
| `ruff format .` | Format code |
| `mypy .` | Type check |
| `python scripts/scaffold-satellite.py <name>` | Scaffold new satellite |
| `python scripts/qwen_fallback.py --status` | Check model quota |
| `python scripts/qwen_fallback.py --rotate` | Rotate opencode model |

## Repository structure

```
hub/
├── docs/                    # Architecture, protocol specs, roadmap
│   ├── architecture.md
│   ├── satellite-protocol-v2.md
│   ├── roadmap.md
│   ├── qwen-model-catalog.md
│   └── wiki-*/              # Wiki content for each repo
├── scripts/
│   ├── scaffold-satellite.py  # Generate new satellite skeleton
│   └── qwen_fallback.py       # Model quota rotation
├── tests/                   # Hub-level tests
├── .opencode/               # Agent definitions, skills, commands
│   ├── agents/              # Subagent definitions
│   ├── skills/              # Skill instructions
│   └── commands/            # Slash command definitions
├── AGENTS.md                # Coding standards
├── CONTRIBUTING.md          # Contribution guide
├── opencode.json            # opencode config (generated)
└── opencode.template.json   # Template for rotation
```

## Scaffold a new satellite

```bash
python scripts/scaffold-satellite.py <name>

# Creates rvrb-<name>/ with:
# - pyproject.toml (hatchling build, entry points)
# - src/rvrb_<name>/ (mandatory kernel + optional modules)
# - tests/ (with MockProvider)
```

The scaffold follows [satellite protocol v2](Satellite-Protocol).

## Model quota rotation

```bash
# Check status of all 81 models
python scripts/qwen_fallback.py --status

# Rotate to next available model
python scripts/qwen_fallback.py --rotate

# Force specific model
python scripts/qwen_fallback.py --rotate --model qwen3.7-plus

# Update tracking doc
python scripts/qwen_fallback.py --track
```

The rotation script manages the `opencode.json` config file, rotating through available models when quota is exhausted.

## SDD workflow

The hub uses Spec-Driven Development (SDD) for changes:

```
/sdd-new "description of change"
```

This runs the 8-phase pipeline:
1. Explore — understand the codebase
2. Propose — generate solution approaches
3. Spec — write acceptance criteria
4. Design — create technical design
5. Tasks — break into implementation steps
6. Apply — implement the code
7. Verify — audit against spec
8. Archive — persist to memory

## N3RVERBERAGE orchestration

The hub contains the N3RVERBERAGE orchestration agent (`.opencode/agents/n3rverberage.md`). It coordinates:

- SDD pipeline execution
- Project board updates
- Memory persistence (MAGI)
- A2A task routing

## Wiki management

Wiki content is stored in `docs/wiki-*/` directories. Each satellite repo has its own wiki:

```bash
docs/wiki-rvrb-transcriber/  # Transcriber wiki (10 pages)
docs/wiki-rvrb-verify/       # Verify wiki (10 pages)
docs/wiki-rvrb-hear/         # Hear wiki (10 pages)
docs/wiki-rvrb-see/          # See wiki (10 pages)
docs/wiki-hub/               # Hub wiki (10 pages)
```

Push wikis to GitHub using the `push-wiki.sh` script in each directory.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_scaffold.py
```

## CI checks

Before submitting a PR:

```bash
ruff check .
ruff format --check .
mypy .
pytest
```

All must pass.

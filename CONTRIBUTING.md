# Contributing to reverberage

## Dev Setup

Each satellite is its own repo under [reverberage](https://github.com/reverberage).

```bash
# Clone a satellite
git clone https://github.com/reverberage/transcriber.git
cd transcriber
pip install -e ".[dev]"
pytest
```

## Code Style

All rules are enforced via the project's AGENTS.md (loaded automatically by opencode agent).

## Adding Satellites

See `README.md` → Satellites table. To add a new satellite:
1. Create `reverberage/<name>` repo under the org
2. Follow the existing satellite template (Pydantic + Typer + pytest + hatchling)
3. Register it in the Shipyard project board

---
description: Run tests on the hub's scaffold script
agent: n3rverberage
subtask: true
---
Run the test suite for this project.

This is a meta-repo with one Python module: the satellite scaffold script. Run its tests:

```
pytest
```

If the tests/ directory doesn't exist, run the scaffold script to validate it works:

```
python .opencode/scripts/scaffold-satellite.py test-scaffold
pip install -e "../test-scaffold[dev]" 2>/dev/null && pytest ../test-scaffold
rm -rf ../test-scaffold
```

Report any failures and suggest fixes if needed.

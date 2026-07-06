---
description: Lint YAML and Markdown files
agent: n3rverberage
subtask: true
---
Run linting for this project.

This is a meta-repo — no Python code to lint. Check YAML syntax and Markdown links:

```bash
# Validate YAML syntax
for f in $(find . -name '*.yml' -o -name '*.yaml' | grep -v node_modules | grep -v '.n3rverberage/'); do
  python -c "import yaml; yaml.safe_load(open('$f'))" || echo "FAIL: $f"
done

# Check Markdown links (requires markdown-link-check)
npx markdown-link-check --quiet *.md docs/*.md 2>/dev/null || true
```

Report any issues found.

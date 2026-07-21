# SDD Tasks: github-ops-upgrade

**Change ID**: `github-ops-upgrade` | **Phase**: 5 — Tasks | **Date**: 2026-07-21

---

## Task List

Ordered implementation steps. Each task is atomic and independently testable.

### Task 1: Update agent permissions
- **File**: `.opencode/agents/github-ops.md`
- **What**: Add `gh api *: allow` to bash permissions. Add `gh secret set*`, `gh secret delete*`, `gh variable set*`, `gh variable delete*` with `ask` confirmation.
- **Done when**: Agent file contains `gh api *: allow` and all new `ask` rules for secrets/variables.

### Task 2: Expand "When to Use" section
- **File**: `.opencode/skills/github-ops/SKILL.md`
- **What**: Add new use cases to the "When to Use" section: wiki push, Pages deployment, webhook management, contents CRUD, dispatch events, secrets/variables, search, `gh api` escape hatch.
- **Done when**: "When to Use" section lists at least 10 use cases (current 4 + 6 new).

### Task 3: Add safety rules for destructive operations
- **File**: `.opencode/skills/github-ops/SKILL.md`
- **What**: Expand REJECT list to include: destructive operations (delete webhook, delete file, delete secret) without explicit confirmation, force push to main/master without explicit rationale, modifying repo settings without explicit instruction.
- **Done when**: REJECT section has at least 3 new destructive operation rules.

### Task 4: Add wiki push workflow
- **File**: `.opencode/skills/github-ops/SKILL.md`
- **What**: Add "Workflow: Wiki Push" section with: auth token pattern, clone step, write _Footer.md/_Sidebar.md, commit, push. Note that github-ops agent has `edit: deny` and this requires orchestrator or git-ops execution.
- **Done when**: Wiki push workflow exists with auth pattern and execution note.

### Task 5: Add Pages workflow
- **File**: `.opencode/skills/github-ops/SKILL.md`
- **What**: Add "Workflow: GitHub Pages" section with: get pages config, create pages site, update pages config, trigger build, delete pages site. All via `gh api`.
- **Done when**: Pages workflow has 5 operations (GET, POST create, PUT update, DELETE, POST build).

### Task 6: Add webhooks workflow
- **File**: `.opencode/skills/github-ops/SKILL.md`
- **What**: Add "Workflow: Webhooks" section with: list webhooks, create webhook, update webhook, ping webhook, delete webhook. All via `gh api`.
- **Done when**: Webhooks workflow has 5 operations (list, create, update, ping, delete).

### Task 7: Add contents API workflow
- **File**: `.opencode/skills/github-ops/SKILL.md`
- **What**: Add "Workflow: Contents API" section with: get file contents, get raw file, create file, update file (with SHA), delete file (with SHA). All via `gh api`.
- **Done when**: Contents workflow has 5 operations (get, get raw, create, update, delete).

### Task 8: Add dispatch events workflow
- **File**: `.opencode/skills/github-ops/SKILL.md`
- **What**: Add "Workflow: Dispatch Events" section with: trigger repository dispatch via `gh api -X POST repos/OWNER/REPO/dispatches`.
- **Done when**: Dispatch workflow exists with event_type and client_payload examples.

### Task 9: Add secrets & variables workflow
- **File**: `.opencode/skills/github-ops/SKILL.md`
- **What**: Add "Workflow: Secrets & Variables" section with: list/set/delete repo secrets (native `gh secret`), list/set/delete repo variables (native `gh variable`), org-level secrets via `gh api`.
- **Done when**: Secrets & Variables workflow covers native + API patterns.

### Task 10: Add search workflow
- **File**: `.opencode/skills/github-ops/SKILL.md`
- **What**: Add "Workflow: Search" section with: search repos, search issues, search PRs, search code, search commits. All via `gh search`.
- **Done when**: Search workflow has 5 search types documented.

### Task 11: Add gh api escape hatch reference
- **File**: `.opencode/skills/github-ops/SKILL.md`
- **What**: Add "The gh api Escape Hatch" reference section explaining: when to use gh api, key flags (-X, -F, -f, -H, --paginate, --jq, --template), example GET/POST/PATCH/DELETE patterns.
- **Done when**: Reference section exists with 7 key flags and 4 HTTP method examples.

### Task 12: Add official documentation references
- **File**: `.opencode/skills/github-ops/SKILL.md`
- **What**: Add "Official Documentation References" table with URLs for: gh CLI manual, REST API index, Pages API, Webhooks API, Contents API, Repos API, Wiki docs, Secrets API, Variables API, Dispatch API.
- **Done when**: Reference table has at least 10 doc URLs.

### Task 13: Expand edge cases
- **File**: `.opencode/skills/github-ops/SKILL.md`
- **What**: Add edge cases for new workflows: wiki push failed (git error), Pages not enabled (404), webhook already exists (422), file SHA mismatch (422), invalid JSON response (jq error).
- **Done when**: Edge cases section has at least 5 new entries.

### Task 14: Update orchestrator dispatch rules
- **File**: `.opencode/agents/n3rverberage.md`
- **What**: Add dispatch rules for new github-ops capabilities: wiki, Pages, webhooks, contents API, dispatch events, search, secrets/variables.
- **Done when**: Orchestrator has at least 7 new dispatch rules for github-ops capabilities.

### Task 15: Verify backward compatibility
- **File**: `.opencode/skills/github-ops/SKILL.md`
- **What**: Verify existing workflows (issues, PRs, releases, CI) are unchanged. New content is appended, not modifying existing sections.
- **Done when**: Existing workflow sections are identical to the original SKILL.md.

---

## Execution Order

```
Task 1 (agent permissions) → Tasks 2-13 (SKILL.md sections, any order) → Task 14 (orchestrator) → Task 15 (verify)
```

## Coverage Matrix

| AC | Task(s) |
|:--:|---------|
| AC-1 | Task 2 (When to Use) |
| AC-2 | Task 11 (gh api reference) |
| AC-3 | Task 4 (wiki push) |
| AC-4 | Task 5 (Pages) |
| AC-5 | Task 6 (webhooks) |
| AC-6 | Task 7 (contents) |
| AC-7 | Task 8 (dispatch) |
| AC-8 | Task 2 (repo settings in When to Use) |
| AC-9 | Task 9 (secrets & variables) |
| AC-10 | Task 10 (search) |
| AC-11 | Task 1 (agent permissions) |
| AC-12 | Task 14 (orchestrator rules) |
| AC-13 | Task 3 (safety rules) |
| AC-14 | Task 15 (backward compat) |
| AC-15 | Task 12 (doc references) |
| AC-16 | Tasks 4-10 (copy-pasteable commands) |
| AC-17 | Task 15 (backward compat) |

# SDD Verify: github-ops-upgrade

**Change ID**: `github-ops-upgrade` | **Phase**: 7 — Verify | **Date**: 2026-07-21

---

## Acceptance Criteria Check

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| AC-1 | All gh command groups covered | PASS | 55 references to gh commands across 10 groups (issue, pr, release, run, repo, search, auth, api, secret, variable) |
| AC-2 | gh api universal escape hatch | PASS | "The gh api Escape Hatch" section exists with 7 key flags and 4 HTTP method examples |
| AC-3 | Wiki push workflow | PASS | "Workflow: Wiki Push" section with auth token pattern and execution note |
| AC-4 | Pages deployment | PASS | "Workflow: GitHub Pages" section with 5 operations (GET, POST create, PUT update, POST build, DELETE) |
| AC-5 | Webhook CRUD | PASS | "Workflow: Webhooks" section with 5 operations (list, create, update, ping, delete) |
| AC-6 | Contents CRUD | PASS | "Workflow: Contents API" section with 5 operations (get, get raw, create, update, delete) |
| AC-7 | Dispatch events | PASS | "Workflow: Dispatch Events" section with event_type and client_payload examples |
| AC-8 | Repo settings | PASS | "Workflow: Repository Management" section with repo view, edit, list commands |
| AC-9 | Secrets and variables | PASS | "Workflow: Secrets & Variables" section with native gh secret/variable + gh api patterns |
| AC-10 | Search capabilities | PASS | "Workflow: Search" section with 5 search types (repos, issues, PRs, code, commits) |
| AC-11 | Agent permissions updated | PASS | `.opencode/agents/github-ops.md` contains `gh api *: allow` |
| AC-12 | Orchestrator dispatch rules | PASS | `.opencode/agents/n3rverberage.md` has 7 new dispatch rules (wiki, pages, webhook, contents, dispatch, search, secret/variable) |
| AC-13 | Destructive ops require confirmation | PASS | REJECT section includes destructive operations rule |
| AC-14 | Safety rules preserved | PASS | All 4 original rules present (gh auth status, never close/merge, validate CI, report rate limits) |
| AC-15 | Official doc references | PASS | Reference table with 12 doc URLs |
| AC-16 | Copy-pasteable commands | PASS | 31 OWNER/REPO pattern references, no angle-bracket placeholders |
| AC-17 | No breaking changes | PASS | Existing workflows (PR, issues, releases, CI) unchanged, new content appended |

## Regression Check

No code changes — documentation + configuration only. No tests to run.

## Verdict

**APPROVED** — All 17 acceptance criteria pass. All changes are additive (no existing content modified).

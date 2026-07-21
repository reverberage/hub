# SDD Complete: github-ops-upgrade

**Change ID**: `github-ops-upgrade` | **Phase**: 8 — Archive | **Date**: 2026-07-21

---

## Change: github-ops-upgrade

## Description
Upgrade the github-ops skill and agent to cover all discovered gh CLI + gh API capabilities (wiki push, Pages deployment, webhook management, contents CRUD, dispatch events, etc.).

## Status: COMPLETE

## Approach taken
Expand existing github-ops skill + agent (Approach A) — simplest path that delivers value without creating new abstractions.

## Key design decisions
1. Single SKILL.md file grows from 73 to ~335 lines — acceptable for a reference document
2. Wiki push documented as a pattern but executed by orchestrator/git-ops (github-ops has `edit: deny`)
3. `gh api *: allow` added to agent permissions for universal REST/GraphQL access

## Files modified
- `.opencode/skills/github-ops/SKILL.md` — 73 → 335 lines (added 12 new workflow sections)
- `.opencode/agents/github-ops.md` — 22 → 27 lines (added `gh api *: allow` + secrets/variables ask rules)
- `.opencode/agents/n3rverberage.md` — 106 → 113 lines (added 7 new dispatch rules)

## Tests added
No code changes — documentation + configuration only.

## Verified
2026-07-21 — All 17 acceptance criteria pass. See `docs/verify-github-ops-upgrade.md`.

## Artifacts
- `docs/proposal-github-ops-upgrade.md` — Phase 2: Proposal
- `docs/spec-github-ops-upgrade.md` — Phase 3: Spec (17 ACs)
- `docs/design-github-ops-upgrade.md` — Phase 4: Design
- `docs/tasks-github-ops-upgrade.md` — Phase 5: Tasks (15 tasks)
- `docs/verify-github-ops-upgrade.md` — Phase 7: Verify (all PASS)

## New capabilities documented
1. Wiki push pattern (clone, auth, write _Footer.md/_Sidebar.md, commit, push)
2. GitHub Pages API (GET, POST create, PUT update, POST build, DELETE)
3. Webhooks CRUD (list, create, update, ping, delete)
4. Contents API (get, get raw, create, update, delete)
5. Dispatch events (POST /repos/**/dispatches)
6. Secrets & Variables (native gh + gh api patterns)
7. Search (repos, issues, PRs, code, commits)
8. gh api escape hatch reference (7 key flags, 4 HTTP method examples)
9. Official documentation references (12 doc URLs)

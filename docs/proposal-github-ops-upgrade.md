# SDD Proposal: github-ops-upgrade

**Change ID**: `github-ops-upgrade` | **Phase**: 2 — Propose | **Date**: 2026-07-21

---

## Context

The github-ops skill currently covers only `gh issue`, `gh pr`, `gh release`, and `gh run`. Research revealed the full `gh` CLI command tree (43 top-level commands, ~200+ subcommands) and `gh api` as a universal escape hatch for ANY REST/GraphQL endpoint. Key gaps: wiki push, Pages deployment, webhooks, contents API, dispatch events.

**Constraint**: Wiki push is a git operation (clone, add, commit, push) — not a `gh` subcommand. The github-ops agent has `edit: deny` and bash only allows `gh *`. Wiki push must be handled by git-ops or the orchestrator.

---

## Approach A: Expand existing github-ops skill + agent

**Description**: Update SKILL.md with all discovered workflows. Expand agent permissions to allow `gh api *`. Add wiki push pattern to SKILL.md but note it requires orchestrator execution (git-ops has the git permissions).

**Changes**:
1. `SKILL.md` — add workflows for: `gh api` patterns, wiki push, Pages, webhooks, contents CRUD, dispatch events, repo settings
2. `github-ops.md` agent — add `gh api *: allow` permission
3. `n3rverberage.md` orchestrator — add dispatch rules for new capabilities
4. No new files created

**Pros**:
- Simple, single skill file
- Follows existing pattern (project-board already uses `gh api graphql`)
- No new agents to maintain
- Reversible — just revert the files

**Cons**:
- SKILL.md grows from 73 to ~200 lines
- Agent permissions get complex (`gh *` + `gh api *`)
- Wiki push can't be executed by github-ops agent (edit: deny)

**Blast radius**: Medium — modifies 3 existing files
**Reversibility**: High — git revert
**Testability**: Medium — each workflow can be tested independently

---

## Approach B: Split into github-ops + github-api agents

**Description**: Keep github-ops for native `gh` subcommands (issues, PRs, releases). Create a new `github-api` agent for `gh api` operations (Pages, webhooks, contents, dispatch, wiki push pattern). Separate permission models.

**Changes**:
1. `SKILL.md` — keep existing, add reference to new agent
2. `github-ops.md` agent — unchanged
3. New `github-api.md` agent — `gh api *: allow`, `git *: allow` (for wiki push)
4. New `github-api/SKILL.md` — `gh api` patterns, wiki push, Pages, webhooks, contents, dispatch
5. `n3rverberage.md` orchestrator — add dispatch rules for github-api

**Pros**:
- Clean separation of concerns
- Each agent has focused permissions
- Wiki push can live in github-api (has git permissions)
- Easier to test each agent independently

**Cons**:
- Two agents to maintain
- Orchestrator needs to know which to dispatch
- More files (4 new files)
- Overkill for the actual scope

**Blast radius**: Low — new agent doesn't affect existing
**Reversibility**: High — delete the new files
**Testability**: High — each agent tested independently

---

## Approach C: Single agent + separate skill files

**Description**: Keep single github-ops agent with expanded permissions. Split SKILL.md into two files: `github-ops/SKILL.md` (native gh commands) and `github-ops/api-patterns.md` (gh api reference). Agent loads both skills.

**Changes**:
1. `SKILL.md` — keep existing, add reference to api-patterns
2. New `github-ops/api-patterns.md` — gh api reference, wiki push, Pages, webhooks, contents, dispatch
3. `github-ops.md` agent — add `gh api *: allow`, load both skills
4. `n3rverberage.md` orchestrator — add dispatch rules

**Pros**:
- Single agent (simple dispatch)
- Organized skill files (reference + workflows)
- Reversible — delete the new file
- Follows pattern of other skills (project-board, sdd-* have separate files)

**Cons**:
- SKILL.md still needs updating for references
- Agent permissions still complex
- Wiki push still can't be executed by github-ops (edit: deny)

**Blast radius**: Medium — modifies 2 existing files, adds 1 new
**Reversibility**: High — git revert
**Testability**: Medium — each skill file can be tested independently

---

## Recommended: Approach A

**Rationale**: This is the simplest path that delivers the value. The user's explicit request was "Option B — Upgrade existing automation." Approach A does exactly that — expands the existing skill and agent without creating new abstractions.

The SKILL.md growing to ~200 lines is acceptable — it's a reference document, not code. The agent permissions are already partially defined (just need `gh api *` added). The wiki push pattern can be documented in SKILL.md with a note that it requires orchestrator execution.

Approach B is overkill — two agents for one skill is unnecessary complexity. Approach C adds a new file without meaningful benefit over Approach A.

**Key insight**: Wiki push is a git operation, not a `gh` operation. The github-ops agent has `edit: deny`, so it can't push to git. Wiki push will be documented as a pattern in SKILL.md but executed by the orchestrator or git-ops agent. This is the correct architectural boundary.

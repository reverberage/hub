# SDD Spec: rename l06_p0s3 → lo6
change_id: rename-l06-to-lo6

## Goal
Rename the project from l06_p0s3 to lo6. Remove all One Piece / Log Pose references. Clean, short, ownable name.

## Files to modify (in ~/Projects/l06_p0s3/)

### Package identity
- `package.json` — `"name": "l06-p0s3"` → `"name": "lo6"`
- `package-lock.json` — `"name": "l06-p0s3"` → `"name": "lo6"` (2 occurrences)

### Project config
- `.n3rv/a2a-config.yaml` — `project: l06_p0s3` → `project: lo6`

### README.md
- Title: `# l06_p0s3 (Log Pose)` → `# lo6`
- Shield badges: update URLs from l06_p0s3 to lo6
- Remove: "Like the Log Pose from One Piece that locks onto the next island..." paragraph — replace with a one-liner about what lo6 does without anime reference
- Clone URL: `juanmanueldaza/l06_p0s3.git` → `juanmanueldaza/lo6.git`
- Directory: `cd l06_p0s3` → `cd lo6`
- Concept URL: `juanmanueldaza.github.io/l06_p0s3/concept.html` → `juanmanueldaza.github.io/lo6/concept.html`

### AGENTS.md
- Description: remove One Piece paragraph. Keep the "Newsroom Operating System" description.
- Directory listing: `l06_p0s3/` → `lo6/`

### concept.html
- Title: `<title>l06_p0s3 — Newsroom OS</title>` → `<title>lo6 — Newsroom OS</title>`
- Footer stat: `l06_p0s3` → `lo6`, update GitHub URL

### .opencode/agents/n3rv.md
- "You are N3RV, the orchestration agent for l06_p0s3." → "You are N3RV, the orchestration agent for lo6."

### CONTRIBUTING.md
- Title: `# Contributing to l06_p0s3 (Log Pose)` → `# Contributing to lo6`

### docs/ (all 7+ files)
- `docs/task.md` — title: `l06_p0s3 (Log Pose)` → `lo6`
- `docs/frontend_spec.md` — `l06_p0s3 (Log Pose)` → `lo6`
- `docs/data_model.md` — `l06_p0s3 (Log Pose)` → `lo6`
- `docs/Pitch_Executive_Summary.md` — all `l06_p0s3 (Log Pose)` → `lo6`, remove One Piece reference from first paragraph
- `docs/implementation_plan.md` — `l06_p0s3 (Log Pose)` → `lo6`
- `docs/security_spec.md` — `l06_p0s3 (Log Pose)` → `lo6`
- `docs/agent_interface_spec.md` — `l06_p0s3 (Log Pose)` → `lo6`, also `l06_p0s3 Network` → `lo6 Network`
- `docs/lib/security.md` — `l06_p0s3 (Log Pose)` → `lo6`

### What to REMOVE
- All "Log Pose" references (from One Piece)
- All "One Piece" references
- The "Like the Log Pose from One Piece..." paragraph in README and Pitch
- l33tspeak spelling (l06_p0s3) — replace with clean `lo6`

### What to KEEP
- "Newsroom Operating System" description
- "Ableton Live for News" tagline
- Human-in-the-Loop architecture
- All technical content, specs, docs

## Success Criteria
- `npm run build` passes (if applicable)
- `npm run lint` passes
- No remaining `l06_p0s3`, `l06-p0s3`, `Log Pose`, or `One Piece` in any source file
- All GitHub URLs updated to `lo6`

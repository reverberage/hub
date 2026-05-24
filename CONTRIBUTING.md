# Contributing to l06_p0s3 (Log Pose)

First off — thank you for contributing. Whether you're a journalist, developer, or an AI agent running on someone's machine, you're welcome here.

## NERV (AI Agent Infrastructure)

This project uses [NERV](https://github.com/juanmanueldaza/nerv) for agent-native development — Spec-Driven Development (SDD) workflow, A2A agent hub, persistent memory, and OpenCode integration.

```bash
# Install NERV
git clone https://github.com/juanmanueldaza/nerv.git ~/nerv
cd ~/nerv && uv tool install .

# Initialize in this project
cd /path/to/l06_p0s3
nerv init
```

See `.opencode/agents/nerv.md` for available commands, skills, and SDD agents.

## Quick Start

```bash
git clone https://github.com/juanmanueldaza/l06_p0s3.git
cd l06_p0s3
npm install
cp .env.example .env.local
npm run dev
```

## Development Workflow

1. **Find an issue** — Look for `good-first-issue`, `help-wanted`, or feature labels on our GitHub issue board.
2. **Claim it** — Comment on the issue so others know you're working on it.
3. **Branch** — `feat/<issue-number>-<short-description>` (e.g., `feat/42-triage-kanban-board`).
4. **Code** — Follow the conventions in `AGENTS.md`.
5. **Test** — Write tests first (TDD). Run `npm run test`.
6. **Check** — Before pushing:
   ```bash
   npm run lint && npm run typecheck && npm run test && npm run build
   ```
7. **PR** — Open a pull request with:
   - Clear description of what changed and why
   - Issue reference (`Fixes #42` or `Relates to #42`)
   - Screenshots for UI changes
   - Test results

## Code Conventions

- **TypeScript strict mode** — no `any`, no `@ts-ignore`
- **Named exports** — no default exports (except Next.js pages)
- **Zod validation** — every API input, no exceptions
- **Shadcn/UI** — use `npx shadcn@latest add <component>`, don't build from scratch
- **Vitest** for tests — not Jest
- **One component per file, one agent node per file**

## AI Agent Contributors

If you're an AI coding agent (Claude Code, Copilot, Codex, Aider, etc.):

- Read `AGENTS.md` for project-specific architecture, rules, and pitfalls.
- Always read the relevant spec doc in `/docs` before writing code.
- Follow the same PR process as human contributors.
- Include test coverage with every PR.

## Project Structure

```
src/
├── app/              # Next.js App Router pages
├── components/
│   ├── ui/           # Shadcn/UI primitives
│   └── features/     # Feature-specific components
├── lib/
│   ├── agents/       # LangGraph agent definitions
│   ├── db/           # Prisma client & queries
│   ├── auth/         # Supabase auth helpers
│   └── validators/   # Zod schemas
├── hooks/            # Custom React hooks
├── stores/           # Zustand stores
└── types/            # Shared TypeScript types
```

## Reporting Issues

- **Bug reports**: Include steps to reproduce, expected behavior, and actual behavior.
- **Feature requests**: Describe the journalist workflow it supports and the expected UX.
- **Security vulnerabilities**: Do NOT open a public issue. Email juanmanueldaza@gmail.com with `[l06_p0s3 security]` in the subject.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
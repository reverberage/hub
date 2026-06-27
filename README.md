# lo6

![License](https://img.shields.io/github/license/juanmanueldaza/lo6?style=flat-square&label=License)
![GitHub stars](https://img.shields.io/github/stars/juanmanueldaza/lo6?style=flat-square)

> **The Ableton Live for News** — a Newsroom Operating System that orchestrates AI agents for sourcing, research, and drafting while keeping journalists in creative control.

## Concept Preview

[**→ View the visual concept**](https://juanmanueldaza.github.io/lo6/concept.html)

A static preview of the "Editorial Avant-Garde" design system: dark mode canvas, Playfair Display serif headlines, 50/50 split-pane Reading Room with inline source provenance, floating action bars, and Focus Mode (press `Esc`). Built from `docs/frontend_spec.md`.

## Why?

Journalism doesn't need another CMS — it needs a **Studio**. Current AI writing tools are black boxes that hallucinate. lo6 uses a **Human-in-the-Loop** architecture with strict provenance: every claim is visually linked to a verified source.

## Features

- **Newsroom Engine** — LangGraph state machine: Lead → Triage → Research → Draft → Review → Publish
- **Newsroom Console** — 5 dashboard views: Lead Pipeline, Triage Board, Research Desk, Writing Studio, Editorial Review
- **Signal Exchange** — Federated network for sharing verified leads between newsroom instances
- **Source Provenance** — Every AI-generated claim is traced to its source, no black boxes
- **Security-first** — OWASP/NIST/ISO 27001 compliant. MFA, RBAC, audit logging, Zod validation

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 14+ (App Router) |
| Language | TypeScript (strict mode) |
| AI Orchestration | LangChain.js + LangGraph.js |
| Database | PostgreSQL (Supabase/Neon) + Prisma ORM |
| Styling | TailwindCSS + Shadcn/UI |
| State | TanStack Query + Zustand |
| Auth | Supabase Auth (MFA) |
| Queue | BullMQ + Redis (optional, for long-running agents) |

## Project Status

**Phase 1: Design Complete.** Architecture, data model, agent specs, frontend spec, security spec, and funding plan are all documented in [`/docs`](./docs). Implementation starts now.

## Quick Start

```bash
# Clone and install
git clone https://github.com/juanmanueldaza/lo6.git
cd lo6
npm install

# Copy environment template
cp .env.example .env.local

# Run development server
npm run dev
```

## Documentation

| Doc | Description |
|-----|-------------|
| [Implementation Plan](./docs/implementation_plan.md) | Architecture, tech stack, core components |
| [Data Model](./docs/data_model.md) | PostgreSQL schema, Prisma types |
| [Agent Interface Spec](./docs/agent_interface_spec.md) | LangGraph workflows, agent tools & prompts |
| [Frontend Spec](./docs/frontend_spec.md) | UX philosophy, component hierarchy, dashboards |
| [Security Spec](./docs/security_spec.md) | OWASP Top 10 mitigation, RBAC, audit logging |
| [Security Snippets](./docs/lib/security.md) | Copy-pasteable CSP, SSRF, RLS patterns |
| [Accessibility Appendix](./docs/accessibility_appendix.md) | WCAG 2.2 AA compliance |
| [Pitch Executive Summary](./docs/Pitch_Executive_Summary.md) | Investor-facing one-pager |
| [Funding Plan](./docs/Funding_Plan.md) | Grants, consortium, agency, subscription model |

## Contributing

We welcome contributions from humans AND AI agents. See [CONTRIBUTING.md](./CONTRIBUTING.md) for setup instructions, coding standards, and how to claim issues.

If you're using an AI coding assistant (Claude Code, Copilot, Codex, Aider, etc.), read [AGENTS.md](./AGENTS.md) for project-specific guidance.

## Agentic Development (N3RV Framework)

This project uses [N3RV](https://github.com/juanmanueldaza/n3rv) — invisible engineering infrastructure for AI agents. N3RV provides:

- **SDD Workflow**: 8-phase Spec-Driven Development pipeline (`/sdd-new`)
- **A2A Hub**: Agent-to-agent task delegation via JSON-RPC 2.0
- **MAGI Memory**: Persistent semantic memory (ChromaDB + SQLite dual-store)
- **OpenCode Integration**: 9 specialized agents, 14 skills, and slash commands

```bash
# Install N3RV (one-time)
git clone https://github.com/juanmanueldaza/n3rv.git ~/n3rv
cd ~/n3rv && uv tool install .

# Initialize in this project
n3rv init
```

See `.opencode/agents/n3rv.md` for available commands, skills, and SDD agents.

## License

Apache-2.0 © Juan Manuel Daza
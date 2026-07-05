# Implementation Plan — lo6

## Goal Description
To implement lo6 — a robust, scalable "Human-in-the-Loop" media newsroom using TypeScript, React, and LangChain. The system will orchestrate multiple AI agents to source, research, write, and publish news, with distinct dashboards for human oversight.

## User Review Required
> [!IMPORTANT]
> This is a high-level architectural plan. Please review the stack choices and the agent orchestration strategy (LangGraph vs. standard Chains).

## Documentation Strategy
To plan this "seriously", we should produce the following documents:
1.  **Technical Specification (This Document)**: High-level architecture, stack, and system boundaries.
2.  **Data Model Specification**: Database schema (ERD) and type definitions.
3.  **Agent Interface Specification**: Inputs, outputs, and tools for each agent (extending the brief).
4.  **UX/UI Wireframes**: Visual plan for the 5 dashboards.

## Proposed Architecture

### Engineering Principles
To ensure long-term maintainability and scalability, we will strictly adhere to:
- **KISS (Keep It Simple, Stupid)**: Avoid over-engineering. Use standard Next.js patterns (Server Actions, App Router) instead of complex custom layers unless necessary.
- **DRY (Don't Repeat Yourself)**: Centralize logic in shared utilities and hooks. Use a shared UI component library.
- **SOLID**:
    - **S**: Single Responsibility Principle for Agents (one agent, one job) and React Components.
    - **O**: Open/Closed - Design agents to be extensible without modifying core orchestration logic.
    - **L/I/D**: Interface segregation for API responses and Dependency Injection for services (e.g., swapping LLM providers).
- **Clean Code**: Strict TypeScript (no `any`), Prettier/ESLint enforcement, and self-documenting variable names.

### Security & Compliance
We commit to **OWASP, NIST, ISO 27001, CIS, and SEI CERT** standards to ensure highest security:
- **Authentication**: Multi-factor authentication (MFA) via Supabase Auth (NIST IAA).
- **Authorization**: Strict Role-Based Access Control (RBAC) (e.g., *Journalist* vs. *Publisher*).
- **Input Validation**: All API inputs validated with **Zod** schemas to prevent Injection attacks.
- **XSS Protection**: React's default escaping + DOMPurify for any rich text rendering.
- **CSRF**: Next.js built-in protection for Server Actions and API routes.
- **Audit Logging**: Comprehensive logging of all agent and user actions for accountability.

### Tech Stack
- **Full Stack Framework**: Next.js 14+ (App Router) - Handles both React Frontend and API Backend.
- **Language**: TypeScript (Strict mode).
- **AI Orchestration**: LangChain.js & LangGraph.js (for stateful, multi-step agent flows).
- **Database**: PostgreSQL (via Supabase or Neon) + Prisma ORM.
- **Styling**: TailwindCSS + Shadcn/UI.
- **State Management**: TanStack Query (Server state) + Zustand (Client state).

### Core Components

#### 1. The "Newsroom" Engine (Backend)
- **Workflow Manager**: Uses `LangGraph` to define the state machine of a story (Lead -> Triage -> Research -> Draft -> Review -> Publish).
- **Agent Nodes**: Individual functions wrapping LangChain calls for specific tasks (e.g., `researchNode`, `draftingNode`, `crawlerNode`).
- **Queue System**: (Optional) BullMQ/Redis if agent tasks are very long-running ( > 1 min). Required for Web Crawler jobs.
#### 3. The "Newsroom Network" (Signal Exchange)
- **Signal Protocol**: A lightweight JSON standard for sharing verified leads between instances.
- **Federation Node**: An optional service that broadcasts `Approved Leads` to the network and listens for incoming signals.
#### 2. The "Newsroom" Console (Frontend)
- **Dashboard Layout**: Persistent sidebar navigation for the 5 views.
- **Kanban/List Views**: For Triage and Editorial dashboards.
- **Rich Text Editor**: For the News Editor (e.g., Tiptap or Lexical).

## Verification Plan
- **Unit Tests**: Jest/Vitest for individual agent logic.
- **Integration Tests**: End-to-end flow from "New Lead" to "Draft Created".
- **Manual Review**: User testing of each Dashboard interface.

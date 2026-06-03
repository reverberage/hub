# Security Specification (OWASP Compliance)

## Overview
This document outlines the security measures for lo6, specifically addressing the **OWASP Top 10 (2021)** vulnerabilities.

## OWASP Top 10 Mitigation Strategy

| Vulnerability | Mitigation Strategy in Our Stack |
| :--- | :--- |
| **A01: Broken Access Control** | **RBAC Middleware**: Next.js Middleware to enforce roles on all routes.<br>**Row Level Security (RLS)**: Supabase RLS policies to ensure users only access data they are permitted to. |
| **A02: Cryptographic Failures** | **HTTPS Everywhere**: Enforced by Vercel/Deployment platform.<br>**Env Vars**: Secrets managed via `.env.local` and never committed.<br>**Encryption**: Data at rest encrypted by PostgreSQL provider. |
| **A03: Injection** | **ORM Usage**: Prisma/Supabase client prevents SQL injection.<br>**Zod Validation**: Strict schema validation for all LLM inputs and User inputs. |
| **A04: Insecure Design** | **Threat Modeling**: Reviewing agent workflows for "prompt injection" risks.<br>**Rate Limiting**: Upstash Redis to rate limit API routes. |
| **A05: Security Misconfiguration** | **Headers**: Helmet.js equivalent security headers (CSP, HSTS).<br>**Minimal Docker Image**: Distroless images for container deployment. |
| **A06: Vulnerable and Outdated Components** | **Dependabot**: Automated dependency updates.<br>**Snyk**: CI/CD pipeline scanning for vulnerable packages. |
| **A07: Identification and Authentication Failures** | **Supabase Auth**: Delegated secure auth (OAuth/Magic Links).<br>**MFA**: Enforced for Admin/Publisher roles. |
| **A08: Software and Data Integrity Failures** | **CI/CD Signing**: Verified commits and build pipelines.<br>**Subresource Integrity**: For any external scripts. |
| **A09: Security Logging and Monitoring** | **Audit Logs**: Dedicated `audit_logs` table for all critical actions (Publish, Delete).<br>**Alerting**: Sentry for runtime errors and security exceptions. |
| **A10: Server-Side Request Forgery (SSRF)** | **URL Validation**: Strict allowlisting of domains.<br>**Private Network Block**: Agents cannot access internal IPs.<br>**Crawler Ethics**: Respect `robots.txt`, identify via User-Agent, and enforce per-domain rate limits. |

## Role-Based Access Control (RBAC)

| Role | Permissions |
| :--- | :--- |
| **Viewer** | Read-only access to published content. |
| **Journalist** | Create Leads, Write Stories, Trigger Research Agents. |
| **Editor** | Approve Leads, Edit Stories, Reject Content. |
| **Publisher** | Publish to external platforms, Manage Configuration. |
| **Admin** | Manage Users, View Audit Logs, System Configuration. |

## AI-Specific Security (LLM Top 10)
- **Prompt Injection**: Separate system instructions from user content. Use "sandwich" defense where applicable.
- **Output Handling**: Treat all LLM output as untrusted. Sanitize markdown/HTML before rendering.
- **Excessive Agency**: Agents require "Human-in-the-Loop" approval for high-impact actions (Publishing).

## Comprehensive Compliance Mapping

### NIST Cybersecurity Framework (CSF)
| Function | Category | Implementation |
| :--- | :--- | :--- |
| **Identify** | Asset Management | Automated inventory of all Agent Tools and API endpoints. |
| **Protect** | Access Control | RBAC + MFA (Supabase). Least Privilege for Agent API keys. |
| **Detect** | Anomalies | Real-time monitoring of Token Usage spikes (Cost/Security). |
| **Respond** | Mitigation | Kill-switch for all Agents via "Emergency Stop" feature. |
| **Recover** | Backups | Point-in-time recovery (PITR) enabled on PostgreSQL. |

### ISO/IEC 27001:2022 Controls
- **A.5.15 Access Control**: Strict segregation of duties (Journalist vs Publisher).
- **A.8.25 Secure Development Lifecycle**: CI/CD pipeline with automated SAST (Static Application Security Testing).
- **A.8.28 Secure Coding**: Enforcement of SEI CERT coding standards via ESLint/SonarQube.

### CIS Controls (v8) - Implementation Group 1
- **Control 3 (Data Protection)**: All sensitive data (API Keys, PII) encrypted at rest and in transit.
- **Control 4 (Secure Configuration)**: Infrastructure as Code (Terraform/Pulumi) to prevent drift.
- **Control 11 (Data Recovery)**: Automated weekly backups tested for restoration.

### SEI CERT C/C++ (Adapted for TypeScript)
While originally for C/C++, we adapt core principles for TypeScript:
- **Input Validation**: "Validate all input from untrusted sources" -> Zod Schemas for every API route.
- **Error Handling**: "Do not leak information in error messages" -> Generic error responses for clients, detailed logs for internal audit.
- **Concurrency**: "Prevent race conditions" -> Database transactions (Prisma `$transaction`) for multi-step agent updates.

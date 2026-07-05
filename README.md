# reverberage — hub

The meta-repository for the [reverberage](https://github.com/reverberage) ecosystem.

**Composable LEGO pieces for the newsroom.** Reverb + Beverage.

## Satellites

Each satellite is an independent Python package — usable alone or together.

| Satellite | Repo | Package | Status |
|-----------|------|---------|--------|
| **transcriber** | [reverberage/transcriber](https://github.com/reverberage/transcriber) | `rvrb-transcriber` | ![alpha](https://img.shields.io/badge/maturity-alpha-crimson) |
| **verify** | — | `rvrb-verify` | planned |
| **scout** | — | `rvrb-scout` | planned |

→ [Shipyard board](https://github.com/orgs/reverberage/projects/1)

## Concept

[**→ View the visual concept**](https://juanmanueldaza.github.io/lo6/concept.html)

The "Editorial Avant-Garde" design system: dark mode canvas, Playfair Display serif headlines, 50/50 split-pane Reading Room with inline source provenance, floating action bars, Focus Mode.

## Philosophy

- Each satellite does ONE thing. Audio in, text out. Claim in, verdict out.
- Each satellite is independently `pip install`-able and usable.
- Each satellite can connect to any MCP-compatible agentic system.
- No monolith. No framework lock-in. No "you must use our entire ecosystem."

## Docs

| Doc | Status |
|-----|--------|
| [Security Spec](./docs/security_spec.md) | OWASP/NIST/ISO 27001 |
| [Data Model](./docs/data_model.md) | Entity reference |
| [Agent Interface Spec](./docs/agent_interface_spec.md) | Legacy LangGraph spec — being decomposed into satellite protocols |
| [Accessibility Appendix](./docs/accessibility_appendix.md) | WCAG design tokens |
| [Funding Plan](./docs/Funding_Plan.md) | Grants, consortium, subscription |

## License

Apache-2.0 © Juan Manuel Daza

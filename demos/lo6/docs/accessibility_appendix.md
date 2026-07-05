# Accessibility Appendix — Checklist & Color Tokens

This appendix provides a compact accessibility checklist, recommended color tokens with contrast-safe values, and testing guidance to apply to the Newsroom UI.

## Color Tokens (WCAG-compliant pairs)
- `--color-canvas`: #FDFBF7 (Paper) — background
- `--color-ink`: #0B0B0B (Ink) — primary text
- `--color-accent`: #B00020 (Accent/Action) — buttons/alerts (approved for normal text contrast)
- `--color-muted`: #6B6B6B — secondary text
- `--color-success`: #0A7A3E
- `--color-warning`: #B36A00

Notes: these values were selected to meet at least 4.5:1 contrast for body text against `--color-canvas` and to provide clear semantic mapping.

## Typography & Sizing
- Use relative units (`rem`) for font sizes and spacing. Base font-size: `16px` (1rem).
- Headline sizes: `1.5rem` (h1 small screens) up to `2.5rem` (desktop), ensure responsive scaling.
- Minimum touch target: `44x44` CSS pixels for interactive elements.

## Keyboard & Focus
- All interactive controls must be keyboard operable.
- Maintain visible focus outlines; do not remove the focus ring globally.
- Provide `skip to content` link at the top of the page.
- Ensure global shortcuts (J/K, Cmd+Enter) are configurable and can be disabled; do not interfere when focus is inside an input or editor.

## ARIA & Semantic Patterns
- Use semantic HTML elements: `nav`, `main`, `header`, `footer`, `button`, `form`.
- For modals and dialogs, use `role="dialog"` with `aria-modal="true"` and ensure focus trap and return focus to the opener on close.
- For dynamic regions (Research Sidebar), use `aria-live="polite"` for non-critical updates and `aria-live="assertive"` for critical alerts.

## Swipe / Drag Actions
- Provide an accessible alternative to swipe gestures (explicit Approve/Archive buttons and keyboard actions).
- Keep drag-and-drop optional; supply a keyboard mechanism to reorder or insert items.

## Images & Generated Media
- Provide `alt` text for generated images derived from `prompt_used` or journalist-specified caption.
- Provide captions and transcripts for audio/video assets.

## Contrast Checks & Tools
- Automate contrast checks in the design system build step. Use `color-contrast-checker` or `axe`.
- Run `axe-core` integration in Playwright tests for critical paths (Triage, Editor, Publish flow).

## Example Playwright + axe test command
Add an accessibility test in CI using Playwright + `axe-core`:

```bash
# Example: run a11y checks locally
npx playwright test tests/a11y.spec.ts
```

Example minimal test (Playwright + axe) should load the page and run axe on main regions.

## Quick Checklist (Developer Friendly)
- [ ] All interactive controls reachable and usable with keyboard.
- [ ] Color contrast >= 4.5:1 for normal text.
- [ ] Alt text or caption for all images.
- [ ] Focus is managed on opening/closing overlays.
- [ ] ARIA roles and labels present for complex widgets.
- [ ] No functionality depends only on color.
- [ ] Accessible alternatives for swipe/drag.

## Integration Notes for `frontend_spec.md`
- Add a link to this appendix from the main frontend spec.
- Implement color tokens in the design system and validate them during CI.

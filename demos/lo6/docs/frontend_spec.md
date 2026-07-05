# Frontend Specification: The "Newsroom OS"

## Overview
This document defines the frontend architecture for lo6.
**Design Philosophy**: "Editorial Avant-Garde" (Option C).
**Core Experience**: A distraction-free "Reading Room" and "Writing Desk" for journalists.

## Design System (The "Vogue" Stack)
- **Typography**:
    - **Headlines**: *Playfair Display* or *GT Super* (Serif). Used for all content and major headers.
    - **UI/Metadata**: *Geist Sans* or *Inter* (Sans-serif). Small, uppercase, tracking-wide. Used for buttons, labels, and system status.
- **Palette**:
    - **Canvas**: Off-white / Paper (`#FDFBF7`) or Deep Ink (`#0A0A0A`) for dark mode.
    - **Ink**: Sharp Black (`#000000`).
    - **Accent**: Crimson (`#D00000`) for alerts/actions. No other colors unless semantic.
- **Layout**:
    - **No Visible Borders**: Structure defined by whitespace and alignment.
    - **Floating Elements**: Action bars float at the bottom or side, disappearing when not in use.

## Component Hierarchy

### Layouts
- **`NewsroomLayout`**:
    - **`SidebarNav`**: Minimal icon-only rail. Expands on hover.
    - **`FocusModeTrigger`**: Global toggle to hide all UI chrome.

### Routes & Views

#### 1. The Reading Room (`/dashboard/triage`)
*Replaces the "Kanban Board"*
- **Layout**: **Split Pane (50/50)**.
- **Left Pane (The Feed)**: Vertical list of Leads. Large serif headlines.
    - **Action**: Swipe Right (Approve), Swipe Left (Archive), Long Press (Snooze/Monitor).
- **Right Pane (The Source)**: Live preview of the URL (iframe) OR rendered raw HTML/Text from the Crawler.
- **Goal**: Instant verification of provenance.

#### 2. The Writing Desk (`/dashboard/editor/[id]`)
*Replaces the "Rich Text Editor"*
- **Layout**: **Three-Column (Collapsible)**.
    - **Left**: Outline / Navigation (Hidden by default).
    - **Center**: The Paper. Typography mirrors the final publication.
    - **Right**: **Integrated Research Sidebar**.
- **Research Sidebar**:
    - Tabs: *Facts*, *Quotes*, *Timeline*.
    - **Interaction**: Drag-and-drop a quote card into the text to insert it with citation.
- **Copilot**:
    - Inline "/" commands for "Expand", "Counter-argument", "Fact-check this paragraph".

#### 3. The Gallery (`/dashboard/assets`)
*New View*
- **Layout**: Masonry grid of generated images.
- **Interaction**: Click to "Refine Prompt" or "Approve".

## State Management Updates

### Client State (Zustand)
- **`useFocusStore`**: Tracks `isFocusMode` (boolean).
- **`useResearchStore`**: Tracks active "Dossier" items pinned to the side.

## Accessibility
- **High Contrast**: The Black/White aesthetic naturally supports high contrast.
- **Keyboard Shortcuts**: `J/K` for Triage navigation. `Cmd+Enter` to Approve.

## Accessibility Appendix
See `docs/accessibility_appendix.md` for a WCAG checklist, contrast-safe color tokens, keyboard and ARIA guidance, and automated test suggestions.

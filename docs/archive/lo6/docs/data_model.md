# Data Model Specification

## Overview
This document defines the database schema for lo6. We use a relational model (PostgreSQL) to ensure data integrity.

## Entity Relationship Diagram (Mermaid)

```mermaid
erDiagram
    Configuration ||--o{ Lead : generates
    Lead ||--o| Story : becomes
    Story ||--o{ Asset : contains
    Story ||--o{ Publication : produces

    Configuration {
        uuid id PK
        string name
        jsonb sources "List of URLs/RSS"
        jsonb interests "Topics/Keywords"
        string schedule_cron
        timestamp created_at
    }

    Lead {
        uuid id PK
        uuid config_id FK
        string source_url
        string title
        text summary
        float relevance_score
        string status "NEW, TRIAGED, REJECTED, APPROVED"
        timestamp created_at
    }

    Story {
        uuid id PK
        uuid lead_id FK
        string title
        text content_markdown
        string status "DRAFT, REVIEW, APPROVED, PUBLISHED"
        jsonb research_notes
        timestamp updated_at
    }

    Asset {
        uuid id PK
        uuid story_id FK
        string type "IMAGE, VIDEO"
        string url
        string prompt_used
        boolean is_approved
    }

    Publication {
        uuid id PK
        uuid story_id FK
        string platform "TWITTER, BLOG, LINKEDIN"
        string external_id
        string status "SCHEDULED, PUBLISHED, FAILED"
        timestamp published_at
    }
```

## Table Definitions

### 1. Configuration
Stores user settings for the "Configuration Agent".
- **sources**: JSON array of source objects `{ type: 'rss' | 'twitter' | 'crawler' | 'network_signal', url: string }`.
- **interests**: JSON array of strings.

### 2. Lead
Represents a raw item found by the "Source Finding Agent".
- **status**: State machine tracking (New -> Triaged -> Approved).

### 3. Story
The core content entity managed by "Editorial" and "Journalist" agents.
- **content_markdown**: The actual article text.
- **research_notes**: Structured output from the Research Agent.

### 4. Asset
Media files associated with a story.
- **prompt_used**: Stored for reproducibility/debugging of Image Gen Agent.

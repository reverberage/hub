# Agentic Interface Specification

## Overview
This document defines the **LangGraph** architecture for lo6. We utilize a stateful graph approach where agents (Nodes) modify a shared state object.

## Shared Graph State
The `NewsroomState` interface defines the data passed between agents.

```typescript
interface NewsroomState {
  // Messages for chat history
  messages: BaseMessage[];
  // The core entities (Optional as they populate over time)
  lead?: Lead;
  story?: Story;
  research?: ResearchDossier;
  assets?: Asset[];
  // Workflow control
  next_agent: string;
  human_feedback?: string;
  errors?: string[];
  // Status flags
  lead_status?: 'NEW' | 'APPROVED' | 'REJECTED' | 'MONITOR';
}
```

## Workflows (Sub-Graphs)

### 1. Triage Workflow
**Goal**: Ingest raw data and filter for relevance.
- **Nodes**:
    - `TriageManager`: Orchestrator. Spawns specialized tools based on source type.
    - `RSSFetcher`: Parses RSS feeds.
    - `APIConnector`: Connects to external APIs.
    - `WebCrawler`: Scrapes and crawls websites.
    - `SignalReceiver`: Listens for verified leads from the lo6 Network.
    - `SignalReceiver`: Listens for verified leads from the lo6 Network.
    - `ConfigAgent`: Filters items based on "Interests". Scores relevance (0-100).
    - `HumanTriage`: **Interrupt Node**. Waits for user to Approve/Reject/Note.
- **Edges**:
    - `TriageManager` -> `RSSFetcher` / `APIConnector` / `WebCrawler` / `SignalReceiver`
    - `RSSFetcher` / `APIConnector` / `WebCrawler` / `SignalReceiver` -> `ConfigAgent`
    - `ConfigAgent` -> (Score > 50?) -> `HumanTriage`
    - `ConfigAgent` -> (Score <= 50?) -> `END`

### 2. Editorial Workflow
**Goal**: Turn an approved Lead into a Draft Story.
- **Nodes**:
    - `EditorialAgent`: Orchestrator. Decides if research is needed.
    - `ResearchAgent`: Uses tools to gather facts.
    - `JournalistAgent`: Writes the markdown content.
    - `ImageGenAgent`: Generates assets based on story content.
    - `HumanEditor`: **Interrupt Node**. Review draft.
- **Edges**:
    - `EditorialAgent` -> `ResearchAgent`
    - `ResearchAgent` -> `JournalistAgent`
    - `JournalistAgent` -> `ImageGenAgent`
    - `ImageGenAgent` -> `HumanEditor`

### 3. Publishing Workflow
**Goal**: Distribute approved content.
- **Nodes**:
    - `PublisherAgent`: Formats content for specific platforms (Twitter thread vs Blog post).
    - `HumanPublisher`: **Interrupt Node**. Final "Go" button.
    - `Distributor`: API calls to external platforms.

## Agent Tools Definition

| Agent | Tools Available | Description |
| :--- | :--- | :--- |
| **Config Agent** | `calculate_relevance(text, interests)` | Local NLP scoring function. |
| **Research Agent** | `tavily_search(query)`<br>`scrape_webpage(url)` | Web browsing capabilities. |
| **Journalist Agent** | `read_research_dossier()`<br>`check_style_guide()` | Context retrieval tools. |
| **Image Gen Agent** | `dalle_3(prompt)`<br>`stable_diffusion(prompt)` | Image generation APIs. |
| **Publisher Agent** | `twitter_api_post()`<br>`wordpress_api_post()` | External publishing tools. |

## System Prompts Strategy
- **Role**: "You are an expert [Role Name]..."
- **Context**: "You are working on a story about [Title]..."
- **Constraint**: "Output must be valid JSON/Markdown..."
- **Security**: "Do not invent facts. Cite sources from the Research Dossier."

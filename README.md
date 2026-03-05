# ***NOTE: After being given the assignment and investing significant time and effort to complete it, I was ghosted (1 submission email, 2 follow-up emails, 1 LinkedIn message with a follow-up to the founder, and 1 message to another founder) and eventually received only a generic rejection email. I will not be applying there again. The hosting has been removed, so the public links will no longer work. Please install the dependencies from requirements.txt and use run.py to execute the project locally.***


# Status Feed Poller: OpenAI Service Monitor

## Overview

This project is a high-performance, Python-based monitoring system designed to track service updates from the OpenAI Status Page and scale to 100+ similar status providers. Instead of simple manual refreshing, it utilizes a robust, asynchronous polling architecture that transforms RSS/Atom feeds into a real-time event stream.

Updates are pushed via **Server-Sent Events (SSE)** and displayed in the console using **Rich-formatted Markdown panels**, providing a clear, operator-friendly view of infrastructure health.

---

## Design Approach & Thought Process

The primary challenge was balancing the "event-based" requirement with the reality that most status pages do not support modern push protocols.

### 1. Evolution of the Strategy

* **Webhooks:** Initially considered, but rejected because status pages (including OpenAI’s) rarely allow users to register custom webhooks directly without third-party middleware.
* **Email Triggers:** Thought of using emails as a trigger mechanism, but this lacks scalability. Not all providers offer email alerts, and automating an inbox adds unnecessary points of failure.
* **RSS/Atom Feeds (The Winner):** I identified that almost every major status page (Atlassian Statuspage, AWS, Google, OpenAI) exposes an RSS or Atom feed. This is the most standardized way to track updates across 100+ providers.

### 2. Efficiency & Scaling

To ensure the system is "event-like" and doesn't overwhelm providers:

* **ETags & Last-Modified:** I researched using HTTP caching headers to avoid downloading the same content twice. Since support is inconsistent across providers, I implemented a **fetch-and-compare** logic based on the `updated` field within the feed entries.
* **Smart Polling:** To prevent "retry storms" and stay within rate limits, I implemented **Exponential Backoff with Jitter**. The system increases wait times after unsuccessful attempts and adds random noise (jitter) to ensure that 100+ concurrent polls don't hit servers at the exact same millisecond.

---

## Architecture & Structure

The project is built as a professional FastAPI application rather than a simple script, ensuring it can be managed via API and integrated into larger DevOps workflows.

### Folder Structure

```text
bolna_ai_assignment/
├── api/v1/                   # FastAPI routes (Health, Registration, SSE Streaming)
│   ├── health_probes/        # Liveness/Readiness checks
│   ├── rss_atom_feeds.py     # Feed management logic
│   └── stream_console_out.py # SSE Log streaming
├── config/                   # Global constants and polling intervals
├── model/                    # Data models (Pydantic) and State Management
├── service/                  # The "Brain" - FeedManager singleton & polling logic
└── tests/                     # Unit tests
├── main.py                   # FastAPI app initialization
├── run.py                    # Uvicorn entry point
└── requirements.txt          # dependencies (FastAPI, httpx, rich, etc.)



```

### Key Components

* **FeedManager (Singleton):** A central service that manages the lifecycle of all feeds. It ensures that even if you have multiple API consumers, the polling state remains consistent and unique.
* **SSE Streaming:** Instead of just printing to a local console, I exposed `/api/v1/stream-console/logs`. This allows you to view the "Console Output" from any terminal in the world by connecting to the server stream.

---

## API Endpoints & Usage

The service provides a versioned REST API for dynamic control. Below are the key commands for both local and production (Railway) environments.

### 1. Health Check

Verify the service is up and running.

```bash
curl --location 'http://localhost:8000/api/v1/health'

```

### 2. Register a Feed

Add a new status feed URL for monitoring.

```bash
curl --location 'https://bolnaaiassignment-production.up.railway.app/api/v1/feeds/rssatom/register' \
--header 'Content-Type: application/json' \
--data '{
        "url": "https://status.openai.com/feed.atom"
      }'

```

### 3. Deregister a Feed

Stop monitoring a specific feed.

```bash
curl --location 'https://bolnaaiassignment-production.up.railway.app/api/v1/feeds/rssatom/deregister' \
--header 'Content-Type: application/json' \
--data '{
        "url": "https://status.openai.com/feed.atom"
      }'

```

### 4. Stream Logs (Real-time Output)

Connect to the SSE stream to see updates as they happen.

```bash
curl --location 'https://bolnaaiassignment-production.up.railway.app/api/v1/stream-console/logs'

```

---

## Running the Project Locally

1. **Set up Python (3.10+):**
```bash
python3 -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Start the server:**
```bash
python run.py

```



---

## Console Output Example

When an update is detected (e.g., from the OpenAI Atom feed), the SSE stream renders a formatted panel:

```text
╭──────────────────────── Status Update ────────────────────────╮
│ OpenAI API: Chat Completions                                  │
│                                                               │
│ ● Status: Degraded performance due to upstream issue          │
│ ● Updated: 2026-02-21 14:32:00                                │
╰───────────────────────────────────────────────────────────────╯

```

---

## Future Scope & Improvements

* **Persistence:** Currently, the `FeedManager` stores state in memory. Transitioning to **Redis or SQLite** would allow the system to remember the "last seen" update across restarts.
* **Rate Limiting:** Implementing a Redis-based rate limiter to ensure the application doesn't get IP-banned when scaling to 1000+ feeds.
* **Advanced Filtering:** Adding the ability to register feeds with specific keywords (e.g., "Only alert if 'API' is in the title").

---

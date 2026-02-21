# Status Feed Poller

## Overview

This project is a Python-based status page monitor that polls RSS/Atom feeds (such as those used by OpenAI’s status pages) and streams updates in real time to the console. It is designed to scale to 100+ status pages. When new updates are detected, a summary is printed using **Rich-formatted Markdown panels**.

**Typical use cases:** Monitoring cloud service status pages, product incident feeds, and infrastructure alerts.

---

## Design Approach & Thought Process

During design, several strategies were evaluated:

* **Webhooks or Push:** Rejected because most status pages do not expose webhooks or support protocols like WebSub (PubSubHubbub) consistently.
* **Email Alerts:** Rejected due to the complexity of automating inbox monitoring and reliability concerns. Also the fact that not all providers send email alerts for every update.
* **Direct Polling (Chosen):** Universally compatible. To prevent system overload:
* **Exponential Backoff:** Increases delay after unsuccessful attempts (1s, 2s, 4s, etc.).
* **Jitter:** Adds randomness to delays to prevent "retry storms."


* **ETags/Last-Modified:** Considered for caching, but skipped in the initial version due to inconsistent server-side support; uses a **fetch-and-compare** strategy instead.
* **FeedManager Singleton:** A central manager tracks all registered feeds and their state (last update timestamp) to ensure data consistency.

---

## Architecture & Structure

The project follows a layered separation of concerns:

```text
bolna_ai_assignment/
├── api/v1/                   # FastAPI routes (Health, Registration, SSE Streaming)
├── config/                   # Timeouts and constants
├── model/                    # Data classes and FeedManager singleton
├── service/                  # Business logic (Polling, Parsing, Detection)
├── main.py                   # FastAPI app & middleware configuration
├── run.py                    # Entry point (Uvicorn launcher)
└── requirements.txt          # dependencies (FastAPI, httpx, rich, etc.)

```

### Key Components

* **SSE (Server-Sent Events):** Used in `stream_console_out.py` to provide a one-way real-time push of logs from the server to the client.
* **Async Polling:** The service layer uses `httpx` and `asyncio` to fetch multiple feeds concurrently without blocking.

---

## API Endpoints

### 1. Register a Feed

`POST /api/v1/rssatom/register`

```bash
curl -X POST "http://localhost:8000/api/v1/rssatom/register" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://status.openai.com/atom.xml"}'

```

### 2. Deregister a Feed

`POST /api/v1/rssatom/deregister`

```bash
curl -X POST "http://localhost:8000/api/v1/rssatom/deregister" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://status.openai.com/atom.xml"}'

```

### 3. Stream Console Logs (SSE)

`GET /api/v1/stream-console/logs`

```bash
curl -N "http://localhost:8000/api/v1/stream-console/logs"

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

## Console Output

Updates are rendered using the **Rich** library. Example output:

```text
╭──────────────────────── Status Update ────────────────────────╮
│ **OpenAI Status Page:** Partial System Outage                 │
│                                                               │
│ - **Title:** Service degradation in us-east-1               │
│ - **Details:** Users may experience higher latency            │
│ - **Time:** 2026-02-21T12:34:56Z                           │
╰───────────────────────────────────────────────────────────────╯

```

---

## Improvements & Scope

* **Persistence:** Integrate SQLite or Redis to store feed state across restarts.
* **Filtering:** Add rules to only alert on "Critical" or "Major" incident levels.
* **Web Dashboard:** A frontend UI to manage feeds and view history visually.
* **Scaling:** Implement worker pools for even larger scale (1000+ feeds).

---

Would you like me to generate a `docker-compose.yml` file to help you containerize this setup?
<div align="center">

# RECON//OS

**Subdomain reconnaissance dashboard with built-in change tracking**

_Orchestrate. Discover. Diff. All from one dark-mode console._

![Version](https://img.shields.io/badge/version-1.0.0-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Tests](https://img.shields.io/badge/tests-8%20passed-brightgreen)
![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)

[Features](#features) · [Architecture](#architecture) · [Installation](#installation) · [Usage](#usage) · [Testing](#testing) · [Roadmap](#roadmap)

<!-- Replace with a screenshot or demo GIF of the running app -->
<img src="docs/demo.gif" alt="RECON//OS dashboard: a re-scan flags a new subdomain" width="820">

</div>

---

## Overview

RECON//OS turns a pile of recon CLI tools into one searchable asset inventory. It runs `subfinder`, `httpx`, `shuffledns` and friends concurrently in the background, merges their output, and stores every scan so you can see **what changed** between runs. Built for bug bounty hunters, penetration testers and security researchers who monitor targets over time.

### The diff engine

Most recon tooling is stateless: it shows what exists _now_. RECON//OS keeps history and labels every asset after each scan:

| Label       | Meaning                                                             |
| ----------- | ------------------------------------------------------------------- |
| **NEW**     | Subdomain seen for the first time                                   |
| **CHANGED** | Status code, IP or technologies differ from the previous scan       |
| **GONE**    | Present in earlier scans, absent now (decommissioned or firewalled) |

New and changed assets are where fresh attack surface tends to appear.

---

## Features

### Multi-tool orchestration

Start a **Quick** or **Deep** scan with one click. Tools run concurrently as async subprocesses, so the API never blocks.

| Category               | Tools                                            | Status                                          |
| ---------------------- | ------------------------------------------------ | ----------------------------------------------- |
| Passive enumeration    | `subfinder`, `findomain`                         | Available                                       |
| Passive enumeration    | `amass`, `assetfinder`, `sublist3r`, `oneforall` | Installed by the setup script, adapters planned |
| Active DNS             | `shuffledns` + `massdns`, `dnsx`                 | Available                                       |
| Active DNS             | `gobuster`, `dnsrecon`                           | Installed by the setup script, adapters planned |
| HTTP probing           | `httpx` (status, title, tech, CDN)               | Available                                       |
| Vulnerability scanning | `nuclei`                                         | Planned (v1.2)                                  |
| Screenshots            | `gowitness`, `eyewitness`                        | Planned (v1.2)                                  |

### Processing pipeline

- **Wildcard DNS detection** flags `*.domain.com` patterns so brute-forcing doesn't flood results with false positives.
- **Enrichment** resolves IP and CNAME through `dnsx`, even for hosts that don't answer over HTTP.
- **Empty-result guard** treats a zero-finding scan as a failure, never as "everything died" — one rate-limited tool can't wipe your inventory.
- **Diff engine** compares each scan against history to assign NEW, CHANGED and GONE.

### Interface

- Color-coded status strips: 2xx green, 3xx blue, 4xx orange, 5xx red
- Yellow **NEW** badges on first-seen subdomains
- Filter chips for status class, CDN, dead hosts, starred and new-only
- Search by subdomain, title or IP
- Three.js particle background and JetBrains Mono typography

---

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                  │
│  ┌──────────┐  ┌───────────────┐  ┌──────────────────────┐  │
│  │ Three.js │  │  Dashboard    │  │  Zustand store       │  │
│  │ particles│  │  table/stats  │  │  (single source)     │  │
│  └──────────┘  └───────────────┘  └──────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API (JSON)
┌──────────────────────────▼──────────────────────────────────┐
│                    BACKEND (FastAPI)                        │
│                                                             │
│  API routes → Orchestrator → Scanner adapters → Diff engine │
│               (asyncio.gather)  (subprocess)                │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
    ┌────────▼─────────┐            ┌─────────▼─────────┐
    │  CLI binaries    │            │  SQLite (async)   │
    │  subfinder       │            │  - domains        │
    │  httpx           │            │  - scans          │
    │  shuffledns      │            │  - assets         │
    │  ...             │            │  - observations   │
    └──────────────────┘            └───────────────────┘
```

### Design decisions

1. **Asset vs. observation.** An `Asset` is the persistent identity (the subdomain); an `Observation` is its per-scan snapshot. This split is what makes history and diffing cheap.
2. **Adapter pattern.** Each tool is a class inheriting `BaseScanner` and returning a standardized `set[str]`. Adding or swapping a tool never touches the orchestrator.
3. **Absolute binary paths.** `settings.gobin()` resolves tools explicitly, avoiding PATH shadowing such as Python `httpx` versus ProjectDiscovery `httpx`.
4. **Background tasks.** `POST /scans` returns `202 Accepted` immediately and progress is polled. WebSocket streaming is planned.

### Tech stack

| Layer       | Technology                           | Why                                     |
| ----------- | ------------------------------------ | --------------------------------------- |
| Backend     | FastAPI, SQLAlchemy 2.0, Pydantic v2 | Async-first, typed, auto-generated docs |
| Database    | SQLite via aiosqlite                 | Zero config, single portable file       |
| Frontend    | React 18, Vite, Tailwind CSS v4      | Fast dev loop, utility-first styling    |
| 3D          | Three.js via @react-three/fiber      | Declarative scene graph in React        |
| State       | Zustand                              | Small, minimal boilerplate              |
| Recon tools | External CLIs (Go, Rust, Python)     | Mature, fast, run as subprocesses       |
| Testing     | pytest + pytest-asyncio              | Async fixtures, in-memory SQLite        |
| Packaging   | Docker + docker-compose              | One-command, reproducible deployment    |

---

## Installation

Two paths: **Docker** (fastest, reproducible) or **manual** (full control, recommended for development on WSL2).

### Prerequisites

- **Docker path:** Docker Engine + Compose v2
- **Manual path:** Python 3.12+, Node.js 20+, Go 1.22+
- **Windows users:** WSL2 (Ubuntu) is strongly recommended — the recon binaries are Linux-native

### Option A — Docker (one command)

```bash
git clone https://github.com/HosseinShahverdi/recon_dashboard.git
cd recon_dashboard
docker compose up --build
```

| Service  | URL                        | Notes                              |
| -------- | -------------------------- | ---------------------------------- |
| Frontend | http://localhost:5173      | nginx serving the production build |
| Backend  | http://localhost:8000      | uvicorn, recon tools baked in      |
| API docs | http://localhost:8000/docs | Swagger UI                         |

- The SQLite database persists in `backend/data/` via a bind mount — scans survive container restarts.
- Wordlists are mounted from `backend/wordlists/`.
- The backend has a healthcheck; the frontend waits for it via `depends_on`.
- Add `-d` to run detached: `docker compose up --build -d`.

### Option B — Manual setup

#### 1. Clone

```bash
git clone https://github.com/HosseinShahverdi/recon_dashboard.git
cd recon_dashboard
```

#### 2. Install the recon tools

```bash
chmod +x scripts/install_tools.sh
./scripts/install_tools.sh
```

The script installs:

- ProjectDiscovery tools: `subfinder`, `httpx`, `dnsx`, `nuclei`, `shuffledns`
- OWASP Amass
- `massdns` (built from source)
- `findomain` (Rust binary)
- Python tools: `dnsrecon`, `sublist3r`, `oneforall`
- Wordlists: top 110k subdomains and public resolvers

#### 3. Start the backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

#### 5. Open it

| Service            | URL                        |
| ------------------ | -------------------------- |
| Dashboard          | http://localhost:5173      |
| API docs (Swagger) | http://localhost:8000/docs |

> **Security note:** v1 has no authentication. Keep it bound to `localhost` and don't expose the API to a network you don't control.

---

## Usage

### 1. Add a domain

Use the **+** field in the top bar, or call the API:

```bash
curl -X POST http://localhost:8000/api/v1/domains/ \
  -H "Content-Type: application/json" \
  -d '{"name": "example.com"}'
```

### 2. Run a scan

| Mode      | What runs                                                              | Use it for                                     |
| --------- | ---------------------------------------------------------------------- | ---------------------------------------------- |
| **Quick** | Passive sources only (`subfinder`, `findomain`)                        | Fast checks and routine re-scans               |
| **Deep**  | Passive sources plus brute-force (`shuffledns` with the 110k wordlist) | Finding hidden subdomains, at the cost of time |

### 3. Analyze results

- **Stat cards:** total assets, new discoveries, live hosts, unique IPs, CDN usage, scan count
- **Filter chips:** `2xx`, `3xx`, `4xx`, `5xx`, `dead`, `new only`, `starred`, `hide gone`
- **Search:** subdomain, title or IP
- **Export:** CSV, JSON and TXT (planned for v1.1)

### 4. Track changes

Run the same scan again. The diff engine will:

- badge new subdomains with a yellow **NEW**
- highlight status changes such as `200 → 403`
- gray out gone assets (toggle **hide gone** to remove them)

---

## Testing

The test suite runs against an **in-memory SQLite database** — your real `recon.db` is never touched.

```bash
cd backend
source .venv/bin/activate
pytest -v
```

Coverage (8 tests):

| File                        | What it verifies                                                                                                          |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `tests/test_diff_engine.py` | Unseen assets marked GONE; seen assets stay alive; returning assets revive; other domains untouched; empty history is safe |
| `tests/test_api.py`         | Health endpoint; domain creation; duplicate-domain rejection                                                               |

Fixtures live in `tests/conftest.py` (fresh engine + session per test, sample domain/scan factories).

---

## Project structure

```text
recon-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI entry, lifespan, CORS
│   │   ├── core/config.py        # Settings, gobin() path resolver
│   │   ├── db/
│   │   │   ├── models.py         # Domain, Scan, Asset, Observation
│   │   │   └── session.py        # Async engine and session maker
│   │   ├── api/v1/
│   │   │   ├── domains.py        # CRUD for target domains
│   │   │   ├── scans.py          # POST /scans, GET /scans/{id}
│   │   │   ├── assets.py         # Filtered asset list
│   │   │   ├── stats.py          # Stat card aggregations
│   │   │   └── tools.py          # Tool health check
│   │   ├── services/
│   │   │   ├── orchestrator.py   # asyncio.gather over scanners
│   │   │   ├── scan_manager.py   # Background task pipeline
│   │   │   ├── wildcard.py       # Wildcard DNS detection
│   │   │   └── diff_engine.py    # NEW / CHANGED / GONE logic
│   │   └── scanners/             # One adapter per tool
│   │       ├── base.py           # BaseScanner abstract class
│   │       ├── subfinder.py
│   │       ├── httpx_probe.py
│   │       ├── shuffledns.py
│   │       └── dnsx_resolve.py
│   ├── tests/                    # pytest suite (in-memory SQLite)
│   ├── wordlists/                # subdomains-top110k.txt, resolvers.txt
│   ├── data/                     # recon.db (SQLite, gitignored)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Main layout
│   │   ├── three/ParticleField.jsx
│   │   ├── components/
│   │   │   ├── Topbar.jsx        # Domain selector and scan buttons
│   │   │   ├── StatCards.jsx
│   │   │   ├── FilterBar.jsx     # Status chips and toggles
│   │   │   └── ResultsTable.jsx
│   │   ├── store/useReconStore.js
│   │   └── services/api.js       # API client
│   ├── Dockerfile
│   └── vite.config.js
├── scripts/install_tools.sh      # One-shot tool installer
├── docker-compose.yml
├── .gitignore
├── LICENSE
└── README.md
```

---

## Troubleshooting

| Symptom                             | Fix                                                                                                   |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `command not found` for recon tools | Ensure `~/go/bin` and `~/.recon-tools-venv/bin` are on PATH; check `GET /api/v1/tools/health`           |
| `400` on `OPTIONS` requests (CORS)  | Open the dashboard on an allowed origin — `localhost:5173` and `127.0.0.1:5173` are different origins  |
| Scan marks everything GONE          | The empty-result guard marks such scans `failed`; inspect `GET /scans/{id}` and re-run                 |
| React "Invalid hook call"           | Duplicate React copies: `rm -rf node_modules package-lock.json && npm install`                        |
| Tools fail on native Windows        | Use WSL2 — the binaries target Linux                                                                   |
| Port already in use                 | Change ports in `docker-compose.yml`, or pass `--port` to uvicorn / `server.port` to Vite              |

---

## Roadmap

**v1.1**

- [ ] WebSocket live scan progress (replacing polling)
- [ ] Build-scan modal that generates a `recon.sh` script
- [ ] Export menu: CSV, JSON, TXT
- [ ] Column visibility menu, persisted to localStorage
- [ ] Scan history timeline

**v1.2**

- [ ] Nuclei integration
- [ ] Screenshot gallery (gowitness)
- [ ] Subdomain takeover detection (dangling CNAMEs)
- [ ] ASN and port enrichment (naabu, masscan)
- [ ] Adapters for amass, assetfinder, sublist3r, oneforall, gobuster, dnsrecon

**v2.0**

- [ ] Authentication and multi-user support
- [ ] PostgreSQL backend
- [ ] 3D subdomain graph
- [ ] Webhook alerts for NEW and CHANGED assets

---

## Contributing

Contributions are welcome, especially:

- new scanner adapters (subclass `BaseScanner`)
- UI work: export, columns, history
- bug fixes in wildcard handling and diff logic

Please open an issue before starting a large change.

---

## Responsible use

Use RECON//OS only against domains you own or have explicit written permission to test, such as an in-scope bug bounty program. Unauthorized scanning may violate laws including the CFAA and the Computer Misuse Act. The authors accept no liability for misuse.

---

## Acknowledgments

- Inspired by ideas and feedback from **Reza Sharifzadeh**.
- Built on the shoulders of the open-source recon ecosystem: ProjectDiscovery, OWASP Amass, SecLists and the massdns/findomain authors.

---

## License

Released under the [MIT License](LICENSE).

---

<div align="center">

If RECON//OS helps you find a bug, consider giving it a star. ⭐

</div>

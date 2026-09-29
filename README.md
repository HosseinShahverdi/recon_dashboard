<div align="center">

# RECON//OS

**Subdomain reconnaissance dashboard with built-in change tracking**

_Orchestrate. Discover. Diff. All from one dark-mode console._

![Version](https://img.shields.io/badge/version-1.0.0-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)

[Features](#features) · [Architecture](#architecture) · [Installation](#installation) · [Usage](#usage) · [Roadmap](#roadmap)

<!-- Replace with a screenshot or the demo GIF of the running app -->
<img src="docs/demo.gif" alt="RECON//OS dashboard: a re-scan flags a new subdomain" width="820">

</div>

---

## Overview

RECON//OS turns a pile of recon CLI tools into one searchable asset inventory. It runs `subfinder`, `httpx`, `shuffledns` and friends concurrently in the background, merges their output, and stores every scan so you can see **what changed** between runs. It is built for bug bounty hunters, penetration testers and security researchers who monitor targets over time.

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
- **Diff engine** compares each scan against history to assign NEW, CHANGED and GONE.

### Interface

- Color-coded status strips: 2xx green, 3xx blue, 4xx orange, 5xx red
- Yellow **NEW** badges on first-seen subdomains
- Filter chips for status class, CDN, dead hosts, starred and new-only
- Search by subdomain, title or IP
- Three.js particle background and JetBrains Mono typography

---

## Architecture

```
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

---

## Installation

### Prerequisites

- Python 3.12+
- Node.js 20+
- Go 1.22+ (to build the recon tools)
- WSL2 on Windows (recommended)

### 1. Clone

```bash
git clone https://github.com/<your-username>/recon-dashboard.git
cd recon-dashboard
```

### 2. Install the recon tools

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

### 3. Start the backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Open it

| Service            | URL                        |
| ------------------ | -------------------------- |
| Dashboard          | http://localhost:5173      |
| API docs (Swagger) | http://localhost:8000/docs |

> **Note:** v1 has no authentication. Keep it bound to `localhost` and don't expose the API to a network you don't control.

---

## Usage

### 1. Add a domain

Use the **+** button in the top bar, or call the API:

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

- **Stat cards:** total assets, new discoveries, live hosts, CDN usage
- **Filter chips:** `2xx`, `3xx`, `4xx`, `5xx`, `dead`, `new only`, `starred`
- **Search:** subdomain, title or IP
- **Export:** CSV, JSON and TXT (planned for v1.1)

### 4. Track changes

Run the same scan again. The diff engine will:

- badge new subdomains with a yellow **NEW**
- highlight status changes such as `200 → 403`
- gray out gone assets (toggle **hide gone** to remove them)

---

## Project structure

```
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
│   ├── wordlists/                # subdomains-top110k.txt, resolvers.txt
│   └── data/                     # recon.db (SQLite)
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
│   └── vite.config.js
├── scripts/install_tools.sh      # One-shot tool installer
├── LICENSE
└── README.md
```

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

## License

Released under the [MIT License](LICENSE).

---

<div align="center">

If RECON//OS helps you find a bug, consider giving it a star.

</div>

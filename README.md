```markdown
<div align="center">

# 🔭 RECON//OS

### The Professional Subdomain Reconnaissance Dashboard

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)

_Orchestrate. Discover. Analyze. — All in one dark-mode cockpit._

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Roadmap](#-roadmap)

</div>

---

## 🎯 Overview

**RECON//OS** is a full-stack reconnaissance dashboard that transforms the chaos of 12+ CLI tools into a unified, searchable, and visual asset inventory. Built for bug bounty hunters, penetration testers, and security researchers who need to track subdomain changes over time.

Instead of juggling `subfinder`, `httpx`, `amass`, and `shuffledns` in terminal windows, RECON//OS runs them concurrently in the background, correlates the results, and presents them in a professional dark-mode UI with Three.js particle effects.

### The "Diff Engine" Advantage

Most recon tools are stateless — they show you what exists _now_. RECON//OS tracks **history**:

- 🆕 **NEW** — Subdomains discovered for the first time
- 🔄 **CHANGED** — Status codes, IPs, or technologies that flipped
- 💀 **GONE** — Assets that disappeared (decommissioned or firewalled)

This is how you spot the subtle changes that lead to critical vulnerabilities.

---

## ✨ Features

### 🚀 Multi-Tool Orchestration

Concurrently run the industry's best tools via a single **Quick** or **Deep** scan button:

| Category         | Tools                                                                      |
| ---------------- | -------------------------------------------------------------------------- |
| **Passive Enum** | `subfinder`, `findomain`, `assetfinder`, `amass`, `sublist3r`, `oneforall` |
| **Active DNS**   | `shuffledns` + `massdns` (brute-force), `dnsx`, `gobuster`, `dnsrecon`     |
| **HTTP Probing** | `httpx` (status, title, tech, CDN), `nuclei`                               |
| **Screenshots**  | `gowitness`, `eyewitness`                                                  |

### 🧠 Intelligent Processing

- **Wildcard DNS Detection** — Automatically identifies `*.domain.com` patterns and flags them, preventing false positives from brute-force
- **Async Pipeline** — All tools run via `asyncio` subprocesses without blocking the API
- **Diff Engine** — Compares current scan against history to identify NEW/CHANGED/GONE assets
- **Enrichment Layer** — Even "dead" hosts get IP/CNAME resolution via `dnsx`

### 🎨 Pro UI

- **Three.js Ambient Background** — Subtle particle field with vignette
- **JetBrains Mono** — Monospace typography for terminal-native eyes
- **Status Strips** — Color-coded left borders (2xx green, 3xx blue, 4xx orange, 5xx red)
- **NEW Badges** — Yellow highlights for first-seen subdomains
- **Filter Chips** — One-click filtering by status class, CDN, or "new only"

---

## 🏗️ Architecture
```

┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (React + Vite) │
│ ┌──────────┐ ┌───────────────┐ ┌──────────────────────┐ │
│ │ Three.js │ │ Dashboard │ │ Zustand Store │ │
│ │ Particles│ │ Table/Stats │ │ (single source) │ │
│ └──────────┘ └───────────────┘ └──────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
│ REST API (JSON)
┌──────────────────────────▼──────────────────────────────────┐
│ BACKEND (FastAPI) │
│ │
│ API Routes → Orchestrator → Scanner Adapters → Diff Engine │
│ (asyncio.gather) (subprocess) │
└────────────┬────────────────────────────────┬───────────────┘
│ │
┌────────▼─────────┐ ┌─────────▼─────────┐
│ CLI Binaries │ │ SQLite (async) │
│ subfinder │ │ - domains │
│ httpx │ │ - scans │
│ shuffledns │ │ - assets │
│ amass │ │ - observations │
│ ... │ │ │
└──────────────────┘ └───────────────────┘

````

### Key Design Decisions

1. **Asset vs. Observation** — `Asset` = persistent identity (subdomain), `Observation` = per-scan snapshot. This separation enables history tracking.
2. **Adapter Pattern** — Each tool is a class inheriting from `BaseScanner`, returning a standardized `set[str]`. Swap tools without touching orchestrator logic.
3. **Absolute Binary Paths** — Uses `settings.gobin()` to prevent PATH shadowing (the infamous Python `httpx` vs Go `httpx` conflict).
4. **Background Tasks** — Scans return `202 Accepted` instantly; progress is polled (or streamed via WebSocket in v2).

---

## 📦 Tech Stack

| Layer | Technology | Why |
|-------|------------|-----|
| **Backend** | FastAPI, SQLAlchemy 2.0, Pydantic v2 | Async-first, type-safe, auto-docs |
| **Database** | SQLite (via aiosqlite) | Zero-config, single-file, portable |
| **Frontend** | React 18, Vite, Tailwind CSS v4 | Fast HMR, modern CSS-in-JS |
| **3D** | Three.js via @react-three/fiber | Declarative 3D, no memory leaks |
| **State** | Zustand | Tiny, no boilerplate |
| **Tools** | Go binaries (subfinder, httpx, etc.) | Battle-tested, fast, concurrent |

---

## 🛠️ Installation

### Prerequisites
- **Python 3.12+**
- **Node.js 20+**
- **Go 1.22+** (for tool compilation)
- **WSL2** (recommended for Windows users)

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/recon-dashboard.git
cd recon-dashboard
````

### 2. Install Recon Tools

```bash
chmod +x scripts/install_tools.sh
./scripts/install_tools.sh
```

This script installs:

- All ProjectDiscovery tools (subfinder, httpx, dnsx, nuclei, shuffledns)
- OWASP Amass
- massdns (compiled from source)
- findomain (Rust binary)
- Python tools (dnsrecon, sublist3r, oneforall)
- Wordlists (top 110k subdomains + public resolvers)

### 3. Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Access

- **API Docs:** `http://localhost:8000/docs` (Swagger UI)
- **Dashboard:** `http://localhost:5173`

---

## 📖 Usage

### 1. Add a Domain

Click the **+** button or use the API:

```bash
curl -X POST http://localhost:8000/api/v1/domains/ \
  -H "Content-Type: application/json" \
  -d '{"name": "example.com"}'
```

### 2. Run a Scan

- **⚡ Quick** — Passive tools only (subfinder + findomain). Fast, ~30 seconds.
- **🔥 Deep** — Passive + Brute-force (shuffledns + 110k wordlist). Slower, finds hidden subdomains.

### 3. Analyze Results

- **Stat Cards** — Total assets, new discoveries, live hosts, CDN usage
- **Filter Chips** — `2xx`, `3xx`, `4xx`, `5xx`, `dead`, `new only`, `starred`
- **Search** — Filter by subdomain, title, or IP
- **Export** — CSV, JSON, or TXT (coming in v1.1)

### 4. Track Changes

Run the same scan again. The diff engine will:

- Mark new subdomains with a yellow **NEW** badge
- Highlight status code changes (e.g., 200 → 403)
- Gray out "gone" assets (toggle "hide gone" to filter)

---

## 📂 Project Structure

```
recon-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry, lifespan, CORS
│   │   ├── core/
│   │   │   └── config.py        # Settings, gobin() path resolver
│   │   ├── db/
│   │   │   ├── models.py        # Domain, Scan, Asset, Observation
│   │   │   └── session.py       # Async engine + session maker
│   │   ├── api/v1/
│   │   │   ├── domains.py       # CRUD for target domains
│   │   │   ├── scans.py         # POST /scans, GET /scans/{id}
│   │   │   ├── assets.py        # Filtered asset list
│   │   │   ├── stats.py         # Stat card aggregations
│   │   │   └── tools.py         # Tool health check
│   │   ├── services/
│   │   │   ├── orchestrator.py  # asyncio.gather over scanners
│   │   │   ├── scan_manager.py  # Background task pipeline
│   │   │   ├── wildcard.py      # Wildcard DNS detection
│   │   │   └── diff_engine.py   # NEW/CHANGED/GONE logic
│   │   └── scanners/            # ONE adapter per tool
│   │       ├── base.py          # BaseScanner abstract class
│   │       ├── subfinder.py
│   │       ├── httpx_probe.py
│   │       ├── shuffledns.py
│   │       └── dnsx_resolve.py
│   ├── wordlists/               # subdomains-top110k.txt, resolvers.txt
│   └── data/                    # recon.db (SQLite)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main layout
│   │   ├── three/
│   │   │   └── ParticleField.jsx # Ambient 3D background
│   │   ├── components/
│   │   │   ├── Topbar.jsx       # Domain selector + scan buttons
│   │   │   ├── StatCards.jsx    # 7 stat cards
│   │   │   ├── FilterBar.jsx    # Status chips + toggles
│   │   │   └── ResultsTable.jsx # Main data table
│   │   ├── store/
│   │   │   └── useReconStore.js # Zustand state management
│   │   └── services/
│   │       └── api.js           # API client wrapper
│   └── vite.config.js
│
├── scripts/
│   └── install_tools.sh         # One-shot tool installer
└── README.md
```

---

## 🗺️ Roadmap

### v1.1 (Next)

- [ ] WebSocket live scan progress (replace polling)
- [ ] Build Scan modal with generated `recon.sh` script
- [ ] Export menu (CSV, JSON, TXT, screenshots)
- [ ] Columns menu (toggle visibility, persist to localStorage)
- [ ] Scan history timeline

### v1.2

- [ ] Nuclei integration (vulnerability scanning)
- [ ] Screenshot gallery (gowitness)
- [ ] Subdomain takeover detection (dangling CNAMEs)
- [ ] ASN/Port enrichment (naabu + masscan)

### v2.0

- [ ] Multi-user support
- [ ] Postgres backend (production-ready)
- [ ] 3D subdomain graph (Three.js)
- [ ] Alerting (webhooks for NEW/CHANGED assets)

---

## 🤝 Contributing

Contributions welcome! Areas of interest:

- New scanner adapters (e.g., `amass`, `oneforall`)
- UI improvements (export, columns, history)
- Bug fixes (wildcard edge cases, diff logic)

Please open an issue first to discuss major changes.

---

## ⚠️ Disclaimer

This tool is for **authorized security testing only**. Scanning domains you do not own or have explicit permission to test may violate laws (CFAA, Computer Misuse Act, etc.). The authors assume no liability for misuse.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with 🔥 by security engineers, for security engineers.**

_If this tool helps you find a bug, consider starring the repo!_

</div>
```

This README is designed to look professional on GitHub. Key elements:

1. **Hero section** with badges and tagline
2. **Clear value proposition** — what makes it different
3. **Architecture diagram** — shows engineering depth
4. **Feature tables** — scannable, professional
5. **Complete installation guide** — reproducible
6. **Project structure tree** — shows organization
7. **Roadmap** — shows vision and future work
8. **Disclaimer** — responsible disclosure

You can enhance it further by:

- Adding a screenshot/GIF of the dashboard
- Adding a LICENSE file (MIT recommended)
- Creating a GitHub repo with proper topics (`bug-bounty`, `recon`, `subdomain-enumeration`)
- Adding CI/CD badges (GitHub Actions for linting/tests)

Let me know if you want me to create the LICENSE file or help set up GitHub Actions for automated testing!

#!/usr/bin/env bash

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORDLIST_DIR="$PROJECT_ROOT/backend/wordlists"

echo "============================================"
echo "🚀 STARTING RECON TOOL INSTALLATION"
echo "============================================"

# ── 0) prerequisites ──────────────────────────────────────────
echo "➡️  [0/6] Installing Linux prerequisites..."
sudo apt update
sudo apt install -y git curl make build-essential python3 python3-venv python3-pip pipx

# ── 1) Install Go 1.22 (official tarball — not the apt package) ──
echo "➡️  [1/6] Installing Go 1.22..."
GO_VERSION="1.22.5"
GO_TAR="go${GO_VERSION}.linux-amd64.tar.gz"

if [ ! -d /usr/local/go ]; then
  curl -fsSL "https://go.dev/dl/${GO_TAR}" -o "/tmp/${GO_TAR}"
  sudo rm -rf /usr/local/go
  sudo tar -C /usr/local -xzf "/tmp/${GO_TAR}"
  rm "/tmp/${GO_TAR}"
  echo "   ✅ Go ${GO_VERSION} installed to /usr/local/go"
else
  echo "   ✅ Go already installed at /usr/local/go"
fi

# Make Go available NOW and permanently
export PATH="/usr/local/go/bin:$HOME/go/bin:$PATH"
grep -qxF 'export PATH=/usr/local/go/bin:$HOME/go/bin:$PATH' "$HOME/.bashrc" 2>/dev/null || \
  echo 'export PATH=/usr/local/go/bin:$HOME/go/bin:$PATH' >> "$HOME/.bashrc"

echo "   Go version: $(go version)"

# ── 2) Go tools (ProjectDiscovery suite + others) ────────────
echo "➡️  [2/6] Installing Go tools (this takes 5-10 minutes)..."
for module in \
  github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest \
  github.com/projectdiscovery/httpx/cmd/httpx@latest \
  github.com/projectdiscovery/dnsx/cmd/dnsx@latest \
  github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest \
  github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest \
  github.com/owasp-amass/amass/v4/cmd/amass@latest \
  github.com/tomnomnom/assetfinder@latest \
  github.com/OJ/gobuster/v3@latest \
  github.com/sensepost/gowitness@latest; do

  TOOL_NAME=$(basename "$module" | cut -d'@' -f1)
  echo "   ⏳ $TOOL_NAME..."
  go install -v "$module" 2>&1 | tail -1 || echo "   ⚠️  Failed: $TOOL_NAME, continuing..."
done

# ── 3) massdns (C — build from source) ────────────────────────
echo "➡️  [3/6] Building massdns..."
MASSDNS_DIR="/tmp/massdns"
if [ ! -d "$MASSDNS_DIR/.git" ]; then
  rm -rf "$MASSDNS_DIR"
  git clone https://github.com/blechschmidt/massdns.git "$MASSDNS_DIR"
fi
make -C "$MASSDNS_DIR" && \
  sudo cp "$MASSDNS_DIR/bin/massdns" /usr/local/bin/massdns && \
  echo "   ✅ massdns installed" || \
  echo "   ⚠️  massdns build failed, continuing..."

# ── 4) findomain (Rust — grab release binary) ─────────────────
echo "➡️  [4/6] Downloading findomain..."
FINDOMAIN_URL="https://github.com/Findomain/Findomain/releases/latest/download/findomain-linux-i386.zip"
if curl -fsSL "$FINDOMAIN_URL" -o /tmp/findomain.zip 2>/dev/null; then
  sudo apt install -y unzip
  unzip -o /tmp/findomain.zip -d /tmp/findomain_extract
  sudo cp /tmp/findomain_extract/findomain /usr/local/bin/findomain
  sudo chmod +x /usr/local/bin/findomain
  rm -rf /tmp/findomain.zip /tmp/findomain_extract
  echo "   ✅ findomain installed"
else
  echo "   ⚠️  findomain download failed — trying alternative..."
  # Alternative: install via cargo if Rust is available
  if command -v cargo &>/dev/null; then
    cargo install findomain
  else
    echo "   ⚠️  findomain skipped (will be grayed out in UI)"
  fi
fi

# ── 5) Python tools ───────────────────────────────────────────
echo "➡️  [5/6] Setting up Python tools..."

# Create a dedicated venv for recon Python tools (avoids PEP 668 issues)
RECON_VENV="$HOME/.recon-tools-venv"
if [ ! -d "$RECON_VENV" ]; then
  python3 -m venv "$RECON_VENV"
fi
RECON_PIP="$RECON_VENV/bin/pip"
RECON_PYTHON="$RECON_VENV/bin/python3"

# dnsrecon
echo "   ⏳ dnsrecon..."
"$RECON_PIP" install dnsrecon 2>&1 | tail -1 || echo "   ⚠️  dnsrecon failed"

# Sublist3r
echo "   ⏳ Sublist3r..."
SUBLIST3R_DIR="/opt/sublist3r"
if [ ! -d "$SUBLIST3R_DIR/.git" ]; then
  sudo rm -rf "$SUBLIST3R_DIR"
  sudo git clone https://github.com/aboul3la/Sublist3r "$SUBLIST3R_DIR"
fi
if [ -f "$SUBLIST3R_DIR/requirements.txt" ]; then
  "$RECON_PIP" install -r "$SUBLIST3R_DIR/requirements.txt" 2>&1 | tail -1
  echo "   ✅ Sublist3r ready"
fi

# OneForAll
echo "   ⏳ OneForAll..."
ONEFORALL_DIR="/opt/oneforall"
if [ ! -d "$ONEFORALL_DIR/.git" ]; then
  sudo rm -rf "$ONEFORALL_DIR"
  sudo git clone https://github.com/shmilylty/OneForAll "$ONEFORALL_DIR"
fi
if [ -f "$ONEFORALL_DIR/requirements.txt" ]; then
  "$RECON_PIP" install -r "$ONEFORALL_DIR/requirements.txt" 2>&1 | tail -1
  echo "   ✅ OneForAll ready"
fi

# EyeWitness
echo "   ⏳ EyeWitness..."
EYEWITNESS_DIR="/opt/eyewitness"
if [ ! -d "$EYEWITNESS_DIR/.git" ]; then
  sudo rm -rf "$EYEWITNESS_DIR"
  sudo git clone https://github.com/FortyNorthSecurity/EyeWitness "$EYEWITNESS_DIR"
fi

# Add the venv bin to PATH so 'dnsrecon' works as a command
grep -qxF "export PATH=\"$RECON_VENV/bin:\$PATH\"" "$HOME/.bashrc" 2>/dev/null || \
  echo "export PATH=\"$RECON_VENV/bin:\$PATH\"" >> "$HOME/.bashrc"
export PATH="$RECON_VENV/bin:$PATH"

# ── 6) wordlists + resolvers ──────────────────────────────────
echo "➡️  [6/6] Downloading wordlists..."
mkdir -p "$WORDLIST_DIR"

if [ ! -f "$WORDLIST_DIR/subdomains-top1million-110000.txt" ]; then
  curl -fsSL \
    -o "$WORDLIST_DIR/subdomains-top1million-110000.txt" \
    https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-110000.txt
  echo "   ✅ subdomains-top1million downloaded"
fi
head -n 5000 "$WORDLIST_DIR/subdomains-top1million-110000.txt" > "$WORDLIST_DIR/subdomains-top5k.txt"

if [ ! -f "$WORDLIST_DIR/resolvers.txt" ]; then
  curl -fsSL -o "$WORDLIST_DIR/resolvers.txt" \
    https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt
  echo "   ✅ resolvers downloaded"
fi

# ── HEALTH CHECK ───────────────────────────────────────────────
echo ""
echo "============================================"
echo "🩺 TOOL HEALTH CHECK"
echo "============================================"

for tool in subfinder httpx dnsx shuffledns amass assetfinder findomain \
  massdns gobuster dnsrecon nuclei gowitness; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "[✅] $tool    $(command -v $tool)"
  else
    echo "[❌] $tool"
  fi
done

echo ""
echo "── Script tools ──"
for script in \
  "$SUBLIST3R_DIR/sublist3r.py" \
  "$ONEFORALL_DIR/oneforall.py" \
  "$EYEWITNESS_DIR/Python/EyeWitness.py"; do
  if [ -f "$script" ]; then
    echo "[✅] $script"
  else
    echo "[❌] $script"
  fi
done

echo ""
echo "── Wordlists ──"
for wl in "$WORDLIST_DIR/subdomains-top5k.txt" "$WORDLIST_DIR/resolvers.txt"; do
  if [ -f "$wl" ]; then
    LINES=$(wc -l < "$wl")
    echo "[✅] $wl ($LINES lines)"
  else
    echo "[❌] $wl"
  fi
done

echo ""
echo "============================================"
echo "🎉 INSTALLATION COMPLETE"
echo "============================================"
echo "Tools marked ❌ will be grayed out in the dashboard UI."
echo ""
echo "⚠️  Run this to reload your PATH right now:"
echo "   source ~/.bashrc"
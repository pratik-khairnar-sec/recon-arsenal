# 🛡️ recon-arsenal

> A collection of battle-tested reconnaissance & OSINT automation scripts for bug bounty hunters and penetration testers.

<p align="center">
  <img src="https://img.shields.io/badge/author-Pratik%20Khairnar-blueviolet?style=for-the-badge" />
  <img src="https://img.shields.io/badge/purpose-Bug%20Bounty%20%7C%20OSINT-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/language-Python%20%7C%20Bash-yellow?style=for-the-badge" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" />
</p>

---

> ⚠️ **Disclaimer**: All tools in this repository are intended for **educational and research purposes only**. Use them only on systems you own or have **explicit written authorization** to test. The author holds no responsibility for misuse. Always act within legal and ethical boundaries.

---

## 📦 Scripts Overview

| Script | Type | Description |
|---|---|---|
| [`alienvault.sh`](./alienvault.sh) | Bash | Dumps all URLs for a domain from AlienVault OTX with pagination support |
| [`wayback.sh`](./wayback.sh) | Bash | Fetches archived URLs from Wayback Machine with filtering by status code & extensions |
| [`virustotal.sh`](./virustotal.sh) | Bash | Queries VirusTotal API for undetected URLs and hostname resolutions (supports bulk + API key rotation) |
| [`lostfuzzer.sh`](./lostfuzzer.sh) | Bash | Full recon pipeline: GAU → URO → httpx → Nuclei DAST fuzzing |
| [`dorking.py`](./dorking.py) | Python | Google dorking automation — search & save results with configurable result count |
| [`urlscan.py`](./urlscan.py) | Python | urlscan.io API wrapper — enumerate subdomains or URLs per domain |
| [`naabutonmap.py`](./naabutonmap.py) | Python | Converts naabu port scan output → threaded nmap deep scans with XML merge |
| [`punycode_gen.py`](./punycode_gen.py) | Python | Generates punycode variants for homoglyph attacks / IDN domain spoofing research |

---

## ⚡ Quick Start

### Requirements

**Bash scripts:**
```bash
# Core tools
apt install jq curl

# For lostfuzzer.sh
go install github.com/lc/gau/v2/cmd/gau@latest
go install github.com/s0md3v/uro@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
```

**Python scripts:**
```bash
pip install googlesearch-python requests
```

---

## 🔍 Script Details

### `alienvault.sh` — AlienVault OTX URL Harvester
Automatically paginates through all archived URLs for a domain in AlienVault OTX.

```bash
./alienvault.sh example.com
```

---

### `wayback.sh` — Wayback Machine Crawler
Fetches archived URLs with powerful filtering options.

```bash
# Basic usage
./wayback.sh example.com

# Include subdomains + only 200 responses
./wayback.sh example.com -s -sc 200

# Sensitive file extensions only
./wayback.sh example.com -e

# Exclude 404s and 500s
./wayback.sh example.com -scx 404,500
```

**Flags:**
| Flag | Description |
|---|---|
| `-s` | Include subdomains |
| `-e` | Filter sensitive extensions (sql, zip, env, keys, etc.) |
| `-sc <codes>` | Include only these HTTP status codes |
| `-scx <codes>` | Exclude these HTTP status codes |

---

### `virustotal.sh` — VirusTotal Recon
Query VirusTotal for domain/IP intelligence. Supports bulk input files and automatic API key rotation every 5 requests.

```bash
# Single target
./virustotal.sh example.com

# Bulk targets from file
./virustotal.sh targets.txt
```

> 📌 Add your own API keys in the `api_key` variables at the top of the script.

---

### `lostfuzzer.sh` — Full Recon Pipeline
End-to-end automated pipeline: URL collection → deduplication → live-check → vulnerability scan.

```bash
# Single domain
./lostfuzzer.sh -d example.com

# List of subdomains
./lostfuzzer.sh -l subdomains.txt

# Custom thread count
./lostfuzzer.sh -d example.com -t 20
```

**Pipeline:**
```
GAU (URL harvest) → URO (dedup + filter params) → httpx (live check) → Nuclei DAST (vuln scan)
```

---

### `dorking.py` — Google Dork Automation
Interactive Google dorking with configurable result limits and optional output saving.

```bash
python3 dorking.py
# Prompts: dork query → result count (or 'all') → save to file?
```

---

### `urlscan.py` — URLScan.io Wrapper
Enumerate subdomains or full URLs indexed by urlscan.io for a target domain.

```bash
# Subdomains mode
python3 urlscan.py -m subdomains -d example.com

# URL discovery mode
python3 urlscan.py -m urls -d example.com

# Bulk from file
python3 urlscan.py -m subdomains -df domains.txt
```

> 📌 Set your `API_KEY` variable in the script before running.

---

### `naabutonmap.py` — Naabu → Nmap Bridge
Takes naabu's `ip:port` output and runs deep, threaded nmap scans with service detection, NSE scripts, and vuln scanning.

```bash
# Default (reads naabu_results.txt)
python3 naabutonmap.py

# Custom input/output/threads
python3 naabutonmap.py -i ports.txt -o scans/ -t 8
```

**Output:** Timestamped XML reports per IP + a merged `nmap_out.xml`.

---

### `punycode_gen.py` — Punycode / Homoglyph Generator
Generates all valid punycode variants for a given letter using a comprehensive homoglyphs map — useful for IDN squatting research.

```bash
python3 punycode_gen.py
# Enter a letter (a-z): a
# → à -> xn--0ca, á -> xn--1ca, ...
```

---

## 🗂️ Directory Structure

```
recon-arsenal/
├── alienvault.sh       # AlienVault OTX URL harvester
├── wayback.sh          # Wayback Machine crawler
├── virustotal.sh       # VirusTotal API recon
├── lostfuzzer.sh       # Full recon → nuclei pipeline
├── dorking.py          # Google dorking automation
├── urlscan.py          # urlscan.io API wrapper
├── naabutonmap.py      # Naabu → Nmap bridge
├── punycode_gen.py     # Homoglyph/punycode generator
└── README.md
```

---

## 👤 Author

**Pratik Khairnar**  
🔗 [github.com/pratik-khairnar-sec](https://github.com/pratik-khairnar-sec)

---

## 📄 License

MIT License — see [LICENSE](./LICENSE) for details.

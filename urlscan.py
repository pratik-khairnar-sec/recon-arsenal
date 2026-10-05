#!/usr/local/python3.13/bin/python3.13
# Author: Pratik Khairnar (https://github.com/pratik-khairnar-sec)
# Description: urlscan.io API wrapper for subdomain and URL enumeration

import requests
import argparse
import re
import os
import sys
import time

# ─────────────────────────────────────────
#  Colors
# ─────────────────────────────────────────
R   = "\033[91m"
G   = "\033[92m"
Y   = "\033[93m"
B   = "\033[94m"
M   = "\033[95m"
C   = "\033[96m"
W   = "\033[97m"
DIM = "\033[2m"
BLD = "\033[1m"
RST = "\033[0m"

API_KEY = "xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # ← Insert your API Key here

if not API_KEY or "xxxx" in API_KEY:
    print(f"\n  {R}[✘] No API key set!{RST}  Edit the {Y}API_KEY{RST} variable in this script.\n")
    sys.exit(1)

def banner():
    print(f"""
{C}  ██╗   ██╗██████╗ ██╗     ███████╗ ██████╗ █████╗ ███╗   ██╗
{C}  ██║   ██║██╔══██╗██║     ██╔════╝██╔════╝██╔══██╗████╗  ██║
{B}  ██║   ██║██████╔╝██║     ███████╗██║     ███████║██╔██╗ ██║
{B}  ██║   ██║██╔══██╗██║     ╚════██║██║     ██╔══██║██║╚██╗██║
{M}  ╚██████╔╝██║  ██║███████╗███████║╚██████╗██║  ██║██║ ╚████║
{M}  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝{RST}
{DIM}{W}  ─────────────────────────────────────────────────────────
  urlscan.io Recon Tool  •  by Pratik Khairnar
  github.com/pratik-khairnar-sec
  ─────────────────────────────────────────────────────────{RST}
""")

parser = argparse.ArgumentParser(
    description="urlscan.io recon wrapper by Pratik Khairnar",
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument('-m', '--mode',        required=True, choices=['subdomains', 'urls'],
                    help="Scan mode:\n  subdomains — enumerate subdomains\n  urls       — enumerate full URLs")
parser.add_argument('-d', '--domain',      help="Single domain to scan")
parser.add_argument('-df', '--domain-file',help="File containing multiple domains")
args = parser.parse_args()

def sanitize_domain(domain):
    domain = domain.strip().lower()
    domain = re.sub(r'^https?://', '', domain)
    return domain if domain and not domain.startswith('#') else None

def safe_request(url, headers):
    try:
        return requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as e:
        print(f"  {R}[✘] Request failed: {e}{RST}")
        return None

def dedup_and_sort(items):
    return sorted(set(items))

def scan_domain(domain, mode, api_key):
    domain = sanitize_domain(domain)
    if not domain:
        return

    print(f"\n  {C}[»]{RST} Scanning {BLD}{domain}{RST}  [{Y}{mode}{RST}]")
    url     = f"https://urlscan.io/api/v1/search/?q=page.domain:{domain}&size=100"
    headers = {"API-Key": api_key}

    sys.stdout.write(f"  {DIM}Querying urlscan.io")
    for _ in range(5):
        time.sleep(0.15)
        sys.stdout.write(".")
        sys.stdout.flush()
    print(f"  done{RST}")

    response = safe_request(url, headers=headers)
    if not response:
        return

    results = []
    if mode == "subdomains":
        matched  = re.findall(rf"https?://((?:[a-zA-Z0-9_-]+\.)+{re.escape(domain)})", response.text)
        stripped = [re.sub(r"^https?://", "", u) for u in matched]
        filtered = [u for u in stripped if u != domain]
        results  = [u.split("/")[0] for u in filtered]

    elif mode == "urls":
        matched = re.findall(rf"https?://(?:[a-zA-Z0-9_-]+\.)+{re.escape(domain)}/[^\s\"'>]+", response.text)
        results = matched

    unique = dedup_and_sort(results)

    if not unique:
        print(f"  {Y}[!]{RST} No results found for {domain}")
        return

    print(f"  {G}[✔]{RST} Found {BLD}{len(unique)}{RST} unique {mode}:\n")
    for i, item in enumerate(unique, 1):
        print(f"  {DIM}[{i:>4}]{RST}  {item}")

# ─────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────
banner()

print(f"  {DIM}{'─' * 55}{RST}")
print(f"  {G}Mode   :{RST}  {Y}{args.mode}{RST}")

domains_to_scan = []

if args.domain:
    single = sanitize_domain(args.domain)
    if single:
        domains_to_scan = [single]
    else:
        print(f"  {R}[✘] Invalid domain.{RST}")
        sys.exit(1)

elif args.domain_file:
    if os.path.isfile(args.domain_file):
        with open(args.domain_file, 'r') as f:
            domains_to_scan = [sanitize_domain(l) for l in f if sanitize_domain(l)]
    else:
        print(f"  {R}[✘] File not found: {args.domain_file}{RST}")
        sys.exit(1)
else:
    print(f"  {R}[✘] Provide -d <domain> or -df <file>{RST}")
    sys.exit(1)

print(f"  {G}Targets:{RST}  {len(domains_to_scan)}")
print(f"  {DIM}{'─' * 55}{RST}")

for domain in domains_to_scan:
    scan_domain(domain, args.mode, API_KEY)

print(f"\n  {DIM}{'─' * 55}{RST}")
print(f"  {M}[✔]{RST} Scan complete — {BLD}{len(domains_to_scan)}{RST} domain(s) processed.\n")

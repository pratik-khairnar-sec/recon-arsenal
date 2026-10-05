#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🛡️ RECON ARSENAL — UNIFIED OSINT & ATTACK SURFACE DISCOVERY SUITE
================================================================================
Author      : Pratik Khairnar (https://github.com/pratik-khairnar-sec)
Repository  : https://github.com/pratik-khairnar-sec/recon-arsenal
License     : MIT License
Description : Modular, high-speed OSINT & passive reconnaissance orchestrator.
              Unifies Wayback Machine, AlienVault OTX, VirusTotal, urlscan.io,
              Google Dorking, Punycode/Homoglyphs, and Port Bridges with
              instant Telegram push alerts and zero third-party dependencies.
================================================================================
"""

import sys
import os
import re
import time
import json
import argparse
import urllib.request
import urllib.parse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ANSI Color Palette
class C:
    R = "\033[91m"       # Red
    G = "\033[92m"       # Green
    Y = "\033[93m"       # Yellow
    B = "\033[94m"       # Blue
    M = "\033[95m"       # Magenta
    C = "\033[96m"       # Cyan
    CYN = "\033[96m"     # Cyan alias
    W = "\033[97m"       # White
    DIM = "\033[2m"      # Dim
    BOLD = "\033[1m"     # Bold
    RST = "\033[0m"      # Reset

CONFIG_PATH = os.path.expanduser("~/.recon_arsenal_env")

def log_info(msg):
    print(f"  {C.G}[✔]{C.RST} {msg}")

def log_warn(msg):
    print(f"  {C.Y}[!]{C.RST} {msg}")

def log_err(msg):
    print(f"  {C.R}[✘]{C.RST} {msg}")

def log_task(msg):
    print(f"  {C.C}[»]{C.RST} {msg}")

def log_step(title):
    print(f"\n  {C.M}[STEP]{C.RST} {C.BOLD}{title}{C.RST}")
    print(f"  {C.DIM}────────────────────────────────────────────────────────{C.RST}")

def banner():
    print(f"""
{C.C}  ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
{C.C}  ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
{C.B}  ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
{C.B}  ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
{C.M}  ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
{C.M}  ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
{C.G}   A  R  S  E  N  A  L   v 1 . 0 . 0{C.RST}
{C.DIM}{C.W}  ─────────────────────────────────────────────────────────────
  Unified OSINT & Passive Reconnaissance Arsenal
  by Pratik Khairnar  •  github.com/pratik-khairnar-sec
  {C.Y}[🛡️ FOR EDUCATIONAL & DEFENSIVE RESEARCH USE ONLY]{C.RST}
{C.DIM}  ─────────────────────────────────────────────────────────────{C.RST}
""")

# ================================================================
# 📦 TELEGRAM NOTIFICATION SYSTEM
# ================================================================
def load_telegram_config():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if (not token or not chat_id) and os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TELEGRAM_BOT_TOKEN="):
                        token = token or line.split("=", 1)[1].strip('"\'')
                    elif line.startswith("TELEGRAM_CHAT_ID="):
                        chat_id = chat_id or line.split("=", 1)[1].strip('"\'')
        except Exception:
            pass
    return token, chat_id

def send_telegram(message, token=None, chat_id=None, silent=False):
    tok, chat = load_telegram_config()
    tok = token or tok
    chat = chat_id or chat

    if not tok or not chat:
        if not silent:
            log_warn("Telegram not configured. Run --setup-telegram to configure.")
        return False

    url = f"https://api.telegram.org/bot{tok}/sendMessage"
    payload = {
        "chat_id": chat,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": "true"
    }

    try:
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"User-Agent": "ReconArsenal/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                if not silent:
                    log_info("Telegram alert dispatched successfully!")
                return True
    except Exception as e:
        if not silent:
            log_err(f"Telegram dispatch failed: {e}")
        return False
    return False

def setup_telegram_wizard():
    print(f"\n{C.C}╔═════════════════════════════════════════════════════════╗")
    print(f"║  🤖 ReconArsenal — Telegram Bot Setup Wizard           ║")
    print(f"╚═════════════════════════════════════════════════════════╝{C.RST}")

    cur_tok, cur_chat = load_telegram_config()
    if cur_tok:
        print(f"  Current Token  : {cur_tok[:8]}...{cur_tok[-4:]}")
        print(f"  Current Chat ID: {cur_chat}")
        ans = input(f"  {C.Y}Reconfigure? (y/N): {C.RST}").strip().lower()
        if ans != "y":
            return

    token = input(f"  {C.C}Enter Telegram Bot Token:{C.RST} ").strip()
    chat_id = input(f"  {C.C}Enter Telegram Chat ID  :{C.RST} ").strip()

    if token and chat_id:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(f'export TELEGRAM_BOT_TOKEN="{token}"\n')
            f.write(f'export TELEGRAM_CHAT_ID="{chat_id}"\n')
        log_info(f"Credentials saved to {C.W}{CONFIG_PATH}{C.RST}")
        log_task("Sending test notification...")
        test_msg = (
            "🛡️ *ReconArsenal Notification*\n\n"
            "✅ *Telegram alerts successfully configured!*\n"
            "👤 Maintainer: Pratik Khairnar\n"
            f"🕒 Timestamp: `{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}`"
        )
        send_telegram(test_msg, token=token, chat_id=chat_id)
    else:
        log_err("Token and Chat ID cannot be empty.")

# ================================================================
# 🌐 MODULE 1: WAYBACK MACHINE CDX RECON
# ================================================================
def run_wayback(domain, subdomains=True, extensions=False, status_codes=None):
    log_task(f"Querying Wayback Machine for: {C.W}{domain}{C.RST}")
    ext_pattern = r"\.(xls|xml|xlsx|json|pdf|sql|doc|docx|pptx|txt|git|zip|tar\.gz|tgz|bak|7z|rar|log|secret|db|backup|yml|gz|config|csv|yaml|env|key|pem)$"
    
    if subdomains:
        url = f"https://web.archive.org/cdx/search/cdx?url=*.{domain}/*&collapse=urlkey&output=text&fl=original,statuscode"
    else:
        url = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&collapse=urlkey&output=text&fl=original,statuscode"

    if status_codes:
        sc_regex = "|".join(status_codes.split(","))
        url += f"&filter=statuscode:({sc_regex})"

    results = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            for line in content.splitlines():
                parts = line.strip().split()
                if parts:
                    u = parts[0]
                    if extensions:
                        if re.search(ext_pattern, u, re.IGNORECASE):
                            results.append(u)
                    else:
                        results.append(u)
    except Exception as e:
        log_err(f"Wayback query error: {e}")

    results = sorted(set(results))
    log_info(f"Wayback Machine discovered: {C.Y}{len(results)}{C.RST} URLs")
    return results

# ================================================================
# 🌐 MODULE 2: ALIENVAULT OTX HARVESTER
# ================================================================
def run_alienvault(domain, limit_per_page=500, max_pages=10):
    log_task(f"Querying AlienVault OTX for: {C.W}{domain}{C.RST}")
    results = []
    page = 1

    while page <= max_pages:
        url = f"https://otx.alienvault.com/api/v1/indicators/hostname/{domain}/url_list?limit={limit_per_page}&page={page}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ReconArsenal/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                url_list = data.get("url_list", [])
                if not url_list:
                    break
                for item in url_list:
                    u = item.get("url")
                    if u:
                        results.append(u)
                if len(url_list) < limit_per_page:
                    break
                page += 1
        except Exception as e:
            log_err(f"AlienVault OTX page {page} error: {e}")
            break

    results = sorted(set(results))
    log_info(f"AlienVault OTX discovered: {C.Y}{len(results)}{C.RST} URLs")
    return results

# ================================================================
# 🌐 MODULE 3: URLSCAN.IO RECON
# ================================================================
def run_urlscan(domain, mode="subdomains"):
    log_task(f"Querying urlscan.io ({mode}) for: {C.W}{domain}{C.RST}")
    results = []
    url = f"https://urlscan.io/api/v1/search/?q=domain:{domain}&size=100"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ReconArsenal/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            items = data.get("results", [])
            for item in items:
                page_info = item.get("page", {})
                if mode == "subdomains":
                    sub = page_info.get("domain")
                    if sub and sub.endswith(domain):
                        results.append(sub)
                else:
                    u = page_info.get("url")
                    if u:
                        results.append(u)
    except Exception as e:
        log_err(f"urlscan.io error: {e}")

    results = sorted(set(results))
    log_info(f"urlscan.io discovered: {C.Y}{len(results)}{C.RST} {mode}")
    return results

# ================================================================
# 🌐 MODULE 4: VIRUSTOTAL PASSIVE RECON
# ================================================================
def run_virustotal(target, api_key=None):
    api_key = api_key or os.getenv("VT_API_KEY", "")
    if not api_key:
        log_warn("VirusTotal API Key not provided. Set VT_API_KEY in environment or pass --vt-key.")
        return []

    log_task(f"Querying VirusTotal for: {C.W}{target}{C.RST}")
    is_ip = bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target))
    if is_ip:
        url = f"https://www.virustotal.com/vtapi/v2/ip-address/report?apikey={api_key}&ip={target}"
    else:
        url = f"https://www.virustotal.com/vtapi/v2/domain/report?apikey={api_key}&domain={target}"

    results = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ReconArsenal/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            if is_ip:
                for res in data.get("resolutions", []):
                    h = res.get("hostname")
                    if h:
                        results.append(h)
            for u_entry in data.get("undetected_urls", []):
                if isinstance(u_entry, list) and u_entry:
                    results.append(u_entry[0])
    except Exception as e:
        log_err(f"VirusTotal error: {e}")

    results = sorted(set(results))
    log_info(f"VirusTotal discovered: {C.Y}{len(results)}{C.RST} entries")
    return results

# ================================================================
# 🌐 MODULE 5: PUNYCODE / HOMOGLYPH GENERATOR
# ================================================================
def run_punycode(domain):
    log_task(f"Generating IDN Punycode variants for: {C.W}{domain}{C.RST}")
    homoglyphs = {
        'a': ['à','á','â','ã','ä','å','ɑ','а'],
        'c': ['ϲ','с','ƈ','ç'],
        'e': ['е','é','è','ê','ë','ē'],
        'i': ['і','ı','í','ì','î','ï'],
        'l': ['ⅼ','ӏ','1'],
        'o': ['ο','о','ӧ','ö','ó','0'],
        'p': ['р','ρ'],
        's': ['ѕ','ș'],
        'x': ['х','ҳ']
    }

    base = domain.split(".")[0].lower()
    tld = ".".join(domain.split(".")[1:]) if "." in domain else "com"

    variants = []
    for char, subs in homoglyphs.items():
        if char in base:
            for sub in subs:
                replaced = base.replace(char, sub, 1)
                full = f"{replaced}.{tld}"
                try:
                    puny = full.encode("idna").decode("ascii")
                    if puny != domain:
                        variants.append((full, puny))
                except Exception:
                    pass

    log_info(f"Generated {C.Y}{len(variants)}{C.RST} lookalike Punycode variants:")
    for unicode_dom, puny in variants[:10]:
        print(f"    {C.CYN}•{C.RST} {unicode_dom:<25} ➔  {C.G}{puny}{C.RST}")
    if len(variants) > 10:
        print(f"    {C.DIM}... and {len(variants) - 10} more.{C.RST}")

    return [p for _, p in variants]

# ================================================================
# 🌐 MODULE 6: GOOGLE DORKING GENERATOR
# ================================================================
def run_dork_generator(domain):
    log_task(f"Generating high-value Google Dorks for: {C.W}{domain}{C.RST}")
    dorks = [
        ("Administrative Portals", f"site:{domain} inurl:admin | inurl:login | inurl:dashboard"),
        ("Exposed Configuration & Env", f"site:{domain} ext:env | ext:yml | ext:yaml | ext:ini | ext:conf"),
        ("Database Backups & Dumps", f"site:{domain} ext:sql | ext:db | ext:bak | ext:backup"),
        ("Public Cloud Buckets", f'site:s3.amazonaws.com "{domain}" | site:storage.googleapis.com "{domain}"'),
        ("Exposed Documents & Spreadsheets", f"site:{domain} ext:pdf | ext:xlsx | ext:docx | ext:csv"),
        ("API Endpoints & Swagger", f"site:{domain} inurl:api | inurl:v1 | inurl:swagger | inurl:graphql"),
        ("Log Files & Source Maps", f"site:{domain} ext:log | ext:map | inurl:debug")
    ]

    for category, query in dorks:
        print(f"\n  {C.Y}[{category}]{C.RST}")
        print(f"    {C.W}{query}{C.RST}")
        encoded = urllib.parse.quote(query)
        print(f"    {C.DIM}➔ https://www.google.com/search?q={encoded}{C.RST}")

    return dorks

# ================================================================
# ⚡ MASTER PIPELINE: RUN ALL PASSIVE SOURCES IN PARALLEL
# ================================================================
def run_full_recon(domain, send_tg=False, output_file=None):
    start_time = time.time()
    banner()
    log_step(f"Executing Full Passive Recon Chain on: {domain}")

    all_urls = []
    all_subdomains = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_wb = executor.submit(run_wayback, domain, True, False, None)
        future_otx = executor.submit(run_alienvault, domain, 500, 10)
        future_us = executor.submit(run_urlscan, domain, "subdomains")

        wb_urls = future_wb.result()
        otx_urls = future_otx.result()
        us_subs = future_us.result()

    all_urls.extend(wb_urls)
    all_urls.extend(otx_urls)
    all_urls = sorted(set(all_urls))

    # Extract subdomains from all collected URLs
    for u in all_urls:
        try:
            parsed = urllib.parse.urlparse(u)
            host = parsed.netloc.split(":")[0].lower()
            if host.endswith(domain):
                all_subdomains.append(host)
        except Exception:
            pass

    all_subdomains.extend(us_subs)
    all_subdomains = sorted(set(all_subdomains))

    elapsed = round(time.time() - start_time, 2)

    print(f"\n  {C.M}╔═════════════════════════════════════════════════════════╗{C.RST}")
    print(f"  {C.M}║{C.RST}  {C.BOLD}RECON ARSENAL — CHAIN SUMMARY{C.RST}")
    print(f"  {C.M}║{C.RST}  Target Domain   : {C.W}{domain}{C.RST}")
    print(f"  {C.M}║{C.RST}  Wayback URLs    : {C.Y}{len(wb_urls)}{C.RST}")
    print(f"  {C.M}║{C.RST}  AlienVault URLs : {C.Y}{len(otx_urls)}{C.RST}")
    print(f"  {C.M}║{C.RST}  Total Unique URLs: {C.G}{len(all_urls)}{C.RST}")
    print(f"  {C.M}║{C.RST}  Subdomains Found: {C.C}{len(all_subdomains)}{C.RST}")
    print(f"  {C.M}║{C.RST}  Duration        : {C.W}{elapsed}s{C.RST}")
    print(f"  {C.M}╚═════════════════════════════════════════════════════════╝{C.RST}\n")

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            for u in all_urls:
                f.write(u + "\n")
        log_info(f"Results saved to: {C.W}{output_file}{C.RST}")

    if send_tg:
        tg_msg = (
            f"🛡️ *ReconArsenal — Scan Complete*\n\n"
            f"🎯 *Target Domain*: `{domain}`\n"
            f"📦 *Total Unique URLs*: `{len(all_urls)}`\n"
            f"🌐 *Subdomains Discovered*: `{len(all_subdomains)}`\n"
            f"⏱️ *Duration*: `{elapsed}s`\n"
            f"👤 *Author*: Pratik Khairnar\n"
            f"🕒 `{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}`"
        )
        send_telegram(tg_msg)

    return all_urls

# ================================================================
# 🎮 INTERACTIVE MENU INTERFACE (TUI)
# ================================================================
def interactive_menu():
    banner()
    while True:
        print(f"\n  {C.M}╔═══ RECON ARSENAL MODULES ═════════════════════════════════╗{C.RST}")
        print(f"  {C.M}║{C.RST}  {C.C}1.{C.RST} ⚡ Full Automated Passive Chain (All Sources)        {C.M}║{C.RST}")
        print(f"  {C.M}║{C.RST}  {C.C}2.{C.RST} 📜 Wayback Machine URL Streamer                     {C.M}║{C.RST}")
        print(f"  {C.M}║{C.RST}  {C.C}3.{C.RST} 🌐 AlienVault OTX URL Harvester                     {C.M}║{C.RST}")
        print(f"  {C.M}║{C.RST}  {C.C}4.{C.RST} 📡 urlscan.io Subdomain / URL Extractor             {C.M}║{C.RST}")
        print(f"  {C.M}║{C.RST}  {C.C}5.{C.RST} 🦠 VirusTotal Domain & Host Recon                   {C.M}║{C.RST}")
        print(f"  {C.M}║{C.RST}  {C.C}6.{C.RST} 🎯 IDN Punycode & Homoglyph Generator              {C.M}║{C.RST}")
        print(f"  {C.M}║{C.RST}  {C.C}7.{C.RST} 🔎 Google Dork Query Generator                      {C.M}║{C.RST}")
        print(f"  {C.M}║{C.RST}  {C.C}8.{C.RST} 🤖 Configure Telegram Notifications                 {C.M}║{C.RST}")
        print(f"  {C.M}║{C.RST}  {C.C}0.{C.RST} 🚪 Exit                                             {C.M}║{C.RST}")
        print(f"  {C.M}╚═══════════════════════════════════════════════════════════╝{C.RST}")

        choice = input(f"\n  {C.C}Select an option [0-8]: {C.RST}").strip()
        if choice == "0":
            print(f"  {C.G}Goodbye! Happy ethical hunting.{C.RST}\n")
            break
        elif choice == "1":
            dom = input(f"  {C.C}Enter target domain (e.g. example.com): {C.RST}").strip()
            if dom:
                tg = input(f"  {C.Y}Send Telegram alert upon completion? (y/N): {C.RST}").strip().lower() == "y"
                run_full_recon(dom, send_tg=tg, output_file=f"{dom}_recon_urls.txt")
        elif choice == "2":
            dom = input(f"  {C.C}Enter target domain: {C.RST}").strip()
            if dom:
                urls = run_wayback(dom)
                print(f"  Preview: {len(urls)} items. First 5:")
                for u in urls[:5]:
                    print(f"    {C.CYN}•{C.RST} {u}")
        elif choice == "3":
            dom = input(f"  {C.C}Enter target domain: {C.RST}").strip()
            if dom:
                urls = run_alienvault(dom)
                for u in urls[:5]:
                    print(f"    {C.CYN}•{C.RST} {u}")
        elif choice == "4":
            dom = input(f"  {C.C}Enter target domain: {C.RST}").strip()
            if dom:
                run_urlscan(dom, "subdomains")
        elif choice == "5":
            dom = input(f"  {C.C}Enter target domain or IP: {C.RST}").strip()
            if dom:
                run_virustotal(dom)
        elif choice == "6":
            dom = input(f"  {C.C}Enter domain for Punycode analysis: {C.RST}").strip()
            if dom:
                run_punycode(dom)
        elif choice == "7":
            dom = input(f"  {C.C}Enter target domain for Dorks: {C.RST}").strip()
            if dom:
                run_dork_generator(dom)
        elif choice == "8":
            setup_telegram_wizard()

# ================================================================
# 🚀 CLI ENTRYPOINT
# ================================================================
def main():
    parser = argparse.ArgumentParser(
        description="ReconArsenal — Unified OSINT & Passive Reconnaissance Suite by Pratik Khairnar",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-d", "--domain", help="Target domain (e.g. example.com)")
    parser.add_argument("--all", action="store_true", help="Run full passive recon chain across all sources")
    parser.add_argument("--wayback", action="store_true", help="Query Wayback Machine CDX API")
    parser.add_argument("--alienvault", action="store_true", help="Query AlienVault OTX")
    parser.add_argument("--urlscan", action="store_true", help="Query urlscan.io subdomains")
    parser.add_argument("--virustotal", action="store_true", help="Query VirusTotal passive DNS")
    parser.add_argument("--punycode", action="store_true", help="Generate IDN Punycode / Homoglyph variants")
    parser.add_argument("--dorks", action="store_true", help="Generate targeted Google Dorks")
    parser.add_argument("-o", "--output", help="Save discovered URLs to specified output file")
    parser.add_argument("--telegram", action="store_true", help="Dispatch scan completion alert to Telegram")
    parser.add_argument("--setup-telegram", action="store_true", help="Run interactive Telegram setup wizard")

    args = parser.parse_args()

    if args.setup_telegram:
        setup_telegram_wizard()
        return

    if not args.domain:
        # Launch interactive menu if no flags provided
        interactive_menu()
        return

    domain = args.domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]

    if args.all:
        run_full_recon(domain, send_tg=args.telegram, output_file=args.output)
    else:
        banner()
        results = []
        if args.wayback:
            results.extend(run_wayback(domain))
        if args.alienvault:
            results.extend(run_alienvault(domain))
        if args.urlscan:
            results.extend(run_urlscan(domain))
        if args.virustotal:
            results.extend(run_virustotal(domain))
        if args.punycode:
            run_punycode(domain)
        if args.dorks:
            run_dork_generator(domain)

        if results and args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                for r in sorted(set(results)):
                    f.write(r + "\n")
            log_info(f"Results saved to: {args.output}")

        if results and args.telegram:
            send_telegram(
                f"🛡️ *ReconArsenal Alert*\n"
                f"🎯 *Target*: `{domain}`\n"
                f"📦 *Results*: `{len(set(results))}` items\n"
                f"👤 Maintainer: Pratik Khairnar"
            )

if __name__ == "__main__":
    main()

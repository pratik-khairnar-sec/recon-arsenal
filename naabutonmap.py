#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Pratik Khairnar (https://github.com/pratik-khairnar-sec)
# Description: Naabu → Nmap bridge — threaded deep scans with XML merge

import subprocess
import os
import concurrent.futures
import logging
from collections import defaultdict
import argparse
from datetime import datetime
from xml.etree import ElementTree as ET
import sys
import time

# ─────────────────────────────────────────
#  ANSI Colors
# ─────────────────────────────────────────
R  = "\033[91m"   # red
G  = "\033[92m"   # green
Y  = "\033[93m"   # yellow
B  = "\033[94m"   # blue
M  = "\033[95m"   # magenta
C  = "\033[96m"   # cyan
W  = "\033[97m"   # white
DIM = "\033[2m"
RST = "\033[0m"
BOLD = "\033[1m"

def banner():
    print(f"""
{M}╔═══════════════════════════════════════════════════════╗
║  {W}{BOLD}  ███╗   ██╗██████╗ ██████╗ ██████╗ ██╗██████╗  {M}       ║
║  {W}{BOLD}  ████╗  ██║██╔══██╗╚════██╗╚════██╗██║╚════██╗ {M}       ║
║  {W}{BOLD}  ██╔██╗ ██║╚█████╔╝ █████╔╝ █████╔╝██║ █████╔╝ {M}      ║
║  {W}{BOLD}  ██║╚██╗██║ ╚═══██╗██╔═══╝  ╚═══██╗██║██╔═══╝  {M}      ║
║  {W}{BOLD}  ██║ ╚████║██████╔╝███████╗███████╔╝██║███████╗ {M}      ║
║  {W}{BOLD}  ╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝╚═╝╚══════╝ {M}      ║
{M}╠═══════════════════════════════════════════════════════╣
║  {C}  Naabu → Nmap Deep Scan Bridge                       {M}║
║  {DIM}{W}  by Pratik Khairnar  •  github.com/pratik-khairnar-sec{M} ║
╚═══════════════════════════════════════════════════════╝{RST}
""")

def log_info(msg):
    print(f"  {G}[✔]{RST} {W}{msg}{RST}")

def log_warn(msg):
    print(f"  {Y}[!]{RST} {Y}{msg}{RST}")

def log_err(msg):
    print(f"  {R}[✘]{RST} {R}{msg}{RST}")

def log_task(msg):
    print(f"  {C}[»]{RST} {msg}")

logging.basicConfig(
    filename='nmap_scan.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

completed = 0
failed    = 0

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Naabu → Nmap threaded deep scanner by Pratik Khairnar",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-i', '--input',   default='naabu_results.txt', help='Naabu output file  (default: naabu_results.txt)')
    parser.add_argument('-o', '--output',  default='nmap-out',          help='Output directory   (default: nmap-out)')
    parser.add_argument('-t', '--threads', type=int, default=4,         help='Thread count       (default: 4)')
    return parser.parse_args()

def create_output_directory(path):
    os.makedirs(path, exist_ok=True)

def parse_file(path):
    if not os.path.isfile(path):
        log_err(f"Input file not found: {path}")
        sys.exit(1)
    data = defaultdict(list)
    with open(path) as f:
        for line in f:
            line = line.strip()
            if ":" in line:
                ip, port = line.split(":", 1)
                data[ip].append(port)
    return data

def run_nmap(ip, ports, outdir):
    global completed, failed
    ports_str = ",".join(ports)
    outfile   = os.path.join(outdir, f"nmap_out_{ip}.xml")
    log_task(f"Scanning {C}{ip}{RST} → ports {Y}{ports_str}{RST}")

    cmd = [
        "nmap",
        "-sS",                       # Stealth SYN scan
        "-sV",                       # Service version detection
        "-sC",                       # Default NSE scripts
        "--version-all",             # Aggressive version probing
        "--script", "vuln,default",  # Vuln + default scripts
        "--open",                    # Show only open ports
        "--reason",                  # Port state reason
        "-T4",                       # Faster timing
        "-Pn",                       # Skip host discovery
        "-p", ports_str,
        "-oX", outfile,
        ip
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log_info(f"Done: {ip}  →  {DIM}{outfile}{RST}")
        completed += 1
    except subprocess.CalledProcessError:
        log_err(f"nmap failed for {ip}")
        logging.error(f"nmap failed for {ip}")
        failed += 1

def combine_nmap_xml_files(output_dir):
    xmls = [f for f in os.listdir(output_dir)
            if f.startswith("nmap_out_") and f.endswith(".xml")]

    base_root = None
    hosts     = []

    for x in xmls:
        try:
            root = ET.parse(os.path.join(output_dir, x)).getroot()
            if base_root is None:
                base_root = root
            hosts.extend(root.findall("host"))
        except Exception:
            continue

    if not base_root or not hosts:
        log_warn("No XML results to merge.")
        return

    for h in base_root.findall("host"):
        base_root.remove(h)
    for h in hosts:
        base_root.append(h)

    out = os.path.join(output_dir, "nmap_out.xml")
    ET.ElementTree(base_root).write(out)
    log_info(f"Merged XML → {G}{out}{RST}")

def print_summary(outdir, total, elapsed):
    print(f"""
{M}╔══════════════════  SCAN SUMMARY  ══════════════════╗{RST}
  {G}✔  Completed  :{RST}  {completed}
  {R}✘  Failed     :{RST}  {failed}
  {C}◈  Total IPs  :{RST}  {total}
  {Y}⏱  Time taken :{RST}  {elapsed:.1f}s
  {W}📁  Output dir :{RST}  {outdir}
{M}╚════════════════════════════════════════════════════╝{RST}
""")

def main():
    banner()
    args   = parse_arguments()
    outdir = os.path.join(args.output, datetime.now().strftime("%Y%m%d_%H%M%S"))
    create_output_directory(outdir)

    log_info(f"Input   : {args.input}")
    log_info(f"Output  : {outdir}")
    log_info(f"Threads : {args.threads}")
    print()

    targets = parse_file(args.input)
    total   = len(targets)

    if total == 0:
        log_warn("No targets found in input file. Exiting.")
        sys.exit(0)

    log_task(f"Loaded {C}{total}{RST} unique IPs — starting threaded scans...\n")
    t_start = time.time()

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=args.threads)
    try:
        futures = [executor.submit(run_nmap, ip, ports, outdir)
                   for ip, ports in targets.items()]
        concurrent.futures.wait(futures)
    except KeyboardInterrupt:
        log_warn("Interrupted — merging partial results...")
    finally:
        executor.shutdown(wait=False)
        print()
        combine_nmap_xml_files(outdir)

    elapsed = time.time() - t_start
    print_summary(outdir, total, elapsed)

if __name__ == "__main__":
    main()

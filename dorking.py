#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Pratik Khairnar (https://github.com/pratik-khairnar-sec)
# Description: Google dorking automation with configurable result count and output saving

from __future__ import print_function
import sys
import time

try:
    from googlesearch import search
except ImportError:
    print("\033[91m[ERROR] Missing dependency: googlesearch-python\033[0m")
    print("\033[93m[INFO] Install it using: pip install googlesearch-python\033[0m")
    sys.exit(1)

if sys.version_info[0] < 3:
    print("\n\033[91m[ERROR] This script requires Python 3.x\033[0m\n")
    sys.exit(1)

# ─────────────────────────────────────────
#  ANSI Colors
# ─────────────────────────────────────────
class C:
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    MAGENTA= "\033[95m"
    WHITE  = "\033[97m"
    DIM    = "\033[2m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

log_file = "dorks_output.txt"

def banner():
    print(f"""
{C.MAGENTA}  ██████╗  ██████╗ ██████╗ ██╗  ██╗███████╗██████╗
{C.MAGENTA}  ██╔══██╗██╔═══██╗██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
{C.CYAN}  ██║  ██║██║   ██║██████╔╝█████╔╝ █████╗  ██████╔╝
{C.CYAN}  ██║  ██║██║   ██║██╔══██╗██╔═██╗ ██╔══╝  ██╔══██╗
{C.BLUE}  ██████╔╝╚██████╔╝██║  ██║██║  ██╗███████╗██║  ██║
{C.BLUE}  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
{C.DIM}{C.WHITE}  ─────────────────────────────────────────────────────
  Google Dork Automation Tool  •  by Pratik Khairnar
  github.com/pratik-khairnar-sec
{C.DIM}  ─────────────────────────────────────────────────────{C.RESET}
""")

def logger(data):
    """Logs data to a file."""
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(data + "\n")

def spinner(msg):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for i in range(15):
        sys.stdout.write(f"\r  {C.CYAN}{frames[i % len(frames)]}{C.RESET}  {msg}")
        sys.stdout.flush()
        time.sleep(0.08)
    sys.stdout.write("\r" + " " * 60 + "\r")

def dorks():
    """Main function for handling Google Dorking."""
    global log_file
    banner()
    try:
        dork = input(f"  {C.CYAN}╔══ Dork Query{C.RESET}\n  {C.CYAN}╚═▶{C.RESET} ")

        print()
        user_choice = input(
            f"  {C.YELLOW}╔══ Result Count (number or 'all'){C.RESET}\n"
            f"  {C.YELLOW}╚═▶{C.RESET} "
        ).strip().lower()
        print()

        if user_choice == "all":
            total_results = float("inf")
        else:
            try:
                total_results = int(user_choice)
                if total_results <= 0:
                    raise ValueError
            except ValueError:
                print(f"  {C.RED}[✘] Invalid input — enter a positive integer or 'all'.{C.RESET}\n")
                return

        save_output = input(
            f"  {C.GREEN}╔══ Save output to file? (Y/N){C.RESET}\n"
            f"  {C.GREEN}╚═▶{C.RESET} "
        ).strip().lower()

        if save_output == "y":
            log_file = input(f"\n  {C.GREEN}╔══ Output filename{C.RESET}\n  {C.GREEN}╚═▶{C.RESET} ").strip()
            if not log_file:
                log_file = "dorks_output.txt"
            if not log_file.endswith(".txt"):
                log_file += ".txt"

        print(f"\n  {C.DIM}{'─' * 55}{C.RESET}")
        spinner("Sending dork query to Google...")
        print(f"  {C.GREEN}[✔]{C.RESET} {C.WHITE}Results:{C.RESET}\n")

        fetched = 0
        for result in search(dork):
            if fetched >= total_results:
                break
            print(f"  {C.CYAN}[{fetched + 1:>4}]{C.RESET}  {result}")
            if save_output == "y":
                logger(result)
            fetched += 1

        print(f"\n  {C.DIM}{'─' * 55}{C.RESET}")
        if save_output == "y":
            print(f"  {C.GREEN}[✔]{C.RESET} Saved {C.YELLOW}{fetched}{C.RESET} results → {C.WHITE}{log_file}{C.RESET}")
        print(f"  {C.MAGENTA}[✔]{C.RESET} {C.BOLD}All done!{C.RESET}\n")

    except KeyboardInterrupt:
        print(f"\n\n  {C.RED}[!] Interrupted. Goodbye!{C.RESET}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n  {C.RED}[✘] Error: {str(e)}{C.RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    dorks()

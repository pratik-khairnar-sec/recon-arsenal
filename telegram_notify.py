#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================================
# 🛡️ ReconArsenal - Shared Telegram Notification Engine
# Author: Pratik Khairnar (https://github.com/pratik-khairnar-sec)
# Notice: For educational and defensive security research only.
# ================================================================

import os
import sys
import json
import urllib.request
import urllib.parse

CONFIG_PATH = os.path.expanduser("~/.recon_arsenal_env")

def load_credentials():
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
    """
    Sends a formatted Markdown alert to Telegram using native urllib
    (Zero third-party library dependencies required).
    """
    tok, chat = load_credentials()
    tok = token or tok
    chat = chat_id or chat

    if not tok or not chat:
        if not silent:
            print("  \033[93m[!]\033[0m Telegram not configured. Run with setup or set TELEGRAM_BOT_TOKEN & TELEGRAM_CHAT_ID.")
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
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status == 200:
                if not silent:
                    print("  \033[92m[✔]\033[0m Telegram alert dispatched successfully!")
                return True
    except Exception as e:
        if not silent:
            print(f"  \033[91m[✘]\033[0m Failed to send Telegram alert: {e}")
        return False

    return False

def setup_wizard():
    print("\n\033[96m╔═════════════════════════════════════════════════════════╗")
    print("║  🤖 ReconArsenal — Telegram Bot Setup Wizard           ║")
    print("╚═════════════════════════════════════════════════════════╝\033[0m")
    
    current_token, current_chat = load_credentials()
    if current_token:
        print(f"  Current Token  : {current_token[:8]}...{current_token[-4:]}")
        print(f"  Current Chat ID: {current_chat}")
        overwrite = input("  Reconfigure? (y/N): ").strip().lower()
        if overwrite != "y":
            return

    token = input("  Enter Telegram Bot Token: ").strip()
    chat_id = input("  Enter Telegram Chat ID  : ").strip()

    if token and chat_id:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(f'export TELEGRAM_BOT_TOKEN="{token}"\n')
            f.write(f'export TELEGRAM_CHAT_ID="{chat_id}"\n')
        print(f"\n  \033[92m[✔]\033[0m Configuration saved to \033[97m{CONFIG_PATH}\033[0m")
        
        print("  \033[96m[»]\033[0m Testing alert delivery...")
        test_msg = (
            "🛡️ *ReconArsenal Setup Test*\n\n"
            "✅ Telegram notifications configured successfully!\n"
            "👤 Maintainer: Pratik Khairnar"
        )
        send_telegram(test_msg, token=token, chat_id=chat_id)
    else:
        print("  \033[91m[✘]\033[0m Token and Chat ID cannot be empty.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("""
🛡️ ReconArsenal - Telegram Notification Client
Author: Pratik Khairnar (@pratik-khairnar-sec)
Notice: For educational and defensive security research only.

Usage:
  python telegram_notify.py --setup                # Interactive setup wizard
  python telegram_notify.py "Your message here"    # Send instant text alert
  python telegram_notify.py -h, --help             # Show this help guide
""")
    elif len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_wizard()
    elif len(sys.argv) > 1:
        send_telegram(" ".join(sys.argv[1:]))
    else:
        setup_wizard()


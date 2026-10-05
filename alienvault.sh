#!/bin/bash
# Author: Pratik Khairnar (https://github.com/pratik-khairnar-sec)
# Description: Fetches all URLs for a domain from AlienVault OTX with pagination

# ─────────────────────────────────────────
#  Colors
# ─────────────────────────────────────────
RED='\033[91m'
GRN='\033[92m'
YLW='\033[93m'
CYN='\033[96m'
MGN='\033[95m'
WHT='\033[97m'
DIM='\033[2m'
RST='\033[0m'

banner() {
  echo -e "${CYN}"
  cat << 'EOF'
   ▄▄▄      ██▓     ██▓▓█████  ███▄    █ ██▒   █▓ ▄▄▄      ██▓    ▄▄▄█████▓
  ▒████▄   ▓██▒    ▓██▒▓█   ▀  ██ ▀█   █▓██░   █▒▒████▄   ▓██▒    ▓  ██▒ ▓▒
  ▒██  ▀█▄ ▒██░    ▒██▒▒███   ▓██  ▀█ ██▒▓██  █▒░▒██  ▀█▄ ▒██░    ▒ ▓██░ ▒░
  ░██▄▄▄▄██░██░    ░██░▒▓█  ▄ ▓██▒  ▐▌██▒ ▒██ █░░░██▄▄▄▄██░██░    ░ ▓██▓ ░
   ▓█   ▓██░██████▒░██░░▒████▒▒██░   ▓██░  ▒▀█░   ▓█   ▓██░██████▒  ▒██▒ ░
   ▒▒   ▓▒█░ ▒░▓  ░░▓  ░░ ▒░ ░░ ▒░   ▒ ▒   ░ ▐░   ▒▒   ▓▒█░ ▒░▓  ░  ▒ ░░
    ▒   ▒▒ ░ ░ ▒  ░ ▒ ░ ░ ░  ░░ ░░   ░ ▒░  ░ ░░    ▒   ▒▒ ░ ░ ▒  ░    ░
    ░   ▒    ░ ░    ▒ ░   ░      ░   ░ ░     ░░    ░   ▒    ░ ░     ░
        ░  ░   ░  ░ ░     ░  ░         ░      ░        ░  ░   ░  ░
EOF
  echo -e "${DIM}${WHT}  OTX URL Harvester  •  by Pratik Khairnar  •  github.com/pratik-khairnar-sec${RST}"
  echo -e "${DIM}  ─────────────────────────────────────────────────────────────────────────${RST}"
  echo
}

log_info()  { echo -e "  ${GRN}[✔]${RST} $*"; }
log_warn()  { echo -e "  ${YLW}[!]${RST} $*"; }
log_err()   { echo -e "  ${RED}[✘]${RST} $*"; }
log_task()  { echo -e "  ${CYN}[»]${RST} $*"; }

# ─────────────────────────────────────────
#  Checks
# ─────────────────────────────────────────
banner

if ! command -v jq &>/dev/null; then
  log_err "jq is required but not installed."
  echo -e "  ${YLW}[→]${RST} Install: ${WHT}sudo apt install jq${RST}"
  exit 1
fi

if [ -z "$1" ]; then
  echo -e "  ${YLW}Usage:${RST}  $0 ${CYN}<domain>${RST}"
  echo -e "  ${DIM}Example: $0 example.com${RST}"
  echo
  exit 1
fi

domain=$1
page=1
limit=500
total_urls=0

echo -e "  ${DIM}────────────────────────────────────────────────────${RST}"
log_task "Target  : ${WHT}${domain}${RST}"
log_task "API     : AlienVault OTX"
log_task "Limit   : ${limit} URLs/page"
echo -e "  ${DIM}────────────────────────────────────────────────────${RST}\n"

# ─────────────────────────────────────────
#  Fetch Loop
# ─────────────────────────────────────────
while true; do
  echo -ne "  ${CYN}[»]${RST} Fetching page ${YLW}${page}${RST}..."

  response=$(curl -s \
    "https://otx.alienvault.com/api/v1/indicators/hostname/${domain}/url_list?limit=${limit}&page=${page}")

  urls=$(echo "$response" | jq -r '.url_list[]?.url')

  if [[ -z "$urls" ]]; then
    echo -e "  ${YLW}no more data.${RST}"
    break
  fi

  count=$(echo "$response" | jq -r '.url_list | length')
  total_urls=$((total_urls + count))
  echo -e "  ${GRN}${count} URLs${RST}"

  echo "$urls"

  if (( count < limit )); then
    break
  fi

  page=$((page + 1))
done

echo
echo -e "  ${DIM}────────────────────────────────────────────────────${RST}"
log_info "Done!  Total URLs collected: ${YLW}${total_urls}${RST}"
echo -e "  ${DIM}────────────────────────────────────────────────────${RST}"
echo

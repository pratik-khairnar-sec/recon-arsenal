#!/bin/bash
# Author: Pratik Khairnar (https://github.com/pratik-khairnar-sec)
# Description: Queries VirusTotal API for undetected URLs and hostname resolutions with API key rotation

# ─────────────────────────────────────────
#  Colors
# ─────────────────────────────────────────
RED='\033[91m'
GRN='\033[92m'
YLW='\033[93m'
BLU='\033[94m'
MGN='\033[95m'
CYN='\033[96m'
WHT='\033[97m'
DIM='\033[2m'
BLD='\033[1m'
RST='\033[0m'

banner() {
  echo -e "${RED}"
  cat << 'EOF'
  ██╗   ██╗██╗██████╗ ██╗   ██╗███████╗    ████████╗ ██████╗ ████████╗ █████╗ ██╗
  ██║   ██║██║██╔══██╗██║   ██║██╔════╝    ╚══██╔══╝██╔═══██╗╚══██╔══╝██╔══██╗██║
  ██║   ██║██║██████╔╝██║   ██║███████╗       ██║   ██║   ██║   ██║   ███████║██║
  ╚██╗ ██╔╝██║██╔══██╗██║   ██║╚════██║       ██║   ██║   ██║   ██║   ██╔══██║██║
   ╚████╔╝ ██║██║  ██║╚██████╔╝███████║       ██║   ╚██████╔╝   ██║   ██║  ██║███████╗
    ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝       ╚═╝    ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚══════╝
EOF
  echo -e "${DIM}${WHT}  VirusTotal Recon Tool  •  by Pratik Khairnar  •  github.com/pratik-khairnar-sec${RST}"
  echo -e "${DIM}  ───────────────────────────────────────────────────────────────────────────────${RST}"
  echo
}

log_info()  { echo -e "  ${GRN}[✔]${RST} $*"; }
log_warn()  { echo -e "  ${YLW}[!]${RST} $*"; }
log_err()   { echo -e "  ${RED}[✘]${RST} $*"; }
log_task()  { echo -e "  ${CYN}[»]${RST} $*"; }
log_found() { echo -e "  ${MGN}[+]${RST} $*"; }

# ─────────────────────────────────────────
#  Check if IP
# ─────────────────────────────────────────
is_ip() {
  [[ $1 =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]
}

# ─────────────────────────────────────────
#  Countdown
# ─────────────────────────────────────────
countdown() {
  local secs=$1
  while [ $secs -gt 0 ]; do
    echo -ne "  ${DIM}${CYN}[⏱]${RST}${DIM}  Cooling down: ${YLW}${secs}s${DIM} remaining...${RST}\r"
    sleep 1
    : $((secs--))
  done
  echo -ne "\033[2K"
}

# ─────────────────────────────────────────
#  Fetch function
# ─────────────────────────────────────────
fetch_vt() {
  local input=$1
  local key_idx=$2
  local api_key

  case $key_idx in
    1) api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" ;;
    2) api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" ;;
    3) api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" ;;
  esac

  echo -e "\n  ${DIM}────────────────────────────────────────────────────${RST}"
  if is_ip "$input"; then
    log_task "Target (IP)    : ${WHT}${input}${RST}  [key #${key_idx}]"
    local URL="https://www.virustotal.com/vtapi/v2/ip-address/report?apikey=${api_key}&ip=${input}"
  else
    log_task "Target (domain): ${WHT}${input}${RST}  [key #${key_idx}]"
    local URL="https://www.virustotal.com/vtapi/v2/domain/report?apikey=${api_key}&domain=${input}"
  fi
  echo -e "  ${DIM}────────────────────────────────────────────────────${RST}"

  response=$(curl -s "$URL")

  if [[ $? -ne 0 || -z "$response" ]]; then
    log_err "Failed to fetch data for ${input}"
    return
  fi

  # Hostnames for IP
  if is_ip "$input"; then
    hostnames=$(echo "$response" | jq -r '.resolutions[].hostname' 2>/dev/null)
    if [[ -n "$hostnames" ]]; then
      echo -e "\n  ${MGN}[Hostnames resolved for ${input}]${RST}"
      echo "$hostnames" | while read -r h; do echo -e "    ${CYN}•${RST} $h"; done
    else
      log_warn "No hostnames found for ${input}"
    fi
  fi

  # Undetected URLs
  undetected=$(echo "$response" | jq -r '.undetected_urls[][0]' 2>/dev/null)
  if [[ -z "$undetected" ]]; then
    log_warn "No undetected URLs found for ${input}"
  else
    url_count=$(echo "$undetected" | wc -l | tr -d ' ')
    echo -e "\n  ${GRN}[Undetected URLs — ${input}  (${url_count} found)]${RST}"
    echo "$undetected" | while read -r u; do echo -e "    ${GRN}•${RST} $u"; done
  fi
}

# ─────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────
banner

if [ -z "$1" ]; then
  echo -e "  ${YLW}Usage:${RST}  $0 ${CYN}<ip_or_domain | file_with_targets>${RST}"
  echo -e "  ${DIM}Examples:"
  echo -e "    $0 example.com"
  echo -e "    $0 1.2.3.4"
  echo -e "    $0 targets.txt${RST}"
  echo
  exit 1
fi

api_key_index=1
request_count=0

# ─────────────────────────────────────────
#  File or single target
# ─────────────────────────────────────────
if [ -f "$1" ]; then
  total=$(wc -l < "$1" | tr -d ' ')
  log_info "Loaded ${YLW}${total}${RST} targets from file: ${WHT}$1${RST}"

  while IFS= read -r input; do
    input=$(echo "$input" | sed 's|https\?://||')
    [[ -z "$input" ]] && continue

    fetch_vt "$input" $api_key_index
    countdown 20

    request_count=$((request_count + 1))
    if [ $request_count -ge 5 ]; then
      request_count=0
      api_key_index=$(( api_key_index % 3 + 1 ))
      log_info "Rotating to API key #${api_key_index}"
    fi
  done < "$1"
else
  input=$(echo "$1" | sed 's|https\?://||')
  fetch_vt "$input" $api_key_index
fi

echo
echo -e "  ${DIM}────────────────────────────────────────────────────${RST}"
log_info "All done!"
echo -e "  ${DIM}────────────────────────────────────────────────────${RST}"
echo

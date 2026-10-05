#!/bin/bash
# Author: Pratik Khairnar (https://github.com/pratik-khairnar-sec)
# Description: Full recon pipeline — GAU → URO → httpx → Nuclei DAST vulnerability scanning

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
  echo -e "${MGN}"
  cat << 'EOF'
  ██╗      ██████╗ ███████╗████████╗    ███████╗██╗   ██╗███████╗███████╗███████╗██████╗
  ██║     ██╔═══██╗██╔════╝╚══██╔══╝    ██╔════╝██║   ██║╚════██║╚════██║██╔════╝██╔══██╗
  ██║     ██║   ██║███████╗   ██║       █████╗  ██║   ██║    ██╔╝    ██╔╝█████╗  ██████╔╝
  ██║     ██║   ██║╚════██║   ██║       ██╔══╝  ██║   ██║   ██╔╝    ██╔╝ ██╔══╝  ██╔══██╗
  ███████╗╚██████╔╝███████║   ██║       ██║     ╚██████╔╝   ██║     ██║  ███████╗██║  ██║
  ╚══════╝ ╚═════╝ ╚══════╝   ╚═╝       ╚═╝      ╚═════╝    ╚═╝     ╚═╝  ╚══════╝╚═╝  ╚═╝
EOF
  echo -e "${DIM}${WHT}  GAU → URO → httpx → Nuclei DAST Pipeline  •  by Pratik Khairnar  •  github.com/pratik-khairnar-sec${RST}"
  echo -e "${DIM}  ────────────────────────────────────────────────────────────────────────────────────────────────${RST}"
  echo
}

log_info()  { echo -e "  ${GRN}[✔]${RST} $*"; }
log_warn()  { echo -e "  ${YLW}[!]${RST} $*"; }
log_err()   { echo -e "  ${RED}[✘]${RST} $*"; }
log_step()  { echo -e "\n  ${MGN}[STEP]${RST} ${BLD}$*${RST}"; echo -e "  ${DIM}$(printf '─%.0s' {1..55})${RST}"; }
log_task()  { echo -e "  ${CYN}[»]${RST} $*"; }

# ─────────────────────────────────────────
#  Usage
# ─────────────────────────────────────────
usage() {
  banner
  echo -e "  ${YLW}Usage:${RST}  $0 ${CYN}[-d domain.com | -l subdomains.txt]${RST} [-t threads]"
  echo
  echo -e "  ${WHT}Flags:${RST}"
  echo -e "    ${CYN}-d${RST} domain.com      Single domain target"
  echo -e "    ${CYN}-l${RST} subdomains.txt  List of subdomains"
  echo -e "    ${CYN}-t${RST} threads         Thread count (default: 10)"
  echo
  exit 1
}

# ─────────────────────────────────────────
#  Tool check
# ─────────────────────────────────────────
check_tools() {
  REQUIRED_TOOLS=("gau" "uro" "httpx-toolkit" "nuclei")
  local missing=0
  for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" &>/dev/null; then
      log_err "Missing tool: ${YLW}${tool}${RST}"
      missing=1
    else
      log_info "Found: ${GRN}${tool}${RST}"
    fi
  done
  [[ $missing -eq 1 ]] && { echo; log_err "Install missing tools and retry."; exit 1; }
}

# ─────────────────────────────────────────
#  Summary
# ─────────────────────────────────────────
summary() {
  local end_time=$(date +%s)
  local elapsed=$(( end_time - START_TIME ))

  echo
  echo -e "  ${MGN}╔══════════════════  SCAN SUMMARY  ══════════════════╗${RST}"
  echo -e "  ${MGN}║${RST}  ${CYN}URLs Fetched (GAU)  :${RST}  $(wc -l < "$GAU_FILE" 2>/dev/null || echo 0)"
  echo -e "  ${MGN}║${RST}  ${YLW}URLs with Params    :${RST}  $(wc -l < "$FILTERED_URLS_FILE" 2>/dev/null || echo 0)"
  echo -e "  ${MGN}║${RST}  ${GRN}Live URLs (httpx)   :${RST}  $(wc -l < "$LIVE_URLS" 2>/dev/null || echo 0)"
  echo -e "  ${MGN}║${RST}  ${RED}Vulnerabilities     :${RST}  $(wc -l < "$NUCLEI_RESULTS" 2>/dev/null || echo 0)"
  echo -e "  ${MGN}║${RST}  ${WHT}Output Directory    :${RST}  ${OUTPUT_DIR}/"
  echo -e "  ${MGN}║${RST}  ${DIM}Time Elapsed        :  ${elapsed}s${RST}"
  echo -e "  ${MGN}╚════════════════════════════════════════════════════╝${RST}"
  echo
}

# ─────────────────────────────────────────
#  Args
# ─────────────────────────────────────────
DOMAIN=""
LIST=""
THREADS=10

while getopts "d:l:t:" opt; do
  case "$opt" in
    d) DOMAIN=$OPTARG ;;
    l) LIST=$OPTARG ;;
    t) THREADS=$OPTARG ;;
    *) usage ;;
  esac
done

if [ -z "$DOMAIN" ] && [ -z "$LIST" ]; then
  usage
fi

banner
check_tools

# ─────────────────────────────────────────
#  Setup
# ─────────────────────────────────────────
START_TIME=$(date +%s)
OUTPUT_DIR="results_$(date +%F_%H-%M-%S)"
mkdir -p "$OUTPUT_DIR"

GAU_FILE="$OUTPUT_DIR/gau_urls.txt"
FILTERED_URLS_FILE="$OUTPUT_DIR/filtered_urls.txt"
LIVE_URLS="$OUTPUT_DIR/live_urls.txt"
NUCLEI_RESULTS="$OUTPUT_DIR/nuclei_results.txt"

trap 'rm -f "$GAU_FILE.tmp"' EXIT

echo -e "  ${DIM}────────────────────────────────────────────────────────${RST}"
[[ -n "$DOMAIN" ]] && log_task "Target   : ${WHT}${DOMAIN}${RST}"
[[ -n "$LIST"   ]] && log_task "List     : ${WHT}${LIST}${RST}"
log_task "Threads  : ${YLW}${THREADS}${RST}"
log_task "Output   : ${WHT}${OUTPUT_DIR}/${RST}"
echo -e "  ${DIM}────────────────────────────────────────────────────────${RST}"

# ─────────────────────────────────────────
#  Collect targets
# ─────────────────────────────────────────
if [ -n "$DOMAIN" ]; then
  TARGETS="$DOMAIN"
elif [ -f "$LIST" ]; then
  TARGETS=$(cat "$LIST")
else
  log_err "List file not found: ${LIST}"
  exit 1
fi

TARGETS=$(echo "$TARGETS" | sed 's|https\?://||g')

# ─────────────────────────────────────────
#  Step 1 — GAU
# ─────────────────────────────────────────
log_step "1 / 4  |  Fetching URLs with gau..."
echo "$TARGETS" | xargs -P"$THREADS" -I{} gau "{}" >> "$GAU_FILE"

if [ ! -s "$GAU_FILE" ]; then
  log_err "No URLs found. Exiting."
  exit 1
fi
log_info "Fetched $(wc -l < "$GAU_FILE") URLs"

# ─────────────────────────────────────────
#  Step 2 — Filter with uro
# ─────────────────────────────────────────
log_step "2 / 4  |  Filtering URLs with parameters (uro)..."
grep -E '\?[^=]+=.+$' "$GAU_FILE" | uro | awk '!seen[$0]++' > "$FILTERED_URLS_FILE"
log_info "URLs with params: $(wc -l < "$FILTERED_URLS_FILE")"

# ─────────────────────────────────────────
#  Step 3 — httpx live check
# ─────────────────────────────────────────
log_step "3 / 4  |  Checking live URLs with httpx..."
httpx-toolkit -silent -t 300 -rl 200 < "$FILTERED_URLS_FILE" > "$LIVE_URLS"
log_info "Live URLs: $(wc -l < "$LIVE_URLS")"

# ─────────────────────────────────────────
#  Step 4 — Nuclei DAST
# ─────────────────────────────────────────
log_step "4 / 4  |  Running Nuclei DAST scan..."
nuclei -dast -retries 2 -silent -o "$NUCLEI_RESULTS" < "$LIVE_URLS"
log_info "Vulnerabilities: $(wc -l < "$NUCLEI_RESULTS")"

# ─────────────────────────────────────────
#  Done
# ─────────────────────────────────────────
summary

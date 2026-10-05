#!/bin/bash
# Author: Pratik Khairnar (https://github.com/pratik-khairnar-sec)
# Description: Fetches archived URLs from Wayback Machine with flexible status-code and extension filtering

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
  echo -e "${BLU}"
  cat << 'EOF'
  ██╗    ██╗ █████╗ ██╗   ██╗██████╗  █████╗  ██████╗██╗  ██╗
  ██║    ██║██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝
  ██║ █╗ ██║███████║ ╚████╔╝ ██████╔╝███████║██║     █████╔╝
  ██║███╗██║██╔══██║  ╚██╔╝  ██╔══██╗██╔══██║██║     ██╔═██╗
  ╚███╔███╔╝██║  ██║   ██║   ██████╔╝██║  ██║╚██████╗██║  ██╗
   ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
EOF
  echo -e "${DIM}${WHT}  Wayback Machine URL Crawler  •  by Pratik Khairnar  •  github.com/pratik-khairnar-sec${RST}"
  echo -e "${DIM}  ─────────────────────────────────────────────────────────────────────────────────${RST}"
  echo
}

log_info() { echo -e "  ${GRN}[✔]${RST} $*"; }
log_warn() { echo -e "  ${YLW}[!]${RST} $*"; }
log_err()  { echo -e "  ${RED}[✘]${RST} $*"; }
log_task() { echo -e "  ${CYN}[»]${RST} $*"; }

# ─────────────────────────────────────────
#  Help
# ─────────────────────────────────────────
usage() {
  banner
  echo -e "  ${YLW}Usage:${RST}  $0 ${CYN}<domain>${RST} [flags]"
  echo
  echo -e "  ${WHT}Flags:${RST}"
  echo -e "    ${CYN}-s${RST}          Include subdomains"
  echo -e "    ${CYN}-e${RST}          Filter by sensitive extensions (sql, env, zip, keys…)"
  echo -e "    ${CYN}-sc${RST}  codes  Include only these HTTP status codes  (e.g. 200,302)"
  echo -e "    ${CYN}-scx${RST} codes  Exclude these HTTP status codes        (e.g. 404,500)"
  echo
  echo -e "  ${DIM}Examples:"
  echo -e "    $0 example.com -s -sc 200"
  echo -e "    $0 example.com -e"
  echo -e "    $0 example.com -scx 404,500${RST}"
  echo
  exit 1
}

# ─────────────────────────────────────────
#  Arg parsing
# ─────────────────────────────────────────
if [ -z "$1" ]; then
  usage
fi

banner

domain=$1
shift

subdomains=false
extensions=false
status_code=""
exclude_status_code=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -s)   subdomains=true ;;
    -e)   extensions=true ;;
    -sc)  status_code=$2;         shift ;;
    -scx) exclude_status_code=$2; shift ;;
    *)    log_warn "Unknown flag: $1" ;;
  esac
  shift
done

# ─────────────────────────────────────────
#  Config summary
# ─────────────────────────────────────────
echo -e "  ${DIM}────────────────────────────────────────────────────${RST}"
log_task "Target      : ${WHT}${domain}${RST}"
log_task "Subdomains  : ${YLW}${subdomains}${RST}"
log_task "Extensions  : ${YLW}${extensions}${RST}"
[[ -n "$status_code" ]]         && log_task "Include SC  : ${GRN}${status_code}${RST}"
[[ -n "$exclude_status_code" ]] && log_task "Exclude SC  : ${RED}${exclude_status_code}${RST}"
echo -e "  ${DIM}────────────────────────────────────────────────────${RST}\n"

# ─────────────────────────────────────────
#  Sensitive extensions
# ─────────────────────────────────────────
ext_regex='xls|xml|xlsx|json|pdf|sql|doc|docx|pptx|txt|git|zip|tar\.gz|tgz|bak|7z|rar|log|cache|secret|db|backup|yml|gz|config|csv|yaml|md|md5|exe|dll|bin|ini|bat|sh|tar|deb|rpm|iso|img|env|apk|msi|dmg|tmp|crt|pem|key|pub|asc'

# ─────────────────────────────────────────
#  Build URL
# ─────────────────────────────────────────
if $subdomains; then
  base_url="https://web.archive.org/cdx/search/cdx?url=*.$domain/*&collapse=urlkey&output=text&fl=original,statuscode"
else
  base_url="https://web.archive.org/cdx/search/cdx?url=$domain/*&collapse=urlkey&output=text&fl=original,statuscode"
fi

$extensions       && base_url="${base_url}&filter=original:.*\.(${ext_regex})$"
[[ -n "$status_code" ]] && {
  sc_regex=$(echo "$status_code" | sed 's/,/|/g')
  base_url="${base_url}&filter=statuscode:(${sc_regex})"
}
[[ -n "$exclude_status_code" ]] && {
  exc_regex=$(echo "$exclude_status_code" | sed 's/,/|/g')
  base_url="${base_url}&filter=!statuscode:(${exc_regex})"
}

# ─────────────────────────────────────────
#  Fetch
# ─────────────────────────────────────────
log_task "Querying Wayback Machine..."
echo

urls=$(curl -s "$base_url")

if [ -z "$urls" ]; then
  log_warn "No results found for ${domain}."
else
  count=$(echo "$urls" | wc -l | tr -d ' ')
  echo "$urls" | awk '{print $1}'
  echo
  echo -e "  ${DIM}────────────────────────────────────────────────────${RST}"
  log_info "Done!  ${YLW}${count}${RST} URLs retrieved for ${WHT}${domain}${RST}."
  echo -e "  ${DIM}────────────────────────────────────────────────────${RST}"
fi
echo

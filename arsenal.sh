#!/usr/bin/env bash
# ================================================================
# 🛡️ ReconArsenal Launcher Wrapper
# Author: Pratik Khairnar (https://github.com/pratik-khairnar-sec)
# ================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$DIR/arsenal.py" "$@"

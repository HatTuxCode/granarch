#!/bin/bash
# Gran invokes hooks through Bash, regardless of the script's shebang.
set -euo pipefail
exec /usr/bin/python3 "${XDG_CONFIG_HOME:-$HOME/.config}/gran/scripts/sync-nautilus-zen.py"

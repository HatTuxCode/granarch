#!/usr/bin/env bash
set -euo pipefail
project=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
python3 "$project/scripts/verify.py"
mkdir -p "$project/dist"
tar -C "$project" --exclude=.git --exclude=.agents --exclude=.codex --exclude=.aws --exclude=dist --exclude=__pycache__ --exclude='*.pyc' --transform='s,^,granarch/,' -czf "$project/dist/granarch-installer.tar.gz" .
cd "$project/dist"
sha256sum granarch-installer.tar.gz > granarch-installer.tar.gz.sha256
printf '%s\n' "$project/dist/granarch-installer.tar.gz"

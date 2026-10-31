#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
bash "$ROOT/install.sh" --verify
mkdir -p "$ROOT/dist"
tar -czf "$ROOT/dist/granarch-bootstrap.tar.gz" --transform='s,^,GranArch/,' \
  -C "$ROOT" --exclude=__pycache__ --exclude='*.pyc' \
  install.sh README.md manifests docs scripts tests overlay snapshot licenses skills .gitignore
(cd "$ROOT/dist" && sha256sum granarch-bootstrap.tar.gz > granarch-bootstrap.tar.gz.sha256)
printf 'Bundle: %s/dist/granarch-bootstrap.tar.gz\n' "$ROOT"

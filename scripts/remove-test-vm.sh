#!/usr/bin/env bash
# Remove only the GranArch test VM and generated test/publication artifacts.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
URI=qemu:///session
NAME=granarch-endeavouros
VM_DIR="$ROOT/vm/endeavouros"
virsh -c "$URI" list --all >/dev/null
if virsh -c "$URI" dominfo "$NAME" >/dev/null 2>&1; then
  expected=$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["uuid"])' "$VM_DIR/config.json")
  actual=$(virsh -c "$URI" domuuid "$NAME")
  [[ "$actual" == "$expected" ]] || { echo 'UUID diferente: remoção cancelada.' >&2; exit 1; }
  if virsh -c "$URI" list --uuid | grep -Fxq "$actual"; then
    virsh -c "$URI" destroy "$NAME"
  fi
  virsh -c "$URI" undefine "$NAME" --nvram
fi
# A separately launched QEMU must release the disk before deleting its files.
if command -v fuser >/dev/null && [[ -e "$VM_DIR/granarch-test.qcow2" ]]; then
  if fuser "$VM_DIR/granarch-test.qcow2" >/dev/null 2>&1; then
    echo 'O disco ainda está aberto por outro processo. Feche a VM e execute novamente.' >&2
    exit 1
  fi
fi
rm -rf -- "$VM_DIR"
printf 'VM e arquivos gerados removidos. Código do projeto e ISO original preservados.\n'

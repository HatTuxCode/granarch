#!/usr/bin/env bash
# Explicitly retire only the previous CachyOS test VM, preserving the new VM/ISOs.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
LEGACY="$ROOT/vm"
URI=qemu:///session
NAME=granarch-test
[[ -f $LEGACY/config.json ]] || { echo 'A VM antiga já foi removida.'; exit 0; }
expected=$(python - "$LEGACY/config.json" "$LEGACY" <<'PY'
import json, sys
from pathlib import Path
config = json.loads(Path(sys.argv[1]).read_text())
base = Path(sys.argv[2]).resolve()
if not Path(config['iso']).name.lower().startswith('cachyos-'):
    raise SystemExit('O destino antigo não é a VM CachyOS; nada removido.')
if config['name'] != 'granarch-test' or Path(config['disk']).resolve() != base / 'granarch-test.qcow2':
    raise SystemExit('Configuração inesperada da VM antiga; nada removido.')
print(config['uuid'])
PY
)
# A failed connection must never be treated as an absent domain.
virsh -c "$URI" list --all >/dev/null
actual=$(virsh -c "$URI" domuuid "$NAME" 2>/dev/null || true)
if [[ -n $actual ]]; then
  [[ $actual == "$expected" ]] || { echo 'UUID diferente; nada removido.' >&2; exit 1; }
  if virsh -c "$URI" list --uuid | grep -Fxq "$actual"; then
    echo 'Encerrando a VM de teste CachyOS para removê-la...'
    virsh -c "$URI" destroy "$NAME"
  fi
  virsh -c "$URI" undefine "$NAME" --keep-nvram
fi
# Also catches a direct QEMU process still holding the old disk.
if [[ -f $LEGACY/granarch-test.qcow2 ]]; then
  qemu-img info "$LEGACY/granarch-test.qcow2" >/dev/null
fi
for file in granarch-test.qcow2 OVMF_VARS.fd granarch-files.iso granarch-files.iso.tmp granarch-test.xml config.json run.lock; do
  rm -f -- "$LEGACY/$file"
done
echo 'VM CachyOS removida; ISOs em Downloads e VM EndeavourOS preservadas.'

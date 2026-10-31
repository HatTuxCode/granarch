#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
VM_DIR="$ROOT/vm"
URI=qemu:///session
NAME=granarch-test
action=${1:-open}
if [[ $action == prepare ]]; then shift; exec python "$ROOT/scripts/prepare-vm.py" "$@"; fi
[[ -f $VM_DIR/config.json ]] || { echo 'Prepare primeiro: bash scripts/vm.sh prepare' >&2; exit 1; }
if [[ $action == status ]]; then exec virsh -c "$URI" dominfo "$NAME"; fi
if [[ $action == stop ]]; then exec virsh -c "$URI" shutdown "$NAME"; fi
if [[ $action == open ]]; then
  [[ -r /dev/kvm && -w /dev/kvm ]] || {
    echo 'KVM indisponível neste ambiente. Execute este comando no terminal do notebook, fora do sandbox do agente.' >&2
    exit 1
  }
  expected_uuid=$(python -c 'import json,sys;print(json.load(open(sys.argv[1]))["uuid"])' "$VM_DIR/config.json")
  existing_uuid=$(virsh -c "$URI" domuuid "$NAME" 2>/dev/null || true)
  [[ -z $existing_uuid || $existing_uuid == "$expected_uuid" ]] || {
    echo 'Já existe outra VM com esse nome; ela não será substituída.' >&2
    exit 1
  }
  if ! virsh -c "$URI" domstate "$NAME" 2>/dev/null | grep -q '^running'; then
    virsh -c "$URI" define "$VM_DIR/granarch-test.xml"
    virsh -c "$URI" start "$NAME"
  fi
  exec virt-manager --connect "$URI" --show-domain-console "$NAME"
fi
if [[ $action == direct ]]; then
  [[ -r /dev/kvm && -w /dev/kvm ]] || { echo 'Execute no terminal do notebook com acesso ao KVM.' >&2; exit 1; }
  mapfile -t settings < <(python - "$VM_DIR/config.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
for key in ('memory_mib','cpus','disk','iso','media','firmware','nvram'): print(d[key])
PY
  )
  exec 9>"$VM_DIR/run.lock"
  flock -n 9 || { echo 'A VM já está em execução.' >&2; exit 1; }
  exec qemu-system-x86_64 -name GranArch-Test -machine q35,accel=kvm -cpu host \
    -m "${settings[0]}" -smp "${settings[1]}" \
    -drive "if=pflash,format=raw,unit=0,readonly=on,file=${settings[5]}" \
    -drive "if=pflash,format=raw,unit=1,file=${settings[6]}" \
    -drive "file=${settings[2]},format=qcow2,if=virtio,discard=unmap" \
    -drive "file=${settings[3]},format=raw,media=cdrom,readonly=on" \
    -drive "file=${settings[4]},format=raw,media=cdrom,readonly=on" \
    -device virtio-vga-gl -display gtk,gl=on -boot order=c,menu=on \
    -netdev user,id=network0 -device virtio-net-pci,netdev=network0 \
    -device qemu-xhci -device usb-tablet
fi
echo 'Uso: bash scripts/vm.sh prepare|open|direct|status|stop' >&2
exit 2

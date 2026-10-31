#!/usr/bin/env python3
"""Prepare an isolated UEFI VM and read-only GranArch installer media."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def prepare(iso, memory=2048, cpus=2):
    iso = iso.expanduser().resolve()
    if not iso.is_file():
        raise ValueError('ISO do Arch não encontrada: ' + str(iso))
    if memory < 1024 or memory > 4096 or cpus < 1 or cpus > 4:
        raise ValueError('Use 1024–4096 MiB e 1–4 CPUs neste notebook.')
    base = ROOT / 'vm'
    base.mkdir(exist_ok=True)
    disk = base / 'granarch-test.qcow2'
    if not disk.exists():
        subprocess.run(['qemu-img', 'create', '-f', 'qcow2', str(disk), '64G'], check=True)
    else:
        info = json.loads(subprocess.check_output(['qemu-img', 'info', '--output=json', str(disk)], text=True))
        if info['format'] != 'qcow2':
            raise ValueError('O disco existente não é qcow2; não será substituído.')
    code = Path('/usr/share/edk2/x64/OVMF_CODE.4m.fd')
    template = Path('/usr/share/edk2/x64/OVMF_VARS.4m.fd')
    if not code.is_file() or not template.is_file():
        raise ValueError('Firmware UEFI OVMF não encontrado.')
    nvram = base / 'OVMF_VARS.fd'
    if not nvram.exists():
        shutil.copyfile(template, nvram)
    bundle = ROOT / 'dist/granarch-bootstrap.tar.gz'
    checksum = ROOT / 'dist/granarch-bootstrap.tar.gz.sha256'
    if not bundle.is_file() or not checksum.is_file():
        raise ValueError('Gere primeiro o pacote com bash scripts/build-bundle.sh')
    if hashlib.sha256(bundle.read_bytes()).hexdigest() != checksum.read_text().split()[0]:
        raise ValueError('Checksum do pacote GranArch não confere.')
    media = base / 'granarch-files.iso'
    staging_media = base / 'granarch-files.iso.tmp'
    subprocess.run(['xorriso', '-as', 'mkisofs', '-quiet', '-V', 'GRANARCH', '-o', str(staging_media),
                    '-graft-points', 'granarch-bootstrap.tar.gz=' + str(bundle),
                    'granarch-bootstrap.tar.gz.sha256=' + str(checksum)], check=True)
    staging_media.replace(media)
    configuration = base / 'config.json'
    previous = json.loads(configuration.read_text()) if configuration.exists() else {}
    settings = {'name': 'granarch-test', 'uuid': previous.get('uuid', str(uuid.uuid4())),
                'memory_mib': memory, 'cpus': cpus, 'disk': str(disk), 'iso': str(iso),
                'media': str(media), 'firmware': str(code), 'nvram': str(nvram)}
    configuration.write_text(json.dumps(settings, indent=2) + '\n')
    domain = ET.Element('domain', type='kvm')
    def node(parent, tag, text=None, **attrs):
        item = ET.SubElement(parent, tag, attrs)
        item.text = text
        return item
    node(domain, 'name', settings['name'])
    node(domain, 'uuid', settings['uuid'])
    node(domain, 'title', 'GranArch — teste isolado')
    node(domain, 'memory', str(memory), unit='MiB')
    node(domain, 'currentMemory', str(memory), unit='MiB')
    node(domain, 'vcpu', str(cpus), placement='static')
    os = node(domain, 'os')
    node(os, 'type', 'hvm', arch='x86_64', machine='q35')
    node(os, 'loader', str(code), readonly='yes', secure='no', type='pflash')
    node(os, 'nvram', str(nvram), template=str(template))
    node(os, 'boot', dev='hd')
    node(os, 'boot', dev='cdrom')
    features = node(domain, 'features')
    node(features, 'acpi')
    node(features, 'apic')
    node(domain, 'cpu', mode='host-passthrough', check='none', migratable='off')
    node(domain, 'clock', offset='utc')
    for event, action in [('on_poweroff', 'destroy'), ('on_reboot', 'restart'), ('on_crash', 'preserve')]:
        node(domain, event, action)
    devices = node(domain, 'devices')
    node(devices, 'emulator', shutil.which('qemu-system-x86_64'))
    drive = node(devices, 'disk', type='file', device='disk')
    node(drive, 'driver', name='qemu', type='qcow2', discard='unmap')
    node(drive, 'source', file=str(disk))
    node(drive, 'target', dev='vda', bus='virtio')
    node(devices, 'controller', type='sata', index='0')
    for path, name in [(iso, 'sda'), (media, 'sdb')]:
        drive = node(devices, 'disk', type='file', device='cdrom')
        node(drive, 'driver', name='qemu', type='raw')
        node(drive, 'source', file=str(path))
        node(drive, 'target', dev=name, bus='sata')
        node(drive, 'readonly')
    network = node(devices, 'interface', type='user')
    node(network, 'model', type='virtio')
    node(devices, 'controller', type='usb', model='qemu-xhci')
    node(devices, 'input', type='tablet', bus='usb')
    graphics = node(devices, 'graphics', type='spice', autoport='yes')
    node(graphics, 'listen', type='none')
    node(graphics, 'gl', enable='yes')
    video = node(devices, 'video')
    model = node(video, 'model', type='virtio', heads='1', primary='yes')
    node(model, 'acceleration', accel3d='yes')
    sound = node(devices, 'sound', model='ich9')
    node(sound, 'audio', id='1')
    node(devices, 'audio', id='1', type='spice')
    node(devices, 'memballoon', model='virtio')
    ET.indent(domain)
    ET.ElementTree(domain).write(base / 'granarch-test.xml', encoding='unicode', xml_declaration=True)
    print(f'VM preparada: {base}\nDisco próprio: {disk}\nISO Arch: {iso}\nGranArch: {media}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iso', type=Path)
    parser.add_argument('--memory', type=int, default=2048)
    parser.add_argument('--cpus', type=int, default=2)
    args = parser.parse_args()
    candidates = sorted((Path.home() / 'Downloads').glob('archlinux-*-x86_64.iso'))
    if args.iso is None and not candidates:
        parser.error('Não encontrei a ISO Arch em Downloads; use --iso CAMINHO.')
    prepare(args.iso or candidates[-1], args.memory, args.cpus)

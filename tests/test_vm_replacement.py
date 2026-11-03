"""Exercise legacy VM removal using fake libvirt commands and temporary disks."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class VMReplacementTests(unittest.TestCase):
    def run_cleanup(self, mode):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / 'scripts'
            scripts.mkdir()
            shutil.copy2(ROOT / 'scripts/retire-cachyos-vm.sh', scripts)
            legacy = root / 'vm'
            new = legacy / 'endeavouros'
            new.mkdir(parents=True)
            (new / 'config.json').write_text('new VM preserved')
            for file in ('granarch-test.qcow2', 'OVMF_VARS.fd', 'granarch-files.iso', 'granarch-test.xml'):
                (legacy / file).write_text('old test data')
            (legacy / 'config.json').write_text(json.dumps({
                'name': 'granarch-test', 'uuid': 'expected-uuid',
                'iso': str(root / 'cachyos-test.iso'),
                'disk': str(legacy / 'granarch-test.qcow2'),
            }))
            commands = root / 'commands'
            commands.mkdir()
            (commands / 'virsh').write_text('''#!/bin/bash
case "$3" in
  list)
    [[ $TEST_MODE != disconnected ]] || exit 1
    [[ $4 != --uuid ]] || echo expected-uuid ;;
  domuuid)
    if [[ $TEST_MODE == mismatch ]]; then echo other-uuid; else echo expected-uuid; fi ;;
  destroy|undefine) printf '%s\\n' "$3" >> "$TEST_LOG" ;;
  *) exit 9 ;;
esac
''')
            (commands / 'qemu-img').write_text('#!/bin/bash\n[[ $TEST_MODE != locked ]]\n')
            for file in commands.iterdir():
                file.chmod(0o755)
            log = root / 'actions.log'
            result = subprocess.run(['bash', str(scripts / 'retire-cachyos-vm.sh')],
                                    capture_output=True, text=True,
                                    env=dict(os.environ, PATH=str(commands) + ':' + os.environ['PATH'],
                                             TEST_MODE=mode, TEST_LOG=str(log)))
            self.assertEqual((new / 'config.json').read_text(), 'new VM preserved')
            if mode == 'ok':
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse((legacy / 'config.json').exists())
                self.assertFalse((legacy / 'granarch-test.qcow2').exists())
                self.assertEqual(log.read_text().splitlines(), ['destroy', 'undefine'])
            else:
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue((legacy / 'config.json').is_file())
                self.assertTrue((legacy / 'granarch-test.qcow2').is_file())
                if mode in ('mismatch', 'disconnected'):
                    self.assertFalse(log.exists())

    def test_remove_only_old_vm_and_preserve_endeavouros(self):
        self.run_cleanup('ok')

    def test_uuid_mismatch_prevents_removal(self):
        self.run_cleanup('mismatch')

    def test_connection_failure_prevents_removal(self):
        self.run_cleanup('disconnected')

    def test_locked_disk_prevents_file_removal(self):
        self.run_cleanup('locked')

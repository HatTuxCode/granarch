import hashlib
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def app_module():
    loader = importlib.machinery.SourceFileLoader('gran_app', str(ROOT / 'overlay/.local/share/gran/bin/gran-app'))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
    loader.exec_module(module)
    return module


class BundleTests(unittest.TestCase):
    def apply(self, home):
        return subprocess.run(['python', str(ROOT / 'scripts/apply-home.py'), '--home', str(home)],
                              text=True, capture_output=True)

    def test_all_binding_modules_are_preserved_and_original_backup_survives(self):
        with tempfile.TemporaryDirectory(prefix='gran-test-') as directory:
            home = Path(directory) / 'user'
            original = home / '.config/hypr/bindings.lua'
            original.parent.mkdir(parents=True)
            original.write_text('-- personal original\n')
            result = self.apply(home)
            self.assertEqual(result.returncode, 0, result.stderr)
            backups = sorted((home / '.local/state/gran/backups').iterdir())
            self.assertEqual((backups[0] / '.config/hypr/bindings.lua').read_text(), '-- personal original\n')
            value = original.read_text()
            for optional in ('warp-terminal', 'virt-manager', 'tuios', 'GranCtrl.desktop', 'chromium http://localhost:3000'):
                self.assertIn(optional, value)
            self.assertNotIn('/home/hattux', value)
            self.assertNotIn('omarchy', value.lower())
            metadata = json.loads((ROOT / 'snapshot/metadata.json').read_text())
            for entry in metadata['binding_sources']:
                relative = '.config/hypr/bindings.lua' if entry['module'] == 'bindings.lua' else (
                    '.local/share/gran/default/hypr/bindings/' + entry['module'])
                deployed = (home / relative).read_text().replace(str(home), '@@GRAN_HOME@@').encode()
                self.assertEqual(hashlib.sha256(deployed).hexdigest(), entry['gran_sha256'], entry['module'])
            startup = (home / '.local/share/gran/default/hypr/autostart.lua').read_text()
            self.assertNotIn('provision', startup)
            self.assertEqual((home / '.local/state/gran/current/background').resolve(),
                             home / '.local/share/gran/wallpaper.jpg')
            agent = (home / '.local/share/gran/bin/gran-agent').read_text()
            self.assertNotIn('--dangerously', agent)
            result = self.apply(home)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(original.read_text(), value)
            backups = sorted((home / '.local/state/gran/backups').iterdir())
            self.assertEqual(len(backups), 2)
            self.assertEqual((backups[0] / '.config/hypr/bindings.lua').read_text(), '-- personal original\n')
            self.assertEqual((backups[1] / '.config/hypr/bindings.lua').read_text(), value)
            changes = json.loads((backups[1] / 'changes.json').read_text())
            self.assertEqual(len(changes), len(set(changes)))

    def test_cli_dispatches_gran_commands_and_discovers_shared_skills(self):
        with tempfile.TemporaryDirectory(prefix='gran-cli-test-') as directory:
            home = Path(directory)
            result = self.apply(home)
            self.assertEqual(result.returncode, 0, result.stderr)
            env = os.environ.copy()
            env.update(HOME=directory, GRAN_PATH=str(home / '.local/share/gran'))
            cli = str(home / '.local/bin/gran')
            for arguments in [('commands', '--check'), ('skills', 'list'), ('app', 'sources'), ('sources',)]:
                result = subprocess.run([cli, *arguments], env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                if arguments[0] == 'skills':
                    for name in ('gran', 'gran-app', 'gran-diagnose'):
                        self.assertIn('/.agents/skills/' + name + '/SKILL.md', result.stdout)
                if arguments[0] == 'sources':
                    sources = json.loads(result.stdout)
                    self.assertEqual(sources['hyprland']['delivery'], 'extra/hyprland')
                    self.assertEqual(sources['quickshell']['delivery'], 'extra/quickshell')
                    self.assertNotIn('omarchy', result.stdout.lower())
            help_result = subprocess.run([cli, '--help'], env=env, capture_output=True, text=True)
            self.assertNotIn('Omarchy', help_result.stdout)
            self.assertNotIn('channel ', help_result.stdout)

    def test_parent_symlink_cannot_escape_target(self):
        with tempfile.TemporaryDirectory(prefix='gran-symlink-test-') as directory:
            base = Path(directory)
            home, outside = base / 'home', base / 'outside'
            home.mkdir()
            outside.mkdir()
            (home / '.local').symlink_to(outside, target_is_directory=True)
            result = self.apply(home)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Symlink parent', result.stderr)
            self.assertEqual(list(outside.iterdir()), [])

    def test_payload_has_no_repository_state_or_account_payload(self):
        forbidden = {'auth.json', 'fish_variables', 'clipboard-history.json', 'cookies.sqlite',
                     'places.sqlite', 'logins.json', 'key4.db', 'id_rsa', 'id_ed25519', '.git', '.env',
                     'pacman.conf', 'keyring', 'gran-apply-pacman', 'gran-system-factory-reset'}
        for path in (ROOT / 'snapshot').rglob('*'):
            self.assertFalse(path.is_symlink(), str(path))
            self.assertNotIn(path.name, forbidden, str(path))
        packages = [line.strip() for line in (ROOT / 'manifests/packages.txt').read_text().splitlines()
                    if line.strip() and not line.startswith('#')]
        self.assertTrue(all(name.startswith(('core/', 'extra/')) for name in packages))
        self.assertIn('extra/hyprland', packages)
        self.assertIn('extra/quickshell', packages)
        self.assertFalse(any('omarchy' in name for name in packages))
        self.assertNotIn('LoadPatch', (ROOT / 'snapshot/runtime/shell/shell.qml').read_text())

    def test_ported_icon_font_has_the_gran_family(self):
        result = subprocess.run(['fc-scan', '--format', '%{family}',
                                 str(ROOT / 'snapshot/runtime/default/fonts/gran/gran.ttf')],
                                capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout, 'gran')


class UpstreamDeliveryTests(unittest.TestCase):
    def test_zen_verifies_digest_and_switches_to_the_verified_binary(self):
        module = app_module()
        archive = io.BytesIO()
        with tarfile.open(fileobj=archive, mode='w:xz') as tar:
            member = tarfile.TarInfo('zen/zen-bin')
            member.mode = 0o755
            payload = b'#!/bin/sh\nprintf zen\n'
            member.size = len(payload)
            tar.addfile(member, io.BytesIO(payload))
        payload = archive.getvalue()
        release = {'tag_name': 'test-1', 'assets': [{
            'name': 'zen.linux-x86_64.tar.xz', 'digest': 'sha256:' + hashlib.sha256(payload).hexdigest(),
            'browser_download_url': 'https://github.com/zen-browser/desktop/releases/download/test-1/zen.linux-x86_64.tar.xz'}]}
        with tempfile.TemporaryDirectory(prefix='gran-upstream-test-') as directory:
            home = Path(directory)
            with patch.object(module, 'api', return_value=release), patch.object(module, 'request', return_value=io.BytesIO(payload)):
                state = module.install_zen(home, {})
            self.assertTrue((home / '.local/share/gran/apps/zen/current/zen-bin').is_file())
            self.assertEqual(state['sha256'], hashlib.sha256(payload).hexdigest())
            release['tag_name'] = 'test-2'
            release['assets'][0]['digest'] = 'sha256:' + '0' * 64
            with patch.object(module, 'api', return_value=release), patch.object(module, 'request', return_value=io.BytesIO(payload)):
                with self.assertRaisesRegex(RuntimeError, 'SHA-256 mismatch'):
                    module.install_zen(home, state)
            self.assertEqual((home / '.local/share/gran/apps/zen/current').resolve().name, 'test-1')

    def test_archive_traversal_is_rejected(self):
        module = app_module()
        with tempfile.TemporaryDirectory(prefix='gran-archive-test-') as directory:
            archive = Path(directory) / 'bad.tar'
            with tarfile.open(archive, 'w') as tar:
                member = tarfile.TarInfo('../escaped')
                member.size = 1
                tar.addfile(member, io.BytesIO(b'x'))
            with self.assertRaises(tarfile.FilterError):
                module.extract(archive, Path(directory) / 'target')
            self.assertFalse((Path(directory) / 'escaped').exists())


if __name__ == '__main__':
    unittest.main()

import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class MenuWorkflowTests(unittest.TestCase):
    def test_menu_actions_and_providers_resolve_in_the_deployed_desktop(self):
        with tempfile.TemporaryDirectory(prefix='gran-menu-test-') as directory:
            home = Path(directory)
            subprocess.run(['python', str(ROOT / 'scripts/apply-home.py'), '--home', directory], check=True, capture_output=True)
            runtime = home / '.local/share/gran'
            menu = json.loads((runtime / 'default/gran/gran-menu.jsonc').read_text())
            for key in ('apps', 'appearance', 'trigger', 'setup', 'install', 'remove', 'update', 'system',
                        'install.webapp', 'install.package', 'setup.typing.keyboard', 'setup.default.browser'):
                self.assertIn(key, menu)
            for key, item in menu.items():
                if '.' in key:
                    self.assertIn(key.rsplit('.', 1)[0], menu)
                if item.get('provider'):
                    self.assertIn(item['provider'], ('apps', 'fonts', 'languages', 'power-profiles'))
                for field in ('action', 'when', 'checked', 'disabled'):
                    for command in re.findall(r'\bgran-[a-z0-9-]+', str(item.get(field, ''))):
                        self.assertTrue((runtime / 'bin' / command).exists() or (home / '.local/bin' / command).exists(), (key, field, command))
            self.assertEqual(menu['apps']['provider'], 'apps')
            self.assertNotIn('setup.reset', menu)
            self.assertFalse(any(key.startswith('update.channel') for key in menu))
            environment = os.environ.copy()
            environment.update(HOME=directory, GRAN_PATH=str(runtime))
            for route in (['launch', 'apps', '--help'], ['webapp', 'install', '--help'],
                          ['pkg', 'install', '--help'], ['pkg', 'remove', '--help'], ['setup', '--help']):
                result = subprocess.run([str(home / '.local/bin/gran'), *route], env=environment, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_webapp_launch_and_removal_keep_profile_and_backup_shortcut(self):
        module = load('gran_webapp', ROOT / 'overlay/.local/share/gran/bin/gran-webapp')
        with tempfile.TemporaryDirectory(prefix='gran webapp $ %-test-') as directory:
            home = Path(directory)
            identity = module.create(home, 'My App', 'https://example.org/?q=a%20b', 'chromium')
            desktop = home / '.local/share/applications' / ('gran-webapp-' + identity + '.desktop')
            if shutil.which('desktop-file-validate'):
                result = subprocess.run(['desktop-file-validate', str(desktop)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with patch.object(module.os, 'execvp') as execute:
                module.launch(home, identity)
            executable, arguments = execute.call_args.args
            self.assertEqual(executable, 'chromium')
            self.assertIn('--app=https://example.org/?q=a%20b', arguments)
            profile = home / '.local/share/gran/webapps/profiles' / identity
            profile.mkdir(parents=True)
            (profile / 'keep').write_text('user browser data')
            module.remove(home, identity)
            self.assertFalse(desktop.exists())
            self.assertEqual(module.records(home), [])
            self.assertTrue((profile / 'keep').is_file())
            self.assertTrue(list((home / '.local/state/gran/webapp-backups').rglob('*.desktop')))

    def test_invalid_webapp_values_cannot_escape_or_add_launcher_arguments(self):
        module = load('gran_webapp_validation', ROOT / 'overlay/.local/share/gran/bin/gran-webapp')
        with tempfile.TemporaryDirectory(prefix='gran-webapp-validation-') as directory:
            home = Path(directory)
            for name, url in (('../bad', 'https://example.org'), ('Bad\nExec=sh', 'https://example.org'),
                              ('Bad', 'javascript:alert(1)'), ('Bad', 'file:///etc/passwd'),
                              ('Bad', 'https://example.org --no-sandbox'), ('Bad', 'https://user:pass@example.org')):
                with self.subTest(name=name, url=url), self.assertRaises(ValueError):
                    module.create(home, name, url)
            self.assertEqual(list(home.iterdir()), [])

    def test_package_workflow_uses_pacman_confirmation_without_unattended_flags(self):
        module = load('gran_control', ROOT / 'overlay/.local/share/gran/lib/control.py')
        with patch.object(module, 'output', return_value='[core]\n[extra]\n'), patch.object(module, 'run') as execute:
            module.packages('install', ['extra/firefox'])
            self.assertEqual(execute.call_args.args[0], ['sudo', 'pacman', '-Syu', '--needed', '--', 'extra/firefox'])
            self.assertNotIn('--noconfirm', execute.call_args.args[0])
        with patch.object(module, 'output', return_value='[omarchy]\n'), patch.object(module, 'run') as execute:
            with self.assertRaises(ValueError):
                module.packages('install', ['extra/firefox'])
            execute.assert_not_called()

    def test_launcher_removal_keeps_the_webapp_manifest_in_sync(self):
        with tempfile.TemporaryDirectory(prefix='gran-webapp-remove-') as directory:
            home = Path(directory)
            subprocess.run(['python', str(ROOT / 'scripts/apply-home.py'), '--home', directory], check=True, capture_output=True)
            module = load('gran_webapp_remove', ROOT / 'overlay/.local/share/gran/bin/gran-webapp')
            identity = module.create(home, 'Remove Me', 'https://example.org', 'zen')
            env = os.environ.copy()
            runtime = home / '.local/share/gran'
            env.update(HOME=directory, GRAN_PATH=str(runtime), PATH=str(runtime / 'bin') + ':' + env['PATH'])
            env['XDG_DATA_HOME'] = str(home / '.local/share')
            result = subprocess.run([str(runtime / 'bin/gran-remove-launcher-entry'),
                                     'gran-webapp-' + identity, 'Remove Me'], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(module.records(home), [])


if __name__ == '__main__':
    unittest.main()

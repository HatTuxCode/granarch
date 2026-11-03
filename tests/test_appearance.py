"""Verify installed desktop appearance and safe upgrades of existing profiles."""
import base64
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aE1sAAAAASUVORK5CYII=')


def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader))
    loader.exec_module(module)
    return module


def prepare(home):
    subprocess.run(['python', str(ROOT / 'scripts/apply-home.py'), '--home', str(home)],
                   check=True, capture_output=True, text=True)
    browser = home / '.local/share/gran/apps/zen/1.24b'
    icons = browser / 'browser/chrome/icons/default'
    icons.mkdir(parents=True)
    (icons / 'default128.png').write_bytes(PNG)
    (icons / 'default32.png').write_bytes(PNG)
    (browser / 'zen-bin').write_text('#!/bin/sh\nexit 0\n')
    (browser / 'zen-bin').chmod(0o755)
    (browser.parent / 'current').symlink_to(browser)
    return browser


@patch.dict(os.environ, {'DBUS_SESSION_BUS_ADDRESS': '', 'DCONF_BACKEND': 'memory'})
class AppearanceTests(unittest.TestCase):
    def test_logo_and_about_use_the_custom_art_and_live_system_information(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            prepare(home)
            env = dict(os.environ, HOME=str(home))
            result = subprocess.run([str(home / '.local/share/gran/bin/gran-show-logo')],
                                    env=env, capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout, (home / '.config/gran/branding/about.txt').read_text())
            self.assertIn('████', result.stdout)
            menu = (home / '.local/share/gran/shell/plugins/menu/BarWidget.qml').read_text()
            self.assertIn('iconComponent: Component', menu)
            self.assertNotIn('text: "G"', menu)
            about = (home / '.local/share/gran/bin/gran-launch-about').read_text()
            self.assertIn('fastfetch --config', about)
            config = json.loads((home / '.config/fastfetch/config.jsonc').read_text())
            self.assertEqual(config['logo']['source'], '~/.config/gran/branding/about.txt')
            self.assertIn('"type": "cpu"', json.dumps(config))
            self.assertIn('"type": "os"', json.dumps(config))

    def test_new_install_uses_native_bar_with_current_margins_and_theme_rounding(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            prepare(home)
            config = json.loads((home / '.config/gran/shell.json').read_text())
            self.assertEqual(config['bar']['id'], 'gran.bar')
            bar = home / '.local/share/gran/shell/plugins/bar'
            self.assertEqual(json.loads((bar / 'manifest.json').read_text())['id'], 'gran.bar')
            source = (bar / 'Bar.qml').read_text()
            margins = source.split('    margins {', 1)[1].split('    }', 1)[0]
            self.assertIn('(root.position === "right" ? 0 : 6)', margins)
            self.assertIn('(root.position === "left" ? 0 : 6)', margins)
            self.assertIn('(root.position === "bottom" ? 0 : 3)', margins)
            self.assertIn('radius: Style.cornerRadius', source)
            self.assertIn('rounding = 4', (home / '.config/hypr/looknfeel.lua').read_text())

    def test_same_version_install_repairs_deleted_icons_and_launcher_without_download(self):
        module = load('zen_repair', ROOT / 'overlay/.local/share/gran/bin/gran-app')
        with tempfile.TemporaryDirectory(prefix='gran appearance ') as directory:
            home = Path(directory)
            prepare(home)
            desktop = home / '.local/share/applications/zen.desktop'
            desktop.write_text('[Desktop Entry]\nIcon=missing\n')
            with patch.object(module, 'api', return_value={'tag_name': '1.24b'}), \
                 patch.object(module, 'request', side_effect=AssertionError('must not download')):
                module.install_zen(home, {'version': '1.24b'}, release_tag='1.24b')
            icon = home / '.local/share/icons/hicolor/128x128/apps/zen-browser.png'
            self.assertEqual(icon.read_bytes(), PNG)
            self.assertIn('Icon=' + str(icon), desktop.read_text())
            self.assertIn('Exec="' + str(home / '.local/bin/zen-browser') + '" %u', desktop.read_text())
            if __import__('shutil').which('desktop-file-validate'):
                subprocess.run(['desktop-file-validate', str(desktop)], check=True)

    def test_first_launch_gets_compact_mode_palette_and_frosted_files(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            prepare(home)
            env = dict(os.environ, HOME=str(home), GRAN_PATH=str(home / '.local/share/gran'))
            env['PATH'] = str(home / '.local/share/gran/bin') + ':' + str(home / '.local/bin') + ':' + os.environ['PATH']
            subprocess.run([str(home / '.local/bin/zen-browser')], env=env, check=True)
            profile = home / '.config/zen/gran.default'
            prefs = (profile / 'user.js').read_text()
            self.assertIn('user_pref("zen.view.compact.enable-at-startup", true);', prefs)
            self.assertIn('user_pref("browser.theme.toolbar-theme", 0);', prefs)
            self.assertIn('--zen-main-browser-background: #2e3440', (profile / 'chrome/gran-colors.css').read_text())
            gtk = (home / '.config/gtk-4.0/gtk.css').read_text()
            self.assertTrue(gtk.rstrip().endswith('@import url("gran-nautilus-blur.css");'))
            self.assertIn('backdrop-filter: blur(20px)', (home / '.config/gtk-4.0/gran-nautilus-blur.css').read_text())
            launcher = (home / '.local/share/applications/org.gnome.Nautilus.desktop').read_text()
            self.assertIn('Exec=nautilus-remember --new-window %U', launcher)
            self.assertIn('DBusActivatable=false', launcher)

    def test_theme_sync_writes_files_css_even_before_browser_profile_exists(self):
        module = load('appearance_theme', ROOT / 'overlay/.local/share/gran/bin/gran-theme-sync')
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            prepare(home)
            module.sync(home, configure_gsettings=False)
            self.assertTrue((home / '.config/gtk-4.0/gran-nautilus.css').is_file())
            self.assertFalse((home / '.config/zen/profiles.ini').exists())

    def test_existing_install_upgrade_keeps_browser_data_bindings_and_monitors(self):
        module = load('appearance_upgrade', ROOT / 'scripts/apply-appearance.py')
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            prepare(home)
            sentinels = {
                '.config/hypr/bindings.lua': '-- personal bindings\n',
                '.config/hypr/monitors.lua': '-- personal monitors\n',
                '.config/zen/existing/prefs.js': 'user_pref("personal.preference", true);\n',
                '.config/zen/existing/cookies.sqlite': 'personal cookie data',
                '.config/zen/existing/places.sqlite': 'personal bookmarks',
            }
            for relative, value in sentinels.items():
                path = home / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(value)
            (home / '.config/zen/profiles.ini').write_text('[Profile0]\nName=Existing\nIsRelative=1\nPath=existing\nDefault=1\n')
            user = home / '.config/zen/existing/user.js'
            user.write_text('user_pref("personal.preference", true);\nuser_pref("zen.view.compact.enable-at-startup", false);\n')
            chrome = home / '.config/zen/existing/chrome/userChrome.css'
            chrome.parent.mkdir()
            chrome.write_text('/* personal CSS */\n')
            shell_path = home / '.config/gran/shell.json'
            legacy = json.loads(shell_path.read_text())
            legacy['bar']['id'] = 'hattux.bar'
            legacy['bar']['layout']['left'].append({'id': 'personal.widget'})
            legacy['personalPreference'] = 'keep'
            shell_path.write_text(json.dumps(legacy))
            about = home / '.local/share/gran/bin/gran-launch-about'
            about.write_text('#!/bin/sh\necho old about\n')
            backup = module.apply(home)
            updated = json.loads(shell_path.read_text())
            expected = dict(legacy, bar=dict(legacy['bar'], id='gran.bar'))
            self.assertEqual(updated, expected)
            self.assertEqual(json.loads((backup / '.config/gran/shell.json').read_text()), legacy)
            self.assertEqual((backup / '.local/share/gran/bin/gran-launch-about').read_text(), '#!/bin/sh\necho old about\n')
            for relative, value in sentinels.items():
                self.assertEqual((home / relative).read_text(), value)
            self.assertIn('/* personal CSS */', chrome.read_text())
            self.assertIn('user_pref("personal.preference", true);', user.read_text())
            self.assertNotIn('enable-at-startup", false', user.read_text())
            self.assertEqual(user.read_text().count('enable-at-startup'), 1)
            before = user.read_bytes()
            module.apply(home)
            self.assertEqual(user.read_bytes(), before)
            for relative, value in sentinels.items():
                self.assertEqual((home / relative).read_text(), value)
            self.assertFalse((home / '.config/zen/gran.default').exists())


if __name__ == '__main__':
    unittest.main()

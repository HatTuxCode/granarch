import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader))
    loader.exec_module(module)
    return module


class SystemProfileTests(unittest.TestCase):
    def setUp(self):
        self.module = load('gran_system', ROOT / 'scripts/apply-system.py')

    def prepare(self, root, loader):
        (root / 'etc/mkinitcpio.d').mkdir(parents=True)
        (root / 'etc/mkinitcpio.d/linux.preset').write_text('# target kernel preset\n')
        (root / 'sys/class/dmi/id').mkdir(parents=True)
        (root / 'sys/class/dmi/id/sys_vendor').write_text('ASUSTeK COMPUTER INC.\n')
        if loader == 'limine':
            (root / 'boot').mkdir()
            (root / 'boot/limine.conf').write_text('timeout: 5\n/Arch\n  protocol: linux\n  path: boot():/vmlinuz-linux\n  cmdline: cryptdevice=UUID=TARGET-DISK:root root=/dev/mapper/root rootflags=subvol=@ rw\n')
        elif loader == 'systemd-boot':
            (root / 'boot/loader/entries').mkdir(parents=True)
            (root / 'boot/loader/loader.conf').write_text('default arch.conf\ntimeout 4\n')
            (root / 'boot/loader/entries/arch.conf').write_text('title Arch\nlinux /vmlinuz-linux\ninitrd /initramfs-linux.img\noptions rd.luks.name=TARGET-DISK=root root=/dev/mapper/root rw\n')
        else:
            (root / 'boot/grub').mkdir(parents=True)
            (root / 'boot/grub/grub.cfg').write_text('# Existing generated GRUB\n')
            (root / 'etc/default').mkdir()
            (root / 'etc/default/grub').write_text("GRUB_TIMEOUT=5\nGRUB_CMDLINE_LINUX_DEFAULT='cryptdevice=UUID=TARGET-DISK:root root=/dev/mapper/root rw'\n")

    def test_boot_profiles_preserve_target_storage_and_install_ported_login(self):
        for loader in ('limine', 'systemd-boot', 'grub'):
            with self.subTest(loader=loader), tempfile.TemporaryDirectory(prefix='gran-system-test-') as directory:
                root = Path(directory)
                self.prepare(root, loader)
                result = self.module.apply(root, 'alice', Path('/home/alice'))
                self.assertEqual(result['bootloader'], loader)
                text = '\n'.join(p.read_text() for p in (root / 'boot').rglob('*.conf'))
                if loader == 'grub':
                    text += (root / 'etc/default/grub').read_text()
                self.assertIn('TARGET-DISK', text)
                self.assertIn('root=/dev/mapper/root', text)
                self.assertIn('quiet splash', text)
                self.assertNotIn('resume_offset=', text)
                login = (root / 'etc/sddm.conf.d/90-gran.conf').read_text()
                self.assertIn('User=alice', login)
                self.assertIn('Session=gran.desktop', login)
                self.assertIn('Relogin=false', login)
                self.assertNotIn('hattux', login)
                self.assertIn('95', (root / 'usr/local/libexec/gran-charge-limit').read_text())
                self.assertIn('Theme=gran', (root / 'etc/plymouth/plymouthd.conf').read_text())
                self.assertTrue((root / 'usr/share/plymouth/themes/gran/gran.plymouth').is_file())
                self.assertFalse((root / 'etc/crypttab').exists())
                self.assertFalse((root / 'etc/pacman.conf').exists())

    def test_plymouth_addition_preserves_both_encryption_hook_flavors(self):
        for flavor, base in (('encrypt', 'base udev keyboard block encrypt filesystems fsck'),
                             ('sd-encrypt', 'base systemd keyboard sd-vconsole block sd-encrypt filesystems fsck')):
            source = f'HOOKS=({base}); FILES=();\n' + self.module.PLYMOUTH_DROPIN
            source += self.module.PLYMOUTH_DROPIN + '\nprintf "%s\\n" "${HOOKS[*]}"\n'
            result = subprocess.run(['bash', '-c', source], capture_output=True, text=True, check=True)
            hooks = result.stdout.strip().split()
            self.assertEqual(hooks.count('plymouth'), 1)
            self.assertLess(hooks.index('plymouth'), hooks.index(flavor))
            self.assertEqual([h for h in hooks if h != 'plymouth'], base.split())

    def test_unknown_bootloader_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory(prefix='gran-system-test-') as directory:
            root = Path(directory)
            with self.assertRaisesRegex(RuntimeError, 'Nenhuma configuração'):
                self.module.apply(root, 'alice', Path('/home/alice'))
            self.assertEqual(list(root.iterdir()), [])

    def test_execute_cannot_run_against_a_staging_root(self):
        with tempfile.TemporaryDirectory(prefix='gran-system-test-') as directory:
            root = Path(directory)
            with self.assertRaisesRegex(RuntimeError, '--execute'):
                self.module.apply(root, 'alice', Path('/home/alice'), execute=True)
            self.assertEqual(list(root.iterdir()), [])


class ThemeProfileTests(unittest.TestCase):
    def test_theme_sync_generates_shared_palette_and_preserves_css(self):
        module = load('gran_theme_sync', ROOT / 'overlay/.local/share/gran/bin/gran-theme-sync')
        with tempfile.TemporaryDirectory(prefix='gran-theme-test-') as directory:
            home = Path(directory)
            result = subprocess.run(['python', str(ROOT / 'scripts/apply-home.py'), '--home', str(home)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            entry = home / '.config/gtk-3.0/gtk.css'
            entry.parent.mkdir(parents=True, exist_ok=True)
            entry.write_text('/* original user CSS */\n')
            changed = module.sync(home, configure_gsettings=False)
            self.assertTrue(changed)
            self.assertIn('/* original user CSS */', entry.read_text())
            self.assertIn('#2e3440', (home / '.config/gtk-3.0/gran-colors.css').read_text())
            self.assertIn('--window-bg-color: #2e3440', (home / '.config/gtk-4.0/gran-colors.css').read_text())
            self.assertEqual(module.sync(home, configure_gsettings=False), [])
            kitty = (home / '.config/kitty/kitty.conf').read_text()
            for preference in ('shell /usr/bin/fish', 'cursor_trail 1', 'cursor_trail_start_threshold 1',
                               'cursor_trail_decay 0.1 0.25', 'window_padding_width 14'):
                self.assertIn(preference, kitty)
            self.assertIn('.local/state/gran/current/theme/kitty.conf', kitty)


if __name__ == '__main__':
    unittest.main()

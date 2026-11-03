"""Regressions for minimal homes and pre-install dependency checks."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class MinimalInstallTests(unittest.TestCase):
    def test_empty_home_has_directories_required_before_upstream_installs(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / 'new-user'
            result = subprocess.run(['python', str(ROOT / 'scripts/apply-home.py'), '--home', str(home)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for relative in ('.config/mise', '.config/dconf', '.local/bin',
                             '.local/share/applications', '.local/share/icons',
                             '.local/share/glib-2.0/schemas', '.cache/gran'):
                self.assertTrue((home / relative).is_dir(), relative)

    def preflight(self, version='0.57.0', missing=False, distro='cachyos', boot='0'):
        script = '''
set -euo pipefail
die() { echo "$*" >&2; exit 1; }
source "$1/scripts/preflight.sh"
DISTRO=$TEST_DISTRO CONFIGURE_BOOT=$TEST_BOOT
PACKAGES=(hyprland quickshell) NOTEBOOK_PACKAGES=()
pacman-conf() { printf '[cachyos]\\n[core]\\n[extra]\\n'; }
pacman() {
  case "${2#*/}" in
    missing) return 1 ;;
    hyprland) printf 'Version : %s\\n' "$TEST_HYPR_VERSION" ;;
    quickshell) printf 'Version : 0.3.2\\n' ;;
    *) return 1 ;;
  esac
}
gran_preflight
'''
        if missing:
            script = script.replace('PACKAGES=(hyprland quickshell)', 'PACKAGES=(missing quickshell)')
        import os
        with tempfile.TemporaryDirectory() as home:
            env = dict(os.environ, TEST_HYPR_VERSION=version, TEST_DISTRO=distro, TEST_BOOT=boot, HOME=home)
            return subprocess.run(['bash', '-c', script, 'preflight-test', str(ROOT)],
                                  capture_output=True, text=True, env=env)

    def test_cachyos_repositories_and_supported_versions_are_accepted(self):
        result = self.preflight()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_endeavouros_official_packages_are_accepted_without_boot_presets(self):
        result = self.preflight(distro='endeavouros')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_endeavouros_rejects_forcing_mkinitcpio_boot(self):
        result = self.preflight(distro='endeavouros', boot='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('preserve dracut', result.stderr)

    def test_distro_boot_defaults_and_package_filtering(self):
        for distro, expected in (('arch', '1'), ('cachyos', '0'), ('endeavouros', '0')):
            with self.subTest(distro=distro):
                script = r'''set -euo pipefail
source "$1/scripts/preflight.sh"
DISTRO=$2 CONFIGURE_BOOT=auto
PACKAGES=(extra/hyprland core/mkinitcpio extra/plymouth extra/sddm)
gran_select_boot
gran_filter_boot_packages
printf '%s\n' "$CONFIGURE_BOOT" "${PACKAGES[@]}"
'''
                result = subprocess.run(['bash', '-c', script, 'test', str(ROOT), distro],
                                        capture_output=True, text=True, check=True)
                lines = result.stdout.splitlines()
                self.assertEqual(lines[0], expected)
                self.assertIn('extra/hyprland', lines)
                self.assertIn('extra/sddm', lines)
                self.assertEqual('core/mkinitcpio' in lines, expected == '1')
                self.assertEqual('extra/plymouth' in lines, expected == '1')

    def test_endeavouros_dracut_tree_is_preserved_without_mkinitcpio(self):
        spec = importlib.util.spec_from_file_location('system_eos', ROOT / 'scripts/apply-system.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sentinels = {
                'etc/dracut.conf.d/eos-defaults.conf': 'hostonly="yes"\n',
                'etc/kernel/cmdline': 'root=UUID=KEEP rw rd.luks.uuid=KEEP\n',
                'efi/loader/entries/eos.conf': 'title EndeavourOS\nlinux /KEEP/linux\n',
                'usr/lib/kernel/install.d/50-dracut.install': '# original kernel-install hook\n',
            }
            for relative, value in sentinels.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(value)
            module.apply(root, 'alice', Path('/home/alice'), boot=False)
            for relative, value in sentinels.items():
                self.assertEqual((root / relative).read_text(), value)
            self.assertFalse((root / 'etc/mkinitcpio.conf.d').exists())
            self.assertFalse((root / 'etc/plymouth').exists())
            self.assertTrue((root / 'usr/share/wayland-sessions/gran.desktop').is_file())

    def test_old_hyprland_stops_before_installation(self):
        result = self.preflight(version='0.56.2')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('API Lua', result.stderr)

    def test_missing_package_has_actionable_error(self):
        result = self.preflight(missing=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Pacote indisponível: missing', result.stderr)

    def test_managed_cachyos_boot_is_rejected_before_writes(self):
        spec = importlib.util.spec_from_file_location('system_apply', ROOT / 'scripts/apply-system.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'etc/default').mkdir(parents=True)
            (root / 'etc/default/limine').write_text('KERNEL_CMDLINE[default]="root=UUID=KEEP rw"\n')
            original = (root / 'etc/default/limine').read_bytes()
            with patch.object(module, 'boot_files', return_value=('limine', [])):
                with self.assertRaisesRegex(RuntimeError, 'Boot gerenciado'):
                    module.apply(root, 'alice', Path('/home/alice'))
            self.assertEqual((root / 'etc/default/limine').read_bytes(), original)
            self.assertFalse((root / 'var').exists())
            result = module.apply(root, 'alice', Path('/home/alice'), boot=False)
            self.assertIsNone(result['bootloader'])
            self.assertFalse((root / 'etc/mkinitcpio.conf.d').exists())
            self.assertEqual((root / 'etc/default/limine').read_bytes(), original)


if __name__ == '__main__':
    unittest.main()

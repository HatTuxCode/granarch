#!/usr/bin/env python3
"""Capture only an explicit allowlist of desktop assets, never account data."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone
from gran_namespace import content, json_content, rename
from port_font import port_font

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
SOURCE = Path('/usr/share/omarchy')


def ignored(directory, names):
    return [name for name in names if name.startswith('.') or
            any(marker in name for marker in ('.bak', '-backup', '.log', '__pycache__')) or
            name in ('node_modules', 'target', 'build', 'models')]


def copy(source, destination):
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, ignore=ignored, symlinks=False)
    else:
        shutil.copy2(source, destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replace', action='store_true', help='Replace the project snapshot only')
    args = parser.parse_args()
    target = ROOT / 'snapshot'
    if target.exists():
        if not args.replace:
            parser.error('snapshot already exists; use --replace to recapture')
        shutil.rmtree(target)
    runtime = target / 'runtime'
    for name in ('bin', 'shell', 'config'):
        copy(SOURCE / name, runtime / name)
    for name in ('hypr', 'omarchy', 'i18n', 'themed', 'gtk', 'fonts', 'fontconfig',
                 'xdg-terminal-exec', 'xcompose'):
        copy(SOURCE / 'default' / name, runtime / 'default' / name)
    excluded = ('install', 'update', 'upgrade', 'migrate', 'migration', 'channel',
                'branch', 'dev', 'provision', 'reinstall', 'reset', 'refresh-pacman',
                'pkg', 'tui-install', 'tui-remove', 'webapp-install', 'webapp-remove',
                'kernel', 'limine', 'snapper', 'partition', 'drive', 'version',
                'debug', 'keyring', 'setup', 'finalize', 'seed', 'apply', 'lifecycle',
                'boot', 'plymouth', 'system-factory-reset', 'mise', 'snapshot',
                'remove-service', 'games-retro-install', 'hibernation-setup', 'hibernation-remove')
    for path in (runtime / 'bin').iterdir():
        suffix = path.name.removeprefix('omarchy-')
        if any(suffix == item or suffix.startswith(item + '-') for item in excluded):
            path.unlink()
    (runtime / 'default/omarchy/omarchy-menu.jsonc').unlink(missing_ok=True)
    # Licensing belongs beside the bundled sources, including plugin licenses.
    for name in ('LICENSE', 'LICENSE.md', 'COPYING'):
        copy(SOURCE / name, runtime / name)
    user = target / 'home'
    for name in ('hypr', 'kitty', 'fontconfig'):
        copy(HOME / '.config' / name, user / '.config' / name)
    for name in ('shell.json', 'shell.toml', 'language', 'omasettings.json'):
        copy(HOME / '.config/omarchy' / name, user / '.config/omarchy' / name)
    for directory in (HOME / '.config/omarchy/plugins').iterdir():
        if directory.is_dir() and not directory.name.startswith('.'):
            copy(directory, user / '.config/omarchy/plugins' / directory.name)
    for name in ('starship.toml', 'btop/btop.conf',
                 'gtk-4.0/gtk.css', 'gtk-4.0/omarchy-nautilus.css',
                 'omarchy/scripts/sync-nautilus-zen.py',
                 'omarchy/hooks/theme-set.d/90-sync-nautilus-zen.sh',
                 'omarchy/hooks/post-boot.d/kbd-backlight-boot.sh',
                 'pipewire/pipewire.conf.d/omarchy-eq.conf',
                 'wireplumber/wireplumber.conf.d/bluetooth-a2dp-autoconnect.conf',
                 'wireplumber/wireplumber.conf.d/kef-lsx-no-suspend.conf',
                 'environment.d/omarchy-firefox-wayland.conf'):
        copy(HOME / '.config' / name, user / '.config' / name)
    # No fish universal variables: they can contain arbitrary user environment values.
    copy(HOME / '.config/fish/config.fish', user / '.config/fish/config.fish')
    for name in ('nautilus-remember', 'rename-selected', 'omarchy-nightlight-soft',
                 'omarchy-lid-open-wake', 'omarchy-brightness-keyboard',
                 'omarchy-kbd-backlight-cycle', 'omarchy-kbd-backlight-idle',
                 'omarchy-kbd-backlight-monitor', 'omarchy-eq', 'omarchy-eq-control',
                 'omarchy-theme-bg-persist', 'omarchy-adaptive-power', 'omarchy-media-stay-awake'):
        copy(HOME / '.local/bin' / name, user / '.local/bin' / name)
    for name in ('nautilus-remember.service', 'omarchy-kbd-backlight-monitor.service',
                 'omarchy-adaptive-power.service', 'omarchy-adaptive-power.timer',
                 'omarchy-media-stay-awake.service', 'omarchy-media-stay-awake.timer'):
        copy(HOME / '.config/systemd/user' / name, user / '.config/systemd/user' / name)
    copy(SOURCE / 'default/systemd/user/omarchy-sleep-lock.service',
         user / '.config/systemd/user/omarchy-sleep-lock.service')
    copy(SOURCE / 'default/systemd/system-sleep/keyboard-backlight',
         target / 'system/usr/lib/systemd/system-sleep/gran-keyboard-backlight')
    for kind, origin in (('plymouth', Path('/usr/share/plymouth/themes/omarchy')),
                         ('sddm', Path('/usr/share/sddm/themes/omarchy'))):
        copy(origin, target / 'system/usr/share' / kind / 'themes/omarchy')
    copy(Path('/usr/share/sddm/hyprland.lua'), target / 'system/usr/share/sddm/gran-hyprland.lua')
    copy(Path('/etc/asusd/asusd.ron'), target / 'system/etc/asusd/asusd.ron')
    copy(Path('/etc/vconsole.conf'), target / 'system/etc/vconsole.conf')
    for relative in ('powerprofiles/ac', 'powerprofiles/battery', 'indicators/kbd-backlight-default'):
        copy(HOME / '.local/state/omarchy' / relative, user / '.local/state/omarchy' / relative)
    current = HOME / '.local/state/omarchy/current'
    for name in ('theme', 'theme.name'):
        copy(current / name, user / '.local/state/omarchy/current' / name)
    copy(current / 'background', user / '.local/share/gran/wallpaper.jpg')
    copy(current / 'theme/btop.theme', user / '.config/btop/themes/current.theme')
    copy(HOME / '.local/state/omarchy/settings/weather.json',
         user / '.local/state/omarchy/settings/weather.json')
    copy(Path('/etc/xdg/kitty/kitty.conf'), target / 'kitty-defaults.conf')
    copy(Path('/etc/fonts/conf.d/50-omarchy.conf'),
         user / '.config/fontconfig/conf.d/50-omarchy.conf')
    preferences = {}
    for key in ('gtk-theme', 'icon-theme', 'cursor-theme', 'cursor-size', 'font-name',
                'document-font-name', 'monospace-font-name', 'color-scheme'):
        preferences[key] = subprocess.check_output(
            ['gsettings', 'get', 'org.gnome.desktop.interface', key],
            text=True, stderr=subprocess.DEVNULL).strip()
    (target / 'appearance.json').write_text(json.dumps(preferences, indent=2) + '\n')
    copy(Path('/etc/pam.d/omarchy-lock-password'), target / 'pam/omarchy-lock-password')
    # Relocatable paths in Lua, shell, systemd and plugin code. Original files stay intact.
    count = 0
    for path in target.rglob('*'):
        if not path.is_file():
            continue
        try:
            value = path.read_text()
        except (UnicodeError, ValueError):
            continue
        if str(HOME) in value:
            path.write_text(value.replace(str(HOME), '@@GRAN_HOME@@'))
            count += 1
    # Preserve the stock theme too, so applying Nord again does not lose its palette.
    copy(user / '.local/state/omarchy/current/theme', runtime / 'themes/nord')
    binding_sources = [HOME / '.config/hypr/bindings.lua',
                       *sorted((SOURCE / 'default/hypr/bindings').glob('*.lua'))]
    bindings = [{'module': path.name,
                 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                 'gran_sha256': hashlib.sha256(content(path.read_text()).replace(
                     str(HOME), '@@GRAN_HOME@@').encode()).hexdigest()}
                for path in binding_sources]
    for path in sorted(target.rglob('*'), key=lambda p: len(p.parts), reverse=True):
        if path.is_file() and not path.name.lower().startswith(('license', 'copying')):
            try:
                value = path.read_text()
                value = json_content(value) if path.suffix == '.json' else content(value)
                path.write_text(value)
            except (UnicodeError, json.JSONDecodeError):
                pass
        renamed = path.with_name(rename(path.name))
        if path != renamed:
            path.rename(renamed)
    weather = runtime / 'shell/plugins/panels/weather/Panel.qml'
    weather.write_text(weather.read_text().replace(
        '["curl", "-fsS", "--max-time", "4", "https://geo.omarchy.org/"]',
        '["gran-weather-location", "--json"]'))
    shell = runtime / 'shell/shell.qml'
    shell.write_text(shell.read_text().replace('//@ pragma GranLoadPatch\n', ''))
    font = runtime / 'default/fonts/gran/gran.ttf'
    font.write_bytes(port_font(font.read_bytes()))
    copy(font, user / '.local/share/fonts/gran.ttf')
    menu_widget = runtime / 'shell/plugins/menu/BarWidget.qml'
    menu_widget.write_text(menu_widget.read_text().replace('text: "\\ue900"', 'text: "G"').replace(
        'fontFamily: "gran"', 'fontFamily: root.bar ? root.bar.fontFamily : "monospace"'))
    browser_sync = user / '.config/gran/scripts/sync-nautilus-zen.py'
    browser_sync.write_text(browser_sync.read_text().replace('import shutil', 'import shutil\nimport os').replace(
        "ini = config / 'zen/profiles.ini'",
        "ini = Path(os.environ.get('GRAN_ZEN_INI', str(config / 'zen/profiles.ini')))"))
    (runtime / 'version').write_text('0.3.0\n')
    theme_install = runtime / 'bin/gran-theme-install'
    theme_install.write_text(theme_install.read_text().replace(
        'echo -e "\\e[32mSee https://omarchy.org/themes/\\n\\e[0m"',
        'echo "Usage: gran theme install <git-url>"'))
    metadata = {
        'captured_at': datetime.now(timezone.utc).isoformat(),
        'theme': (current / 'theme.name').read_text().strip(),
        'namespace': 'gran',
        'requires': {'hyprland': '0.57.0', 'quickshell': '0.3.2'},
        'binding_sources': bindings,
        'relocated_files': count,
        'excluded': ['repository keys/configs', 'distribution installers/migrations',
                     'credentials', 'browser profiles', 'SSH/GPG keys', 'fish_variables',
                     'clipboard history', 'notifications', 'plugin git history', 'camera models'],
    }
    (target / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    files = sorted(p for p in target.rglob('*') if p.is_file())
    (target / 'SHA256SUMS').write_text(''.join(
        f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(target)}\n' for p in files))
    print(f'Snapshot: {len(files)} files; theme {metadata["theme"]}; no host changes.')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Port the source menu's supported desktop sections and add native Gran workflows."""
import json
from pathlib import Path
import re
from gran_namespace import content

ROOT = Path(__file__).resolve().parents[1]


def build(source):
    available = {p.name for directory in (ROOT / 'snapshot/runtime/bin', ROOT / 'overlay/.local/share/gran/bin')
                 for p in directory.glob('gran*') if p.is_file()}
    rows = {}
    for line in source.read_text().splitlines():
        if not line.lstrip().startswith('"'):
            continue
        for key, value in json.loads('{' + content(line.strip().rstrip(',')) + '}').items():
            if key.split('.')[0] not in ('apps', 'learn', 'appearance', 'trigger', 'setup', 'update', 'system', 'about'):
                continue
            if key.startswith(('setup.default.', 'setup.security.', 'setup.typing.', 'setup.direct-boot',
                               'setup.reset', 'update.channel', 'update.kernel', 'update.password.drive',
                               'learn.gran', 'learn.community')):
                continue
            if value.get('provider') == 'kernels':
                continue
            commands = set(re.findall(r'\bgran-[a-z0-9-]+', ' '.join(str(value.get(f, '')) for f in ('action', 'when', 'checked', 'disabled'))))
            if commands - available:
                continue
            if key.startswith('learn.') and 'action' in value:
                value['action'] = value['action'].replace('gran-launch-webapp', 'gran-launch-browser')
            rows[key] = value
    def row(key, label, action=None, **extra):
        rows[key] = {'label': label, **({'action': action} if action else {}), **extra}
    def terminal(command):
        return 'gran-launch-floating-terminal-with-presentation ' + "'" + command + "'"
    row('apps', 'Apps', 'gran-launch-apps', icon='󰀻', aliases=['app', 'applications'], provider='apps')
    row('setup', 'Setup', icon='', aliases=['settings'])
    for key, label, command in (
        ('monitors', 'Monitors', 'monitors'), ('keybindings', 'Keybindings', 'bindings'),
        ('input', 'Input', 'input'), ('typing.keyboard', 'Keyboard Layout', 'keyboard'),
        ('config.git', 'Git', 'git'), ('timezone', 'Timezone', 'timezone'),
        ('power', 'Notebook Power Policy', 'power'), ('kitty', 'Kitty', 'kitty'),
        ('fish', 'Fish', 'fish'), ('network.connections', 'Connections / Wi-Fi', 'network'),
        ('security.password', 'User Password', 'password'), ('security.fingerprint', 'Enroll Fingerprint', 'fingerprint'),
        ('security.sshd', 'SSH Server', 'sshd'), ('printing', 'Printers', 'printing')):
        row('setup.' + key, label, terminal('gran setup ' + command))
    row('setup.language', 'Interface Language', provider='languages')
    for kind, label in (('agent', 'Agent'), ('browser', 'Browser'), ('terminal', 'Terminal'), ('editor', 'Editor')):
        row('setup.default.' + kind, label, terminal('gran setup default-' + kind))
    row('setup.palette', 'Synchronize App Colors', terminal('gran theme sync'))
    row('install', 'Install', icon='󰉉')
    row('install.package', 'Package', terminal('gran pkg install'), icon='󰣇')
    row('install.webapp', 'Web App', terminal('gran webapp install'), icon='')
    row('install.aur', 'AUR', terminal('gran pkg aur install'), icon='󰣇')
    row('install.tui', 'TUI / Command-line Package', terminal('gran pkg install'))
    row('install.style', 'Style')
    row('install.style.theme', 'Theme from Git', terminal('gran theme install'))
    row('install.style.background', 'Background', 'gran-theme-bg-install')
    catalog = json.loads((ROOT / 'manifests/optional-apps.json').read_text())
    labels = {'browser': 'Browser', 'terminal': 'Terminal', 'editor': 'Editor', 'development': 'Development',
              'service': 'Services', 'font': 'Fonts', 'gaming': 'Gaming', 'ai': 'AI'}
    for key, item in catalog.items():
        category = item['category']
        row('install.' + category, labels[category])
        options = {}
        if any(p.startswith('multilib/') for p in item.get('packages', [])):
            options['when'] = 'pacman-conf --repo-list | grep -qx multilib'
        row('install.' + category + '.' + key, item['label'], terminal('gran install ' + category + ' ' + key), **options)
    row('remove', 'Remove', icon='󰭌', aliases=['uninstall'])
    row('remove.package', 'Package', terminal('gran pkg remove'))
    row('remove.webapp', 'Web App', terminal('gran webapp remove'))
    row('remove.theme', 'Theme', 'gran-theme-remove')
    row('remove.plugin', 'Plugin', 'gran-menu-plugin remove')
    row('update.gran', 'Gran', terminal('gran update'), icon='')
    row('update.palette', 'App Colors', terminal('gran theme sync'))
    row('learn.gran', 'Gran Commands', terminal('gran commands'))
    row('learn.skills', 'AI Skills', terminal('gran skills list'))
    row('appearance.background', 'Background', 'gran-theme-bg-persist', aliases=['background', 'wallpaper'])
    row('about', 'About Gran', 'gran-launch-about', icon='')
    # Every row needs an actual parent. Remove empty structural rows after filtering.
    for key in list(rows):
        parts = key.split('.')
        for length in range(1, len(parts)):
            parent = '.'.join(parts[:length])
            rows.setdefault(parent, {'label': parts[length - 1].replace('-', ' ').title()})
    changed = True
    while changed:
        changed = False
        for key, value in list(rows.items()):
            if not value.get('action') and not value.get('provider') and not any(k.startswith(key + '.') for k in rows):
                del rows[key]
                changed = True
    return rows


if __name__ == '__main__':
    menu = build(Path('/usr/share/omarchy/default/omarchy/omarchy-menu.jsonc'))
    destination = ROOT / 'overlay/.local/share/gran/default/gran/gran-menu.jsonc'
    destination.write_text(json.dumps(menu, ensure_ascii=False, indent=2) + '\n')
    print(f'Gran menu: {len(menu)} rows, with native install/remove/setup workflows.')

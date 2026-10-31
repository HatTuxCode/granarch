"""Interactive Gran setup and optional package workflows. No distribution repositories."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


def run(arguments, **kwargs):
    return subprocess.run(arguments, check=True, **kwargs)


def output(arguments, **kwargs):
    return subprocess.check_output(arguments, text=True, **kwargs).strip()


def choose(title, choices, filter=False):
    if not choices:
        raise ValueError('Nenhuma opção disponível.')
    command = ['gum', 'filter', '--placeholder', title] if filter else ['gum', 'choose', '--header', title]
    return output(command, input='\n'.join(choices) + '\n')


def prompt(title, value=''):
    return output(['gum', 'input', '--header', title, '--value', value])


def save(home, relative, value):
    destination = home / relative
    if destination.exists():
        backup = home / '.local/state/gran/setup-backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ') / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(destination, backup)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(value)


def packages(action, names=()):
    configuration = output(['pacman-conf'])
    if re.search(r'omarchy\.(org|cn)|\[omarchy\]', configuration, re.I):
        raise ValueError('O Gran não utiliza repositórios Omarchy.')
    names = list(names)
    if action == 'install':
        if not names:
            rows = output(['pacman', '-Sl']).splitlines()
            choices = [row.split()[0] + '/' + row.split()[1] for row in rows]
            names = [choose('Instalar pacote — pesquise nome ou repositório', choices, filter=True)]
        command = ['sudo', 'pacman', '-Syu', '--needed', '--', *names]
        run(['pacman', '-Si', '--', *names])
    elif action == 'remove':
        if not names:
            names = [choose('Remover pacote', output(['pacman', '-Qqe']).splitlines(), filter=True)]
        command = ['sudo', 'pacman', '-Rns', '--', *names]
        run(['pacman', '-Qi', '--', *names])
    elif action == 'search':
        query = names[0] if names else prompt('Pesquisar pacotes')
        run(['pacman', '-Ss', '--', query])
        return
    elif action == 'aur':
        if not shutil.which('yay'):
            packages('install', ['core/base-devel', 'extra/git'])
            directory = Path.home() / '.cache/gran/builds/yay'
            if not directory.exists():
                run(['git', 'clone', 'https://aur.archlinux.org/yay.git', str(directory)])
            print((directory / 'PKGBUILD').read_text())
            run(['gum', 'confirm', 'Compilar a receita AUR exibida e instalar yay?'])
            run(['makepkg', '-si'], cwd=directory)
        name = names[0] if names else prompt('Pacote AUR para instalar (receita da comunidade)')
        if not re.fullmatch(r'[a-zA-Z0-9@._+-]+', name):
            raise ValueError('Nome de pacote inválido.')
        run(['yay', '-S', '--', name])
        return
    else:
        raise ValueError('Ação de pacotes desconhecida.')
    if not names or any(not re.fullmatch(r'[A-Za-z0-9@._+:/-]+', name) or name.startswith('-') for name in names):
        raise ValueError('Nome de pacote inválido.')
    # Pacman presents the actual transaction and dependency changes before installation/removal.
    run(command)


def optional(kind, name=None):
    catalog = json.loads((Path(os.environ['GRAN_PATH']) / 'optional-apps.json').read_text())
    entries = {key: value for key, value in catalog.items() if kind == 'app' or value['category'] == kind}
    if name is None:
        selected = choose('Instalar — ' + kind, [f'{key}\t{value["label"]}' for key, value in entries.items()], filter=True)
        name = selected.split('\t', 1)[0]
    if name not in entries:
        raise ValueError('Aplicativo não listado nesta categoria.')
    item = entries[name]
    if item.get('delivery') == 'upstream':
        run(['gran-app', 'install', name])
    elif item.get('delivery') == 'mise':
        run(['mise', 'use', '-g', item['tool']])
    else:
        packages('install', item['packages'])


def setup(section, value=None):
    home = Path.home()
    if section == 'keyboard':
        layout = prompt('Layout XKB', 'br')
        variant = prompt('Variante XKB (pode ficar vazia)')
        if not all(re.fullmatch(r'[a-zA-Z0-9_,+-]*', item) for item in (layout, variant)) or not layout:
            raise ValueError('Layout inválido.')
        save(home, '.config/gran/keyboard-layouts', f'XKBLAYOUT={layout}\nXKBVARIANT={variant}\n')
        run(['hyprctl', 'reload'])
        run(['hyprctl', 'configerrors'])
    elif section == 'git':
        name = prompt('Nome para commits Git', output(['git', 'config', '--global', 'user.name']) if run_exists(['git', 'config', '--global', 'user.name']) else '')
        email = prompt('E-mail para commits Git')
        run(['git', 'config', '--global', 'user.name', name])
        run(['git', 'config', '--global', 'user.email', email])
    elif section == 'timezone':
        zone = choose('Fuso horário', output(['timedatectl', 'list-timezones']).splitlines(), filter=True)
        run(['sudo', 'timedatectl', 'set-timezone', zone])
    elif section == 'default-agent':
        agents = [name for name in ('codex', 'opencode', 'claude', 'pi', 'omp', 'aider', 'gemini') if shutil.which(name)]
        value = value or choose('Agente padrão', agents)
        if not re.fullmatch(r'[a-zA-Z0-9._+-]+', value) or not shutil.which(value):
            raise ValueError('Agente não instalado.')
        save(home, '.config/gran/defaults/agent', value + '\n')
    elif section == 'default-browser':
        browsers = {'zen': ('zen-browser', 'zen.desktop'), 'firefox': ('firefox', 'firefox.desktop'), 'chromium': ('chromium', 'chromium.desktop')}
        value = value or choose('Navegador padrão', [key for key, (command, _) in browsers.items() if shutil.which(command)])
        if value not in browsers or not shutil.which(browsers[value][0]):
            raise ValueError('Navegador não instalado.')
        desktop = browsers[value][1]
        run(['xdg-settings', 'set', 'default-web-browser', desktop])
        for mime in ('text/html', 'application/xhtml+xml', 'x-scheme-handler/http', 'x-scheme-handler/https'):
            run(['xdg-mime', 'default', desktop, mime])
    elif section == 'default-terminal':
        terminals = {'kitty': 'kitty.desktop', 'foot': 'foot.desktop', 'alacritty': 'Alacritty.desktop', 'ghostty': 'com.mitchellh.ghostty.desktop'}
        value = value or choose('Terminal padrão', [key for key in terminals if shutil.which(key)])
        if value not in terminals or not shutil.which(value):
            raise ValueError('Terminal não instalado.')
        save(home, '.config/xdg-terminals.list', terminals[value] + '\n')
    elif section == 'default-editor':
        editors = [name for name in ('nano', 'nvim', 'vim', 'hx', 'code', 'zed') if shutil.which(name)]
        value = value or choose('Editor padrão', editors)
        if value not in editors:
            raise ValueError('Editor não instalado.')
        save(home, '.local/state/gran/defaults/editor', value + '\n')
    elif section == 'network':
        run(['nmtui'])
    elif section == 'password':
        run(['passwd'])
    elif section == 'fingerprint':
        if not shutil.which('fprintd-enroll'):
            packages('install', ['extra/fprintd'])
        run(['fprintd-enroll'])
        print('Digital cadastrada. A integração de autenticação/PAM deve ser configurada para seu hardware; a senha permanece válida.')
    elif section == 'printing':
        if not shutil.which('system-config-printer'):
            packages('install', ['extra/cups', 'extra/system-config-printer'])
        run(['sudo', 'systemctl', 'enable', '--now', 'cups.service'])
        run(['system-config-printer'])
    elif section == 'sshd':
        if not shutil.which('sshd'):
            packages('install', ['core/openssh'])
        action = choose('Servidor SSH', ['enable', 'disable'])
        run(['sudo', 'systemctl', action, '--now', 'sshd.service'])
    elif section in ('power', 'monitors', 'bindings', 'input', 'kitty', 'fish'):
        files = {'power': '.config/gran/notebook.json', 'monitors': '.config/hypr/monitors.lua',
                 'bindings': '.config/hypr/bindings.lua', 'input': '.config/hypr/input.lua',
                 'kitty': '.config/kitty/kitty.conf', 'fish': '.config/fish/config.fish'}
        run(['gran-launch-config-editor', str(home / files[section])])
    else:
        raise ValueError('Setup não reconhecido: ' + section)


def run_exists(arguments):
    return subprocess.run(arguments, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['packages', 'install', 'setup'])
    parser.add_argument('action')
    parser.add_argument('values', nargs='*')
    args = parser.parse_args()
    if args.mode == 'packages':
        packages(args.action, args.values)
    elif args.mode == 'install':
        optional(args.action, args.values[0] if args.values else None)
    else:
        setup(args.action, args.values[0] if args.values else None)


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode)
    except (ValueError, OSError) as error:
        raise SystemExit(f'gran: {error}')

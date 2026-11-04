"""Generate Dolphin's KDE colors and a Qt stylesheet from the Gran palette."""
import configparser
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil


def sync_dolphin(home, palette):
    home = Path(home)
    def color(key):
        value = palette[key]
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
            raise ValueError(f'Invalid Dolphin color: {key}')
        return value
    bg, fg, accent, dark, raised, muted = (color(k) for k in (
        'background', 'foreground', 'accent', 'dark_background', 'lighter_background', 'light_foreground'))
    backup = home / '.local/state/gran/theme-backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    def write(relative, value):
        path = home / relative
        if path.exists() and path.read_text() == value:
            return
        if path.exists():
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, saved)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
    def update(relative, sections):
        path = home / relative
        config = configparser.ConfigParser(interpolation=None, strict=False)
        config.optionxform = str
        if path.exists(): config.read(path)
        for section, values in sections.items():
            if not config.has_section(section): config.add_section(section)
            for key, value in values.items(): config.set(section, key, str(value))
        import io
        output = io.StringIO(); config.write(output, space_around_delimiters=False)
        write(relative, output.getvalue())
    def rgb(value): return ','.join(str(int(value[i:i+2], 16)) for i in (1, 3, 5))
    groups = {}
    for name, background in (('Window', bg), ('View', bg), ('Button', raised), ('Selection', accent), ('Tooltip', dark), ('Complementary', dark), ('Header', dark)):
        text = bg if name == 'Selection' else fg
        groups['Colors:' + name] = {'BackgroundNormal': rgb(background), 'BackgroundAlternate': rgb(raised),
            'ForegroundNormal': rgb(text), 'ForegroundInactive': rgb(muted), 'ForegroundActive': rgb(accent),
            'ForegroundLink': rgb(accent), 'ForegroundVisited': rgb(muted), 'ForegroundNegative': rgb(color('red')),
            'ForegroundNeutral': rgb(color('yellow')), 'ForegroundPositive': rgb(color('green')),
            'DecorationFocus': rgb(accent), 'DecorationHover': rgb(accent)}
    groups['General'] = {'Name': 'Gran Nord', 'ColorScheme': 'Gran', 'TerminalApplication': 'kitty',
                         'TerminalService': 'kitty.desktop', 'BrowserApplication': 'zen-browser.desktop'}
    # Explicit scheme ID is needed by KDE applications outside Plasma.
    groups['UiSettings'] = {'ColorScheme': 'Gran'}
    from breeze_folders import build
    icon_theme = build(home)
    groups['Icons'] = {'Theme': icon_theme}
    update('.config/qt6ct/qt6ct.conf', {'Appearance': {'icon_theme': icon_theme}})
    groups['KDE'] = {'widgetStyle': 'Fusion'}
    groups['ColorEffects:Inactive'] = {'Enable': 'false'}
    update('.config/kdeglobals', groups)
    update('.local/share/color-schemes/Gran.colors', groups)
    update('.config/dolphinrc', {'UiSettings': {'ColorScheme': 'Gran'},
        'General': {'ShowFullPath': 'true'}, 'KFileDialog Settings': {'Show hidden files': 'false'}})
    # QSS also covers the Qt widgets that do not read KDE color schemes.
    # Explicit RGB prevents a translucent or low-contrast application palette
    # from being reused for the menu. Compositor opacity remains independent.
    write('.config/gran/dolphin.qss', f"""/* Gran palette: opaque menu paint and readable toolbar labels. */
QMenu {{ background-color: {bg}; color: {fg}; border: 1px solid {muted}; padding: 4px; qproperty-windowOpacity: 1.0; }}
QMenu::item {{ background-color: transparent; color: {fg}; padding: 5px 24px; }}
QMenu::item:selected, QMenuBar::item:selected {{ background-color: {accent}; color: {bg}; }}
QMenu::item:disabled {{ color: {muted}; }}
QMenu::separator {{ height: 1px; background: {raised}; margin: 4px 8px; }}
QMenuBar, QToolBar {{ background-color: {dark}; color: {fg}; }}
QToolButton {{ color: {fg}; }}
QToolButton:hover {{ background-color: {raised}; }}
""")
    if __import__('os').environ.get('DBUS_SESSION_BUS_ADDRESS'):
        import subprocess
        subprocess.run(['dbus-send','--session','--type=signal','/KGlobalSettings',
                        'org.kde.KGlobalSettings.notifyChange','int32:0','int32:0'],check=False)

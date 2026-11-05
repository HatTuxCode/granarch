#!/usr/bin/env python3
"""Retire only GranArch's old portable Zen launcher; preserve all browser data."""
from pathlib import Path
from datetime import datetime,timezone
import shutil
home=Path.home();launcher=home/'.local/bin/zen-browser'
if launcher.is_symlink() and launcher.resolve().is_relative_to(home/'.local/share/gran/apps/zen'):
    backup=home/'.local/state/gran/backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    backup.mkdir(parents=True);shutil.move(launcher,backup/'zen-browser')
apps=home/'.local/share/applications';apps.mkdir(parents=True,exist_ok=True)
(apps/'zen-browser.desktop').write_text('[Desktop Entry]\nType=Application\nName=Zen\nExec=gran-launch-zen %u\nIcon=zen-browser\nCategories=Network;WebBrowser;\nMimeType=text/html;x-scheme-handler/http;x-scheme-handler/https;\n')

# Hide the package's duplicate menu entry; keep one short Zen launcher.
(apps/'zen.desktop').write_text('[Desktop Entry]\nType=Application\nName=Zen\nExec=gran-launch-zen %u\nIcon=zen-browser\nNoDisplay=true\n')
launcher.parent.mkdir(parents=True,exist_ok=True)
if not launcher.exists() and not launcher.is_symlink():
    launcher.write_text('#!/bin/sh\nexec gran-launch-zen "$@"\n')
    launcher.chmod(0o755)

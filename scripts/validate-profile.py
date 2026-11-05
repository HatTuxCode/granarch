#!/usr/bin/env python3
"""Validate desktop configs without requiring an existing graphical login."""
import os,subprocess,tempfile
from pathlib import Path

def validate(home):
    env=os.environ.copy();env['HOME']=str(home)
    for key in ('HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY','DISPLAY','DBUS_SESSION_BUS_ADDRESS'):
        env.pop(key,None)
    with tempfile.TemporaryDirectory(prefix='granarch-validate-') as runtime:
        env['XDG_RUNTIME_DIR']=runtime
        subprocess.run(['noctalia','config','validate',str(home/'.config/noctalia/config.toml')],env=env,cwd=runtime,check=True)
        subprocess.run(['Hyprland','--verify-config','--config',str(home/'.config/hypr/hyprland.lua')],env=env,cwd=runtime,check=True)
if __name__=='__main__':validate(Path.home())

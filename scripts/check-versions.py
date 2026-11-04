#!/usr/bin/env python3
"""Read the product's version line, accepting the upstream optional v prefix."""
import re
import subprocess

MINIMUMS={'Hyprland':(0,57,1),'noctalia':(5,4,1)}

def version_from_output(command,output):
    pattern=rf'^\s*{re.escape(command)}\s+v?(\d+)\.(\d+)\.(\d+)\b'
    match=re.search(pattern,output,flags=re.M|re.I)
    return tuple(map(int,match.groups())) if match else None

def main():
    for command,minimum in MINIMUMS.items():
        result=subprocess.run([command,'--version'],capture_output=True,text=True,check=True)
        version=version_from_output(command,result.stdout+'\n'+result.stderr)
        expected='.'.join(map(str,minimum))
        if version is None:raise SystemExit(f'Não foi possível identificar a versão de {command}; requer >= {expected}')
        detected='.'.join(map(str,version))
        if version<minimum:raise SystemExit(f'{command} {detected} instalado; requer >= {expected}')
        print(command,detected,'OK')
if __name__=='__main__':main()

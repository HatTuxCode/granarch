#!/usr/bin/env python3
import re,subprocess
for command,minimum in [('Hyprland',(0,57,1)),('noctalia',(5,4,1))]:
    result=subprocess.run([command,'--version'],capture_output=True,text=True,check=True)
    found=re.search(r'\b(\d+)\.(\d+)\.(\d+)\b',result.stdout+result.stderr)
    if found is None or tuple(map(int,found.groups()))<minimum:
        raise SystemExit(f'{command} requer versão >= '+'.'.join(map(str,minimum)))
    print(command,found.group(), 'OK')

"""Preserve upstream Breeze folder geometry, with a muted Nord green-gray tint."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

TINT='#8fa89b'
def build(home,source=Path('/usr/share/icons/breeze')):
    if not source.is_dir(): raise FileNotFoundError('Instale breeze-icons')
    theme=Path(home)/'.local/share/icons/GranBreezeNord'
    directories=[]
    ET.register_namespace('','http://www.w3.org/2000/svg')
    for directory in sorted((source/'places').iterdir()):
        if not directory.is_dir(): continue
        output=theme/'places'/directory.name;output.mkdir(parents=True,exist_ok=True)
        directories.append('places/'+directory.name)
        for icon in directory.glob('folder*.svg'):
            root=ET.fromstring(icon.read_text())
            for element in root.iter():
                # Breeze's semantic accent controls the folder body; text/detail
                # colors, opacity, paths, gradients and silhouettes stay native.
                if 'ColorScheme-Accent' in element.get('class','').split():
                    style=element.get('style','')
                    style=re.sub(r'fill\s*:[^;]+',f'fill:{TINT}',style)
                    if 'fill:' not in style:style+=';fill:'+TINT
                    element.set('style',style)
            (output/icon.name).write_text(ET.tostring(root,encoding='unicode')+'\n')
    lines=['[Icon Theme]','Name=Gran Breeze Nord','Inherits=breeze,hicolor','Directories='+','.join(directories)]
    for directory in directories:
        size=directory.split('/')[-1];numeric=int(size) if size.isdigit() else 32
        lines+=['',f'[{directory}]','Context=Places',f'Size={numeric}','Type=Scalable','MinSize=8','MaxSize=256']
    (theme/'index.theme').write_text('\n'.join(lines)+'\n')
    return 'GranBreezeNord'

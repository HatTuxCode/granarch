"""Keep stock Breeze folders and recolor only action icons for dark surfaces."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

THEME_NAME='GranBreezeContrast'
def build(home,source=Path('/usr/share/icons/breeze'),foreground='#d8dee9'):
    if not source.is_dir():raise FileNotFoundError('Instale breeze-icons')
    if not re.fullmatch(r'#[0-9a-fA-F]{6}',foreground):raise ValueError('Cor de ícone inválida')
    theme=Path(home)/'.local/share/icons'/THEME_NAME;theme.mkdir(parents=True,exist_ok=True)
    directories=[];ET.register_namespace('','http://www.w3.org/2000/svg')
    action_root=source/'actions'
    if action_root.is_dir():
        for directory in sorted(action_root.iterdir()):
            if not directory.is_dir():continue
            relative='actions/'+directory.name
            output=theme/relative;output.mkdir(parents=True,exist_ok=True)
            directories.append(relative)
            for icon in directory.glob('*.svg'):
                try:root=ET.fromstring(icon.read_text())
                except (OSError,ET.ParseError):continue
                root.set('fill',foreground);root.set('color',foreground)
                def repaint(text):
                    def value(match):
                        color=match[2].strip()
                        return match[0] if color.lower() in ('none','transparent') or color.startswith('url(') else match[1]+':'+foreground
                    return re.sub(r'(?<![\w-])(fill|stroke|color)\s*:\s*([^;}]+)',value,text)
                for element in root.iter():
                    for attr in ('fill','stroke'):
                        value=element.get(attr)
                        if value and value.lower() not in ('none','transparent') and not value.startswith('url('):element.set(attr,foreground)
                    if element.get('style'):element.set('style',repaint(element.get('style')))
                    if element.tag.endswith('style') and element.text:element.text=repaint(element.text)
                (output/icon.name).write_text(ET.tostring(root,encoding='unicode')+'\n')
    lines=['[Icon Theme]','Name=Gran Breeze Contrast','Inherits=breeze,hicolor',
           'Directories='+','.join(d for d in directories if '@' not in d),
           'ScaledDirectories='+','.join(d for d in directories if '@' in d)]
    for directory in directories:
        size=directory.split('/')[-1]
        base,multiplier=size.split('@',1) if '@' in size else (size,'1x')
        numeric=int(base) if base.isdigit() else 24;scale=int(multiplier.rstrip('x'))
        lines+=['',f'[{directory}]','Context=Actions',f'Size={numeric}',f'Scale={scale}','Type=Fixed']
    (theme/'index.theme').write_text('\n'.join(lines)+'\n')
    return THEME_NAME

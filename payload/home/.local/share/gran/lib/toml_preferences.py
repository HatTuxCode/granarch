"""Round-trip TOML preferences using only Python's standard library."""
import json
import tomllib

WORKSPACE_SETTINGS = {
    'style':'regular', 'show_labels':True, 'label_source':'id',
    'labels_only_when_occupied':False, 'hide_when_empty':False,
    'show_all_outputs':True,
}


def dumps(data):
    def value(item):
        if isinstance(item,bool):return str(item).lower()
        if isinstance(item,str):return json.dumps(item,ensure_ascii=False)
        if isinstance(item,(int,float)):return str(item)
        if isinstance(item,list):return '['+', '.join(value(v) for v in item)+']'
        if isinstance(item,dict):return '{'+', '.join(json.dumps(k)+' = '+value(v) for k,v in item.items())+'}'
        return item.isoformat()
    def table(item,path=()):
        lines=['['+'.'.join(json.dumps(k) for k in path)+']'] if path else []
        for key,entry in item.items():
            if not isinstance(entry,dict):lines.append(json.dumps(key)+' = '+value(entry))
        for key,entry in item.items():
            if isinstance(entry,dict):lines.extend(['',*table(entry,(*path,key))])
        return lines
    result='\n'.join(table(data))+'\n'
    if tomllib.loads(result)!=data:raise ValueError('Preferences cannot be preserved as TOML')
    return result

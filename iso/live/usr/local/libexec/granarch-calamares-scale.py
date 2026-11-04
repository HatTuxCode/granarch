#!/usr/bin/env python3
"""Scale only the installer to keep navigation visible on small live displays."""
import json,sys

def factor(monitors):
    if not monitors:return 1.0
    monitor=next((m for m in monitors if m.get('focused')),monitors[0])
    width,height=monitor['width'],monitor['height']
    if monitor.get('transform',0) in (1,3,5,7):width,height=height,width
    left,top,right,bottom=monitor.get('reserved',[0,0,0,0])
    scale=monitor.get('scale',1)
    usable_width=width/scale-left-right-32
    usable_height=height/scale-top-bottom-32
    # Include page minimum sizes, sidebar, navigation and installation progress.
    return max(0.5,min(1.0,usable_width/1000,usable_height/720))
if __name__=='__main__':
    try:print(f'{factor(json.load(sys.stdin)):.3f}')
    except (ValueError,TypeError,KeyError,ZeroDivisionError):print('0.750')

"""Map the reference Nord colors to the native Noctalia v5.2+ palette format."""
import json
from pathlib import Path


def palette(colors):
    c = colors
    dark = {'mPrimary':c['accent'], 'mOnPrimary':c['background'], 'mSecondary':c['cyan'],
        'mOnSecondary':c['background'], 'mTertiary':c['magenta'], 'mOnTertiary':c['background'],
        'mError':c['red'], 'mOnError':c['background'], 'mSurface':c['background'],
        'mOnSurface':c['foreground'], 'mSurfaceVariant':c['lighter_background'],
        'mOnSurfaceVariant':c['light_foreground'], 'mOutline':c['selection'],
        'mShadow':c['darker_background'], 'mHover':c['selection'], 'mOnHover':c['foreground']}
    names = ('red','green','yellow','blue','magenta','cyan')
    dark['terminal'] = {'background':c['background'],'foreground':c['foreground'],'cursor':c['foreground'],
        'cursorText':c['background'],'selectionBg':c['selection'],'selectionFg':c['foreground'],
        'normal':{'black':c['dark_background'], **{n:c[n] for n in names}, 'white':c['foreground']},
        'bright':{'black':c['muted'], **{n:c['bright_'+n] for n in names}, 'white':c['bright_foreground']}}
    return {'dark':dark}

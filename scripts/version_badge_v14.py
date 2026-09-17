#!/usr/bin/env python3
from pathlib import Path

p=Path(__file__).resolve().parents[1]/'docs'/'index.html'
s=p.read_text(encoding='utf-8')
marker='calculator-version-v14'
if marker in s:
    print('Version badge already present')
    raise SystemExit(0)

css='''\n/* calculator-version-v14 */\n.calcVersionV14{display:block;margin-top:6px;text-align:center;font-size:11px;color:var(--muted);font-weight:700;letter-spacing:.03em;opacity:.82}\n'''
s=s.replace('</style>',css+'\n</style>',1)

# Place a discreet version label under the live/offline feed badge in the hero.
needle='<span class="badge" id="feedBadge">'
pos=s.find(needle)
if pos!=-1:
    end=s.find('</span>',pos)
    if end!=-1:
        end+=7
        s=s[:end]+'<span class="calcVersionV14">v14</span>'+s[end:]
else:
    print('Warning: feed badge anchor not found')

p.write_text(s,encoding='utf-8')
print('Applied small calculator version badge v14')

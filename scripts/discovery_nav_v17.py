#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
for name in ('index.html','fund-explorer.html','add-fund.html','fund-details.html'):
    p=ROOT/'docs'/name
    if not p.exists():
        continue
    s=p.read_text(encoding='utf-8')
    if 'discovery.html' in s:
        continue
    old='<a href="./add-fund.html">Add Fund</a>'
    active='<a class="active" href="./add-fund.html">Add Fund</a>'
    if active in s:
        s=s.replace(active,'<a href="./discovery.html">Discovery Inbox</a>'+active,1)
    elif old in s:
        s=s.replace(old,'<a href="./discovery.html">Discovery Inbox</a>'+old,1)
    else:
        print('Warning: nav anchor not found in',name)
        continue
    p.write_text(s,encoding='utf-8')
print('Applied Discovery Inbox navigation')

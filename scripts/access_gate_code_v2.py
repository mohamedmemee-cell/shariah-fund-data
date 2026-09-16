#!/usr/bin/env python3
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'docs'/'index.html'
s=p.read_text(encoding='utf-8')
NEW_HASH='aa7c871f00d3c85cdb3144ab9d9b2d8e24c88ca45b5d0ebf7682bfe89311f14a'
pattern=r"const ACCESS_HASH='[0-9a-f]{64}';"
replacement=f"const ACCESS_HASH='{NEW_HASH}';"
updated,n=re.subn(pattern,replacement,s,count=1)
if n==0:
    raise SystemExit('Calculator access gate hash was not found in docs/index.html')
if updated==s:
    print('Calculator access code hash already current')
else:
    p.write_text(updated,encoding='utf-8')
    print('Updated calculator access code hash')

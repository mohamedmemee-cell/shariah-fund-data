#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
manual_path=ROOT/'data'/'manual_values.json'
dir_path=ROOT/'docs'/'fund-directory.json'

manual=json.loads(manual_path.read_text(encoding='utf-8'))
directory=json.loads(dir_path.read_text(encoding='utf-8'))

# Old parser bug: a blank 10Y field could consume the following 2026 date.
# Remove that known bad value before docs/shariah-funds.json is regenerated.
mv=(manual.get('values') or {}).get('27four-shariah-balanced') or {}
if mv.get('tenYear') == 2026.0:
    mv['tenYear']=None

d=(directory.get('funds') or {}).get('27four-shariah-balanced') or {}
ver=d.get('verification') or {}
v=ver.get('tenYear')
if isinstance(v,dict) and v.get('value') == 2026.0:
    ver.pop('tenYear',None)

manual_path.write_text(json.dumps(manual,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
dir_path.write_text(json.dumps(directory,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Preflight data cleanup complete')

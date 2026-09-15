#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'docs'/'shariah-funds.json'
data=json.loads(path.read_text(encoding='utf-8'))
assert data.get('schema_version') == 1
assert isinstance(data.get('funds'), list) and data['funds']
ids=set()
for f in data['funds']:
    assert f['id'] not in ids, f"Duplicate id: {f['id']}"
    ids.add(f['id'])
    for k in ('oneYear','threeYear','fiveYear','tenYear','ter'):
        v=f.get(k)
        assert v is None or isinstance(v,(int,float)), f"{f['id']} {k} must be number/null"
print(f"Validated {len(data['funds'])} funds")

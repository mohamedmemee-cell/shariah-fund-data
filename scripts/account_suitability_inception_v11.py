#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'docs' / 'index.html'
DETAILS = ROOT / 'docs' / 'fund-details.html'
DIRECTORY = ROOT / 'docs' / 'fund-directory.json'

# Keep the original verified TFSA list as a fallback for funds whose directory
# account suitability has not yet been recorded. Add every fund explicitly
# verified as TFSA or Both in the directory.
legacy = {
    'satrix-msci-world-islamic-etf',
    'satrix-shariah-top-40-etf',
    'old-mutual-albaraka-balanced',
    'old-mutual-albaraka-equity',
    '27four-shariah-income',
    '27four-shariah-balanced',
}

try:
    directory = json.loads(DIRECTORY.read_text(encoding='utf-8'))
except Exception:
    directory = {'funds': {}}

for fund_id, info in (directory.get('funds') or {}).items():
    if str(info.get('account_suitability') or '').strip() in {'TFSA', 'Both'}:
        legacy.add(fund_id)

# --- Calculator: regenerate the TFSA-eligible set from verified directory data.
s = INDEX.read_text(encoding='utf-8')
ids = ','.join(repr(x) for x in sorted(legacy))
replacement = f"const TFSA_ELIGIBLE=new Set([{ids}]);"
s, count = re.subn(r"const TFSA_ELIGIBLE=new Set\(\[[^\]]*\]\);", replacement, s, count=1)
if count != 1:
    print('Warning: TFSA eligible set not found in calculator; no replacement made')
INDEX.write_text(s, encoding='utf-8')

# --- Fund details: account suitability is distinct from the default portfolio
# bucket. An active fund may legitimately be eligible for BOTH TFSA and ordinary
# investment accounts, so display the verified account suitability first.
d = DETAILS.read_text(encoding='utf-8')
old = "$('accountStatus').textContent=f.bucket==='Watchlist'?(d?.account_suitability||'Not confirmed'):(f.bucket||'—');"
new = "const accountSuitability=d?.account_suitability||(f.bucket==='Watchlist'?'Not confirmed':(f.bucket||'—'));$('accountStatus').textContent=accountSuitability==='Both'?'TFSA & Non-TFSA':accountSuitability;"
if old in d:
    d = d.replace(old, new, 1)

# Make the inception card use the verified directory field, with the verification
# record as a fallback. This avoids the top card lagging behind the verified list.
d = d.replace("v=x.inception_date;if(v){", "v=x.inception_date||x.verification?.inception_date?.value;if(v){", 1)

DETAILS.write_text(d, encoding='utf-8')
print('Applied account suitability and inception display V11')
print('TFSA-eligible fund ids:', ', '.join(sorted(legacy)))

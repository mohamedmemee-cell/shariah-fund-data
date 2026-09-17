#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'docs'/'index.html'
EXPLORER=ROOT/'docs'/'fund-explorer.html'

# --- Calculator version badge: previous v14 patch added CSS but missed the actual
# markup because the feed badge is a div, not a span. Insert a real label next to it.
s=INDEX.read_text(encoding='utf-8')
if 'id="calcVersionV15"' not in s:
    target='<div class="badge" id="feedBadge">Loading fund data…</div>'
    repl='<div><div class="badge" id="feedBadge">Loading fund data…</div><div id="calcVersionV15" class="calcVersionV14">v15</div></div>'
    if target in s:
        s=s.replace(target,repl,1)
    else:
        print('Warning: calculator feed badge markup not found')
else:
    s=s.replace('>v14<','>v15<')
INDEX.write_text(s,encoding='utf-8')

# --- Fund Explorer: account column must use verified account_suitability from the
# directory, not the portfolio bucket. This makes 'Both' show as TFSA & Non-TFSA.
e=EXPLORER.read_text(encoding='utf-8')
old="const $=id=>document.getElementById(id),pct=n=>n==null?'—':Number(n).toFixed(2)+'%';let feed={funds:[]};"
new="const $=id=>document.getElementById(id),pct=n=>n==null?'—':Number(n).toFixed(2)+'%';let feed={funds:[]},directory={funds:{}};function accountLabel(f){const d=(directory.funds||{})[f.id]||{},a=d.account_suitability;if(a==='Both')return'TFSA & Non-TFSA';if(a)return a;return f.bucket==='Watchlist'?'Not confirmed':(f.bucket||'—')}"
if old in e:
    e=e.replace(old,new,1)

e=e.replace("<td>${f.bucket==='Watchlist'?'Not confirmed':(f.bucket||'—')}</td>","<td>${accountLabel(f)}</td>",1)
oldload="async function load(){const r=await fetch('./shariah-funds.json?ts='+Date.now(),{cache:'no-store'});feed=await r.json();"
newload="async function load(){const [r,d]=await Promise.all([fetch('./shariah-funds.json?ts='+Date.now(),{cache:'no-store'}),fetch('./fund-directory.json?ts='+Date.now(),{cache:'no-store'})]);feed=await r.json();directory=await d.json();"
if oldload in e:
    e=e.replace(oldload,newload,1)
EXPLORER.write_text(e,encoding='utf-8')
print('Applied live sync fixes V15')

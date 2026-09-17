#!/usr/bin/env python3
"""Discover possible South African Shariah-compliant retail investments.

This is a DISCOVERY layer, not an approval engine. Search results are never added
straight to the Portfolio Builder. Every new item lands in a review inbox with
status ``needs_verification`` until a human verifies the official fund material.

The script deliberately uses a no-key Bing RSS search endpoint so the scheduled
GitHub Action can run without storing API credentials. If a search engine blocks
or changes its endpoint, the run fails soft and keeps the previous discovery set.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "discovery_candidates.json"
DOC_JSON = ROOT / "docs" / "discovery.json"
DOC_HTML = ROOT / "docs" / "discovery.html"
FEED = ROOT / "docs" / "shariah-funds.json"
DIRECTORY = ROOT / "docs" / "fund-directory.json"

SEARCH_QUERIES = [
    'Shariah fund South Africa investment',
    'Shariah compliant unit trust South Africa',
    'Islamic unit trust South Africa fund',
    'Shariah ETF South Africa',
    'Islamic ETF South Africa investment',
    'Shariah balanced fund South Africa',
    'Shariah income fund South Africa',
    'Shariah equity fund South Africa',
    'Islamic balanced fund South Africa',
    'Islamic income fund South Africa',
    'Shariah fund factsheet South Africa pdf',
    'site:za Shariah investment fund South Africa',
]

# Manager/administrator domains that are useful signals, not automatic approval.
OFFICIAL_HINTS = {
    'satrix.co.za','27four.com','camissa-am.com','albaraka.co.za','oldmutual.co.za',
    'oasiscrescent.com','stanlib.com','sygnia.co.za','sanlam.co.za','momentum.co.za',
    'ninetyone.com','coronation.com','nedgroupinvestments.com','absa.co.za','fnb.co.za',
    'standardbank.co.za','ashburtoninvestments.com','prescient.co.za','asisa.org.za',
}

DISCOVERY_TERMS = ('shariah','shari\'ah','sharia','islamic')
INVESTMENT_TERMS = ('fund','etf','unit trust','portfolio','investment','income','balanced','equity','sukuk')
EXCLUDE_DOMAINS = {'facebook.com','instagram.com','youtube.com','x.com','twitter.com','linkedin.com','tiktok.com'}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; ShariahFundDiscovery/1.0; +https://github.com/)'
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')


def norm_text(s: str) -> str:
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))
    return re.sub(r'\s+', ' ', s).strip()


def domain(url: str) -> str:
    d = (urlparse(url).hostname or '').lower()
    return d[4:] if d.startswith('www.') else d


def looks_relevant(title: str, snippet: str, url: str) -> bool:
    text = f'{title} {snippet} {url}'.lower()
    return any(t in text for t in DISCOVERY_TERMS) and any(t in text for t in INVESTMENT_TERMS)


def confidence(title: str, snippet: str, url: str) -> tuple[int, list[str]]:
    text = f'{title} {snippet}'.lower()
    d = domain(url)
    score = 0
    reasons = []
    if any(d == x or d.endswith('.'+x) for x in OFFICIAL_HINTS):
        score += 45; reasons.append('official/known investment-domain signal')
    if url.lower().endswith('.pdf') or 'factsheet' in text or 'fact sheet' in text:
        score += 20; reasons.append('factsheet/document signal')
    if 'shariah' in text or "shari'ah" in text or 'sharia' in text:
        score += 20; reasons.append('explicit Shariah wording')
    elif 'islamic' in text:
        score += 14; reasons.append('Islamic wording')
    if 'south africa' in text or '.co.za' in d or d.endswith('.za'):
        score += 10; reasons.append('South Africa signal')
    if any(x in text for x in ('fund','etf','unit trust','portfolio')):
        score += 5; reasons.append('investment-product signal')
    return min(score,100), reasons


def search_bing_rss(query: str) -> list[dict]:
    url = 'https://www.bing.com/search?format=rss&q=' + urllib.parse.quote_plus(query)
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    out = []
    for item in root.findall('.//item'):
        title = norm_text(item.findtext('title') or '')
        link = norm_text(item.findtext('link') or '')
        desc = norm_text(item.findtext('description') or '')
        if link:
            out.append({'title': title, 'url': link, 'snippet': desc, 'query': query})
    return out


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default


def existing_catalog() -> tuple[set[str], set[str]]:
    feed = load_json(FEED, {'funds': []})
    directory = load_json(DIRECTORY, {'funds': {}})
    names = set()
    urls = set()
    for f in feed.get('funds', []):
        names.add(re.sub(r'\W+',' ',str(f.get('name','')).lower()).strip())
        for k in ('source_url','data_source_url'):
            if f.get(k): urls.add(str(f[k]).split('#')[0].rstrip('/'))
    for info in (directory.get('funds') or {}).values():
        for k in ('website','manager_website','shariah_source'):
            if info.get(k): urls.add(str(info[k]).split('#')[0].rstrip('/'))
    return names, urls


def candidate_key(title: str, url: str) -> str:
    raw = (domain(url) + '|' + re.sub(r'\W+',' ',title.lower()).strip()).encode()
    return hashlib.sha1(raw).hexdigest()[:16]


def infer_manager(title: str, url: str) -> str:
    d = domain(url)
    mapping = {
        'satrix.co.za':'Satrix','27four.com':'27four','camissa-am.com':'Camissa',
        'albaraka.co.za':'Al Baraka','oldmutual.co.za':'Old Mutual','oasiscrescent.com':'Oasis',
        'stanlib.com':'STANLIB','sygnia.co.za':'Sygnia','sanlam.co.za':'Sanlam',
        'ashburtoninvestments.com':'Ashburton Investments','prescient.co.za':'Prescient',
    }
    for host, name in mapping.items():
        if d == host or d.endswith('.'+host): return name
    return d.split('.')[0].replace('-',' ').title() if d else 'Unknown'


def render_page(payload: dict) -> str:
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Shariah Investment Discovery</title><style>
:root{color-scheme:light dark;--bg:#f4f7f7;--card:#fff;--text:#172022;--muted:#667276;--line:#d8e1e2;--accent:#16715d;--soft:#e7f3ef;--warn:#a86200}*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,Segoe UI,Arial,sans-serif;background:var(--bg);color:var(--text)}main{max-width:1200px;margin:auto;padding:26px 18px 60px}.nav{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}.nav a{padding:9px 12px;border:1px solid var(--line);border-radius:10px;color:var(--text);text-decoration:none;font-weight:750}.nav a.active,.nav a:hover{background:var(--soft);color:var(--accent)}.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px;margin-bottom:14px}.muted{color:var(--muted)}.filters{display:grid;grid-template-columns:2fr 1fr 1fr;gap:10px}.filters input,.filters select{padding:10px;border:1px solid var(--line);border-radius:9px;background:transparent;color:inherit}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.stat{padding:12px;background:var(--soft);border-radius:12px}.stat small{display:block;color:var(--muted)}.stat b{font-size:22px}.table{overflow:auto}table{border-collapse:collapse;width:100%;min-width:1000px}th,td{padding:10px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}a{color:var(--accent)}.pill{display:inline-block;padding:3px 7px;border-radius:999px;background:var(--soft);font-size:11px;font-weight:700}.score{font-weight:800}.warn{color:var(--warn)}@media(max-width:760px){.filters,.stats{grid-template-columns:1fr}.nav{gap:5px}}@media(prefers-color-scheme:dark){:root{--bg:#101718;--card:#182123;--text:#edf3f1;--muted:#9eacab;--line:#334044;--accent:#66d1b5;--soft:#203532}}
</style></head><body><main><nav class="nav"><a href="./">Calculator</a><a href="./fund-explorer.html">Fund Explorer</a><a class="active" href="./discovery.html">Discovery Inbox</a><a href="./add-fund.html">Add Fund</a></nav><section class="card"><h1 style="margin-top:0">Shariah Investment Discovery</h1><p class="muted">Automated web discovery for possible South African Shariah-compliant retail investments. <b>Discovery is not verification.</b> Nothing on this page enters the Portfolio Builder until its Shariah status and product details are verified from reliable official material.</p><div class="stats"><div class="stat"><small>Candidates</small><b id="count">—</b></div><div class="stat"><small>New / review</small><b id="review">—</b></div><div class="stat"><small>Already tracked</small><b id="tracked">—</b></div><div class="stat"><small>Last scan</small><b id="scan" style="font-size:14px">—</b></div></div></section><section class="card"><div class="filters"><input id="q" placeholder="Search candidate or manager"><select id="status"><option value="">All statuses</option><option value="needs_verification">Needs verification</option><option value="already_tracked">Already tracked</option><option value="rejected">Rejected</option></select><select id="confidence"><option value="0">Any confidence</option><option value="50">50+ confidence</option><option value="70">70+ confidence</option></select></div></section><section class="card table"><table><thead><tr><th>Candidate</th><th>Manager</th><th>Status</th><th>Confidence</th><th>Why found</th><th>Search source</th></tr></thead><tbody id="rows"><tr><td colspan="6">Loading…</td></tr></tbody></table></section><section class="card"><h2 style="margin-top:0">How to use this inbox</h2><p class="muted">Open a candidate, verify the official fund page/factsheet and Shariah certificate or governance source, then add it through <b>Add Fund</b>. The existing verification workflow remains the gate before a product becomes Active.</p></section><script>
const $=id=>document.getElementById(id);let data={candidates:[]};function esc(s){return String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]))}function render(){const q=$('q').value.toLowerCase(),st=$('status').value,min=+$('confidence').value;let a=data.candidates.filter(x=>(!q||(x.title+' '+x.manager+' '+x.domain).toLowerCase().includes(q))&&(!st||x.status===st)&&Number(x.confidence||0)>=min);a.sort((x,y)=>Number(y.confidence||0)-Number(x.confidence||0));$('rows').innerHTML=a.length?a.map(x=>`<tr><td><a href="${esc(x.url)}" target="_blank" rel="noopener noreferrer"><b>${esc(x.title)}</b></a><br><small class="muted">${esc(x.domain)}</small></td><td>${esc(x.manager)}</td><td><span class="pill">${esc((x.status||'').replaceAll('_',' '))}</span></td><td class="score">${Number(x.confidence||0)}%</td><td>${esc((x.reasons||[]).join(' · '))}</td><td><small>${esc(x.query||'')}</small></td></tr>`).join(''):'<tr><td colspan="6">No candidates match these filters.</td></tr>';const all=data.candidates;$('count').textContent=all.length;$('review').textContent=all.filter(x=>x.status==='needs_verification').length;$('tracked').textContent=all.filter(x=>x.status==='already_tracked').length;$('scan').textContent=data.generated_at||'—'}async function load(){try{data=await (await fetch('./discovery.json?ts='+Date.now(),{cache:'no-store'})).json();render()}catch(e){$('rows').innerHTML='<tr><td colspan="6" class="warn">Discovery data is not available yet. Run the Discovery workflow in GitHub Actions.</td></tr>'}}['q','status','confidence'].forEach(id=>$(id).addEventListener('input',render));load();
</script></main></body></html>'''


def patch_nav_files():
    for name in ('index.html','fund-explorer.html','add-fund.html','fund-details.html'):
        p = ROOT / 'docs' / name
        if not p.exists(): continue
        s = p.read_text(encoding='utf-8')
        if 'discovery.html' in s: continue
        # Cover both nav class variants used by the site.
        s2 = s.replace('<a href="./add-fund.html">Add Fund</a>', '<a href="./discovery.html">Discovery Inbox</a><a href="./add-fund.html">Add Fund</a>', 1)
        s2 = s2.replace('<a class="active" href="./add-fund.html">Add Fund</a>', '<a href="./discovery.html">Discovery Inbox</a><a class="active" href="./add-fund.html">Add Fund</a>', 1)
        if s2 != s: p.write_text(s2, encoding='utf-8')


def main():
    previous = load_json(DATA, {'candidates': []})
    previous_by_url = {c.get('url'): c for c in previous.get('candidates', []) if c.get('url')}
    catalog_names, catalog_urls = existing_catalog()
    raw = []
    errors = []
    for q in SEARCH_QUERIES:
        try:
            raw.extend(search_bing_rss(q))
        except Exception as e:
            errors.append(f'{q}: {type(e).__name__}: {e}')
        time.sleep(0.35)

    by_url = {}
    for r in raw:
        url = (r.get('url') or '').split('#')[0].strip()
        d = domain(url)
        if not url.startswith(('http://','https://')) or d in EXCLUDE_DOMAINS: continue
        title, snippet = norm_text(r.get('title','')), norm_text(r.get('snippet',''))
        if not looks_relevant(title, snippet, url): continue
        score, reasons = confidence(title, snippet, url)
        if score < 30: continue
        existing = previous_by_url.get(url, {})
        norm_name = re.sub(r'\W+',' ',title.lower()).strip()
        already = url.rstrip('/') in catalog_urls or any(n and (n in norm_name or norm_name in n) for n in catalog_names if len(n)>12)
        status = 'already_tracked' if already else existing.get('status','needs_verification')
        if status not in {'needs_verification','already_tracked','rejected','verified'}:
            status = 'needs_verification'
        c = {
            'id': existing.get('id') or candidate_key(title,url),
            'title': title,
            'manager': infer_manager(title,url),
            'url': url,
            'domain': d,
            'snippet': snippet[:700],
            'status': status,
            'confidence': score,
            'reasons': reasons,
            'query': r.get('query',''),
            'first_seen': existing.get('first_seen') or now_iso(),
            'last_seen': now_iso(),
        }
        old = by_url.get(url)
        if not old or c['confidence'] > old['confidence']:
            by_url[url] = c

    # Preserve reviewed/rejected older items even when a search engine omits them this week.
    for url, old in previous_by_url.items():
        if url not in by_url and old.get('status') in {'rejected','verified','needs_verification'}:
            kept = dict(old); kept['not_seen_in_latest_scan'] = True; by_url[url] = kept

    candidates = sorted(by_url.values(), key=lambda x: (-int(x.get('confidence',0)), x.get('title','').lower()))
    payload = {
        'schema_version': 1,
        'generated_at': now_iso(),
        'search_engine': 'Bing RSS (no API key)',
        'scope': 'Publicly discoverable South African Shariah/Islamic retail investment products',
        'disclaimer': 'Discovery candidates are not verified or approved for the Portfolio Builder until reliable official evidence is reviewed.',
        'queries': SEARCH_QUERIES,
        'errors': errors,
        'candidates': candidates,
    }
    DATA.parent.mkdir(parents=True, exist_ok=True); DOC_JSON.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False) + '\n'
    DATA.write_text(text, encoding='utf-8'); DOC_JSON.write_text(text, encoding='utf-8')
    DOC_HTML.write_text(render_page(payload), encoding='utf-8')
    patch_nav_files()
    print(f'Discovery complete: {len(candidates)} candidates; {len(errors)} search errors')
    for e in errors: print('WARNING', e)

if __name__ == '__main__':
    main()

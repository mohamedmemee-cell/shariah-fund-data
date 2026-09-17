#!/usr/bin/env python3
"""Run one user-requested Shariah investment discovery search.

Inputs are supplied by the issue-trigger workflow through SEARCH_FOR and SEARCH_TOKEN.
Results are merged into the existing Discovery Inbox but remain needs_verification.
A token-specific result file lets the static GitHub Pages UI report either matches
or the explicit message: No Investment Opportunities Found.
"""
from __future__ import annotations

import json, os, re, hashlib, urllib.parse
from pathlib import Path
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
import discover_sharia_investments as d

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'discovery_candidates.json'
DOC_JSON = ROOT / 'docs' / 'discovery.json'
RESULT_DIR = ROOT / 'docs' / 'manual-search-results'
RESULT_DIR.mkdir(parents=True, exist_ok=True)

search_for = (os.environ.get('SEARCH_FOR') or '').strip()
token = re.sub(r'[^A-Za-z0-9_-]', '', os.environ.get('SEARCH_TOKEN') or '')[:80]
if not search_for or not token:
    raise SystemExit('SEARCH_FOR and SEARCH_TOKEN are required')


def load(path, default):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return default


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def is_url(s):
    try:
        u = urlparse(s if '://' in s else 'https://' + s)
        return bool(u.hostname and '.' in u.hostname)
    except Exception:
        return False


def normalized_url(s):
    if '://' not in s: s = 'https://' + s
    return s


def page_candidates(url):
    out=[]
    try:
        r=requests.get(url,headers=d.HEADERS,timeout=25)
        r.raise_for_status()
        soup=BeautifulSoup(r.text,'html.parser')
        title=d.norm_text(soup.title.get_text(' ',strip=True) if soup.title else url)
        text=d.norm_text(soup.get_text(' ',strip=True))[:4000]
        if d.looks_relevant(title,text,url):
            out.append({'title':title,'url':url,'snippet':text[:700],'query':f'manual website: {url}'})
        for a in soup.find_all('a',href=True):
            href=urljoin(url,a.get('href'))
            label=d.norm_text(a.get_text(' ',strip=True))
            probe=f'{label} {href}'
            if any(x in probe.lower() for x in d.DISCOVERY_TERMS) and any(x in probe.lower() for x in d.INVESTMENT_TERMS):
                out.append({'title':label or href,'url':href,'snippet':f'Discovered from {url}','query':f'manual website: {url}'})
    except Exception:
        pass
    return out

raw=[]
queries=[]
if is_url(search_for):
    url=normalized_url(search_for)
    raw.extend(page_candidates(url))
    host=d.domain(url)
    queries=[f'site:{host} Shariah investment fund',f'site:{host} Islamic investment fund']
else:
    # Preserve the user's wording, then add South Africa/Shariah context where useful.
    queries=[search_for]
    low=search_for.lower()
    if not any(x in low for x in ('sharia','islamic')):
        queries.append(f'{search_for} Shariah investment South Africa')
    if 'south africa' not in low:
        queries.append(f'{search_for} South Africa')

errors=[]
for q in queries:
    try: raw.extend(d.search_bing_rss(q))
    except Exception as e: errors.append(f'{q}: {type(e).__name__}: {e}')

previous=load(DATA,{'candidates':[]})
prev_by_url={x.get('url'):x for x in previous.get('candidates',[]) if x.get('url')}
catalog_names,catalog_urls=d.existing_catalog()
new_or_matched=[]
seen=set()
for r in raw:
    url=(r.get('url') or '').split('#')[0].strip()
    if not url.startswith(('http://','https://')) or url in seen: continue
    seen.add(url)
    dom=d.domain(url)
    if dom in d.EXCLUDE_DOMAINS: continue
    title=d.norm_text(r.get('title',''))
    snippet=d.norm_text(r.get('snippet',''))
    if not d.looks_relevant(title,snippet,url): continue
    score,reasons=d.confidence(title,snippet,url)
    if score < 30: continue
    norm_name=re.sub(r'\W+',' ',title.lower()).strip()
    status='already_tracked' if (url.rstrip('/') in catalog_urls or norm_name in catalog_names) else 'needs_verification'
    old=prev_by_url.get(url,{})
    row={
        'id': old.get('id') or d.candidate_key(title,url),
        'title': title,
        'manager': old.get('manager') or d.infer_manager(title,url),
        'url': url,
        'domain': dom,
        'snippet': snippet[:900],
        'status': old.get('status') if old.get('status') in ('rejected','verified') else status,
        'confidence': max(int(old.get('confidence') or 0),score),
        'reasons': reasons,
        'query': f'manual search: {search_for}',
        'first_seen': old.get('first_seen') or d.now_iso(),
        'last_seen': d.now_iso(),
        'manual_search_token': token,
    }
    prev_by_url[url]=row
    new_or_matched.append(row)

all_rows=list(prev_by_url.values())
all_rows.sort(key=lambda x:(x.get('status')=='already_tracked',-int(x.get('confidence') or 0),x.get('title','').lower()))
payload=load(DOC_JSON,{})
payload.update({
    'schema_version':1,
    'generated_at':d.now_iso(),
    'search_engine':'Bing RSS + direct website inspection (manual request)',
    'scope':'Publicly discoverable South African Shariah/Islamic retail investment products',
    'disclaimer':'Discovery candidates are not verified or approved for the Portfolio Builder until reliable official evidence is reviewed.',
    'candidates':all_rows,
})
previous['generated_at']=payload['generated_at']
previous['candidates']=all_rows
save(DATA,previous)
save(DOC_JSON,payload)

result={
    'token':token,
    'search_for':search_for,
    'completed_at':d.now_iso(),
    'count':len(new_or_matched),
    'candidate_ids':[x['id'] for x in new_or_matched],
    'message':f'{len(new_or_matched)} investment opportunit' + ('y found.' if len(new_or_matched)==1 else 'ies found.') if new_or_matched else 'No Investment Opportunities Found',
    'errors':errors,
}
save(RESULT_DIR / f'{token}.json',result)
print(result['message'])

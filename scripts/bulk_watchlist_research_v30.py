#!/usr/bin/env python3
import io, json, re, time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
SOURCES=ROOT/'sources'/'funds.json'
FEED=ROOT/'docs'/'shariah-funds.json'
DIRECTORY=ROOT/'docs'/'fund-directory.json'
REPORT=ROOT/'docs'/'bulk-research.json'
TODAY=str(date.today())
UA={'User-Agent':'Mozilla/5.0 (compatible; ShariahFundResearch/1.0; +https://github.com/mohamedmemee-cell/shariah-fund-data)'}
TIMEOUT=15

# Official manager domains only. Search/discovery is restricted to these sites; no
# third-party blogs or comparison sites are used to auto-verify fund information.
MANAGER_SITES={
 '27four':['https://27four.com/'],
 'alexander forbes investments':['https://invest.alexforbes.com/'],
 'camissa':['https://www.camissa-am.com/'],
 'element investment managers':['https://elementim.co.za/'],
 'foord':['https://www.foord.co.za/'],
 'momentum investments':['https://www.momentum.co.za/'],
 'oasis':['https://www.oasiscrescent.com/'],
 'old mutual investment group':['https://www.oldmutualinvest.com/','https://www.oldmutual.co.za/'],
 'old mutual / al baraka':['https://www.albaraka.co.za/','https://www.oldmutual.co.za/'],
 'sanlam multi-managers':['https://www.sanlaminvestments.com/'],
 'stanlib multi-manager':['https://www.stanlib.com/'],
 'stanlib':['https://www.stanlib.com/'],
 'sentio capital':['https://sentio-capital.com/'],
 'mazi asset management':['https://mazi.co.za/'],
 'mianzo asset management':['https://mianzo.co.za/'],
 'visio fund management':['https://visiofund.co.za/'],
 'wealthvest asset management':['https://wealthvest.co.za/'],
}

def norm(s):
    s=(s or '').lower().replace('’',"'")
    s=re.sub(r"shari['’]?ah",'shariah',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def tokens(s):
    stop={'fund','portfolio','shariah','islamic','the','of','fof','sci','bci','27four'}
    return [x for x in norm(s).split() if len(x)>2 and x not in stop]

def get(url, binary=False):
    try:
        r=requests.get(url,headers=UA,timeout=TIMEOUT,allow_redirects=True)
        if r.status_code>=400:return None
        return r.content if binary else r.text
    except Exception:return None

def sitemap_urls(base):
    out=[]; seen=set()
    seeds=[urljoin(base,'sitemap.xml'),urljoin(base,'sitemap_index.xml')]
    for seed in seeds:
        txt=get(seed)
        if not txt: continue
        for loc in re.findall(r'<loc>\s*(.*?)\s*</loc>',txt,re.I|re.S):
            loc=loc.strip()
            if loc in seen: continue
            seen.add(loc)
            if loc.lower().endswith('.xml') and len(seen)<80:
                sub=get(loc)
                if sub:
                    for x in re.findall(r'<loc>\s*(.*?)\s*</loc>',sub,re.I|re.S):
                        x=x.strip()
                        if x not in seen:
                            seen.add(x);out.append(x)
            else: out.append(loc)
        if out: break
    return out[:7000]

def score_url(url,name):
    u=norm(url); ts=tokens(name)
    if not ts:return 0
    hit=sum(1 for t in ts if t in u)
    phrase=norm(name).replace(' ','-') in url.lower()
    bonus=3 if any(k in u for k in ['fund','factsheet','fact sheet','mdd','minimum disclosure']) else 0
    return hit*3+bonus+(5 if phrase else 0)

def extract_pdf(data):
    try:
        rd=PdfReader(io.BytesIO(data));return '\n'.join((p.extract_text() or '') for p in rd.pages[:25])[:250000]
    except Exception:return ''

def html_text_and_links(url):
    txt=get(url)
    if not txt:return '',[]
    soup=BeautifulSoup(txt,'html.parser')
    text=' '.join(soup.stripped_strings)
    links=[]
    for a in soup.find_all('a',href=True):
        h=urljoin(url,a['href'])
        label=' '.join(a.stripped_strings)
        if '.pdf' in h.lower() or any(k in norm(label) for k in ['factsheet','fact sheet','mdd','minimum disclosure','shariah certificate']):
            links.append(h)
    return text[:250000],links[:40]

def candidate_sources(f):
    name=f.get('name',''); manager=norm(f.get('manager','')); current=f.get('source_url') or ''
    urls=[]
    # Keep an already-official non-Alexforbes source first.
    if current and 'alexforbes.com/za/en/surveys' not in current: urls.append(current)
    sites=[]
    for key,bases in MANAGER_SITES.items():
        if key in manager or manager in key: sites.extend(bases)
    for base in sites:
        sm=sitemap_urls(base)
        ranked=sorted(((score_url(u,name),u) for u in sm),reverse=True)
        urls.extend(u for sc,u in ranked[:8] if sc>=6)
    # De-duplicate, official-domain constrained.
    seen=set();result=[]
    allowed={urlparse(x).netloc.replace('www.','') for x in sites}
    if current: allowed.add(urlparse(current).netloc.replace('www.',''))
    for u in urls:
        host=urlparse(u).netloc.replace('www.','')
        if u not in seen and (not allowed or any(host==a or host.endswith('.'+a) for a in allowed)):
            seen.add(u);result.append(u)
    return result[:10]

def nearby_number(text,labels,percent=False):
    clean=re.sub(r'\s+',' ',text)
    for label in labels:
        # value after label, within a short evidence window
        p=rf'(?i)\b{label}\b[^0-9R%]{{0,80}}(?:R\s*)?([0-9][0-9 ,.]*)\s*({"%" if percent else ""})'
        m=re.search(p,clean)
        if m:
            raw=m.group(1).replace(' ','').replace(',','')
            try:return float(raw)
            except:pass
    return None

def extract_fields(text):
    t=re.sub(r'\s+',' ',text)
    low=t.lower()
    out={}
    ter=nearby_number(t,[r'TER',r'total expense ratio'],True)
    if ter is not None and 0<=ter<=10: out['ter']=round(ter,4)
    minimum=nearby_number(t,[r'minimum monthly investment',r'minimum recurring investment',r'minimum investment',r'monthly debit order'],False)
    if minimum is not None and 0<minimum<10000000: out['minimum_investment']=str(int(minimum))
    # Require explicit tax-free wording before concluding TFSA eligibility.
    if re.search(r'(?i)\b(TFSA|tax[- ]free savings account|tax free investment)\b',t): out['account_suitability']='Both'
    # Risk must be explicitly labelled close to the value.
    rm=re.search(r'(?i)(?:risk profile|risk rating|risk classification|risk level)\s*[:\-]?\s*(low[- ]?medium|low[- ]?moderate|moderate[- ]?high|medium[- ]?high|moderate|medium|low|high|aggressive|conservative)',t)
    if rm: out['risk_level']=rm.group(1).title().replace('Medium High','Medium-High').replace('Moderate High','Moderate-High').replace('Low Medium','Low-Medium').replace('Low Moderate','Low-Moderate')
    dm=re.search(r'(?i)(?:inception date|fund inception|launch date)\s*[:\-]?\s*([0-3]?\d[ /.-](?:[01]?\d|[A-Za-z]{3,9})[ /.-](?:19|20)\d{2}|(?:19|20)\d{2}[ /.-][01]?\d[ /.-][0-3]?\d)',t)
    if dm: out['inception_date']=dm.group(1).strip()
    # Governance evidence: only accept explicit board/committee/adviser wording on official material.
    gov=bool(re.search(r'(?i)shari(?:a|ah)[ -](?:supervisory )?(?:board|committee|adviser|advisor)',t))
    compliant=bool(re.search(r'(?i)shari(?:a|ah)[ -]compliant',t))
    if gov: out['shariah_governance']=True
    elif compliant: out['shariah_compliant_statement']=True
    return out

def verification_set(d,key,value,source,note='Automatically extracted from official manager material.'):
    ver=d.setdefault('verification',{})
    # Never overwrite a manually verified value.
    existing=ver.get(key) or {}
    if existing.get('status')=='verified' and existing.get('method')=='manual': return False
    ver[key]={'status':'verified','method':'automatic','verification_method':'Official manager source','source':source,'verified_at':TODAY,'note':note,'value':value}
    return True

sources=json.loads(SOURCES.read_text(encoding='utf-8'))
feed=json.loads(FEED.read_text(encoding='utf-8')) if FEED.exists() else {'funds':[]}
directory=json.loads(DIRECTORY.read_text(encoding='utf-8')) if DIRECTORY.exists() else {'funds':{}}
feed_by={x.get('id'):x for x in feed.get('funds',[])}; dmap=directory.setdefault('funds',{})
report={'schema_version':1,'generated_at':TODAY,'researched':0,'official_source_found':0,'fields_verified':0,'funds':[]}

for f in sources.get('funds',[]):
    if f.get('bucket')!='Watchlist': continue
    report['researched']+=1
    rec={'id':f.get('id'),'name':f.get('name'),'manager':f.get('manager'),'status':'no_official_match','sources_checked':[],'verified_fields':[],'notes':[]}
    d=dmap.setdefault(f['id'],{})
    best_url=None; best_text=''; best_fields={}; best_score=-1
    for u in candidate_sources(f):
        rec['sources_checked'].append(u)
        if '.pdf' in u.lower():
            data=get(u,binary=True); text=extract_pdf(data) if data else '' ; extra=[]
        else:
            text,extra=html_text_and_links(u)
        corpus=text
        # Look at a few official linked PDFs too; factsheets usually carry the missing details.
        for pdf in extra[:5]:
            data=get(pdf,binary=True)
            if data:
                ptxt=extract_pdf(data)
                if ptxt: corpus+=' '+ptxt
        fields=extract_fields(corpus)
        name_hits=sum(1 for t in tokens(f.get('name')) if t in norm(corpus[:60000]))
        sc=name_hits*5+len(fields)*3
        if sc>best_score and name_hits>=1:
            best_score=sc;best_url=u;best_text=corpus;best_fields=fields
        time.sleep(.08)
    if not best_url:
        rec['notes'].append('No confident official manager page/factsheet match found automatically.')
        report['funds'].append(rec);continue
    report['official_source_found']+=1;rec['status']='official_source_found';rec['official_source']=best_url
    f['source_url']=best_url; d['website']=best_url
    ff=feed_by.get(f['id'])
    if ff: ff['source_url']=best_url
    # Apply only high-confidence, directly labelled fields.
    for key,val in best_fields.items():
        if key=='shariah_compliant_statement':
            rec['notes'].append('Official source states Shariah compliance, but governance/board evidence still needs confirmation.')
            continue
        if key=='shariah_governance':
            d['shariah_source']=best_url;d['board_status']='automatically verified from official manager material';
            if verification_set(d,'shariah_governance',True,best_url): rec['verified_fields'].append('shariah_governance')
            continue
        if key=='minimum_investment':
            d['minimum_investment']=val
            if verification_set(d,'minimum_investment',val,best_url): rec['verified_fields'].append(key)
        elif key=='account_suitability':
            d['account_suitability']=val
            if verification_set(d,'account_suitability',val,best_url): rec['verified_fields'].append(key)
        elif key=='risk_level':
            f['risk_level']=val
            if ff: ff['risk_level']=val
            if verification_set(d,'risk_level',val,best_url): rec['verified_fields'].append(key)
        elif key=='ter':
            if ff: ff['ter']=val
            if verification_set(d,'ter',val,best_url): rec['verified_fields'].append(key)
        elif key=='inception_date':
            d['inception_date']=val
            if verification_set(d,'inception_date',val,best_url): rec['verified_fields'].append(key)
    report['fields_verified']+=len(rec['verified_fields'])
    if rec['verified_fields']: rec['status']='partially_verified'
    report['funds'].append(rec)

sources['bulk_research_last_run']=TODAY
directory['updated_at']=TODAY
SOURCES.write_text(json.dumps(sources,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
FEED.write_text(json.dumps(feed,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
DIRECTORY.write_text(json.dumps(directory,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f"Bulk Watchlist research: {report['researched']} researched, {report['official_source_found']} official source matches, {report['fields_verified']} fields auto-verified.")

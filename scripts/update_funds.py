#!/usr/bin/env python3
import calendar, io, json, re
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
SOURCES=ROOT/'sources'/'funds.json'; MANUAL=ROOT/'data'/'manual_values.json'
OUTPUT=ROOT/'docs'/'shariah-funds.json'; HISTORY=ROOT/'data'/'history'
HEADERS={'User-Agent':'Mozilla/5.0 (compatible; ShariahFundDataBot/2.7; +GitHub Actions)','Accept':'text/html,application/pdf;q=0.9,*/*;q=0.8'}
MONTHS={m.lower():i for i,m in enumerate(calendar.month_name) if m}
MONTHS.update({m.lower():i for i,m in enumerate(calendar.month_abbr) if m})

def load_json(p): return json.loads(p.read_text(encoding='utf-8'))
def get(url):
    r=requests.get(url,headers=HEADERS,timeout=45,allow_redirects=True); r.raise_for_status(); return r

def pdf_text(url):
    r=get(url)
    if not r.content.startswith(b'%PDF'):
        ctype=r.headers.get('content-type','unknown')
        raise ValueError(f'Expected PDF but received {ctype} from {r.url}')
    reader=PdfReader(io.BytesIO(r.content)); return '\n'.join((p.extract_text() or '') for p in reader.pages)

def link_context(a):
    parts=[' '.join(a.stripped_strings)]; node=a
    for _ in range(3):
        node=node.parent
        if not node: break
        txt=' '.join(node.stripped_strings)
        if txt: parts.append(txt)
    return ' '.join(parts).lower()

def discover_pdf(page_url, required_terms=None, excluded_terms=None):
    soup=BeautifulSoup(get(page_url).text,'html.parser')
    required_terms=tuple(required_terms or []); excluded_terms=tuple(excluded_terms or [])
    candidates=[]
    for a in soup.find_all('a',href=True):
        href=urljoin(page_url,a['href'])
        if '.pdf' not in href.lower(): continue
        context=link_context(a)
        if excluded_terms and any(t in context or t in href.lower() for t in excluded_terms): continue
        score=0
        for term in required_terms:
            if term in context: score += 10
            if term.replace(' ','') in href.lower().replace('-','').replace('_','').replace('%20',''): score += 4
        if any(k in context for k in ('fact sheet','factsheet','fund fact','monthly','mdd','minimum disclosure')): score += 5
        if 'cdn.albaraka.co.za' in href.lower(): score += 2
        candidates.append((score,context,href))
    if not candidates: raise ValueError('No suitable PDF link found on fund page')
    candidates.sort(key=lambda x:x[0],reverse=True); best=candidates[0]
    if required_terms and best[0] < 10: raise ValueError('Could not identify the required fund factsheet link')
    return best[2]

def percentages(text): return [float(x) for x in re.findall(r'(-?\d+(?:\.\d+)?)\s*%',text)]
def labelled_percent(text,label):
    m=re.search(label+r'[^\d-]{0,100}(-?\d+(?:\.\d+)?)\s*%',text,re.I|re.S)
    return float(m.group(1)) if m else None

def token_value(token):
    token=(token or '').strip().upper()
    if token in ('N/A','NA','-','--'): return None
    negative=token.startswith('(') and token.endswith(')'); token=token.strip('()%')
    try:
        value=float(token); return -value if negative else value
    except ValueError: return None

def month_end(year,month): return f'{year:04d}-{month:02d}-{calendar.monthrange(year,month)[1]:02d}'

def extract_data_as_of(text,url=''):
    flat=re.sub(r'\s+',' ',text)
    patterns=[
        r'FUND\s+PERFORMANCE\s*\(%\)\s*AT\s+(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})',
        r'(?:performance\s+)?(?:as\s+at|at)\s+(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})']
    for pat in patterns:
        m=re.search(pat,flat,re.I)
        if m:
            month=MONTHS.get(m.group(2).lower())
            if month: return f'{int(m.group(3)):04d}-{month:02d}-{int(m.group(1)):02d}'
    # Camissa monthly factsheet filenames end in _YYMM.pdf, e.g. _2608.pdf.
    m=re.search(r'_(\d{2})(\d{2})\.pdf(?:\?|$)',url,re.I)
    if m:
        year=2000+int(m.group(1)); month=int(m.group(2))
        if 1<=month<=12: return month_end(year,month)
    # Albaraka factsheets use month names in filenames, e.g. FundJuly2026.pdf.
    m=re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)(20\d{2})\.pdf',url,re.I)
    if m:
        month=MONTHS[m.group(1).lower()]; return month_end(int(m.group(2)),month)
    return None

def satrix_values(text):
    flat=re.sub(r'\s+',' ',text)
    vals={'oneYear':None,'threeYear':None,'fiveYear':None,'tenYear':None,'sinceInception':None,'ter':None}
    period=r'(?:1-Year|3-Year|5-Year|10-Year|Inception)'
    value=r'(?:N/?A|NA|--|-|\(?-?\d+(?:\.\d+)?\)?)'
    matches=list(re.finditer(rf'((?:{period}\s+){{1,4}}{period})\s+Fund\s*\(%\)\s+((?:{value}\s+){{1,4}}{value})',flat,re.I))
    if not matches: raise ValueError('Could not identify Satrix Fund (%) performance row')
    m=matches[-1]; headers=re.findall(period,m.group(1),re.I); raw_values=re.findall(value,m.group(2),re.I)
    if len(headers)!=len(raw_values): raise ValueError('Satrix performance header/value count mismatch')
    key_map={'1-year':'oneYear','3-year':'threeYear','5-year':'fiveYear','10-year':'tenYear','inception':'sinceInception'}
    for header,raw in zip(headers,raw_values): vals[key_map[header.lower()]]=token_value(raw)
    ter=labelled_percent(flat,r'(?:total\s+expense\s+ratio\s*\(TER\)|total\s+expense\s+ratio|\bTER\b)')
    if ter is not None and 0<=ter<=5: vals['ter']=ter
    return vals

def old_mutual_albaraka_values(text):
    flat=re.sub(r'\s+',' ',text)
    m=re.search(r'Fund\s*\(Class\s*A\)[^\d-]{0,80}((-?\d+(?:\.\d+)?%\s*){3,6})',flat,re.I)
    if not m: m=re.search(r'1[-\s]*Yr\s+3[-\s]*Yr\s+5[-\s]*Yr\s+7[-\s]*Yr\s+10[-\s]*Yr[^%]{0,160}((?:-?\d+(?:\.\d+)?%\s*){5,6})',flat,re.I)
    if not m: raise ValueError('Could not identify Old Mutual Albaraka Class A performance row')
    nums=percentages(m.group(1))
    if len(nums)<3: raise ValueError('Incomplete Old Mutual Albaraka performance row')
    vals={'oneYear':nums[0],'threeYear':nums[1],'fiveYear':nums[2],'tenYear':nums[4] if len(nums)>=5 else None,'sinceInception':nums[5] if len(nums)>=6 else None,'ter':None}
    ter=labelled_percent(flat,r'(?:total\s+expense\s+ratio|\bTER\b)')
    if ter is not None and 0<=ter<=5: vals['ter']=ter
    return vals

def performance_values(text):
    flat=re.sub(r'\s+',' ',text)
    vals={'oneYear':labelled_percent(flat,r'(?:1\s*year|1[-\s]*yr|one\s*year)'),
          'threeYear':labelled_percent(flat,r'(?:3\s*year|3[-\s]*yr|three\s*year)'),
          'fiveYear':labelled_percent(flat,r'(?:5\s*year|5[-\s]*yr|five\s*year)'),
          'tenYear':labelled_percent(flat,r'(?:10\s*year|10[-\s]*yr|ten\s*year)'),
          'sinceInception':None,'ter':labelled_percent(flat,r'(?:total\s+expense\s+ratio|\bTER\b)')}
    if not any(vals[k] is not None for k in ('oneYear','threeYear','fiveYear')):
        for heading in ('Fund Performance','Performance (Annualised)','Performance','Annualised Performance'):
            p=flat.lower().find(heading.lower())
            if p>=0:
                nums=percentages(flat[p:p+1800])
                if len(nums)>=3:
                    vals['oneYear'],vals['threeYear'],vals['fiveYear']=nums[:3]
                    if len(nums)>=4: vals['tenYear']=nums[3]
                    break
    for k in ('oneYear','threeYear','fiveYear','tenYear'):
        v=vals[k]
        if v is not None and not -60<=v<=100: raise ValueError(f'{k} outside sanity bounds')
    if vals['ter'] is not None and not 0<=vals['ter']<=5: vals['ter']=None
    if not any(vals[k] is not None for k in ('oneYear','threeYear','fiveYear')): raise ValueError('Could not identify performance figures')
    return vals

def main():
    registry=load_json(SOURCES); manual=load_json(MANUAL); stored=manual.get('values',{})
    now=datetime.now(timezone.utc); generated=now.isoformat(timespec='seconds').replace('+00:00','Z'); output=[]
    for f in registry['funds']:
        base=dict(stored.get(f['id'],{})); status='manual'; error=None; resolved=f.get('factsheet_url') or f.get('source_url')
        try:
            typ=f.get('auto_type','manual'); text=None; auto={}
            if typ=='camissa_page_pdf':
                resolved=discover_pdf(f['source_url']); text=pdf_text(resolved); auto=performance_values(text); status='auto'
            elif typ=='page_pdf':
                resolved=discover_pdf(f['source_url']); text=pdf_text(resolved); auto=performance_values(text); status='auto'
            elif typ=='albaraka_page_pdf':
                resolved=discover_pdf(f['source_url'],required_terms=('fund fact','fact sheet','latest fund'),excluded_terms=('graduate','shariah certificate','proof of address'))
                text=pdf_text(resolved); auto=old_mutual_albaraka_values(text); status='auto'
            elif typ=='satrix_mdd':
                text=pdf_text(f['source_url']); auto=satrix_values(text); status='auto'; resolved=f['source_url']
            elif typ=='pdf_performance':
                text=pdf_text(f['factsheet_url']); auto=performance_values(text); status='auto'
            if text is not None:
                source_date=extract_data_as_of(text,resolved)
                if source_date: auto['dataAsOf']=source_date
            for k,v in auto.items():
                if v is not None: base[k]=v
        except Exception as exc:
            if f.get('auto_type')!='manual': status='fallback_manual'; error=str(exc)[:300]
        row={'id':f['id'],'name':f['name'],'manager':f['manager'],'category':f['category'],'bucket':f['bucket'],'suggested_split':f.get('suggested_split',0),'oneYear':base.get('oneYear'),'threeYear':base.get('threeYear'),'fiveYear':base.get('fiveYear'),'tenYear':base.get('tenYear'),'sinceInception':base.get('sinceInception'),'ter':base.get('ter'),'data_as_of':base.get('dataAsOf'),'risk_level':f.get('risk_level'),'source_url':f.get('source_url'),'data_source_url':resolved,'shariah_note':f.get('shariah_note'),'update_status':status,'updated':generated if status=='auto' else manual.get('as_of')}
        if error: row['update_error']=error
        output.append(row)
    feed={'schema_version':1,'generated_at':generated,'currency':'ZAR','disclaimer':'Public fund information for research/planning. Past performance is not a guarantee of future returns. Verify figures against official fund documents before investing.','funds':output}
    OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(json.dumps(feed,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    HISTORY.mkdir(parents=True,exist_ok=True); (HISTORY/f'{now.date().isoformat()}.json').write_text(json.dumps(feed,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Wrote {OUTPUT}')
    for x in output: print(f"{x['name']}: {x['update_status']} as_of={x.get('data_as_of')}" + (f" ({x.get('update_error')})" if x.get('update_error') else ''))
if __name__=='__main__': main()

#!/usr/bin/env python3
import io, json, re
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
SOURCES=ROOT/'sources'/'funds.json'; MANUAL=ROOT/'data'/'manual_values.json'
OUTPUT=ROOT/'docs'/'shariah-funds.json'; HISTORY=ROOT/'data'/'history'
HEADERS={'User-Agent':'Mozilla/5.0 (compatible; ShariahFundDataBot/2.2; +GitHub Actions)','Accept':'text/html,application/pdf;q=0.9,*/*;q=0.8'}

def load_json(p): return json.loads(p.read_text(encoding='utf-8'))
def get(url):
    r=requests.get(url,headers=HEADERS,timeout=45,allow_redirects=True); r.raise_for_status(); return r

def pdf_text(url):
    r=get(url)
    if not r.content.startswith(b'%PDF'):
        ctype=r.headers.get('content-type','unknown')
        raise ValueError(f'Expected PDF but received {ctype} from {r.url}')
    reader=PdfReader(io.BytesIO(r.content)); return '\n'.join((p.extract_text() or '') for p in reader.pages)

def discover_pdf(page_url):
    soup=BeautifulSoup(get(page_url).text,'html.parser')
    links=[]
    for a in soup.find_all('a',href=True):
        href=urljoin(page_url,a['href']); label=' '.join(a.stripped_strings).lower()
        context=' '.join(a.parent.stripped_strings).lower() if a.parent else label
        if '.pdf' in href.lower(): links.append((label+' '+context,href))
    if not links: raise ValueError('No PDF link found on fund page')
    preferred=[x for x in links if any(k in x[0] for k in ('fact','monthly','mdd','minimum disclosure'))]
    return (preferred or links)[0][1]

def percentages(text): return [float(x) for x in re.findall(r'(-?\d+(?:\.\d+)?)\s*%',text)]
def labelled_percent(text,label):
    m=re.search(label+r'[^\d-]{0,100}(-?\d+(?:\.\d+)?)\s*%',text,re.I|re.S)
    return float(m.group(1)) if m else None

def old_mutual_albaraka_values(text):
    flat=re.sub(r'\s+',' ',text)
    # Old Mutual Albaraka factsheets publish the retail Class A row in the order
    # 1Y, 3Y, 5Y, 7Y, 10Y, since inception. Use that explicit row instead of
    # generic heading/value proximity so benchmark figures cannot be mistaken for fund returns.
    m=re.search(r'Fund\s*\(Class\s*A\)[^\d-]{0,60}((-?\d+(?:\.\d+)?%\s*){3,6})',flat,re.I)
    if not m:
        # Some PDF text extractors omit the 'Fund (Class A)' label but keep the first
        # performance row immediately after the repeated 1-Yr/3-Yr/5-Yr headings.
        m=re.search(r'1[-\s]*Yr\s+3[-\s]*Yr\s+5[-\s]*Yr\s+7[-\s]*Yr\s+10[-\s]*Yr[^%]{0,120}((?:-?\d+(?:\.\d+)?%\s*){5,6})',flat,re.I)
    if not m: raise ValueError('Could not identify Old Mutual Albaraka Class A performance row')
    nums=percentages(m.group(1))
    if len(nums)<3: raise ValueError('Incomplete Old Mutual Albaraka performance row')
    vals={'oneYear':nums[0],'threeYear':nums[1],'fiveYear':nums[2],'tenYear':nums[4] if len(nums)>=5 else None,'ter':None}
    ter=labelled_percent(flat,r'(?:total\s+expense\s+ratio|\bTER\b)')
    if ter is not None and 0<=ter<=5: vals['ter']=ter
    return vals

def performance_values(text):
    flat=re.sub(r'\s+',' ',text)
    vals={
      'oneYear':labelled_percent(flat,r'(?:1\s*year|1[-\s]*yr|one\s*year)'),
      'threeYear':labelled_percent(flat,r'(?:3\s*year|3[-\s]*yr|three\s*year)'),
      'fiveYear':labelled_percent(flat,r'(?:5\s*year|5[-\s]*yr|five\s*year)'),
      'tenYear':labelled_percent(flat,r'(?:10\s*year|10[-\s]*yr|ten\s*year)'),
      'ter':labelled_percent(flat,r'(?:total\s+expense\s+ratio|\bTER\b)')}
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
            typ=f.get('auto_type','manual')
            if typ in ('camissa_page_pdf','page_pdf'):
                resolved=discover_pdf(f['source_url']); auto=performance_values(pdf_text(resolved)); status='auto'
            elif typ=='albaraka_page_pdf':
                resolved=discover_pdf(f['source_url']); auto=old_mutual_albaraka_values(pdf_text(resolved)); status='auto'
            elif typ=='pdf_performance':
                auto=performance_values(pdf_text(f['factsheet_url'])); status='auto'
            else: auto={}
            for k,v in auto.items():
                if v is not None: base[k]=v
        except Exception as exc:
            if f.get('auto_type')!='manual': status='fallback_manual'; error=str(exc)[:300]
        row={'id':f['id'],'name':f['name'],'manager':f['manager'],'category':f['category'],'bucket':f['bucket'],'suggested_split':f.get('suggested_split',0),'oneYear':base.get('oneYear'),'threeYear':base.get('threeYear'),'fiveYear':base.get('fiveYear'),'tenYear':base.get('tenYear'),'ter':base.get('ter'),'risk_level':f.get('risk_level'),'source_url':f.get('source_url'),'data_source_url':resolved,'shariah_note':f.get('shariah_note'),'update_status':status,'updated':generated if status=='auto' else manual.get('as_of')}
        if error: row['update_error']=error
        output.append(row)
    feed={'schema_version':1,'generated_at':generated,'currency':'ZAR','disclaimer':'Public fund information for research/planning. Past performance is not a guarantee of future returns. Verify figures against official fund documents before investing.','funds':output}
    OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(json.dumps(feed,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    HISTORY.mkdir(parents=True,exist_ok=True); (HISTORY/f'{now.date().isoformat()}.json').write_text(json.dumps(feed,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Wrote {OUTPUT}')
    for x in output: print(f"{x['name']}: {x['update_status']}" + (f" ({x.get('update_error')})" if x.get('update_error') else ''))
if __name__=='__main__': main()

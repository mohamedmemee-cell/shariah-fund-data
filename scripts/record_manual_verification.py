#!/usr/bin/env python3
import json, os, re
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVENT=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
issue=EVENT.get('issue') or {}
body=issue.get('body') or ''

def field(name):
    # Only read the current line. Using \s here could consume the following line
    # when a field is intentionally left blank.
    m=re.search(r'^'+re.escape(name)+r':[ \t]*([^\r\n]*)$',body,re.I|re.M)
    return (m.group(1).strip() if m else '')

def notes_field():
    m=re.search(r'^Notes:[ \t]*(.*)$',body,re.I|re.M|re.S)
    return (m.group(1).strip() if m else '')

def num(v):
    if not v:return None
    m=re.search(r'-?\d+(?:\.\d+)?',v.replace(',',''))
    return float(m.group(0)) if m else None

fund_id=field('Fund id')
if not fund_id: raise SystemExit('Missing Fund id')
method=field('Verification method') or 'Manual confirmation'
source=field('Source/contact') or 'User supplied verification'
verified_date=field('Verified date') or date.today().isoformat()
note=notes_field()

sources_path=ROOT/'sources'/'funds.json'
dir_path=ROOT/'docs'/'fund-directory.json'
manual_path=ROOT/'data'/'manual_values.json'
sources=json.loads(sources_path.read_text(encoding='utf-8'))
directory=json.loads(dir_path.read_text(encoding='utf-8'))
manual=json.loads(manual_path.read_text(encoding='utf-8'))
src=next((f for f in sources.get('funds',[]) if f.get('id')==fund_id),None)
if not src: raise SystemExit('Unknown fund id: '+fund_id)
d=directory.setdefault('funds',{}).setdefault(fund_id,{})
ver=d.setdefault('verification',{})

def provenance(field_name,value):
    ver[field_name]={
      'status':'verified',
      'method':'manual',
      'verification_method':method,
      'source':source,
      'verified_at':verified_date,
      'note':note,
      'value':value
    }

minimum=field('Minimum investment')
if minimum:
    d['minimum_investment']=minimum
    provenance('minimum_investment',minimum)

account=field('Account suitability')
if account:
    norm={'tfsa':'TFSA','non-tfsa':'Non-TFSA','non tfsa':'Non-TFSA','both':'Both'}.get(account.lower(),account)
    if norm not in ('TFSA','Non-TFSA','Both'):
        raise SystemExit('Account suitability must be TFSA, Non-TFSA or Both')
    d['account_suitability']=norm
    provenance('account_suitability',norm)

risk=field('Risk classification')
if risk:
    src['risk_level']=risk
    provenance('risk_level',risk)

inception=field('Inception date')
if inception:
    d['inception_date']=inception
    provenance('inception_date',inception)

ter=num(field('TER'))
if ter is not None:
    mv=manual.setdefault('values',{}).setdefault(fund_id,{})
    mv['ter']=ter
    mv.setdefault('dataAsOf',verified_date)
    provenance('ter',ter)

shariah=field('Shariah governance verified')
if shariah:
    yes=shariah.lower() in ('yes','true','verified','y')
    d['shariah_manually_verified']=yes
    provenance('shariah_governance','verified' if yes else 'not verified')

perf_map={'1Y return':'oneYear','3Y return':'threeYear','5Y return':'fiveYear','10Y return':'tenYear','Since inception return':'sinceInception'}
perf_date=field('Performance data as at') or verified_date
for label,key in perf_map.items():
    raw=field(label)
    v=num(raw)
    if v is not None:
        mv=manual.setdefault('values',{}).setdefault(fund_id,{})
        mv[key]=v
        mv['dataAsOf']=perf_date
        provenance(key,v)

manual['as_of']=date.today().isoformat()
directory['updated_at']=date.today().isoformat()
sources_path.write_text(json.dumps(sources,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
dir_path.write_text(json.dumps(directory,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
manual_path.write_text(json.dumps(manual,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Recorded manual verification for',fund_id)

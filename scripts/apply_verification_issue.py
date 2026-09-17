#!/usr/bin/env python3
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENT = Path(os.environ.get('GITHUB_EVENT_PATH',''))
DIRECTORY = ROOT/'docs'/'fund-directory.json'
MANUAL = ROOT/'data'/'manual_values.json'

if not EVENT.exists():
    raise SystemExit('No GitHub event payload')
ev = json.loads(EVENT.read_text(encoding='utf-8'))
issue = ev.get('issue') or {}
title = issue.get('title') or ''
body = issue.get('body') or ''
if not title.startswith('Verify fund data:'):
    print('Not a fund verification issue; nothing to do')
    raise SystemExit(0)

fields = {}
for line in body.splitlines():
    if ': ' in line:
        k,v = line.split(': ',1)
        fields[k.strip()] = v.strip()

fund_id = fields.get('Fund id','').strip()
if not fund_id:
    raise SystemExit('Fund id missing')

dir_data = json.loads(DIRECTORY.read_text(encoding='utf-8'))
fund = (dir_data.get('funds') or {}).get(fund_id)
if fund is None:
    raise SystemExit(f'Unknown fund id: {fund_id}')

verified_at = fields.get('Verified date') or dir_data.get('updated_at') or ''
method = fields.get('Verification method') or 'Manual verification'
source = fields.get('Source/contact') or fields.get('Shariah certificate/governance source URL') or 'User supplied verification'
note = fields.get('Notes','')
ver = fund.setdefault('verification',{})

def rec(key,value):
    if value in ('',None): return
    ver[key] = {
      'status':'verified','method':'manual','verification_method':method,
      'source':source,'verified_at':verified_at,'note':note,'value':value
    }

minimum = fields.get('Minimum investment','')
account = fields.get('Account suitability','')
risk = fields.get('Risk classification','')
inception = fields.get('Inception date','')
ter = fields.get('TER','')
shariah = fields.get('Shariah governance verified','')
shariah_url = fields.get('Shariah certificate/governance source URL','')

if minimum:
    fund['minimum_investment']=minimum; rec('minimum_investment',minimum)
if account:
    fund['account_suitability']=account; rec('account_suitability',account)
if risk: rec('risk_level',risk)
if inception:
    fund['inception_date']=inception; rec('inception_date',inception)
if ter:
    try: rec('ter',float(ter))
    except ValueError: rec('ter',ter)
if shariah.lower()=='yes':
    fund['shariah_manually_verified']=True; rec('shariah_governance','verified')
elif shariah.lower()=='no':
    fund['shariah_manually_verified']=False; rec('shariah_governance','not verified')
if shariah_url:
    fund['shariah_source']=shariah_url
    fund['shariah_source_verified_at']=verified_at

returns = [('1Y return','oneYear'),('3Y return','threeYear'),('5Y return','fiveYear'),('10Y return','tenYear')]
manual = json.loads(MANUAL.read_text(encoding='utf-8'))
vals = manual.setdefault('values',{}).setdefault(fund_id,{})
for label,key in returns:
    v=fields.get(label,'')
    if v:
        try: n=float(v)
        except ValueError: continue
        vals[key]=n; rec(key,n)
if ter:
    try: vals['ter']=float(ter)
    except ValueError: pass
perf_date=fields.get('Performance data as at','')
if perf_date: vals['dataAsOf']=perf_date
manual['as_of']=verified_at or manual.get('as_of')
dir_data['updated_at']=verified_at or dir_data.get('updated_at')

DIRECTORY.write_text(json.dumps(dir_data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
MANUAL.write_text(json.dumps(manual,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f'Applied verification issue for {fund_id}')

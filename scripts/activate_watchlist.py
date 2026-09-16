#!/usr/bin/env python3
import json, os, re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
event=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
body=(event.get('issue') or {}).get('body') or ''
m=re.search(r'^Fund id:\s*(.+)$',body,re.M)
if not m: raise SystemExit('Missing Fund id')
fund_id=m.group(1).strip()

sources_path=root/'sources'/'funds.json'; feed_path=root/'docs'/'shariah-funds.json'; dir_path=root/'docs'/'fund-directory.json'
sources=json.loads(sources_path.read_text(encoding='utf-8')); feed=json.loads(feed_path.read_text(encoding='utf-8')); directory=json.loads(dir_path.read_text(encoding='utf-8'))
src=next((x for x in sources['funds'] if x['id']==fund_id),None); f=next((x for x in feed['funds'] if x['id']==fund_id),None); d=(directory.get('funds') or {}).get(fund_id,{})
if not src or not f: raise SystemExit('Fund not found')
if src.get('bucket')!='Watchlist': raise SystemExit('Fund is not on Watchlist')
perf=sum(v is not None for v in [f.get('oneYear'),f.get('threeYear'),f.get('fiveYear'),f.get('tenYear'),f.get('sinceInception')])
board=(d.get('board_status') or '').lower(); board_ok=bool(d.get('shariah_source') and d.get('board_status')) and not any(x in board for x in ['pending','historical','not published','not verified'])
account=d.get('account_suitability')
checks={
 'risk':bool(f.get('risk_level')),
 'performance':perf>=2,
 'source_and_date':bool(f.get('source_url') and f.get('data_as_of')),
 'minimum':bool(d.get('minimum_investment')),
 'account':account in ('TFSA','Non-TFSA'),
 'shariah':board_ok,
}
failed=[k for k,v in checks.items() if not v]
if failed: raise SystemExit('Activation blocked; missing or unverified: '+', '.join(failed))
src['bucket']=account
src['suggested_split']=0
sources_path.write_text(json.dumps(sources,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f'Activated {fund_id} for {account}; suggested split remains 0 until selected by portfolio rules.')

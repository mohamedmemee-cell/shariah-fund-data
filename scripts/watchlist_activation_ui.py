#!/usr/bin/env python3
from pathlib import Path
root=Path(__file__).resolve().parents[1]

# Fund Explorer: separate account suitability from fund status.
p=root/'docs'/'fund-explorer.html'
s=p.read_text(encoding='utf-8')
if 'watchlist-activation-ui' not in s:
    s=s.replace('<th>Bucket</th><th>Risk</th>','<th>Account</th><th>Fund status</th><th>Risk</th>',1)
    s=s.replace('colspan="11"','colspan="12"')
    old="<td>${f.manager||'—'}</td><td>${f.bucket||'—'}</td><td>${f.risk_level||'—'}</td>"
    new="<td>${f.manager||'—'}</td><td>${f.bucket==='Watchlist'?'Not confirmed':(f.bucket||'—')}</td><td>${f.bucket==='Watchlist'?'Watchlist':'Active'}</td><td>${f.risk_level||'—'}</td>"
    s=s.replace(old,new)
    s=s.replace('</style>','<style>/* watchlist-activation-ui */ .statusPill{font-weight:750}.statusPill.watch{color:var(--warn)}.statusPill.active{color:var(--accent)}</style></style>' if False else '</style>',1)
    p.write_text(s,encoding='utf-8')

# Fund details: add clear status/account/readiness and review action.
p=root/'docs'/'fund-details.html'
s=p.read_text(encoding='utf-8')
if 'watchlistActivationV1' not in s:
    s=s.replace('<div class="stat"><small>Risk</small><b id="risk">—</b></div>','<div class="stat"><small>Status</small><b id="fundStatus">—</b></div><div class="stat"><small>Account</small><b id="accountStatus">—</b></div><div class="stat"><small>Risk</small><b id="risk">—</b></div>',1)
    s=s.replace('grid-template-columns:repeat(5,1fr)','grid-template-columns:repeat(7,1fr)',1)
    activation='''<section class="card" id="activationCard"><h2>Portfolio Builder status</h2><p class="note" id="activationIntro">Checking whether this fund is ready for use in the calculator…</p><div id="activationChecks"></div><div class="links" style="margin-top:12px"><button class="btn primary" id="activationBtn" type="button" style="display:none">Activate for Portfolio Builder</button></div><div id="activationConfirm" style="display:none;margin-top:12px;padding:12px;border:1px solid var(--line);border-radius:10px;background:var(--soft)"><b>One quick confirmation</b><p class="note">This final confirmation approves the verified fund for use in portfolio calculations.</p><button class="btn primary" id="activationContinue" type="button">Continue</button></div></section>'''
    s=s.replace('<section class="card"><h2>Official fund links</h2>',activation+'<section class="card"><h2>Official fund links</h2>',1)
    s=s.replace("$('category').textContent=`${f.category||'—'} • ${f.bucket||'—'} • Data as at ${f.data_as_of||'—'}`;","$('category').textContent=`${f.category||'—'} • Data as at ${f.data_as_of||'—'}`;$('fundStatus').textContent=f.bucket==='Watchlist'?'Watchlist':'Active';$('accountStatus').textContent=f.bucket==='Watchlist'?(d?.account_suitability||'Not confirmed'):(f.bucket||'—');")
    hook="load();</script>"
    js=r'''/* watchlistActivationV1 */
async function setupActivation(){try{const [fr,dr]=await Promise.all([fetch('./shariah-funds.json?ts='+Date.now(),{cache:'no-store'}),fetch('./fund-directory.json?ts='+Date.now(),{cache:'no-store'})]);const feed=await fr.json(),dir=await dr.json(),f=feed.funds.find(x=>x.id===id),d=dir.funds[id]||{};if(!f)return;const perf=[f.oneYear,f.threeYear,f.fiveYear,f.tenYear,f.sinceInception].filter(v=>v!=null).length;const board=(d.board_status||'').toLowerCase();const boardOK=!!d.shariah_source&&!!d.board_status&&!['pending','historical','not published','not verified'].some(x=>board.includes(x));const checks=[['Risk classification',!!f.risk_level],['Historical performance',perf>=2],['Reliable source and date',!!f.source_url&&!!f.data_as_of],['Minimum investment',!!d.minimum_investment],['Account suitability',d.account_suitability==='TFSA'||d.account_suitability==='Non-TFSA'],['Shariah governance',boardOK]];document.getElementById('activationChecks').innerHTML=checks.map(([n,ok])=>`<div style="padding:5px 0">${ok?'✓':'○'} ${n}</div>`).join('');const ready=checks.every(x=>x[1]);const intro=document.getElementById('activationIntro'),btn=document.getElementById('activationBtn');if(f.bucket!=='Watchlist'){intro.textContent='Active — this fund is available to the Portfolio Builder subject to the user’s portfolio settings.';return}if(ready){intro.textContent='Ready for review. All required checks currently have verified data.';btn.style.display='inline-block';btn.onclick=()=>document.getElementById('activationConfirm').style.display='block';document.getElementById('activationContinue').onclick=()=>{const body=`Fund id: ${f.id}\nFund name: ${f.name}\nAccount suitability: ${d.account_suitability}\n\nFinal activation review requested from the fund details page.`;location.href='https://github.com/mohamedmemee-cell/shariah-fund-data/issues/new?title='+encodeURIComponent('Activate tracked fund: '+f.name)+'&body='+encodeURIComponent(body)}}else{intro.textContent='Watchlist — this fund is tracked but is not yet ready for portfolio calculations. The unchecked items still need verified information.'}}catch(e){}}
setupActivation();
'''
    s=s.replace(hook,'load();'+js+'</script>',1)
    p.write_text(s,encoding='utf-8')
print('Applied watchlist activation UI')

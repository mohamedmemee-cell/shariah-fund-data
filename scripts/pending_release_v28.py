#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'docs'/'index.html'
SOURCES=ROOT/'sources'/'funds.json'
FEED=ROOT/'docs'/'shariah-funds.json'
DIRECTORY=ROOT/'docs'/'fund-directory.json'
REPORT=ROOT/'docs'/'bulk-verification.json'
MARKER='pending-release-v28'

# ---------- Calculator UI: persistent selected state + progressive 6-step wizard ----------
s=INDEX.read_text(encoding='utf-8')
if MARKER not in s:
    css=r'''
/* pending-release-v28 */
.builderbox.selectedBuilderV28{border-color:var(--brand)!important;box-shadow:0 0 0 3px color-mix(in srgb,var(--brand) 14%,transparent),0 10px 24px rgba(15,118,110,.10)!important;transform:none!important}
.builderbox.selectedBuilderV28::after{content:'✓ Selected';position:absolute;right:12px;top:10px;padding:5px 9px;border-radius:999px;background:var(--brand);color:#fff;font-size:11px;font-weight:850;letter-spacing:.02em}
.builderbox.selectedBuilderV28 .btn.primary{box-shadow:0 0 0 2px color-mix(in srgb,#fff 38%,transparent) inset}
#portfolioChoiceStatusV28{margin-top:14px;padding:12px 14px;border-left:4px solid var(--brand);border-radius:10px;background:var(--soft);font-size:14px}.choiceStatusTitleV28{font-weight:850;color:var(--brand-strong);margin-bottom:3px}
.wizardProgressV28{display:grid;grid-template-columns:repeat(6,1fr);gap:7px;margin:0 0 16px}.wizardProgressV28 button{min-width:0;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--muted);padding:9px 7px;cursor:pointer;font:inherit;font-size:11px;font-weight:800;line-height:1.2}.wizardProgressV28 button.current{border-color:var(--brand);background:var(--brand-soft);color:var(--brand-strong)}.wizardProgressV28 button.done{border-color:color-mix(in srgb,var(--brand) 35%,var(--line));color:var(--brand-strong)}.wizardProgressV28 button.done::before{content:'✓ ';}.wizardProgressV28 button.locked{opacity:.5;cursor:not-allowed}.wizardProgressV28 button.stale{border-color:var(--warn);color:var(--warn)}
.wizardHeaderV28{display:flex;align-items:center;gap:10px;padding:4px 0}.wizardHeaderV28 .wizardStepNoV28{display:inline-grid;place-items:center;width:30px;height:30px;border-radius:50%;background:var(--brand-soft);color:var(--brand-strong);font-weight:900;font-size:12px;flex:0 0 auto}.wizardHeaderV28 .wizardSummaryTextV28{min-width:0;flex:1}.wizardHeaderV28 .wizardSummaryTextV28 b{display:block;font-size:15px}.wizardHeaderV28 .wizardSummaryTextV28 span{display:block;color:var(--muted);font-size:12px;margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.wizardHeaderV28 .wizardEditV28{border:1px solid var(--line);background:var(--card);color:var(--brand-strong);padding:7px 10px;border-radius:8px;font-weight:800;cursor:pointer}.wizardHeaderV28 .wizardStateV28{font-size:11px;font-weight:800;color:var(--muted)}
.wizardStepV28{transition:border-color .15s ease,box-shadow .15s ease}.wizardStepV28.wizardCurrentV28{border-color:color-mix(in srgb,var(--brand) 38%,var(--line));box-shadow:0 9px 28px rgba(15,118,110,.07)}.wizardStepV28.wizardLockedV28{display:none!important}.wizardStepV28.wizardCollapsedV28>:not(.wizardHeaderV28){display:none!important}.wizardStepV28.wizardCollapsedV28{padding:12px 18px!important}.wizardStepV28.wizardStaleV28 .wizardStateV28{color:var(--warn)}
.wizardContinueV28{margin-top:16px;display:flex;justify-content:flex-end}.wizardContinueV28 button{min-width:220px}
#planSummaryProgressV28{margin-bottom:14px;padding:13px 14px;border:1px solid var(--line);border-radius:11px;background:var(--soft)}#planSummaryProgressV28 b{display:block;margin-bottom:3px}.wizardReturnV28{margin-top:9px;border:1px solid var(--line);background:var(--card);color:var(--brand-strong);padding:7px 10px;border-radius:8px;font-weight:800;cursor:pointer}
@media(max-width:760px){.wizardProgressV28{grid-template-columns:repeat(3,1fr)}.wizardHeaderV28 .wizardSummaryTextV28 span{white-space:normal}.wizardContinueV28 button{width:100%}.builderbox.selectedBuilderV28::after{position:static;display:inline-block;margin:0 0 8px}}
'''
    s=s.replace('</style>',css+'\n</style>',1)
    js=r'''
<script>
/* pending-release-v28 */
(function(){
 const byId=id=>document.getElementById(id),money=n=>new Intl.NumberFormat('en-ZA',{style:'currency',currency:'ZAR',maximumFractionDigits:0}).format(Number(n)||0);
 const steps=[
  {n:1,title:'Portfolio',el:()=>byId('portfolioBuilderSection')},
  {n:2,title:'Contribution',el:()=>document.querySelector('.inputs')},
  {n:3,title:'Monthly split',el:()=>byId('monthlyPlanSection')},
  {n:4,title:'Projection',el:()=>byId('growthSection')},
  {n:5,title:'Milestones',el:()=>byId('milestonesSection')},
  {n:6,title:'Summary',el:()=>byId('planSummarySection')}
 ];
 let completed=Number(sessionStorage.getItem('wizardCompletedV28')||0),current=1,previewSummary=false,selectedMethod=sessionStorage.getItem('portfolioMethodV28')||'';
 const labels={buildRisk:['risk','Choose your risk split'],buildTarget:['target','Target a return'],buildAdvisable:['advisable','System advisable scenario']};
 function selectedPortfolioSafe(){try{return typeof selectedPortfolio!=='undefined'?selectedPortfolio:null}catch(e){return null}}
 function methodDetail(method){const p=selectedPortfolioSafe();if(method==='risk')return `${byId('riskLow')?.value||0}% Low · ${byId('riskMedium')?.value||0}% Medium · ${byId('riskHigh')?.value||0}% High`;if(method==='target')return `Target ${byId('targetReturn')?.value||0}%${p?.estimate!=null?` · model ${Number(p.estimate).toFixed(1)}%`:''}`;if(method==='advisable')return `20% Low · 60% Medium · 20% High${p?.estimate!=null?` · expected ${Number(p.estimate).toFixed(1)}%`:''}`;return 'Choose one of the three portfolio-building options.'}
 function markChoice(id){const info=labels[id];if(!info)return;selectedMethod=info[0];sessionStorage.setItem('portfolioMethodV28',selectedMethod);document.querySelectorAll('#portfolioBuilderSection .builderbox').forEach(x=>x.classList.remove('selectedBuilderV28'));const b=byId(id),box=b?.closest('.builderbox');box?.classList.add('selectedBuilderV28');Object.keys(labels).forEach(k=>{const btn=byId(k);if(!btn)return;const original=labels[k][1];btn.textContent=k===id?'✓ Selected — '+original:original});const st=byId('portfolioChoiceStatusV28');if(st)st.innerHTML=`<div class="choiceStatusTitleV28">✓ Selected: ${info[1]}</div><div>${methodDetail(selectedMethod)}</div>`;completeStep(1,true)}
 function summaries(n){const p=selectedPortfolioSafe();if(n===1)return selectedMethod?`${labels[Object.keys(labels).find(k=>labels[k][0]===selectedMethod)]?.[1]||'Portfolio selected'} · ${methodDetail(selectedMethod)}`:'Choose a portfolio approach';if(n===2)return `${money(byId('monthly')?.value||0)}/month · ${(Number(byId('increase')?.value||0)).toFixed(1)}% annual increase · ${byId('years')?.value||20} years`;if(n===3)return `TFSA ${byId('tfsaMonth')?.textContent||'—'} · balance ${byId('mixedMonth')?.textContent||'—'}${p?.rows?.length?` · ${p.rows.length} funds`:''}`;if(n===4)return `Expected scenario ${Number(byId('r2')?.value||p?.estimate||0).toFixed(1)}% · ${byId('years')?.value||20} years`;if(n===5)return 'Projection milestones reviewed';return `${completed} of 5 setup steps complete`}
 function ensureHeaders(){steps.forEach(st=>{const el=st.el();if(!el||el.querySelector(':scope > .wizardHeaderV28'))return;el.classList.add('wizardStepV28');const h=document.createElement('div');h.className='wizardHeaderV28';h.innerHTML=`<span class="wizardStepNoV28">${st.n}</span><div class="wizardSummaryTextV28"><b>Step ${st.n} — ${st.title}</b><span>${summaries(st.n)}</span></div><span class="wizardStateV28"></span>${st.n<6?'<button type="button" class="wizardEditV28">Edit</button>':''}`;el.insertBefore(h,el.firstChild);h.querySelector('.wizardEditV28')?.addEventListener('click',()=>openStep(st.n));});
  const p=byId('portfolioBuilderSection');if(p&&!byId('portfolioChoiceStatusV28')){const x=document.createElement('div');x.id='portfolioChoiceStatusV28';x.innerHTML='<div class="choiceStatusTitleV28">Choose one option above</div><div>Your selected portfolio method will stay highlighted here.</div>';p.appendChild(x)}
  [2,3,4,5].forEach(n=>{const el=steps[n-1].el();if(!el||el.querySelector('.wizardContinueV28'))return;const w=document.createElement('div');w.className='wizardContinueV28';w.innerHTML=`<button type="button" class="btn primary">Continue to Step ${n+1} →</button>`;w.querySelector('button').onclick=()=>completeStep(n,true);el.appendChild(w)});
  const sum=byId('planSummarySection');if(sum&&!byId('planSummaryProgressV28')){const b=document.createElement('div');b.id='planSummaryProgressV28';sum.insertBefore(b,sum.querySelector(':scope > .wizardHeaderV28')?.nextSibling||sum.firstChild)}
 }
 function ensureProgress(){let p=byId('wizardProgressV28');if(p)return p;const grid=document.querySelector('.grid');if(!grid)return null;p=document.createElement('nav');p.id='wizardProgressV28';p.className='wizardProgressV28';p.setAttribute('aria-label','Calculator steps');p.innerHTML=steps.map(st=>`<button type="button" data-step="${st.n}">Step ${st.n}<br>${st.title}</button>`).join('');grid.parentNode.insertBefore(p,grid);p.querySelectorAll('button').forEach(b=>b.onclick=()=>{const n=Number(b.dataset.step);if(n===6){showSummaryPreview();return}if(n<=completed+1)openStep(n)});return p}
 function refreshSummaryBox(){const box=byId('planSummaryProgressV28');if(!box)return;const done=Math.min(5,completed);box.innerHTML=done>=5?'<b>✓ Your setup is complete</b><span>This summary reflects all five setup steps. You can edit any completed step from the progress bar above.</span>':`<b>Plan so far — ${done} of 5 setup steps complete</b><span>This is a preview. Complete the remaining setup steps for the final plan.</span><br><button type="button" class="wizardReturnV28">Return to Step ${Math.min(5,done+1)}</button>`;box.querySelector('button')?.addEventListener('click',()=>openStep(Math.min(5,done+1)))}
 function updateUI(){ensureHeaders();const nav=ensureProgress();steps.forEach(st=>{const el=st.el();if(!el)return;const state=el.querySelector(':scope > .wizardHeaderV28 .wizardStateV28'),sum=el.querySelector(':scope > .wizardHeaderV28 .wizardSummaryTextV28 span');if(sum)sum.textContent=summaries(st.n);el.classList.toggle('wizardCurrentV28',st.n===current);const unlocked=st.n===1||st.n<=completed+1||st.n===6&&previewSummary;el.classList.toggle('wizardLockedV28',!unlocked);el.classList.toggle('wizardCollapsedV28',unlocked&&st.n!==current);if(state)state.textContent=st.n<=completed?'Complete':st.n===current?'Current':'Locked'});nav?.querySelectorAll('button').forEach(b=>{const n=Number(b.dataset.step);b.className=n===current?'current':n<=completed?'done':(n===6||n<=completed+1?'':'locked')});refreshSummaryBox()}
 function openStep(n){previewSummary=n===6&&completed<5;current=n;updateUI();steps[n-1].el()?.scrollIntoView({behavior:'smooth',block:'start'})}
 function completeStep(n,advance){if(n===1&&!selectedMethod)return;completed=Math.max(completed,n);sessionStorage.setItem('wizardCompletedV28',String(completed));if(advance)current=Math.min(6,n+1);previewSummary=false;updateUI();if(advance)setTimeout(()=>steps[current-1].el()?.scrollIntoView({behavior:'smooth',block:'start'}),60)}
 function showSummaryPreview(){previewSummary=completed<5;current=6;updateUI();byId('planSummarySection')?.scrollIntoView({behavior:'smooth',block:'start'})}
 function markDownstreamForReview(from){if(completed<=from)return;for(let n=from+1;n<=Math.min(5,completed);n++){steps[n-1].el()?.classList.add('wizardStaleV28');const s=steps[n-1].el()?.querySelector('.wizardStateV28');if(s)s.textContent='Needs review'}completed=from;sessionStorage.setItem('wizardCompletedV28',String(completed));updateUI()}
 Object.keys(labels).forEach(id=>byId(id)?.addEventListener('click',()=>setTimeout(()=>markChoice(id),30)));
 // If an earlier completed step is edited, keep the values but require downstream review.
 ['monthly','increase','annualTfsa','lifetimeTfsa','years','r1','r2','r3'].forEach(id=>byId(id)?.addEventListener('change',()=>{const n=2;if(completed>n)markDownstreamForReview(n)}));
 ['riskLow','riskMedium','riskHigh','targetReturn','maxFunds'].forEach(id=>byId(id)?.addEventListener('change',()=>{if(completed>1)markDownstreamForReview(1)}));
 const plan=byId('planSoFar');if(plan){const go=()=>showSummaryPreview();plan.onclick=go;plan.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();go()}}}
 ensureHeaders();ensureProgress();updateUI();
 // Start clean on a fresh browser session: only Step 1 is shown until the user explicitly chooses an option.
 if(!selectedMethod){completed=0;current=1;sessionStorage.setItem('wizardCompletedV28','0');updateUI()}
})();
</script>
'''
    s=s.replace('</body>',js+'\n<!-- '+MARKER+' -->\n</body>',1)
    INDEX.write_text(s,encoding='utf-8')
    print('Applied selected portfolio state and progressive calculator wizard V28')
else:
    print('V28 calculator UI already present')

# ---------- Bulk watchlist verification/activation ----------
# This deliberately uses the SAME activation gates as activate_watchlist.py. It never
# turns Alexforbes inclusion alone into an activation. It simply applies the gates to
# every Watchlist fund in one pass and activates all records that already have enough
# verified evidence. The rest get a machine-readable missing-fields report.
if SOURCES.exists() and FEED.exists() and DIRECTORY.exists():
    sources=json.loads(SOURCES.read_text(encoding='utf-8'))
    feed=json.loads(FEED.read_text(encoding='utf-8'))
    directory=json.loads(DIRECTORY.read_text(encoding='utf-8'))
    feed_by={f.get('id'):f for f in feed.get('funds',[])}
    dirmap=directory.get('funds') or {}
    report={'schema_version':1,'funds':[],'activated':0,'still_watchlist':0}
    changed=False
    def verified(ver,name):
        v=ver.get(name) or {}
        return v.get('status')=='verified' and v.get('method') in ('manual','automatic')
    def has_prov(ver):
        return any((v or {}).get('status')=='verified' and (v or {}).get('source') and (v or {}).get('verified_at') for v in ver.values())
    for src in sources.get('funds',[]):
        if src.get('bucket')!='Watchlist': continue
        fid=src.get('id');f=feed_by.get(fid) or {};d=dirmap.get(fid) or {};ver=d.get('verification') or {}
        perf=sum(v is not None for v in [f.get('oneYear'),f.get('threeYear'),f.get('fiveYear'),f.get('tenYear'),f.get('sinceInception')])
        board=(d.get('board_status') or '').lower();auto_board_ok=bool(d.get('shariah_source') and d.get('board_status')) and not any(x in board for x in ['pending','historical','not published','not verified'])
        board_ok=auto_board_ok or (d.get('shariah_manually_verified') is True and verified(ver,'shariah_governance'))
        account=d.get('account_suitability') or src.get('account_suitability')
        checks={
          'risk':bool(f.get('risk_level')) or verified(ver,'risk_level'),
          'performance':perf>=2,
          'source_and_date':bool(f.get('source_url') and f.get('data_as_of')) or has_prov(ver),
          'minimum':bool(d.get('minimum_investment')),
          'account':account in ('TFSA','Non-TFSA','Both'),
          'shariah':board_ok,
        }
        missing=[k for k,v in checks.items() if not v]
        corroborated=src.get('discovery_source')=="Alexforbes Shari'ah Manager Watch Survey"
        if not missing:
            src['bucket']='Non-TFSA' if account=='Both' else account
            src['account_suitability']=account;src['suggested_split']=0
            if f:
                f['bucket']=src['bucket'];f['account_suitability']=account
            report['activated']+=1;changed=True;status='activated'
        else:
            report['still_watchlist']+=1;status='watchlist'
        report['funds'].append({'id':fid,'name':src.get('name'),'status':status,'alexforbes_corroborated':corroborated,'checks':checks,'missing':missing})
    SOURCES.write_text(json.dumps(sources,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    FEED.write_text(json.dumps(feed,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f"Bulk Watchlist pass: {report['activated']} activated, {report['still_watchlist']} still need verification")

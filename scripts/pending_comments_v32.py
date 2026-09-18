#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'docs' / 'index.html'
EXPLORER = ROOT / 'docs' / 'fund-explorer.html'
MARK = 'pending-comments-v32'

index = INDEX.read_text(encoding='utf-8')
if MARK not in index:
    css = r'''
/* pending-comments-v32 */
#startNewCalcV32{margin-left:10px}
.portfolioAvailabilityV32{margin-top:14px;padding:14px;border:1px solid color-mix(in srgb,var(--warn) 45%,var(--line));border-radius:12px;background:color-mix(in srgb,var(--warn) 8%,var(--card));line-height:1.45}
.portfolioAvailabilityV32 strong{display:block;margin-bottom:4px}
.portfolioAvailabilityV32 .actionsV32{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.portfolioAvailabilityV32 .actionsV32 button,.portfolioAvailabilityV32 .actionsV32 a{padding:8px 10px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--text);text-decoration:none;font-weight:750;cursor:pointer}
#riskExplanationV9 .mismatchV32{color:var(--warn);font-weight:750}
@media(max-width:720px){#startNewCalcV32{margin-left:0;margin-top:8px}}
'''
    index = index.replace('</style>', css + '\n</style>', 1)
    js = r'''
<script>
/* pending-comments-v32 */
(function(){
 const byId=id=>document.getElementById(id);
 const bands=['Low','Medium','High'];
 const cloneMix=m=>({Low:Number(m?.Low||0),Medium:Number(m?.Medium||0),High:Number(m?.High||0)});
 const mixText=m=>`${Number(m?.Low||0).toFixed(0)}% Low · ${Number(m?.Medium||0).toFixed(0)}% Medium · ${Number(m?.High||0).toFixed(0)}% High`;
 const nearlySame=(a,b)=>bands.every(k=>Math.abs(Number(a?.[k]||0)-Number(b?.[k]||0))<=.6);

 // Only ACTIVE funds may be used to construct a live portfolio.
 try{
   eligibleFunds=function(){
     return feed.funds.filter(f=>f.bucket!=='Watchlist'&&planningReturn(f).value!=null&&['auto','fallback_manual','snapshot'].includes(f.update_status||'snapshot'));
   };
 }catch(e){}

 // Preserve both requested and actual risk mix. This prevents a missing band from
 // silently being displayed as if the requested mix had been achieved.
 try{
   constructPortfolio=function(requested){
     const req=cloneMix(requested),rows=[],missing=[];
     for(const band of bands){
       const bw=(req[band]||0)/100;
       if(!bw)continue;
       const group=bandPortfolio(band);
       if(!group.length){missing.push(band);continue}
       for(const x of group)rows.push({fund:x.fund,band,weight:bw*x.within});
     }
     const rawTotal=rows.reduce((s,r)=>s+r.weight,0);
     if(rawTotal>0)rows.forEach(r=>r.weight/=rawTotal);
     const actual={Low:0,Medium:0,High:0};
     rows.forEach(r=>actual[r.band]+=r.weight*100);
     bands.forEach(k=>actual[k]=Number(actual[k].toFixed(6)));
     const estimate=rows.length?rows.reduce((s,r)=>s+r.weight*planningReturn(r.fund).value,0):0;
     const quality=rows.length?rows.reduce((s,r)=>s+r.weight*dataQuality(r.fund),0):0;
     const terCoverage=rows.filter(r=>r.fund.ter!=null).reduce((s,r)=>s+r.weight,0);
     const ter=terCoverage?rows.filter(r=>r.fund.ter!=null).reduce((s,r)=>s+r.weight*Number(r.fund.ter),0)/terCoverage:null;
     return {mix:actual,requestedMix:req,missingBands:missing,rows,estimate,quality,ter,terCoverage,availabilityAdjusted:missing.length>0};
   };
 }catch(e){}

 function requestedFor(id){
   if(id==='buildAdvisable')return {Low:20,Medium:60,High:20};
   return {Low:Number(byId('riskLow')?.value||0),Medium:Number(byId('riskMedium')?.value||0),High:Number(byId('riskHigh')?.value||0)};
 }
 function missingBands(mix){
   return bands.filter(b=>Number(mix[b]||0)>0 && !bandPortfolio(b).length);
 }
 function showAvailability(id,mix,missing){
   const result=byId('portfolioResult'); if(!result)return;
   const names=missing.join(', ');
   result.innerHTML=`<div class="portfolioAvailabilityV32"><strong>Your requested portfolio cannot currently be built.</strong>
   <div>Requested: ${mixText(mix)}</div>
   <div>There ${missing.length===1?'is':'are'} currently no eligible <b>${names}</b>-risk active Shariah investment${missing.length===1?'':'s'} available for this portfolio.</div>
   <div class="actionsV32">
     <button type="button" id="changeRiskV32">Change my risk mix</button>
     <button type="button" id="closestRiskV32">Use closest available mix</button>
     <a href="./discovery.html">Research/add missing risk funds</a>
   </div></div>`;
   byId('changeRiskV32')?.addEventListener('click',()=>{
     byId('riskLow')?.focus();
     byId('riskLow')?.scrollIntoView({behavior:'smooth',block:'center'});
   });
   byId('closestRiskV32')?.addEventListener('click',()=>{
     window.__closestApprovalV32=true;
     const btn=byId(id);
     btn?.click();
   });
 }
 document.addEventListener('click',e=>{
   const btn=e.target.closest?.('#buildRisk,#buildAdvisable');
   if(!btn)return;
   const id=btn.id,mix=requestedFor(id);
   if(id==='buildRisk'){
     const total=mix.Low+mix.Medium+mix.High;
     if(Math.abs(total-100)>.001){
       e.preventDefault();e.stopImmediatePropagation();
       const v=byId('riskValidation');if(v)v.innerHTML=`<span class="warn">Total: ${total.toFixed(0)}% — must equal 100% before a portfolio can be built.</span>`;
       return;
     }
   }
   const missing=missingBands(mix);
   if(missing.length&&!window.__closestApprovalV32){
     e.preventDefault();e.stopImmediatePropagation();
     showAvailability(id,mix,missing);
     return;
   }
   if(window.__closestApprovalV32){
     window.__closestBuildingV32=true;
     window.__closestApprovalV32=false;
     setTimeout(()=>{window.__closestBuildingV32=false},0);
   }
 },true);

 function correctRiskExplanation(){
   const box=byId('riskExplanationV9');
   let p=null;try{p=selectedPortfolio}catch(e){}
   if(!box||!p?.mix)return;
   let req=p.requestedMix?cloneMix(p.requestedMix):null;
   let ttl='';try{ttl=String(selectedPortfolioTitle||'').toLowerCase()}catch(e){}
   if(!req){
     if(ttl.includes('advisable'))req={Low:20,Medium:60,High:20};
     else if(ttl.includes('risk split'))req=requestedFor('buildRisk');
     else req=cloneMix(p.mix);
   }
   const actual=cloneMix(p.mix),same=nearlySame(req,actual);
   let why='';
   if(ttl.includes('target')){
     why='Target-return mode is allowed to choose a different risk mix because the user asked the calculator to search for the closest historical planning return.';
   }else if(same){
     why='The final portfolio matches the requested Portfolio Builder risk mix.';
   }else{
     const missing=(p.missingBands||[]).filter(Boolean);
     if(missing.length){
       why=`The requested mix could not be built because no eligible active ${missing.join(' / ')}-risk fund was available. The final mix should only be used after you explicitly chose “Use closest available mix”.`;
     }else{
       const diffs=bands.filter(k=>Math.abs(req[k]-actual[k])>.6).map(k=>`${k}: ${req[k].toFixed(0)}% → ${actual[k].toFixed(0)}%`);
       why=`The final portfolio differs materially from the requested mix (${diffs.join('; ')}). Review the active-fund availability and portfolio constraints before relying on this allocation.`;
     }
   }
   box.innerHTML=`<div class="riskExplainGridV9"><div class="riskExplainCardV9"><small>Portfolio Builder requested mix</small><b>${mixText(req)}</b></div><div class="riskExplainArrowV9" aria-hidden="true">→</div><div class="riskExplainCardV9"><small>Final portfolio risk mix</small><b>${mixText(actual)}</b></div></div><p class="riskExplainWhyV9 ${same?'':'mismatchV32'}"><strong>Why can these be different?</strong> ${why}</p>`;
 }
 ['buildRisk','buildTarget','buildAdvisable'].forEach(id=>byId(id)?.addEventListener('click',()=>setTimeout(correctRiskExplanation,180)));
 new MutationObserver(()=>setTimeout(correctRiskExplanation,0)).observe(byId('planSummarySection')||document.body,{childList:true,subtree:true});
 setTimeout(correctRiskExplanation,350);

 // Robustly move Projection period above the fund-count limit. Older scripts can
 // create/move the fund-limit box after load, so retry and observe the Step 2 area.
 function moveProjectionV32(){
   const inputs=document.querySelector('.inputs'),years=byId('years');
   const fund=document.querySelector('.fundLimitBox,#goalFundLimitV4');
   if(!inputs||!years||!fund)return;
   const slider=years.closest('.sliderrow'); if(!slider)return;
   let heading=slider.previousElementSibling;
   if(!heading||!/Projection period/i.test(heading.textContent||'')){
     heading=[...inputs.querySelectorAll('h2,h3')].find(x=>/Projection period/i.test(x.textContent||''));
   }
   if(!heading)return;
   let wrap=byId('projectionPeriodV32');
   if(!wrap){wrap=document.createElement('div');wrap.id='projectionPeriodV32'}
   if(fund.previousElementSibling!==wrap)fund.parentNode.insertBefore(wrap,fund);
   if(heading.parentNode!==wrap)wrap.appendChild(heading);
   if(slider.parentNode!==wrap)wrap.appendChild(slider);
 }
 [0,80,250,700].forEach(ms=>setTimeout(moveProjectionV32,ms));
 const inputsObs=document.querySelector('.inputs');
 if(inputsObs)new MutationObserver(()=>moveProjectionV32()).observe(inputsObs,{childList:true,subtree:false});

 // Clear/new calculation control.
 function addStartNew(){
   const bar=byId('planSoFar');if(!bar||byId('startNewCalcV32'))return;
   const b=document.createElement('button');b.type='button';b.id='startNewCalcV32';b.className='btn';b.textContent='Start new calculation';
   bar.appendChild(b);
   b.addEventListener('click',e=>{
     e.stopPropagation();
     const name=String(byId('planName')?.value||'').trim();
     const label=name?` “${name}”`:'';
     if(!confirm(`Start a new calculation? This will clear the current plan${label} and return you to Step 1.`))return;
     localStorage.removeItem('shariahCalcWeights');
     localStorage.removeItem('shariahMaxFunds');
     sessionStorage.removeItem('wizardCompletedV28');
     sessionStorage.removeItem('portfolioMethodV28');
     const clean=location.pathname;
     location.replace(clean);
   });
 }
 addStartNew();setTimeout(addStartNew,120);
})();
</script>
'''
    index = index.replace('</body>', js + '\n<!-- ' + MARK + ' -->\n</body>', 1)
    INDEX.write_text(index, encoding='utf-8')

explorer = EXPLORER.read_text(encoding='utf-8')
if MARK not in explorer:
    css = r'''
<style>
/* pending-comments-v32 */
.bulkResearchV32{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-top:12px}
.bulkStatV32{padding:11px 12px;border:1px solid var(--line);border-radius:11px;background:var(--soft)}
.bulkStatV32 small{display:block;color:var(--muted);margin-bottom:4px}.bulkStatV32 b{font-size:18px}
.bulkActionsV32{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}.bulkActionsV32 button{padding:8px 10px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--text);font-weight:750;cursor:pointer}
.bulkDetailsV32{margin-top:12px;overflow:auto}.bulkDetailsV32 table{min-width:760px}.bulkDetailsV32[hidden]{display:none}
@media(max-width:900px){.bulkResearchV32{grid-template-columns:1fr 1fr}}@media(max-width:520px){.bulkResearchV32{grid-template-columns:1fr}}
</style>
'''
    explorer = explorer.replace('</head>', css + '\n</head>', 1)
    js = r'''
<script>
/* pending-comments-v32 */
(async function(){
 const firstCard=document.querySelector('main > section.card');
 let panel=document.getElementById('bulkResearchPanelV32');
 if(!panel&&firstCard){
   panel=document.createElement('section');panel.className='card';panel.id='bulkResearchPanelV32';
   panel.innerHTML=`<div class="sectiontitle" style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;flex-wrap:wrap"><div><h2 style="margin:0 0 4px">Automatic Watchlist research</h2><div class="muted">Official manager sources are checked automatically. Ambiguous funds remain on Watchlist.</div></div><span class="muted" id="bulkDateV32">Loading…</span></div>
   <div class="bulkResearchV32">
    <div class="bulkStatV32"><small>Watchlist researched</small><b id="bulkResV32">—</b></div>
    <div class="bulkStatV32"><small>Official sources found</small><b id="bulkSrcV32">—</b></div>
    <div class="bulkStatV32"><small>Fields auto-verified</small><b id="bulkFldV32">—</b></div>
    <div class="bulkStatV32"><small>Still on Watchlist</small><b id="bulkWatchV32">—</b></div>
    <div class="bulkStatV32"><small>Active funds</small><b id="bulkActiveV32">—</b></div>
   </div>
   <div class="bulkActionsV32"><button type="button" id="bulkToggleV32">View research details</button></div>
   <div class="bulkDetailsV32" id="bulkDetailsV32" hidden></div>`;
   firstCard.insertAdjacentElement('afterend',panel);
 }
 if(!panel)return;
 const set=(id,v)=>{const e=document.getElementById(id);if(e)e.textContent=v??'—'};
 try{
   const [rr,vr,fr]=await Promise.all([
     fetch('./bulk-research.json?ts='+Date.now(),{cache:'no-store'}),
     fetch('./bulk-verification.json?ts='+Date.now(),{cache:'no-store'}),
     fetch('./shariah-funds.json?ts='+Date.now(),{cache:'no-store'})
   ]);
   const r=rr.ok?await rr.json():{},v=vr.ok?await vr.json():{},f=fr.ok?await fr.json():{funds:[]};
   const funds=f.funds||[],watch=funds.filter(x=>x.bucket==='Watchlist').length,active=funds.length-watch;
   set('bulkResV32',r.researched);set('bulkSrcV32',r.official_source_found);set('bulkFldV32',r.fields_verified);
   set('bulkWatchV32',v.still_watchlist??watch);set('bulkActiveV32',active);
   set('bulkDateV32',r.generated_at?'Last run: '+r.generated_at:'Not run yet');
   const details=document.getElementById('bulkDetailsV32'),rows=r.funds||[];
   if(details)details.innerHTML=rows.length?`<table><thead><tr><th>Fund</th><th>Research status</th><th>Verified fields</th><th>Note</th></tr></thead><tbody>${rows.map(x=>`<tr><td>${x.name||x.id}</td><td>${String(x.status||'—').replaceAll('_',' ')}</td><td>${(x.verified_fields||[]).join(', ')||'—'}</td><td style="white-space:normal;text-align:left">${(x.notes||[]).join(' ')||'—'}</td></tr>`).join('')}</tbody></table>`:'<p class="muted">No research results yet.</p>';
   const t=document.getElementById('bulkToggleV32');if(t)t.onclick=()=>{details.hidden=!details.hidden;t.textContent=details.hidden?'View research details':'Hide research details'};
 }catch(e){set('bulkDateV32','Status unavailable')}
})();
</script>
'''
    explorer = explorer.replace('</body>', js + '\n<!-- ' + MARK + ' -->\n</body>', 1)
    EXPLORER.write_text(explorer, encoding='utf-8')

print('Applied V32 pending calculator and Fund Explorer changes')

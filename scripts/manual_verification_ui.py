#!/usr/bin/env python3
from pathlib import Path

p=Path(__file__).resolve().parents[1]/'docs'/'fund-details.html'
s=p.read_text(encoding='utf-8')
if 'manualVerificationV1' in s:
    print('Manual verification UI already present')
    raise SystemExit(0)

css=r'''
<style id="manualVerificationStyles">
.verifyPanel{margin-top:12px;padding:14px;border:1px solid var(--line);border-radius:12px;background:var(--soft)}
.verifyGrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.verifyGrid label{display:block;font-size:12px;color:var(--muted);margin-bottom:4px}.verifyGrid input,.verifyGrid select,.verifyGrid textarea{width:100%;padding:9px 10px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--text);font:inherit}.verifyGrid textarea{min-height:74px;resize:vertical}.verifyWide{grid-column:1/-1}.verificationItem{padding:7px 0;border-bottom:1px dashed var(--line)}.verificationItem:last-child{border-bottom:0}.verificationMeta{font-size:12px;color:var(--muted);margin-top:2px}.verifiedBadge{display:inline-block;padding:3px 7px;border-radius:999px;background:var(--soft);color:var(--accent);font-size:11px;font-weight:800}.manualConfirm{display:none;margin-top:12px;padding:12px;border:1px solid var(--line);border-radius:10px;background:var(--card)}
@media(max-width:650px){.verifyGrid{grid-template-columns:1fr}.verifyWide{grid-column:auto}}
</style>
'''
s=s.replace('</head>',css+'</head>',1)

section=r'''
<section class="card" id="manualVerificationCard">
  <div style="display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap">
    <div><h2 style="margin:0 0 5px">Verified information</h2><p class="note" style="margin:0">If information is not available online, it can be confirmed directly with the fund manager and stored as <b>Manual verified</b>. The calculator will distinguish it from automatically sourced data.</p></div>
    <button class="btn" id="openVerifyForm" type="button">Add / update verified information</button>
  </div>
  <div id="verificationList" style="margin-top:12px"></div>
  <div class="verifyPanel" id="verifyForm" style="display:none">
    <div class="verifyGrid">
      <div><label>Minimum investment</label><input id="vMinimum" placeholder="e.g. R500/month or R10,000 once-off"></div>
      <div><label>Account suitability</label><select id="vAccount"><option value="">Leave unchanged</option><option>TFSA</option><option>Non-TFSA</option><option>Both</option></select></div>
      <div><label>Risk classification</label><input id="vRisk" placeholder="e.g. Moderate"></div>
      <div><label>TER (%)</label><input id="vTer" type="number" step="0.01" placeholder="e.g. 1.25"></div>
      <div><label>Shariah governance verified?</label><select id="vShariah"><option value="">Leave unchanged</option><option value="Yes">Yes</option><option value="No">No</option></select></div>
      <div><label>Verification method</label><select id="vMethod"><option>Telephone</option><option>Email</option><option>Official document supplied directly</option><option>In person</option><option>Other</option></select></div>
      <div><label>1Y return (%)</label><input id="v1y" type="number" step="0.01"></div><div><label>3Y return (%)</label><input id="v3y" type="number" step="0.01"></div>
      <div><label>5Y return (%)</label><input id="v5y" type="number" step="0.01"></div><div><label>10Y return (%)</label><input id="v10y" type="number" step="0.01"></div>
      <div><label>Performance data as at</label><input id="vPerfDate" type="date"></div><div><label>Verified date</label><input id="vDate" type="date"></div>
      <div class="verifyWide"><label>Source / person contacted</label><input id="vSource" placeholder="e.g. Fund manager client services, adviser name, email reference"></div>
      <div class="verifyWide"><label>Notes</label><textarea id="vNotes" placeholder="Record enough detail so the verification can be understood later."></textarea></div>
    </div>
    <div class="links" style="margin-top:12px"><button class="btn primary" id="saveVerification" type="button">Save verified information</button><button class="btn" id="cancelVerification" type="button">Cancel</button></div>
    <div class="manualConfirm" id="manualConfirm"><b>One quick confirmation</b><p class="note">This records the information as manually verified. Please only confirm details you obtained from a reliable source.</p><button class="btn primary" id="manualContinue" type="button">Continue</button></div>
  </div>
</section>
'''
s=s.replace('<section class="card"><h2>Official fund links</h2>',section+'<section class="card"><h2>Official fund links</h2>',1)

js=r'''
<script>
/* manualVerificationV1 */
(function(){
 const byId=x=>document.getElementById(x), fundId=new URLSearchParams(location.search).get('id'); let currentFund=null,currentDir={};
 const labels={minimum_investment:'Minimum investment',account_suitability:'Account suitability',risk_level:'Risk classification',ter:'TER',shariah_governance:'Shariah governance',oneYear:'1Y return',threeYear:'3Y return',fiveYear:'5Y return',tenYear:'10Y return',sinceInception:'Since inception return'};
 function renderVerified(){const ver=currentDir.verification||{},keys=Object.keys(ver);const box=byId('verificationList');if(!box)return;if(!keys.length){box.innerHTML='<span class="muted">No manually verified information has been recorded yet.</span>';return}box.innerHTML=keys.map(k=>{const v=ver[k]||{},method=v.method==='manual'?'Manual verified':'Verified';return `<div class="verificationItem"><b>${labels[k]||k}</b> <span class="verifiedBadge">${method}</span><div>${v.value??''}</div><div class="verificationMeta">${v.verification_method||''}${v.source?' • '+v.source:''}${v.verified_at?' • '+v.verified_at:''}${v.note?' • '+v.note:''}</div></div>`}).join('')}
 async function refresh(){try{const [fr,dr]=await Promise.all([fetch('./shariah-funds.json?ts='+Date.now(),{cache:'no-store'}),fetch('./fund-directory.json?ts='+Date.now(),{cache:'no-store'})]);const feed=await fr.json(),dir=await dr.json();currentFund=feed.funds.find(x=>x.id===fundId);currentDir=(dir.funds||{})[fundId]||{};renderVerified();setTimeout(()=>renderActivationV2(currentFund,currentDir),30)}catch(e){}}
 function manualProvenance(ver){return Object.values(ver||{}).some(v=>v&&v.status==='verified'&&v.source&&v.verified_at)}
 function renderActivationV2(f,d){if(!f)return;const ver=d.verification||{},perf=[f.oneYear,f.threeYear,f.fiveYear,f.tenYear,f.sinceInception].filter(v=>v!=null).length,board=(d.board_status||'').toLowerCase(),autoBoard=!!d.shariah_source&&!!d.board_status&&!['pending','historical','not published','not verified'].some(x=>board.includes(x)),manualBoard=d.shariah_manually_verified===true&&ver.shariah_governance?.status==='verified',checks=[['Risk classification',!!f.risk_level],['Historical performance',perf>=2],['Reliable source / verification date',!!(f.source_url&&f.data_as_of)||manualProvenance(ver)],['Minimum investment',!!d.minimum_investment],['Account suitability',['TFSA','Non-TFSA','Both'].includes(d.account_suitability)],['Shariah governance',autoBoard||manualBoard]];const list=byId('activationChecks'),intro=byId('activationIntro'),btn=byId('activationBtn');if(list)list.innerHTML=checks.map(([n,ok])=>`<div style="padding:5px 0">${ok?'✓':'○'} ${n}</div>`).join('');if(!intro||!btn)return;if(f.bucket!=='Watchlist'){intro.textContent='Active — this fund is available to the Portfolio Builder subject to the user’s portfolio settings.';btn.style.display='none';return}const ready=checks.every(x=>x[1]);if(ready){intro.textContent='Ready for review. Required information is known and verified; sources may be automatic or manually confirmed.';btn.style.display='inline-block'}else{intro.textContent='Watchlist — some information is still unknown. Missing facts can be added from official online sources or manually verified directly with the fund manager.';btn.style.display='none'}}
 byId('openVerifyForm')?.addEventListener('click',()=>{byId('verifyForm').style.display='block';byId('vMinimum').value=currentDir.minimum_investment||'';byId('vAccount').value=currentDir.account_suitability||'';byId('vRisk').value=currentFund?.risk_level||'';byId('vTer').value=currentFund?.ter??'';byId('vDate').value=new Date().toISOString().slice(0,10);byId('verifyForm').scrollIntoView({behavior:'smooth',block:'nearest'})});
 byId('cancelVerification')?.addEventListener('click',()=>byId('verifyForm').style.display='none');
 byId('saveVerification')?.addEventListener('click',()=>{if(!byId('vSource').value.trim()){alert('Please record the source or person contacted so the information can be traced later.');return}byId('manualConfirm').style.display='block'});
 byId('manualContinue')?.addEventListener('click',()=>{const line=(label,id)=>`${label}: ${byId(id)?.value||''}`;const body=[`Fund id: ${fundId}`,`Fund name: ${currentFund?.name||''}`,line('Minimum investment','vMinimum'),line('Account suitability','vAccount'),line('Risk classification','vRisk'),line('TER','vTer'),line('Shariah governance verified','vShariah'),line('1Y return','v1y'),line('3Y return','v3y'),line('5Y return','v5y'),line('10Y return','v10y'),line('Performance data as at','vPerfDate'),line('Verification method','vMethod'),line('Source/contact','vSource'),line('Verified date','vDate'),line('Notes','vNotes')].join('\n');location.href='https://github.com/mohamedmemee-cell/shariah-fund-data/issues/new?title='+encodeURIComponent('Verify fund data: '+(currentFund?.name||fundId))+'&body='+encodeURIComponent(body)});
 refresh();
})();
</script>
'''
s=s.replace('</body>',js+'</body>',1)
p.write_text(s,encoding='utf-8')
print('Applied manual verification UI')

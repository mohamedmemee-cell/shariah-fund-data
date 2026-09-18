#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"docs"/"fund-details.html"
MARK="fund-details-state-sync-v36"
s=P.read_text(encoding="utf-8")
if MARK in s:
    print("Fund details state sync V36 already present")
    raise SystemExit(0)

js=r'''
<script id="fundDetailsStateSyncV36">
/* fund-details-state-sync-v36
   Final authority for Fund Details state. Keeps summary cards, readiness checks,
   and activation action in sync with verified fund-directory data. */
(function(){
 const repo='mohamedmemee-cell/shariah-fund-data';
 const params=new URLSearchParams(location.search),fundId=params.get('id');
 if(!fundId)return;
 const byId=id=>document.getElementById(id);

 function verified(ver,key){
   const x=(ver||{})[key];
   return !!(x && x.status==='verified' && x.value!=='' && x.value!=null);
 }
 function provenance(ver){
   return Object.values(ver||{}).some(v=>v&&v.status==='verified'&&v.source&&v.verified_at);
 }
 function displayMinimum(v){
   if(v==null||v==='')return 'Not yet verified';
   const n=Number(String(v).replace(/[^0-9.]/g,''));
   return Number.isFinite(n)&&n>0
     ? new Intl.NumberFormat('en-ZA',{style:'currency',currency:'ZAR',maximumFractionDigits:0}).format(n)
     : String(v);
 }
 async function load(){
   const [fr,dr]=await Promise.all([
     fetch('./shariah-funds.json?ts='+Date.now(),{cache:'no-store'}),
     fetch('./fund-directory.json?ts='+Date.now(),{cache:'no-store'})
   ]);
   if(!fr.ok||!dr.ok)throw new Error('Fund data unavailable');
   const feed=await fr.json(),dir=await dr.json();
   return {f:(feed.funds||[]).find(x=>x.id===fundId),d:(dir.funds||{})[fundId]||{}};
 }
 function checksFor(f,d){
   const ver=d.verification||{};
   const perf=[f?.oneYear,f?.threeYear,f?.fiveYear,f?.tenYear,f?.sinceInception].filter(v=>v!=null).length;
   const board=(d.board_status||'').toLowerCase();
   const autoBoard=!!d.shariah_source&&!!d.board_status&&!['pending','historical','not published','not verified'].some(x=>board.includes(x));
   const manualBoard=d.shariah_manually_verified===true&&verified(ver,'shariah_governance');
   const minOK=!!d.minimum_investment || verified(ver,'minimum_investment');
   const account=d.account_suitability || ver.account_suitability?.value || '';
   const accountOK=['TFSA','Non-TFSA','Both'].includes(account);
   return {
     account,
     rows:[
       ['Risk classification',!!f?.risk_level || verified(ver,'risk_level')],
       ['Historical performance',perf>=2],
       ['Reliable source / verification date',!!(f?.source_url&&f?.data_as_of)||provenance(ver)],
       ['Minimum investment',minOK],
       ['Account suitability',accountOK],
       ['Shariah governance',autoBoard||manualBoard]
     ]
   };
 }
 function showStatus(title,text,kind=''){
   let box=byId('activationStatusV22');
   if(!box){
     const btn=byId('activationBtn');
     box=document.createElement('div');box.id='activationStatusV22';box.className='activationStatusV22';
     btn?.closest('.links')?.insertAdjacentElement('afterend',box);
   }
   if(box){
     box.style.display='block';
     box.className='activationStatusV22 '+kind;
     box.innerHTML='<strong>'+title+'</strong><span>'+text+'</span>';
   }
 }
 async function issueFor(name){
   try{
     const r=await fetch('https://api.github.com/repos/'+repo+'/issues?state=all&per_page=100&ts='+Date.now(),{cache:'no-store'});
     if(!r.ok)return null;
     const rows=await r.json();
     return rows.find(x=>x.title==='Activate tracked fund: '+name)||null;
   }catch(e){return null}
 }
 async function render(){
   try{
     const {f,d}=await load();if(!f)return;
     const state=checksFor(f,d),ready=state.rows.every(x=>x[1]);

     // Summary cards must use the same verified source of truth as the checklist.
     if(byId('minimum'))byId('minimum').textContent=displayMinimum(d.minimum_investment||d.verification?.minimum_investment?.value);
     if(byId('accountStatus')){
       const a=state.account;
       byId('accountStatus').textContent=a==='Both'?'TFSA & Non-TFSA':(a||'Not confirmed');
     }

     if(byId('activationChecks')){
       byId('activationChecks').innerHTML=state.rows.map(([n,ok])=>'<div style="padding:5px 0">'+(ok?'✓':'○')+' '+n+'</div>').join('');
     }

     const intro=byId('activationIntro'),btn=byId('activationBtn'),confirm=byId('activationConfirm');
     if(confirm)confirm.style.display='none';

     if(f.bucket!=='Watchlist'){
       if(intro)intro.textContent='Active — this fund is available to the Portfolio Builder subject to the user’s portfolio settings.';
       if(btn)btn.style.display='none';
       if(byId('fundStatus'))byId('fundStatus').textContent='Active';
       showStatus('Fund activated','This fund is active for Portfolio Builder calculations.','ok');
       return;
     }

     if(byId('fundStatus'))byId('fundStatus').textContent='Watchlist';

     const existingIssue=await issueFor(f.name);
     if(existingIssue){
       if(btn)btn.style.display='none';
       if(intro)intro.textContent='Activation requested — the verified fund is waiting for the activation workflow to complete.';
       showStatus('Activation request accepted','The activation request has been created in GitHub. This page will show Active after processing finishes.','ok');
       return;
     }

     if(!ready){
       if(intro)intro.textContent='Watchlist — some required information is still missing. Complete the unchecked items before this fund can be activated for Portfolio Builder calculations.';
       if(btn)btn.style.display='none';
       showStatus('Not ready for activation','Complete the unchecked verification items above. The activation action will only appear when every required check is complete.','warn');
       return;
     }

     if(intro)intro.textContent='Ready for activation — all required information is verified. Final approval is still required before this fund can be used in Portfolio Builder calculations.';
     if(btn){
       btn.style.display='inline-block';
       btn.textContent='Activate for Portfolio Builder';
       btn.onclick=()=>{
         const body='Fund id: '+f.id+'\nFund name: '+f.name+'\nAccount suitability: '+(state.account||'Not confirmed')+'\n\nFinal activation review requested from the fund details page after all required verification checks passed.';
         showStatus('Confirm activation in GitHub','GitHub will open once. Click the green Create button, close that tab and return here.');
         window.open('https://github.com/'+repo+'/issues/new?title='+encodeURIComponent('Activate tracked fund: '+f.name)+'&body='+encodeURIComponent(body),'_blank','noopener');
       };
     }
     showStatus('Ready for activation','All required checks are complete. Use the activation button for the final approval.','ok');
   }catch(e){
     showStatus('Could not refresh fund status','Refresh the page and try again.','warn');
   }
 }
 window.fundDetailsStateSyncV36=render;
 window.addEventListener('focus',()=>setTimeout(render,250));
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)setTimeout(render,250)});
 setTimeout(render,120);
 setTimeout(render,900);
})();
</script>
'''

s=s.replace("</body>",js+"\n<!-- "+MARK+" -->\n</body>",1)
P.write_text(s,encoding="utf-8")
print("Applied authoritative Fund Details state sync V36")

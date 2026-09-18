#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'docs'/'add-fund.html'
MARK='add-fund-status-sync-v33'
s=P.read_text(encoding='utf-8')
if MARK in s:
    print('V33 already present')
    raise SystemExit(0)

js=r'''
<script>
/* add-fund-status-sync-v33 */
(function(){
 const byId=id=>document.getElementById(id);
 function tracked(){try{return JSON.parse(localStorage.getItem('candidateFundTracking')||'null')}catch(e){return null}}
 async function loadCandidate(){
   const t=tracked(); if(!t?.id)return null;
   try{
     const r=await fetch('./candidates/'+encodeURIComponent(t.id)+'.json?ts='+Date.now(),{cache:'no-store'});
     return r.ok?await r.json():null;
   }catch(e){return null}
 }
 function syncRow(row){
   if(!row)return false;
   const card=byId('statusCard'); card?.classList.remove('hidden');
   if(byId('statusName'))byId('statusName').textContent=row.name||tracked()?.name||'Candidate fund';
   if(byId('statusManager'))byId('statusManager').textContent=row.manager||tracked()?.manager||'';

   try{if(typeof renderProgress==='function')renderProgress(row.stages||{candidate:'complete'})}catch(e){}
   try{if(typeof renderFindings==='function')renderFindings(row)}catch(e){}

   const badge=byId('statusBadge');
   if(badge){
     badge.innerHTML='';
     if(row.activation_ready){
       badge.className='statusBadge ready';
       badge.textContent='Ready for activation review';
     }else if(row.status==='researching'||row.status==='queued'){
       badge.className='statusBadge review';
       badge.textContent=row.status==='queued'?'Research queued':'Researching official sources…';
     }else{
       badge.className='statusBadge review';
       badge.textContent=(row.status||'needs_review').replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase());
     }
   }

   const msg=byId('statusMessage');
   if(msg){
     if(row.activation_ready) msg.textContent='Automated research and validation have reached the review threshold. Check the findings below before activating the fund.';
     else if(row.status==='researching'||row.status==='queued') msg.textContent='Your GitHub confirmation was accepted. Automated research is still running; this page will update automatically.';
     else msg.textContent='GitHub confirmation is complete. Automated research has finished what it can. Review the items marked for attention before activation.';
   }

   byId('reviewNote')?.classList.remove('hidden');
   if(row.source_url&&byId('sourceLink')){
     byId('sourceLink').href=row.source_url;
     byId('sourceLink').classList.remove('hidden');
   }
   if(byId('activate')){
     if(row.activation_ready){
       byId('activate').classList.remove('hidden');
       if(typeof requestActivation==='function')byId('activate').onclick=()=>requestActivation(row);
     }else byId('activate').classList.add('hidden');
   }

   // Keep the upper return-status message consistent with the candidate record.
   const top=byId('githubReturnAddV21');
   if(top){
     top.className='returnStatusV21 ok';
     const state=(row.status||'needs_review').replaceAll('_',' ');
     top.innerHTML='<strong>Onboarding accepted</strong><span>GitHub confirmation is complete. Current status: '+state+'.</span>';
   }
   return true;
 }
 async function sync(){
   const row=await loadCandidate();
   if(row)syncRow(row);
 }
 byId('refresh')?.addEventListener('click',()=>setTimeout(sync,50));
 window.addEventListener('focus',()=>setTimeout(sync,150));
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)setTimeout(sync,150)});
 setTimeout(sync,50);
 setTimeout(sync,700);
})();
</script>
'''
s=s.replace('</body>',js+'\n<!-- '+MARK+' -->\n</body>',1)
P.write_text(s,encoding='utf-8')
print('Applied Add Fund status sync V33')

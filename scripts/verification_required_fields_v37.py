#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"docs"/"fund-details.html"
MARK="verification-required-fields-v37"
s=P.read_text(encoding="utf-8")
if MARK in s:
    print("Verification required-field guard V37 already present")
    raise SystemExit(0)

js=r'''
<script id="verificationRequiredFieldsV37">
/* verification-required-fields-v37 */
(function(){
 const byId=id=>document.getElementById(id);
 const fundId=new URLSearchParams(location.search).get('id');
 if(!fundId)return;

 async function current(){
   try{
     const [fr,dr]=await Promise.all([
       fetch('./shariah-funds.json?ts='+Date.now(),{cache:'no-store'}),
       fetch('./fund-directory.json?ts='+Date.now(),{cache:'no-store'})
     ]);
     const feed=await fr.json(),dir=await dr.json();
     return {f:(feed.funds||[]).find(x=>x.id===fundId)||{},d:(dir.funds||{})[fundId]||{}};
   }catch(e){return {f:{},d:{}}}
 }

 async function validateRequired(){
   const {f,d}=await current(),ver=d.verification||{};
   const minimum=(byId('vMinimum')?.value||'').trim() || d.minimum_investment || ver.minimum_investment?.value || '';
   const account=(byId('vAccount')?.value||'').trim() || d.account_suitability || ver.account_suitability?.value || '';
   const risk=(byId('vRisk')?.value||'').trim() || f.risk_level || ver.risk_level?.value || '';
   const shariahInput=(byId('vShariah')?.value||'').trim();
   const shariahOK=shariahInput==='Yes' || (d.shariah_manually_verified===true && ver.shariah_governance?.status==='verified');
   const source=(byId('vSource')?.value||'').trim() || (byId('vShariahSource')?.value||'').trim() || '';
   const missing=[];
   if(!minimum)missing.push('Minimum investment');
   if(!['TFSA','Non-TFSA','Both'].includes(account))missing.push('Account suitability');
   if(!risk)missing.push('Risk classification');
   if(!shariahOK)missing.push('Shariah governance confirmation');
   if(!source)missing.push('Verification source/contact');
   if(missing.length){
     alert('Please complete the required verification fields before continuing:\n\n• '+missing.join('\n• '));
     return false;
   }
   return true;
 }

 const save=byId('saveVerification');
 if(save){
   save.addEventListener('click',async ev=>{
     if(!(await validateRequired())){
       ev.stopImmediatePropagation();
       ev.preventDefault();
       byId('manualConfirm')?.style.setProperty('display','none');
     }
   },true);
 }
 const cont=byId('manualContinue');
 if(cont){
   cont.addEventListener('click',async ev=>{
     if(!(await validateRequired())){
       ev.stopImmediatePropagation();
       ev.preventDefault();
     }
   },true);
 }
})();
</script>
'''
s=s.replace("</body>",js+"\n<!-- "+MARK+" -->\n</body>",1)
P.write_text(s,encoding="utf-8")
print("Applied verification required-field guard V37")

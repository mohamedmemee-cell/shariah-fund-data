#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'docs'/'index.html'
s=p.read_text(encoding='utf-8')
if 'pdf-projection-and-contacts-v7' in s:
    print('PDF projection/contact V7 already present')
    raise SystemExit(0)

css=r'''
/* pdf-projection-and-contacts-v7 */
@media print{
  #printPlanReport .pdfScenarioGrid{
    display:grid!important;
    grid-template-columns:repeat(4,minmax(0,1fr))!important;
    gap:3mm!important;
    align-items:stretch!important;
  }
  #printPlanReport .pdfScenario{
    min-height:24mm!important;
    padding:3.2mm!important;
    display:flex!important;
    flex-direction:column!important;
    align-items:flex-start!important;
    justify-content:flex-start!important;
    gap:1.2mm!important;
    overflow:hidden!important;
  }
  #printPlanReport .pdfScenario small,
  #printPlanReport .pdfScenario b,
  #printPlanReport .pdfScenario span{
    display:block!important;
    width:100%!important;
    white-space:normal!important;
    line-height:1.25!important;
  }
  #printPlanReport .pdfScenario small{font-size:8.5pt!important;color:#445!important;margin:0!important}
  #printPlanReport .pdfScenario b{font-size:12.5pt!important;margin:1mm 0 .3mm!important;color:#111!important}
  #printPlanReport .pdfScenario span{font-size:8.5pt!important;color:#596267!important;margin:0!important}
  #printPlanReport .pdfFundContact{display:block!important;font-size:8pt!important;color:#596267!important;margin-top:.8mm!important;line-height:1.3!important}
  #printPlanReport .pdfFundContact a{color:#0f5b4b!important;text-decoration:none!important}
}
'''
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
<script>
/* pdf-projection-and-contacts-v7 */
(function(){
 let directoryCache=null;
 fetch('./fund-directory.json?ts='+Date.now(),{cache:'no-store'})
   .then(r=>r.ok?r.json():null).then(x=>directoryCache=x).catch(()=>{});
 function selected(){try{return typeof selectedPortfolio!=='undefined'?selectedPortfolio:null}catch(e){return null}}
 function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
 function patchPdfFundContacts(){
   const report=document.getElementById('printPlanReport');
   if(!report||!directoryCache)return;
   const heading=[...report.querySelectorAll('h2')].find(h=>/Selected funds/i.test(h.textContent||''));
   const table=heading?.nextElementSibling;
   if(!table||table.tagName!=='TABLE'||table.dataset.contactsV7==='1')return;
   const rows=selected()?.rows||[];
   const trs=[...table.querySelectorAll('tbody tr')];
   trs.forEach((tr,i)=>{
     const r=rows[i]; if(!r?.fund)return;
     const d=(directoryCache.funds||{})[r.fund.id]||{};
     const c=d.contact||{};
     const phone=c.phone||c.whatsapp||'';
     const email=c.email||c.alternate_email||'';
     if(!phone&&!email)return;
     const first=tr.querySelector('td'); if(!first)return;
     const pieces=[];
     if(phone) pieces.push('Tel: '+esc(phone));
     if(email) pieces.push('Email: '+esc(email));
     first.insertAdjacentHTML('beforeend','<span class="pdfFundContact">'+pieces.join(' &nbsp; • &nbsp; ')+'</span>');
   });
   table.dataset.contactsV7='1';
 }
 window.addEventListener('beforeprint',patchPdfFundContacts);
})();
</script>
'''
s=s.replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Applied PDF projection/contact V7')

#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'docs'/'index.html'
s=p.read_text(encoding='utf-8')
if 'site-finish-v5' in s:
    print('site finish v5 already present')
    raise SystemExit(0)

css=r'''
/* site-finish-v5 */
@media print{
  #printPlanReport{print-color-adjust:exact!important;-webkit-print-color-adjust:exact!important}
  #printPlanReport .pdfBismillah{color:#0f766e!important}
  #printPlanReport h1{color:#0f5b4b!important}
  #printPlanReport h2{color:#0f5b4b!important;border-bottom:2px solid #8bc9ba!important}
  #printPlanReport .pdfDisclosure{background:#f1f8f6!important;border:1px solid #9bcabd!important;border-left:5px solid #0f766e!important}
  #printPlanReport .pdfItem{background:#f7fbfa!important;border-color:#c8dcd7!important}
  #printPlanReport .pdfItem:nth-child(2n){background:#f5f3ff!important}
  #printPlanReport .pdfScenarioGrid{display:grid!important;grid-template-columns:repeat(4,1fr)!important;gap:3mm!important;margin-top:3mm!important}
  #printPlanReport .pdfScenario{padding:3mm!important;border-radius:2mm!important;border:1px solid #d8e1e2!important}
  #printPlanReport .pdfScenario.capital{background:#f5f7f7!important}
  #printPlanReport .pdfScenario.cautious{background:#edf5ff!important;border-color:#b8cef8!important}
  #printPlanReport .pdfScenario.expected{background:#eaf7f1!important;border-color:#aad9c6!important}
  #printPlanReport .pdfScenario.optimistic{background:#fff6e7!important;border-color:#e8c98f!important}
  #printPlanReport thead th{background:#0f766e!important;color:#fff!important}
  #printPlanReport tbody tr:nth-child(even){background:#f7fbfa!important}
  #printPlanReport .pdfQrWrap{display:grid!important;grid-template-columns:145px 1fr!important;gap:5mm!important;align-items:center!important;margin-top:4mm!important;padding:4mm!important;border:1px solid #c8dcd7!important;border-radius:3mm!important;background:#f7fbfa!important;break-inside:avoid!important}
  #printPlanReport .pdfQrWrap img{width:135px!important;height:135px!important;display:block!important}
  #printPlanReport .pdfAccent{color:#0f766e!important;font-weight:800!important}
}
'''
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
<script>
/* site-finish-v5 */
(function(){
 const byId=id=>document.getElementById(id);
 const money=n=>new Intl.NumberFormat('en-ZA',{style:'currency',currency:'ZAR',maximumFractionDigits:0}).format(Number(n)||0);
 function selected(){try{return typeof selectedPortfolio!=='undefined'?selectedPortfolio:null}catch(e){return null}}
 function setVal(id,v){const e=byId(id);if(!e)return;e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}
 function hasSharedPlan(){return /(?:^#|&)plan=/.test(location.hash)}
 function resetNormalVisit(){
   if(hasSharedPlan())return;
   try{selectedPortfolio=null}catch(e){}
   setVal('monthly',6000);setVal('increase',5);setVal('years',20);setVal('maxFunds',4);setVal('targetReturn',10);
   ['riskLow','lowRisk'].forEach(id=>setVal(id,20));['riskMedium','mediumRisk'].forEach(id=>setVal(id,60));['riskHigh','highRisk'].forEach(id=>setVal(id,20));
   ['r1','r2','r3'].forEach(id=>{const e=byId(id);if(e){e.value='';e.placeholder='—'}});
   localStorage.removeItem('shariahMaxFunds');
   const result=byId('portfolioResult');if(result)result.innerHTML='<div class="muted">Choose one of the three portfolio-building options above to build your portfolio.</div>';
   const note=[...document.querySelectorAll('.inputs p,.inputs .note,.inputs .muted')].find(x=>/Linked to Current portfolio model/i.test(x.textContent||''));if(note)note.textContent='Build a portfolio in Step 1 to generate cautious, expected and optimistic planning scenarios.';
 }
 function planPayload(){const p=selected();let risk=[20,60,20];if(p?.mix)risk=[Number(p.mix.Low||0),Number(p.mix.Medium||0),Number(p.mix.High||0)];return{v:2,created:new Date().toISOString().slice(0,10),monthly:Number(byId('monthly')?.value||0),increase:Number(byId('increase')?.value||0),years:Number(byId('years')?.value||20),risk,target:Number(byId('targetReturn')?.value||0),maxFunds:Number(byId('maxFunds')?.value||0),scenario:['r1','r2','r3'].map(id=>Number(byId(id)?.value||0)),funds:(p?.rows||[]).map(r=>({id:r.fund?.id,w:Number(r.weight||0)}))}}
 function enc(o){return btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')}
 function shareUrl(){const u=new URL(location.href);u.hash='plan='+enc(planPayload());return u.toString()}
 function calc(rate){const years=Math.max(1,Number(byId('years')?.value||20)),start=Math.max(0,Number(byId('monthly')?.value||0)),inc=Math.max(0,Number(byId('increase')?.value||0));let bal=0,capital=0;const mr=Math.pow(1+rate/100,1/12)-1;for(let m=0;m<years*12;m++){bal*=1+mr;const yr=Math.floor(m/12),c=start*Math.pow(1+inc/100,yr);bal+=c;capital+=c}return{balance:bal,capital,profit:bal-capital}}
 function buildPrintReport(){
   let r=byId('printPlanReport');if(!r){r=document.createElement('section');r.id='printPlanReport';document.body.appendChild(r)}
   const p=selected(),years=Math.max(1,Number(byId('years')?.value||20)),monthly=Number(byId('monthly')?.value||0),inc=Number(byId('increase')?.value||0),rates=['r1','r2','r3'].map(id=>Number(byId(id)?.value||0)),max=Number(byId('maxFunds')?.value||0),a=calc(rates[0]),b=calc(rates[1]),c=calc(rates[2]);
   let mix='—';if(p?.mix)mix=`${Number(p.mix.Low||0).toFixed(0)}% Low • ${Number(p.mix.Medium||0).toFixed(0)}% Medium • ${Number(p.mix.High||0).toFixed(0)}% High`;
   const rows=p?.rows||[];const funds=rows.length?`<table><thead><tr><th>Fund</th><th>Portfolio</th><th>Approx. monthly</th></tr></thead><tbody>${rows.map(x=>{const w=Number(x.weight||0),pct=w<=1?w*100:w;return `<tr><td>${x.fund?.name||'Fund'}</td><td>${pct.toFixed(1)}%</td><td>${money(monthly*pct/100)}</td></tr>`}).join('')}</tbody></table>`:'<p>No portfolio funds were selected when this report was generated.</p>';
   const qr=shareUrl(),qrSrc='https://api.qrserver.com/v1/create-qr-code/?size=260x260&data='+encodeURIComponent(qr);
   r.innerHTML=`<div class="pdfBismillah">بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ</div><h1>Shariah Investment Plan</h1><p class="pdfAccent">Personal investment planning summary</p><p>Generated ${new Date().toLocaleDateString('en-ZA',{day:'numeric',month:'long',year:'numeric'})}</p><div class="pdfDisclosure"><b>Important disclosure</b><p>This calculator is an informational and planning tool only and does not constitute financial, investment, tax or other professional advice. Calculations, historical performance and projections are illustrative and are not a recommendation to buy, sell or invest in any particular fund.</p><p>Investment values and returns can rise or fall, and past performance does not guarantee future performance. Users remain responsible for their own investment decisions. The owners and operators of this tool accept no responsibility for decisions made or losses incurred based on its use.</p><p><b>Before making an investment decision, users should consult an appropriately qualified financial adviser and independently verify the latest information directly with the relevant fund provider.</b></p></div><h2>Plan overview</h2><div class="pdfGrid"><div class="pdfItem"><small>Starting monthly investment</small><b>${money(monthly)}</b></div><div class="pdfItem"><small>Investment period</small><b>${years} years</b></div><div class="pdfItem"><small>Annual increase</small><b>${inc.toFixed(1)}%</b></div><div class="pdfItem"><small>Funds to manage</small><b>${max?`Maximum ${max}`:'No limit'}</b></div><div class="pdfItem"><small>Risk mix</small><b>${mix}</b></div><div class="pdfItem"><small>Planning scenarios</small><b>${rates.map(x=>x?x.toFixed(1)+'%':'—').join(' / ')}</b></div></div><h2>Projected value after ${years} years</h2><div class="pdfScenarioGrid"><div class="pdfScenario capital"><small>Capital invested</small><b>${money(b.capital)}</b></div><div class="pdfScenario cautious"><small>Cautious</small><b>${money(a.balance)}</b><span>Profit ${money(a.profit)}</span></div><div class="pdfScenario expected"><small>Expected</small><b>${money(b.balance)}</b><span>Profit ${money(b.profit)}</span></div><div class="pdfScenario optimistic"><small>Optimistic</small><b>${money(c.balance)}</b><span>Profit ${money(c.profit)}</span></div></div><h2>Selected funds</h2>${funds}<h2>Open this investment plan</h2><div class="pdfQrWrap"><img id="pdfPlanQr" alt="QR code to reopen this plan" src="${qrSrc}"><div><b>Scan to reopen this plan</b><p>This QR code contains the calculator settings used for this report. When opened on another device, the shared plan can be restored from the link.</p><p class="pdfFoot">Fund data may change after this report is generated. Always confirm current information with the fund provider before investing.</p></div></div>`;
   return byId('pdfPlanQr');
 }
 function replacePrintButton(){const old=byId('downloadPlanPdf');if(!old||old.dataset.v5)return;const b=old.cloneNode(true);b.dataset.v5='1';old.replaceWith(b);b.addEventListener('click',async()=>{const img=buildPrintReport();try{if(img&&!img.complete)await Promise.race([img.decode(),new Promise(res=>setTimeout(res,1800))])}catch(e){}window.print()})}
 async function restoreSharedPortfolio(){if(!hasSharedPlan())return;const m=location.hash.match(/(?:^#|&)plan=([^&]+)/);if(!m)return;let o;try{o=JSON.parse(decodeURIComponent(escape(atob(m[1].replace(/-/g,'+').replace(/_/g,'/')))))}catch(e){return}if(!o?.funds?.length)return;try{const feed=await fetch('./shariah-funds.json?ts='+Date.now(),{cache:'no-store'}).then(r=>r.json());const rows=o.funds.map(x=>({fund:feed.funds.find(f=>f.id===x.id),weight:x.w})).filter(x=>x.fund);if(!rows.length)return;selectedPortfolio={rows,estimate:Number(o.scenario?.[1]||0),mix:{Low:Number(o.risk?.[0]||0),Medium:Number(o.risk?.[1]||0),High:Number(o.risk?.[2]||0)}};if(typeof displayRecommendation==='function')displayRecommendation('Shared investment plan',selectedPortfolio,'Restored from shared link.');document.querySelectorAll('#monthly,#increase,#years,#maxFunds,#r1,#r2,#r3').forEach(e=>e.dispatchEvent(new Event('input',{bubbles:true})))}catch(e){}
 }
 setTimeout(()=>{resetNormalVisit();replacePrintButton();restoreSharedPortfolio()},80);
 setTimeout(()=>{if(!hasSharedPlan())resetNormalVisit();replacePrintButton()},500);
})();
</script>
'''
s=s.replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Applied site finish V5')

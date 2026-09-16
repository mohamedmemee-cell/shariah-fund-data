#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

# Clean one bad value produced by the old blank-field parser.
manual_path=ROOT/'data'/'manual_values.json'
dir_path=ROOT/'docs'/'fund-directory.json'
if manual_path.exists():
    manual=json.loads(manual_path.read_text(encoding='utf-8'))
    mv=(manual.get('values') or {}).get('27four-shariah-balanced') or {}
    if mv.get('tenYear')==2026.0:
        mv['tenYear']=None
    manual_path.write_text(json.dumps(manual,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
if dir_path.exists():
    directory=json.loads(dir_path.read_text(encoding='utf-8'))
    d=(directory.get('funds') or {}).get('27four-shariah-balanced') or {}
    v=(d.get('verification') or {}).get('tenYear')
    if isinstance(v,dict) and v.get('value')==2026.0:
        d.get('verification',{}).pop('tenYear',None)
    dir_path.write_text(json.dumps(directory,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

# Main calculator finishing pass.
p=ROOT/'docs'/'index.html'
s=p.read_text(encoding='utf-8')
if 'site-finish-v4' not in s:
    css=r'''
/* site-finish-v4 */
html[data-theme="dark"] select,html[data-theme="dark"] option{background:#182123!important;color:#edf3f1!important}
.backTopV4{position:fixed;right:22px;bottom:22px;z-index:80;border:1px solid var(--line);background:var(--card);color:var(--text);padding:10px 14px;border-radius:999px;box-shadow:0 8px 24px rgba(0,0,0,.14);font-weight:800;cursor:pointer;opacity:0;pointer-events:none;transform:translateY(8px);transition:.16s}.backTopV4.show{opacity:1;pointer-events:auto;transform:none}
#goalFundLimitV4{margin:14px 0;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:var(--soft)}#goalFundLimitV4 label{display:block;font-weight:800;margin-bottom:6px}#goalFundLimitV4 select{min-width:240px;max-width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--text);font:inherit}#goalFundLimitV4 small{display:block;color:var(--muted);margin-top:6px;line-height:1.45}
.summaryProjectionV4{margin-top:16px}.summaryProjectionV4 h3{margin:0 0 9px}.projectionGridV4{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.projectionCardV4{padding:12px;border:1px solid var(--line);border-radius:11px;background:var(--soft)}.projectionCardV4 small{display:block;color:var(--muted);margin-bottom:4px}.projectionCardV4 b{font-size:18px}.projectionCardV4 span{display:block;color:var(--muted);font-size:12px;margin-top:3px}
#growthChartV4{width:100%;height:340px;display:block}.growthChartV4Legend{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;color:var(--muted);font-size:12px}.growthChartV4Legend span:before{content:'';display:inline-block;width:18px;height:3px;background:currentColor;border-radius:5px;vertical-align:middle;margin-right:6px}.growthChartV4Legend .a{color:#6f96ef}.growthChartV4Legend .b{color:#54b89e}.growthChartV4Legend .c{color:#c89543}
#printPlanReport{display:none}
@media(max-width:700px){.projectionGridV4{grid-template-columns:1fr 1fr}.backTopV4{right:12px;bottom:12px}}
@media(max-width:430px){.projectionGridV4{grid-template-columns:1fr}}
@media print{
 @page{size:A4;margin:14mm}
 body>*:not(#printPlanReport){display:none!important}
 #printPlanReport{display:block!important;color:#111!important;background:#fff!important;font-family:Arial,"Segoe UI",sans-serif;font-size:11pt;line-height:1.45}
 #printPlanReport .pdfBismillah{font-size:22pt;text-align:center;direction:rtl;margin:2mm 0 5mm;font-family:Arial,"Segoe UI",sans-serif}
 #printPlanReport h1{font-size:22pt;margin:0 0 2mm}#printPlanReport h2{font-size:14pt;margin:7mm 0 2mm;border-bottom:1px solid #bbb;padding-bottom:1mm}
 #printPlanReport .pdfDisclosure{border:1px solid #aaa;padding:4mm;border-radius:3mm;background:#fafafa}
 #printPlanReport .pdfGrid{display:grid;grid-template-columns:repeat(2,1fr);gap:3mm}.pdfItem{border:1px solid #ccc;padding:3mm;border-radius:2mm}.pdfItem small{display:block;color:#555}.pdfItem b{font-size:12pt}
 #printPlanReport table{width:100%;border-collapse:collapse;font-size:9.5pt}#printPlanReport th,#printPlanReport td{border-bottom:1px solid #ddd;padding:2mm;text-align:left;white-space:normal}
 #printPlanReport .pdfFoot{font-size:8.5pt;color:#555;margin-top:6mm}
}
'''
    s=s.replace('</style>',css+'\n</style>',1)
    js=r'''
<script>
/* site-finish-v4 */
(function(){
 const byId=id=>document.getElementById(id), money=n=>new Intl.NumberFormat('en-ZA',{style:'currency',currency:'ZAR',maximumFractionDigits:0}).format(Number(n)||0);
 function getVal(id,d=0){const e=byId(id);return e?Number(e.value||d):d}
 function ensureFundLimit(){let sel=byId('maxFunds'),box=sel?.closest('.fundLimitBox,#goalFundLimitV4');if(!sel){box=document.createElement('div');box.id='goalFundLimitV4';box.innerHTML='<label for="maxFunds">Maximum number of funds in my portfolio</label><select id="maxFunds"><option value="1">1 fund</option><option value="2">2 funds</option><option value="3">3 funds</option><option value="4">4 funds</option><option value="5">5 funds</option><option value="6">6 funds</option><option value="0">No limit</option></select><small>Fewer funds are simpler to manage. Choose 1–6, or No limit. The Portfolio Builder will respect this limit when you build or rebuild a portfolio.</small>';sel=box.querySelector('select');sel.value=localStorage.getItem('shariahMaxFunds')||'0'}else{if(box)box.id='goalFundLimitV4';const saved=localStorage.getItem('shariahMaxFunds');if(saved!=null)sel.value=saved}
   const inputs=document.querySelector('.inputs');if(inputs&&box){const heading=[...inputs.querySelectorAll('h2,h3')].find(x=>/Future return scenarios/i.test(x.textContent));if(heading)heading.parentNode.insertBefore(box,heading);else inputs.appendChild(box)}
   if(sel&&!sel.dataset.boundV4){sel.dataset.boundV4='1';sel.addEventListener('change',()=>{localStorage.setItem('shariahMaxFunds',sel.value);sel.dispatchEvent(new Event('input',{bubbles:true}))})}
 }
 function ensureBackTop(){if(byId('backTopV4'))return;const b=document.createElement('button');b.id='backTopV4';b.className='backTopV4';b.type='button';b.innerHTML='↑&nbsp; Back to Top';b.onclick=()=>window.scrollTo({top:0,behavior:'smooth'});document.body.appendChild(b);const show=()=>b.classList.toggle('show',window.scrollY>420);addEventListener('scroll',show,{passive:true});show()}
 function calc(rate){const years=Math.max(1,getVal('years',20)),start=Math.max(0,getVal('monthly',0)),inc=Math.max(0,getVal('increase',0));let bal=0,capital=0;const mr=Math.pow(1+rate/100,1/12)-1;for(let m=0;m<years*12;m++){bal*=1+mr;const yr=Math.floor(m/12),c=start*Math.pow(1+inc/100,yr);bal+=c;capital+=c}return{balance:bal,capital,profit:bal-capital}}
 function ensureSummaryProjection(){const sec=byId('planSummarySection');if(!sec)return;let box=byId('summaryProjectionV4');if(!box){box=document.createElement('div');box.id='summaryProjectionV4';box.className='summaryProjectionV4';const funds=byId('summaryFunds');sec.insertBefore(box,funds||sec.querySelector('.shareRow')||null)}const years=Math.max(1,getVal('years',20)),a=calc(getVal('r1',0)),b=calc(getVal('r2',0)),c=calc(getVal('r3',0));box.innerHTML=`<h3>Projected value after ${years} years</h3><div class="projectionGridV4"><div class="projectionCardV4"><small>Capital invested</small><b>${money(b.capital)}</b><span>Total money contributed</span></div><div class="projectionCardV4"><small>Cautious</small><b>${money(a.balance)}</b><span>Profit ${money(a.profit)}</span></div><div class="projectionCardV4"><small>Expected</small><b>${money(b.balance)}</b><span>Profit ${money(b.profit)}</span></div><div class="projectionCardV4"><small>Optimistic</small><b>${money(c.balance)}</b><span>Profit ${money(c.profit)}</span></div></div>`}
 function setupCleanGrowth(){const sec=byId('growthSection')||[...document.querySelectorAll('section')].find(x=>/Portfolio growth/i.test(x.querySelector('h2')?.textContent||''));if(!sec)return;sec.querySelectorAll('canvas').forEach(c=>{if(c.id!=='growthChartV4')c.style.display='none'});let canvas=byId('growthChartV4');if(!canvas){canvas=document.createElement('canvas');canvas.id='growthChartV4';const legend=document.createElement('div');legend.className='growthChartV4Legend';legend.innerHTML='<span class="a">Cautious</span><span class="b">Expected</span><span class="c">Optimistic</span>';sec.appendChild(canvas);sec.appendChild(legend)}drawCleanGrowth()}
 function drawCleanGrowth(){const canvas=byId('growthChartV4');if(!canvas)return;const years=Math.max(1,getVal('years',20)),start=Math.max(0,getVal('monthly',0)),inc=Math.max(0,getVal('increase',0)),rates=[getVal('r1'),getVal('r2'),getVal('r3')],dpr=window.devicePixelRatio||1,w=Math.max(560,canvas.clientWidth||900),h=340;canvas.width=w*dpr;canvas.height=h*dpr;const ctx=canvas.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);const pad={l:72,r:24,t:22,b:42},pw=w-pad.l-pad.r,ph=h-pad.t-pad.b;function yearly(rate){let bal=0,out=[0],mr=Math.pow(1+rate/100,1/12)-1;for(let m=0;m<years*12;m++){bal*=1+mr;const yr=Math.floor(m/12);bal+=start*Math.pow(1+inc/100,yr);if((m+1)%12===0)out.push(bal)}return out}const series=rates.map(yearly),max=Math.max(1,...series.flat());const styles=getComputedStyle(document.documentElement),grid=styles.getPropertyValue('--line').trim()||'#ccd5d6',muted=styles.getPropertyValue('--muted').trim()||'#667276',cols=['#6f96ef','#54b89e','#c89543'];ctx.font='12px system-ui';ctx.strokeStyle=grid;ctx.fillStyle=muted;ctx.lineWidth=1;for(let i=0;i<=4;i++){const y=pad.t+ph*i/4,val=max*(1-i/4);ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(w-pad.r,y);ctx.stroke();ctx.fillText(money(val),4,y+4)}const ticks=[0,5,10,15,20,25,30,35,40].filter(x=>x<=years);if(!ticks.includes(years))ticks.push(years);ticks.forEach(y=>{const x=pad.l+pw*y/years;ctx.fillText(y===0?'Year 0':`Year ${y}`,Math.max(2,x-18),h-12)});series.forEach((arr,si)=>{ctx.beginPath();ctx.strokeStyle=cols[si];ctx.lineWidth=2.5;arr.forEach((v,i)=>{const x=pad.l+pw*i/years,y=pad.t+ph*(1-v/max);if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y)});ctx.stroke();const v=arr[arr.length-1],x=w-pad.r,y=pad.t+ph*(1-v/max);ctx.fillStyle=cols[si];ctx.font='700 11px system-ui';ctx.fillText(rates[si].toFixed(1)+'%',Math.max(pad.l,x-38),Math.max(12,y-5))})}
 function currentFundRows(){try{const p=typeof selectedPortfolio!=='undefined'?selectedPortfolio:null;return p?.rows||[]}catch(e){return []}}
 function renderPrintReport(){let r=byId('printPlanReport');if(!r){r=document.createElement('section');r.id='printPlanReport';document.body.appendChild(r)}const years=Math.max(1,getVal('years',20)),monthly=getVal('monthly'),inc=getVal('increase'),rates=[getVal('r1'),getVal('r2'),getVal('r3')],a=calc(rates[0]),b=calc(rates[1]),c=calc(rates[2]),max=Number(byId('maxFunds')?.value||0),rows=currentFundRows();let mix='—';try{const p=typeof selectedPortfolio!=='undefined'?selectedPortfolio:null;if(p?.mix)mix=`${Number(p.mix.Low||0).toFixed(0)}% Low • ${Number(p.mix.Medium||0).toFixed(0)}% Medium • ${Number(p.mix.High||0).toFixed(0)}% High`}catch(e){}const funds=rows.length?`<table><thead><tr><th>Fund</th><th>Portfolio</th><th>Approx. monthly</th></tr></thead><tbody>${rows.map(x=>{const w=Number(x.weight||0),pct=w<=1?w*100:w;return `<tr><td>${x.fund?.name||'Fund'}</td><td>${pct.toFixed(1)}%</td><td>${money(monthly*pct/100)}</td></tr>`}).join('')}</tbody></table>`:'<p>No portfolio funds were selected when this report was generated.</p>';r.innerHTML=`<div class="pdfBismillah">بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ</div><h1>Shariah Investment Plan</h1><p>Personal investment planning summary • Generated ${new Date().toLocaleDateString('en-ZA',{day:'numeric',month:'long',year:'numeric'})}</p><div class="pdfDisclosure"><b>Important disclosure</b><p>This calculator is an informational and planning tool only and does not constitute financial, investment, tax or other professional advice. Calculations, historical performance and projections are illustrative and are not a recommendation to buy, sell or invest in any particular fund.</p><p>Investment values and returns can rise or fall, and past performance does not guarantee future performance. Users remain responsible for their own investment decisions. The owners and operators of this tool accept no responsibility for decisions made or losses incurred based on its use.</p><p><b>Before making an investment decision, users should consult an appropriately qualified financial adviser and independently verify the latest information directly with the relevant fund provider.</b></p></div><h2>Plan overview</h2><div class="pdfGrid"><div class="pdfItem"><small>Starting monthly investment</small><b>${money(monthly)}</b></div><div class="pdfItem"><small>Investment period</small><b>${years} years</b></div><div class="pdfItem"><small>Annual increase</small><b>${inc.toFixed(1)}%</b></div><div class="pdfItem"><small>Funds to manage</small><b>${max?`Maximum ${max}`:'No limit'}</b></div><div class="pdfItem"><small>Risk mix</small><b>${mix}</b></div><div class="pdfItem"><small>Planning scenarios</small><b>${rates[0].toFixed(1)}% / ${rates[1].toFixed(1)}% / ${rates[2].toFixed(1)}%</b></div></div><h2>Projected value after ${years} years</h2><table><thead><tr><th>Capital invested</th><th>Cautious</th><th>Expected</th><th>Optimistic</th></tr></thead><tbody><tr><td>${money(b.capital)}</td><td>${money(a.balance)}<br>Profit ${money(a.profit)}</td><td>${money(b.balance)}<br>Profit ${money(b.profit)}</td><td>${money(c.balance)}<br>Profit ${money(c.profit)}</td></tr></tbody></table><h2>Selected funds</h2>${funds}<p class="pdfFoot">Planning rates are assumptions based on the calculator settings at the time this report was generated. Confirm current fund terms, fees, eligibility and Shariah status before investing.</p>`}
 function setupPrint(){const old=byId('downloadPlanPdf');if(!old||old.dataset.v4)return;const b=old.cloneNode(true);b.dataset.v4='1';old.replaceWith(b);b.addEventListener('click',()=>{renderPrintReport();setTimeout(()=>window.print(),60)})}
 function refresh(){ensureSummaryProjection();drawCleanGrowth()}
 ensureFundLimit();ensureBackTop();setupCleanGrowth();setupPrint();ensureSummaryProjection();
 ['monthly','increase','years','r1','r2','r3','maxFunds'].forEach(id=>{const e=byId(id);if(e&&!e.dataset.finishV4){e.dataset.finishV4='1';e.addEventListener('input',()=>requestAnimationFrame(refresh));e.addEventListener('change',()=>requestAnimationFrame(refresh))}});addEventListener('resize',()=>requestAnimationFrame(drawCleanGrowth));
})();
</script>
'''
    s=s.replace('</body>',js+'\n</body>',1)
    p.write_text(s,encoding='utf-8')

# Shared polish for secondary pages: readable dark selects + persistent back to top.
secondary_css=r'''
<style id="siteFinishV4Shared">html[data-theme="dark"] select,html[data-theme="dark"] option{background:#182123!important;color:#edf3f1!important}.backTopV4{position:fixed;right:22px;bottom:22px;z-index:80;border:1px solid var(--line);background:var(--card);color:var(--text);padding:10px 14px;border-radius:999px;box-shadow:0 8px 24px rgba(0,0,0,.14);font-weight:800;cursor:pointer;opacity:0;pointer-events:none;transform:translateY(8px);transition:.16s}.backTopV4.show{opacity:1;pointer-events:auto;transform:none}@media(max-width:700px){.backTopV4{right:12px;bottom:12px}}</style>
'''
secondary_js=r'''
<script id="siteFinishV4SharedScript">(function(){if(document.getElementById('backTopV4'))return;const b=document.createElement('button');b.id='backTopV4';b.className='backTopV4';b.type='button';b.innerHTML='↑&nbsp; Back to Top';b.onclick=()=>scrollTo({top:0,behavior:'smooth'});document.body.appendChild(b);const show=()=>b.classList.toggle('show',scrollY>420);addEventListener('scroll',show,{passive:true});show()})();</script>
'''
for name in ['fund-explorer.html','add-fund.html','fund-details.html']:
    q=ROOT/'docs'/name
    if not q.exists():continue
    t=q.read_text(encoding='utf-8')
    if 'siteFinishV4Shared' not in t:t=t.replace('</head>',secondary_css+'</head>',1)
    if 'siteFinishV4SharedScript' not in t:t=t.replace('</body>',secondary_js+'</body>',1)
    q.write_text(t,encoding='utf-8')

# Fund details: optional inception date/age and manual verification field.
q=ROOT/'docs'/'fund-details.html'
t=q.read_text(encoding='utf-8')
if 'fundInceptionV4' not in t:
    inception_js=r'''
<script id="fundInceptionV4">(async function(){const id=new URLSearchParams(location.search).get('id');const stats=document.querySelector('.stats');if(stats&&!document.getElementById('inceptionStatV4')){const d=document.createElement('div');d.className='stat';d.id='inceptionStatV4';d.innerHTML='<small>Fund inception</small><b id="inceptionV4">Not yet verified</b><span id="fundAgeV4" style="display:block;color:var(--muted);font-size:11px;margin-top:3px"></span>';stats.appendChild(d)}try{const r=await fetch('./fund-directory.json?ts='+Date.now(),{cache:'no-store'}),j=await r.json(),x=(j.funds||{})[id]||{},v=x.inception_date;if(v){document.getElementById('inceptionV4').textContent=v;const dt=new Date(v+'T00:00:00');if(!isNaN(dt)){const now=new Date();let y=now.getFullYear()-dt.getFullYear();if(now.getMonth()<dt.getMonth()||(now.getMonth()===dt.getMonth()&&now.getDate()<dt.getDate()))y--;document.getElementById('fundAgeV4').textContent=y>=0?`${y} year${y===1?'':'s'} in existence`:''}}}catch(e){}})();</script>
'''
    t=t.replace('</body>',inception_js+'</body>',1)
    t=t.replace('.stats{display:grid;grid-template-columns:repeat(7,1fr);gap:10px;', '.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:10px;',1)
# Add field to manual verification form and issue body if that UI exists.
if 'id="vInception"' not in t and 'id="vRisk"' in t:
    t=t.replace('<div><label>Risk classification</label><input id="vRisk" placeholder="e.g. Moderate"></div>','<div><label>Risk classification</label><input id="vRisk" placeholder="e.g. Moderate"></div><div><label>Fund inception date <span class="muted">(optional)</span></label><input id="vInception" type="date"></div>',1)
    t=t.replace("line('Risk classification','vRisk'),line('TER','vTer')","line('Risk classification','vRisk'),line('Inception date','vInception'),line('TER','vTer')",1)
    t=t.replace("risk_level:'Risk classification',ter:'TER'","risk_level:'Risk classification',inception_date:'Fund inception',ter:'TER'",1)
q.write_text(t,encoding='utf-8')
print('Applied site finish V4')

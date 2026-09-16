#!/usr/bin/env python3
from pathlib import Path

root=Path(__file__).resolve().parents[1]
p=root/'docs'/'index.html'
s=p.read_text(encoding='utf-8')
marker='pending-batch-v1'
if marker in s:
    print('Pending batch V1 already present')
    raise SystemExit(0)

# Beginner wording and stable IDs.
s=s.replace('Your monthly investment plan — Year 1','Your monthly investment plan',1)
s=s.replace('<section class="card full" id="monthlyPlanSection">','<section class="card full" id="monthlyPlanSection">',1)

css=r'''
/* pending-batch-v1 */
.riskinputs .field label{min-height:34px;display:flex;align-items:flex-end;white-space:nowrap}
.planTools{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.themeSelect,.fundLimitSelect{padding:9px 11px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--text);font:inherit}
.planSoFar{position:sticky;top:8px;z-index:15;display:flex;align-items:center;justify-content:space-between;gap:10px;margin:12px 0;padding:10px 13px;border:1px solid var(--line);border-radius:12px;background:color-mix(in srgb,var(--card) 94%,var(--brand-soft));box-shadow:0 5px 18px rgba(0,0,0,.06)}.planSoFar b{color:var(--brand-strong)}.planSoFarText{font-size:13px;color:var(--muted)}
.fundLimitBox{margin-top:12px;padding:11px;border:1px solid var(--line);border-radius:11px;background:color-mix(in srgb,var(--card) 85%,var(--brand-soft))}.fundLimitBox label{display:block;font-weight:750;margin-bottom:6px}.fundLimitBox small{display:block;color:var(--muted);line-height:1.4;margin-top:6px}
.monthlyExplain{margin:-3px 0 13px;color:var(--muted);font-size:13px;line-height:1.45}
.planSummaryGrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.planSummaryItem{padding:12px;border:1px solid var(--line);border-radius:11px;background:var(--soft)}.planSummaryItem small{display:block;color:var(--muted);margin-bottom:4px}.planSummaryItem b{font-size:17px}.summaryFunds{margin-top:14px}.shareRow{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}.qrBox{display:none;margin-top:12px;padding:14px;border:1px solid var(--line);border-radius:12px;background:#fff;color:#111;width:max-content;max-width:100%}.qrBox.open{display:block}.qrBox img{display:block;width:180px;height:180px;max-width:100%}
html[data-theme="light"]{color-scheme:light;--bg:#f4f7f7;--card:#fff;--text:#172022;--muted:#667276;--line:#d8e1e2;--accent:#16715d;--accent2:#0f5b4b;--soft:#e7f3ef;--shadow:0 7px 28px rgba(0,0,0,.045);--brand:#0f766e;--brand-strong:#0b5f59;--brand-soft:#e8f6f3;--blue:#3b82f6;--blue-soft:#edf5ff;--green:#16865f;--green-soft:#eaf7f1;--amber:#b96d08;--amber-soft:#fff6e7;--violet:#7c5cc4;--violet-soft:#f4f0ff;--coral:#b95d54;--coral-soft:#fff0ee}
html[data-theme="dark"]{color-scheme:dark;--bg:#101718;--card:#182123;--text:#edf3f1;--muted:#9eacab;--line:#334044;--accent:#66d1b5;--accent2:#92e4cf;--soft:#203532;--shadow:none;--brand:#64d6bd;--brand-strong:#8ee8d3;--brand-soft:#1f3c37;--blue:#79aaff;--blue-soft:#1d2e46;--green:#66d1a8;--green-soft:#1d3930;--amber:#e2ad5e;--amber-soft:#40321f;--violet:#b09aee;--violet-soft:#302a48;--coral:#e29389;--coral-soft:#472b2a}
@media(max-width:760px){.planSummaryGrid{grid-template-columns:1fr 1fr}.planSoFar{position:static;align-items:flex-start;flex-direction:column}.riskinputs .field label{min-height:0}.planTools{width:100%}}
@media(max-width:460px){.planSummaryGrid{grid-template-columns:1fr}}
'''
s=s.replace('</style>',css+'\n</style>',1)

# Theme control and compact plan-so-far bar.
nav_end='</nav>'
if nav_end in s:
    s=s.replace(nav_end,'''<span class="planTools"><label class="mini muted" for="themeMode">Theme</label><select id="themeMode" class="themeSelect" aria-label="Colour theme"><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></span></nav><div class="planSoFar" id="planSoFar"><b>Your plan so far</b><span class="planSoFarText" id="planSoFarText">Build a portfolio below to see your plan summary.</span></div>''',1)

# Add maximum-fund control to builder section before result.
needle='<div class="resultbox"'
fundctl='''<div class="fundLimitBox"><label for="maxFunds">How many funds do you want to manage?</label><select id="maxFunds" class="fundLimitSelect"><option value="1">Maximum 1 fund</option><option value="2">Maximum 2 funds</option><option value="3">Maximum 3 funds</option><option value="4" selected>Maximum 4 funds</option><option value="5">Maximum 5 funds</option><option value="6">Maximum 6 funds</option><option value="0">No limit</option></select><small>Fewer funds are simpler to manage. More funds can spread your investment across a wider range of funds. The calculator will also respect known minimum investment amounts.</small></div>'''
if needle in s:s=s.replace(needle,fundctl+needle,1)

# Explain first year beneath monthly plan heading.
needle='id="monthlyPlanSection"'
pos=s.find(needle)
if pos>=0:
    h=s.find('</div>',pos)
    if h>=0:s=s[:h+6]+'<p class="monthlyExplain">What to invest each month during your first year. Your monthly amount may increase in future years based on the annual increase you selected.</p>'+s[h+6:]

# Step 6 summary before history/research section.
anchor='<section class="card full" id="historySection">'
summary='''<section class="card full" id="planSummarySection"><div class="sectiontitle"><h2>Your investment plan summary</h2><span class="muted">A quick take-away from Steps 1–5</span></div><div class="planSummaryGrid" id="planSummaryGrid"></div><div class="summaryFunds" id="summaryFunds"></div><p class="note" id="shareDataNote"></p><div class="shareRow"><button class="btn primary" id="downloadPlanPdf" type="button">Download investment plan PDF</button><button class="btn" id="copyPlanLink" type="button">Copy plan link</button><button class="btn" id="showPlanQr" type="button">Show QR code</button></div><div class="qrBox" id="qrBox"><img id="qrImage" alt="QR code for this investment plan"><div class="mini">Scan to open this plan on another device.</div></div></section>'''
if anchor in s:s=s.replace(anchor,summary+anchor,1)

js=r'''
<script>
/* pending-batch-v1 */
(function(){
 const byId=id=>document.getElementById(id), num=id=>Number(byId(id)?.value||0), money=n=>new Intl.NumberFormat('en-ZA',{style:'currency',currency:'ZAR',maximumFractionDigits:0}).format(Number(n)||0);
 const theme=byId('themeMode'); function applyTheme(v){document.documentElement.dataset.theme=v==='system'?'':v;localStorage.setItem('shariahTheme',v)} if(theme){theme.value=localStorage.getItem('shariahTheme')||'system';applyTheme(theme.value);theme.addEventListener('change',()=>applyTheme(theme.value))}
 function limitPortfolio(p){const n=Number(byId('maxFunds')?.value||0);if(!p||!Array.isArray(p.rows)||!n||p.rows.length<=n)return p;const q={...p,rows:[...p.rows].sort((a,b)=>(Number(b.weight)||0)-(Number(a.weight)||0)).slice(0,n)};const tw=q.rows.reduce((a,r)=>a+(Number(r.weight)||0),0)||1;q.rows=q.rows.map(r=>({...r,weight:(Number(r.weight)||0)/tw*100}));if(typeof window.planningReturn==='function')q.estimate=q.rows.reduce((a,r)=>a+(Number(r.weight)||0)/100*window.planningReturn(r.fund),0);q.fundLimitAdjusted=true;return q}
 if(typeof window.displayRecommendation==='function'){const old=window.displayRecommendation;window.displayRecommendation=function(title,p,detail){const q=limitPortfolio(p);const n=Number(byId('maxFunds')?.value||0);const extra=q?.fundLimitAdjusted?` Limited to ${n} fund${n===1?'':'s'} and rebalanced to the closest practical mix.`:'';return old(title,q,(detail||'')+extra)}}
 function payload(){const p=window.selectedPortfolio;return {v:1,created:new Date().toISOString().slice(0,10),monthly:num('monthly'),increase:num('increase'),years:num('years'),risk:[num('lowRisk'),num('mediumRisk'),num('highRisk')],target:num('targetReturn'),maxFunds:Number(byId('maxFunds')?.value||0),scenario:[num('r1'),num('r2'),num('r3')],funds:(p?.rows||[]).map(r=>({id:r.fund?.id,w:+Number(r.weight||0).toFixed(3)}))}}
 function encodePlan(o){return btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')}
 function decodePlan(x){try{return JSON.parse(decodeURIComponent(escape(atob(x.replace(/-/g,'+').replace(/_/g,'/')))))}catch(e){return null}}
 function shareUrl(){const u=new URL(location.href);u.hash='plan='+encodePlan(payload());return u.toString()}
 function restore(){const m=location.hash.match(/(?:^#|&)plan=([^&]+)/);if(!m)return;const o=decodePlan(m[1]);if(!o)return;[['monthly',o.monthly],['increase',o.increase],['years',o.years],['lowRisk',o.risk?.[0]],['mediumRisk',o.risk?.[1]],['highRisk',o.risk?.[2]],['targetReturn',o.target],['maxFunds',o.maxFunds],['r1',o.scenario?.[0]],['r2',o.scenario?.[1]],['r3',o.scenario?.[2]]].forEach(([id,v])=>{const e=byId(id);if(e&&v!=null)e.value=v});document.querySelectorAll('#monthly,#increase,#years,#lowRisk,#mediumRisk,#highRisk,#targetReturn,#maxFunds,#r1,#r2,#r3').forEach(e=>e.dispatchEvent(new Event('change',{bubbles:true})));const n=byId('shareDataNote');if(n)n.textContent=`Shared plan created ${o.created||'previously'}. Fund data may have changed since the plan was created.`}
 function updateSummary(){const p=window.selectedPortfolio, monthly=num('monthly'), years=num('years'), inc=num('increase'), exp=Number(p?.estimate||num('r2')),max=Number(byId('maxFunds')?.value||0);const g=byId('planSummaryGrid');if(g)g.innerHTML=`<div class="planSummaryItem"><small>Starting monthly investment</small><b>${money(monthly)}</b></div><div class="planSummaryItem"><small>Investment period</small><b>${years} years</b></div><div class="planSummaryItem"><small>Annual increase</small><b>${inc.toFixed(1)}%</b></div><div class="planSummaryItem"><small>Funds to manage</small><b>${max?`Maximum ${max}`:'No limit'}</b></div><div class="planSummaryItem"><small>Risk mix</small><b>${num('lowRisk')} / ${num('mediumRisk')} / ${num('highRisk')}</b></div><div class="planSummaryItem"><small>Cautious scenario</small><b>${num('r1').toFixed(1)}%</b></div><div class="planSummaryItem"><small>Expected scenario</small><b>${exp.toFixed(1)}%</b></div><div class="planSummaryItem"><small>Optimistic scenario</small><b>${num('r3').toFixed(1)}%</b></div>`;const sf=byId('summaryFunds');if(sf)sf.innerHTML=p?.rows?.length?`<h3>Selected funds</h3><table><thead><tr><th>Fund</th><th>Portfolio %</th><th>Approx. monthly</th></tr></thead><tbody>${p.rows.map(r=>`<tr><td>${r.fund?.name||'Fund'}</td><td>${Number(r.weight||0).toFixed(1)}%</td><td>${money(monthly*Number(r.weight||0)/100)}</td></tr>`).join('')}</tbody></table>`:'<p class="muted">Choose a portfolio in Step 1 to populate the selected funds.</p>';const top=byId('planSoFarText');if(top)top.textContent=p?`${money(monthly)}/month • ${years} years • Expected ${exp.toFixed(1)}% • ${max?`max ${max} fund${max===1?'':'s'}`:'no fund limit'}`:`${money(monthly)}/month • ${years} years • choose a portfolio in Step 1`}
 ['monthly','increase','years','lowRisk','mediumRisk','highRisk','targetReturn','maxFunds','r1','r2','r3'].forEach(id=>byId(id)?.addEventListener('input',()=>requestAnimationFrame(updateSummary)));['buildRisk','buildTarget','buildAdvisable'].forEach(id=>byId(id)?.addEventListener('click',()=>setTimeout(updateSummary,0)));
 byId('copyPlanLink')?.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(shareUrl());byId('copyPlanLink').textContent='Plan link copied ✓';setTimeout(()=>byId('copyPlanLink').textContent='Copy plan link',1800)}catch(e){prompt('Copy this plan link:',shareUrl())}});
 byId('showPlanQr')?.addEventListener('click',()=>{const box=byId('qrBox'),img=byId('qrImage');box?.classList.toggle('open');if(img&&box?.classList.contains('open'))img.src='https://api.qrserver.com/v1/create-qr-code/?size=220x220&data='+encodeURIComponent(shareUrl())});
 byId('downloadPlanPdf')?.addEventListener('click',()=>window.print());
 restore();updateSummary();
})();
</script>
'''
s=s.replace('</body>',js+'\n</body>',1)
# Step 6 badge after UI polish CSS.
s=s.replace('#milestonesSection .sectiontitle h2::before{content:\'STEP 5\';background:var(--amber-soft);color:var(--amber)}','#milestonesSection .sectiontitle h2::before{content:\'STEP 5\';background:var(--amber-soft);color:var(--amber)}\n#planSummarySection .sectiontitle h2::before{content:\'STEP 6\';background:var(--brand-soft);color:var(--brand-strong)}',1)
# Print-friendly PDF output from static browser.
s=s.replace('</style>','''@media print{body{background:#fff!important;color:#111!important}main>*{display:none!important}#planSummarySection{display:block!important;border:0!important;box-shadow:none!important}#planSummarySection .shareRow,#qrBox{display:none!important}.planSummaryItem{break-inside:avoid;background:#fff!important}.sectiontitle h2::before{content:"INVESTMENT PLAN"!important} }\n</style>''',1)
p.write_text(s,encoding='utf-8')
print('Applied pending UI batch V1')

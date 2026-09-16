#!/usr/bin/env python3
from pathlib import Path

root=Path(__file__).resolve().parents[1]
index=root/'docs'/'index.html'
s=index.read_text(encoding='utf-8')
if 'site-ui-v2' not in s:
    css=r'''
/* site-ui-v2 */
.riskinputs .term{white-space:nowrap}.riskinputs .field label{min-height:34px;display:flex;align-items:flex-end}
#planSoFar{min-height:70px;padding:14px 18px;cursor:pointer;border-color:color-mix(in srgb,var(--brand) 25%,var(--line));transition:transform .12s ease,border-color .12s ease,box-shadow .12s ease}#planSoFar:hover{transform:translateY(-1px);border-color:var(--brand);box-shadow:0 8px 22px rgba(0,0,0,.08)}#planSoFar .planSoFarLeft{display:flex;flex-direction:column;gap:4px}#planSoFar .planSoFarTitle{font-size:15px;font-weight:850;color:var(--brand-strong)}#planSoFar .planSoFarText{font-size:14px;color:var(--text)}#planSoFar .planSoFarCta{font-weight:800;color:var(--brand-strong);white-space:nowrap}
.inputs .fundLimitBox{margin:14px 0}.inputs .fundLimitSelect{min-width:220px}
#planSummarySection{border-top:4px solid var(--brand)}
@media(max-width:760px){#planSoFar{align-items:flex-start}.riskinputs .field label{min-height:0}}
'''
    s=s.replace('</style>',css+'\n</style>',1)
    js=r'''
<script>
/* site-ui-v2 */
(function(){
 const byId=id=>document.getElementById(id), money=n=>new Intl.NumberFormat('en-ZA',{style:'currency',currency:'ZAR',maximumFractionDigits:0}).format(Number(n)||0);
 function selected(){try{return typeof selectedPortfolio!=='undefined'?selectedPortfolio:null}catch(e){return null}}
 function moveFundLimit(){const box=document.querySelector('.fundLimitBox'),inputs=document.querySelector('.inputs');if(!box||!inputs)return;const scenario=[...inputs.querySelectorAll('h3,h2')].find(x=>x.textContent.includes('Future return scenarios'));if(scenario)scenario.parentNode.insertBefore(box,scenario);else inputs.appendChild(box)}
 function orderSections(){const grid=document.querySelector('.grid'),growth=byId('growthSection'),milestones=byId('milestonesSection'),summary=byId('planSummarySection'),history=byId('historySection');if(!grid||!summary)return;if(growth&&milestones){grid.insertBefore(growth,summary);grid.insertBefore(milestones,summary)}if(history)grid.insertBefore(history,summary);grid.appendChild(summary)}
 function quickCard(){const c=byId('planSoFar');if(!c)return;c.setAttribute('role','button');c.tabIndex=0;c.innerHTML='<div class="planSoFarLeft"><span class="planSoFarTitle">Your plan so far</span><span class="planSoFarText" id="planSoFarText">Choose a portfolio in Step 1 to build your summary.</span></div><span class="planSoFarCta">View full summary →</span>';const go=()=>byId('planSummarySection')?.scrollIntoView({behavior:'smooth',block:'start'});c.onclick=go;c.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();go()}}}
 function sync(){const p=selected(),monthly=Number(byId('monthly')?.value||0),years=Number(byId('years')?.value||20),inc=Number(byId('increase')?.value||0),max=Number(byId('maxFunds')?.value||0);let low=Number(byId('riskLow')?.value||0),med=Number(byId('riskMedium')?.value||0),high=Number(byId('riskHigh')?.value||0);if(p?.mix){low=Number(p.mix.Low||0);med=Number(p.mix.Medium||0);high=Number(p.mix.High||0)}const expected=Number(p?.estimate??byId('r2')?.value??0),caut=Number(byId('r1')?.value||Math.max(0,expected-2)),opt=Number(byId('r3')?.value||expected+2);const q=byId('planSoFarText');if(q)q.textContent=p?`${money(monthly)}/month • ${years} years • Expected ${expected.toFixed(1)}% • ${max?`max ${max} fund${max===1?'':'s'}`:'no fund limit'}`:`${money(monthly)}/month • ${years} years • choose a portfolio in Step 1`;const g=byId('planSummaryGrid');if(g)g.innerHTML=`<div class="planSummaryItem"><small>Starting monthly investment</small><b>${money(monthly)}</b></div><div class="planSummaryItem"><small>Investment period</small><b>${years} years</b></div><div class="planSummaryItem"><small>Annual increase</small><b>${inc.toFixed(1)}%</b></div><div class="planSummaryItem"><small>Funds to manage</small><b>${max?`Maximum ${max}`:'No limit'}</b></div><div class="planSummaryItem"><small>Risk mix</small><b>${low.toFixed(0)} / ${med.toFixed(0)} / ${high.toFixed(0)}</b></div><div class="planSummaryItem"><small>Cautious scenario</small><b>${caut.toFixed(1)}%</b></div><div class="planSummaryItem"><small>Expected scenario</small><b>${expected.toFixed(1)}%</b></div><div class="planSummaryItem"><small>Optimistic scenario</small><b>${opt.toFixed(1)}%</b></div>`;const sf=byId('summaryFunds');if(sf)sf.innerHTML=p?.rows?.length?`<h3>Selected funds</h3><table><thead><tr><th>Fund</th><th>Portfolio %</th><th>Approx. monthly</th></tr></thead><tbody>${p.rows.map(r=>{const w=Number(r.weight||0);const pct=w<=1?w*100:w;return `<tr><td>${r.fund?.name||'Fund'}</td><td>${pct.toFixed(1)}%</td><td>${money(monthly*pct/100)}</td></tr>`}).join('')}</tbody></table>`:'<p class="muted">Choose a portfolio in Step 1 to populate the selected funds.</p>'}
 moveFundLimit();orderSections();quickCard();sync();
 ['monthly','increase','years','riskLow','riskMedium','riskHigh','maxFunds','r1','r2','r3'].forEach(id=>byId(id)?.addEventListener('input',()=>requestAnimationFrame(sync)));['buildRisk','buildTarget','buildAdvisable'].forEach(id=>byId(id)?.addEventListener('click',()=>setTimeout(sync,20)));
 new MutationObserver(()=>requestAnimationFrame(sync)).observe(byId('portfolioResult')||document.body,{childList:true,subtree:true});
})();
</script>
'''
    s=s.replace('</body>',js+'\n</body>',1)
    index.write_text(s,encoding='utf-8')

# Shared theme injector for secondary pages.
theme_css='''\n<style id="siteThemeV2">html[data-theme="light"]{color-scheme:light;--bg:#f4f7f7;--card:#fff;--text:#172022;--muted:#667276;--line:#d8e1e2;--accent:#16715d;--soft:#e7f3ef}html[data-theme="dark"]{color-scheme:dark;--bg:#101718;--card:#182123;--text:#edf3f1;--muted:#9eacab;--line:#334044;--accent:#66d1b5;--soft:#203532}.themeControl{display:inline-flex;align-items:center;gap:6px;margin-left:auto}.themeControl label{font-size:12px;color:var(--muted)}.themeControl select{padding:8px 10px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--text)}\n</style>'''
theme_js='''<script id="siteThemeScriptV2">(function(){const saved=localStorage.getItem('shariahTheme')||'system';document.documentElement.dataset.theme=saved==='system'?'':saved;const nav=document.querySelector('.nav,.top');if(nav&&!document.getElementById('themeMode')){const w=document.createElement('span');w.className='themeControl';w.innerHTML='<label for="themeMode">Theme</label><select id="themeMode"><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select>';nav.appendChild(w);const s=w.querySelector('select');s.value=saved;s.onchange=()=>{localStorage.setItem('shariahTheme',s.value);document.documentElement.dataset.theme=s.value==='system'?'':s.value}}})();</script>'''
for name in ['fund-explorer.html','add-fund.html','fund-details.html']:
    q=root/'docs'/name
    if not q.exists(): continue
    t=q.read_text(encoding='utf-8')
    if 'siteThemeV2' not in t:t=t.replace('</head>',theme_css+'\n</head>',1)
    if 'siteThemeScriptV2' not in t:t=t.replace('</body>',theme_js+'\n</body>',1)
    q.write_text(t,encoding='utf-8')
print('Applied site UI V2')

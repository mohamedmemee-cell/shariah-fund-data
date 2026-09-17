#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'docs'/'index.html'
MARKER='summary-fund-risk-v31'
s=INDEX.read_text(encoding='utf-8')
if MARKER in s:
    print('V31 already present')
    raise SystemExit(0)

css=r'''
/* summary-fund-risk-v31 */
#summaryFunds table th:nth-child(2),#summaryFunds table td:nth-child(2){text-align:left}
.riskPillV31{display:inline-block;padding:4px 8px;border-radius:999px;font-size:11px;font-weight:850;border:1px solid var(--line);background:var(--soft);color:var(--text);white-space:nowrap}
.riskPillV31.low{background:var(--green-soft);color:var(--green)}
.riskPillV31.medium{background:var(--amber-soft);color:var(--amber)}
.riskPillV31.high{background:var(--coral-soft);color:var(--coral)}
'''
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
<script>
/* summary-fund-risk-v31 */
(function(){
 const byId=id=>document.getElementById(id);
 const money=n=>new Intl.NumberFormat('en-ZA',{style:'currency',currency:'ZAR',maximumFractionDigits:0}).format(Number(n)||0);
 function selected(){try{return typeof selectedPortfolio!=='undefined'?selectedPortfolio:null}catch(e){return null}}
 function riskLabel(r){
   const raw=(r?.band||r?.fund?.calculator_risk_band||r?.fund?.risk_level||'Not confirmed').toString();
   const x=raw.toLowerCase();
   const cls=x.includes('low')||x.includes('conservative')?'low':x.includes('medium')||x.includes('moderate')?'medium':x.includes('high')||x.includes('aggressive')?'high':'';
   return `<span class="riskPillV31 ${cls}">${raw}</span>`;
 }
 function render(){
   const sf=byId('summaryFunds'),p=selected(),monthly=Number(byId('monthly')?.value||0);
   if(!sf||!p?.rows?.length)return;
   sf.innerHTML=`<h3>Selected funds</h3><table><thead><tr><th>Fund</th><th>Risk</th><th>Portfolio %</th><th>Approx. monthly</th></tr></thead><tbody>${p.rows.map(r=>{const w=Number(r.weight||0),pct=w<=1?w*100:w;return `<tr><td>${r.fund?.name||'Fund'}</td><td>${riskLabel(r)}</td><td>${pct.toFixed(1)}%</td><td>${money(monthly*pct/100)}</td></tr>`}).join('')}</tbody></table>`;
 }
 ['monthly','riskLow','riskMedium','riskHigh','targetReturn','maxFunds'].forEach(id=>byId(id)?.addEventListener('input',()=>setTimeout(render,20)));
 ['buildRisk','buildTarget','buildAdvisable'].forEach(id=>byId(id)?.addEventListener('click',()=>setTimeout(render,60)));
 const target=byId('summaryFunds');if(target)new MutationObserver(()=>{if(!target.querySelector('th:nth-child(2)')?.textContent.includes('Risk'))setTimeout(render,0)}).observe(target,{childList:true,subtree:true});
 setTimeout(render,100);
})();
</script>
'''
s=s.replace('</body>',js+'\n<!-- '+MARKER+' -->\n</body>',1)
INDEX.write_text(s,encoding='utf-8')
print('Added fund risk to Step 6 selected-funds summary')

#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / 'docs' / 'index.html'
s = p.read_text(encoding='utf-8')
marker = 'step6-risk-explanation-v9'
if marker in s:
    print('Step 6 risk explanation V9 already present')
    raise SystemExit(0)

css = r'''
/* step6-risk-explanation-v9 */
.riskExplainV9{margin:12px 0 4px;padding:14px;border:1px solid var(--line);border-radius:13px;background:color-mix(in srgb,var(--card) 88%,var(--brand-soft))}
.riskExplainGridV9{display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:stretch}.riskExplainCardV9{padding:12px;border:1px solid var(--line);border-radius:11px;background:var(--card)}.riskExplainCardV9 small{display:block;color:var(--muted);margin-bottom:5px}.riskExplainCardV9 b{font-size:16px;line-height:1.35}.riskExplainArrowV9{display:grid;place-items:center;color:var(--muted);font-weight:900;font-size:20px}.riskExplainWhyV9{margin:11px 0 0;font-size:13px;line-height:1.5;color:var(--muted)}.riskExplainWhyV9 strong{color:var(--text)}
@media(max-width:700px){.riskExplainGridV9{grid-template-columns:1fr}.riskExplainArrowV9{transform:rotate(90deg);min-height:18px}}
'''
s = s.replace('</style>', css + '\n</style>', 1)

js = r'''
<script>
/* step6-risk-explanation-v9 */
(function(){
 const byId=id=>document.getElementById(id);
 function selected(){try{return typeof selectedPortfolio!=='undefined'?selectedPortfolio:null}catch(e){return null}}
 function title(){try{return String(selectedPortfolioTitle||'')}catch(e){return ''}}
 function mixText(m){return `${Number(m?.Low||0).toFixed(0)}% Low · ${Number(m?.Medium||0).toFixed(0)}% Medium · ${Number(m?.High||0).toFixed(0)}% High`}
 function inputMix(){return {Low:Number(byId('riskLow')?.value||0),Medium:Number(byId('riskMedium')?.value||0),High:Number(byId('riskHigh')?.value||0)}}
 function maxFundsText(){const n=Number(byId('maxFunds')?.value||0);return n?`maximum ${n} fund${n===1?'':'s'}`:'no fund limit'}
 function ensureBox(){
   const grid=byId('planSummaryGrid'); if(!grid)return null;
   let box=byId('riskExplanationV9');
   if(!box){box=document.createElement('div');box.id='riskExplanationV9';box.className='riskExplainV9';const old=byId('riskMixExplanationV8');if(old)old.replaceWith(box);else grid.insertAdjacentElement('afterend',box)}
   return box;
 }
 function render(){
   const box=ensureBox(); if(!box)return;
   const p=selected();
   if(!p?.mix){box.innerHTML='<p class="riskExplainWhyV9">Build a portfolio in Step 1 and the calculator will explain here how the final risk mix was reached.</p>';return}
   const t=title().toLowerCase(), actual=mixText(p.mix), reasons=[];
   let leftLabel='Portfolio Builder choice',leftValue='—';
   if(t.includes('target')){
     leftLabel='Portfolio Builder choice';
     leftValue=`Target return ${Number(byId('targetReturn')?.value||0).toFixed(1)}%`;
     reasons.push('Target-return mode searches different Low, Medium and High combinations to find the closest historical planning return. It does not lock the portfolio to the 20 / 60 / 20 guide mix.');
   }else if(t.includes('system advisable')||t.includes('advisable')){
     leftLabel='Portfolio Builder starting mix';leftValue='20% Low · 60% Medium · 20% High';
   }else if(t.includes('risk split')){
     leftLabel='Portfolio Builder requested mix';leftValue=mixText(inputMix());
   }else if(t.includes('shared')){
     leftLabel='Shared portfolio settings';leftValue=mixText(p.mix);
   }else{
     leftLabel='Portfolio Builder mix';leftValue=mixText(inputMix());
   }
   if(p.fundLimitAdjusted)reasons.push(`Your ${maxFundsText()} setting required the calculator to reduce the number of investment schemes while preserving the risk bands as closely as possible.`);
   if(p.practicalAdjusted||p.riskMixAdjusted)reasons.push('Known minimum monthly investment amounts required some allocations to be rebalanced so the suggested monthly amounts are actually investable.');
   if(!reasons.length){
     const base=(t.includes('advisable')?{Low:20,Medium:60,High:20}:t.includes('risk split')?inputMix():p.mix);
     const changed=['Low','Medium','High'].some(k=>Math.abs(Number(base[k]||0)-Number(p.mix[k]||0))>.6);
     reasons.push(changed?'The final mix reflects the funds that remained after the calculator applied your portfolio constraints.':'The final portfolio still matches the Portfolio Builder risk mix; no material risk-band adjustment was required.');
   }
   box.innerHTML=`<div class="riskExplainGridV9"><div class="riskExplainCardV9"><small>${leftLabel}</small><b>${leftValue}</b></div><div class="riskExplainArrowV9" aria-hidden="true">→</div><div class="riskExplainCardV9"><small>Final portfolio risk mix</small><b>${actual}</b></div></div><p class="riskExplainWhyV9"><strong>Why can these be different?</strong> ${reasons.join(' ')}</p>`;
 }
 ['buildRisk','buildTarget','buildAdvisable'].forEach(id=>byId(id)?.addEventListener('click',()=>setTimeout(render,120)));
 ['riskLow','riskMedium','riskHigh','targetReturn','maxFunds','monthly'].forEach(id=>{const e=byId(id);if(e){e.addEventListener('input',()=>requestAnimationFrame(render));e.addEventListener('change',()=>requestAnimationFrame(render))}});
 const root=byId('portfolioResult')||document.body;new MutationObserver(()=>requestAnimationFrame(render)).observe(root,{childList:true,subtree:true});
 setTimeout(render,350);
})();
</script>
'''
s = s.replace('</body>', js + '\n</body>', 1)
p.write_text(s, encoding='utf-8')
print('Applied Step 6 risk explanation V9')

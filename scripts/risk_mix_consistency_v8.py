#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / 'docs' / 'index.html'
s = p.read_text(encoding='utf-8')
marker = 'risk-mix-consistency-v8'
if marker in s:
    print('Risk mix consistency V8 already present')
    raise SystemExit(0)

# Replace the old max-fund limiter. The old implementation simply kept the N
# largest individual fund weights across all risk bands and then renormalised
# them. That could destroy the requested risk mix. It also left p.mix stale.
old = """function limitPortfolio(p){const n=Number(byId('maxFunds')?.value||0);if(!p||!Array.isArray(p.rows)||!n||p.rows.length<=n)return p;const q={...p,rows:[...p.rows].sort((a,b)=>(Number(b.weight)||0)-(Number(a.weight)||0)).slice(0,n)};const tw=q.rows.reduce((a,r)=>a+(Number(r.weight)||0),0)||1;q.rows=q.rows.map(r=>({...r,weight:(Number(r.weight)||0)/tw*100}));if(typeof window.planningReturn==='function')q.estimate=q.rows.reduce((a,r)=>a+(Number(r.weight)||0)/100*window.planningReturn(r.fund),0);q.fundLimitAdjusted=true;return q}"""
new = """function limitPortfolio(p){
  const n=Number(byId('maxFunds')?.value||0);
  if(!p||!Array.isArray(p.rows)||!p.rows.length)return p;
  const normaliseWeight=w=>{w=Number(w)||0;return w>1?w/100:w};
  const sourceRows=p.rows.map(r=>({...r,weight:normaliseWeight(r.weight)}));
  const targetMix={Low:Number(p.mix?.Low||0),Medium:Number(p.mix?.Medium||0),High:Number(p.mix?.High||0)};
  let rows=sourceRows;
  let limited=false;
  if(n&&rows.length>n){
    limited=true;
    const bands=['Low','Medium','High'];
    const nonZero=bands.filter(b=>targetMix[b]>0&&rows.some(r=>r.band===b));
    const selected=[];
    // When the fund limit allows it, keep at least one representative from
    // every active risk band. This stops a global top-N cut from deleting an
    // entire band such as Medium.
    if(n>=nonZero.length){
      nonZero.forEach(b=>{const candidates=rows.filter(r=>r.band===b).sort((a,b)=>b.weight-a.weight);if(candidates[0])selected.push(candidates[0])});
      const rest=rows.filter(r=>!selected.includes(r)).sort((a,b)=>b.weight-a.weight);
      while(selected.length<n&&rest.length)selected.push(rest.shift());
    }else{
      // If the user asks for fewer funds than active bands, keeping every band
      // is mathematically impossible. Keep the largest requested bands and
      // report the resulting actual mix rather than pretending the old mix survived.
      const keepBands=[...nonZero].sort((a,b)=>targetMix[b]-targetMix[a]).slice(0,n);
      keepBands.forEach(b=>{const candidates=rows.filter(r=>r.band===b).sort((a,b)=>b.weight-a.weight);if(candidates[0])selected.push(candidates[0])});
    }
    rows=selected;
  }
  // Rebuild weights. If every requested band survived, preserve the requested
  // band totals and only redistribute within each band. Otherwise normalise
  // surviving rows and calculate the actual mix from them.
  const survivingBands=new Set(rows.map(r=>r.band));
  const requestedBands=['Low','Medium','High'].filter(b=>targetMix[b]>0);
  const canPreserve=requestedBands.every(b=>survivingBands.has(b));
  if(canPreserve){
    ['Low','Medium','High'].forEach(b=>{const group=rows.filter(r=>r.band===b);if(!group.length)return;const total=group.reduce((a,r)=>a+r.weight,0)||group.length;group.forEach(r=>{r.weight=(targetMix[b]/100)*(total? r.weight/total : 1/group.length)})});
  }else{
    const total=rows.reduce((a,r)=>a+r.weight,0)||1;rows.forEach(r=>r.weight/=total);
  }
  const actualMix={Low:0,Medium:0,High:0};rows.forEach(r=>{actualMix[r.band]=(actualMix[r.band]||0)+r.weight*100});
  const pr=f=>{const x=planningReturn(f);return typeof x==='number'?x:Number(x?.value||0)};
  const estimate=rows.reduce((a,r)=>a+r.weight*pr(r.fund),0);
  const quality=rows.reduce((a,r)=>a+r.weight*(typeof dataQuality==='function'?dataQuality(r.fund):0),0);
  const terCoverage=rows.filter(r=>r.fund?.ter!=null).reduce((a,r)=>a+r.weight,0);
  const ter=terCoverage?rows.filter(r=>r.fund?.ter!=null).reduce((a,r)=>a+r.weight*Number(r.fund.ter),0)/terCoverage:null;
  return {...p,rows,mix:actualMix,estimate,quality,terCoverage,ter,fundLimitAdjusted:limited};
}"""
if old not in s:
    raise SystemExit('Could not find old max-fund limiter; refusing partial risk-mix patch')
s = s.replace(old, new, 1)

# Fix sharing code to use the real risk input IDs and save the actual selected
# portfolio mix when a portfolio exists.
s = s.replace("risk:[num('lowRisk'),num('mediumRisk'),num('highRisk')]", "risk:p?.mix?[Number(p.mix.Low||0),Number(p.mix.Medium||0),Number(p.mix.High||0)]:[num('riskLow'),num('riskMedium'),num('riskHigh')]", 1)
s = s.replace("['lowRisk',o.risk?.[0]],['mediumRisk',o.risk?.[1]],['highRisk',o.risk?.[2]]", "['riskLow',o.risk?.[0]],['riskMedium',o.risk?.[1]],['riskHigh',o.risk?.[2]]", 1)
s = s.replace("#lowRisk,#mediumRisk,#highRisk", "#riskLow,#riskMedium,#riskHigh", 1)

# The older Step 6 renderer used the wrong IDs. Keep it accurate even before
# the later site-wide summary synchroniser runs.
s = s.replace("<small>Risk mix</small><b>${num('lowRisk')} / ${num('mediumRisk')} / ${num('highRisk')}</b>", "<small>Portfolio risk mix</small><b>${p?.mix?`${Number(p.mix.Low||0).toFixed(0)}% Low · ${Number(p.mix.Medium||0).toFixed(0)}% Medium · ${Number(p.mix.High||0).toFixed(0)}% High`:`${num('riskLow').toFixed(0)}% Low · ${num('riskMedium').toFixed(0)}% Medium · ${num('riskHigh').toFixed(0)}% High`}</b>", 1)
s = s.replace("['monthly','increase','years','lowRisk','mediumRisk','highRisk','targetReturn','maxFunds','r1','r2','r3']", "['monthly','increase','years','riskLow','riskMedium','riskHigh','targetReturn','maxFunds','r1','r2','r3']", 1)

# Patch the later Step 6 synchroniser so it clearly labels the numbers as the
# ACTUAL final portfolio mix after fund-limit and minimum-investment rules.
s = s.replace('<small>Risk mix</small><b>${low.toFixed(0)} / ${med.toFixed(0)} / ${high.toFixed(0)}</b>', '<small>Portfolio risk mix</small><b>${low.toFixed(0)}% Low · ${med.toFixed(0)}% Medium · ${high.toFixed(0)}% High</b>', 1)

# Practicalisation can remove a fund that falls below a known minimum. Always
# recompute the displayed mix from final rows and retain a clear flag when the
# result differs from the requested model.
old_practical = """const sum=rows.reduce((a,r)=>a+r.amount,0)||1;rows.forEach(r=>r.weight=r.amount/sum);const mix={Low:0,Medium:0,High:0};rows.forEach(r=>mix[r.band]=(mix[r.band]||0)+r.weight*100);const estimate=rows.reduce((a,r)=>a+r.weight*planReturn(r.fund),0);return {...p,rows,mix,estimate,practicalAdjusted:changed}"""
new_practical = """const sum=rows.reduce((a,r)=>a+r.amount,0)||1;rows.forEach(r=>r.weight=r.amount/sum);const mix={Low:0,Medium:0,High:0};rows.forEach(r=>mix[r.band]=(mix[r.band]||0)+r.weight*100);const estimate=rows.reduce((a,r)=>a+r.weight*planReturn(r.fund),0);const requested=p.mix||{};const riskMixAdjusted=['Low','Medium','High'].some(b=>Math.abs(Number(mix[b]||0)-Number(requested[b]||0))>.5);return {...p,rows,mix,estimate,practicalAdjusted:changed,riskMixAdjusted}"""
if old_practical in s:
    s = s.replace(old_practical, new_practical, 1)

# Explain target-return behaviour in plain language: unlike Choose your risk
# split, target-return search is allowed to move the risk mix to get closest to
# the requested historical planning return.
s = s.replace('The calculator searched 5% risk-band combinations and selected the closest historical-planning result', 'The calculator searched different Low / Medium / High mixes in 5% steps and selected the mix whose historical planning return is closest to your target', 1)

# Add a small actual-mix note under the Step 6 grid when constraints changed it.
insert = r'''
<script>
/* risk-mix-consistency-v8 */
(function(){
 const byId=id=>document.getElementById(id);
 function selected(){try{return typeof selectedPortfolio!=='undefined'?selectedPortfolio:null}catch(e){return null}}
 function ensureMixNote(){
   const p=selected(),grid=byId('planSummaryGrid');if(!grid)return;
   let note=byId('riskMixExplanationV8');
   if(!note){note=document.createElement('p');note.id='riskMixExplanationV8';note.className='note';grid.insertAdjacentElement('afterend',note)}
   if(!p?.mix){note.textContent='Portfolio risk mix will appear after you build a portfolio.';return}
   const actual=`${Number(p.mix.Low||0).toFixed(0)}% Low · ${Number(p.mix.Medium||0).toFixed(0)}% Medium · ${Number(p.mix.High||0).toFixed(0)}% High`;
   if((selectedPortfolioTitle||'').toLowerCase().includes('target')) note.textContent=`Actual final portfolio mix: ${actual}. Target-return mode is allowed to change the risk mix to get as close as possible to the return you entered.`;
   else if(p.riskMixAdjusted) note.textContent=`Actual final portfolio mix: ${actual}. It changed from the starting mix because a fund-limit or minimum-investment rule had to be applied.`;
   else note.textContent=`Actual final portfolio mix: ${actual}.`;
 }
 ['buildRisk','buildTarget','buildAdvisable'].forEach(id=>byId(id)?.addEventListener('click',()=>setTimeout(ensureMixNote,80)));
 new MutationObserver(()=>requestAnimationFrame(ensureMixNote)).observe(byId('portfolioResult')||document.body,{childList:true,subtree:true});
 setTimeout(ensureMixNote,250);
})();
</script>
'''
s = s.replace('</body>', insert + '\n</body>', 1)
s = s.replace('</style>', '\n/* risk-mix-consistency-v8 */\n#riskMixExplanationV8{margin:8px 0 0;font-size:12px;color:var(--muted);line-height:1.45}\n</style>', 1)

p.write_text(s, encoding='utf-8')
print('Applied risk mix consistency V8')

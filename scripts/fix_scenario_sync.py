#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'docs' / 'index.html'
s = p.read_text(encoding='utf-8')

# Fix a subtle bug in the V2 practical-allocation return calculation:
# Number(null) is 0, so missing 3Y/5Y/10Y values were being treated as 0% returns.
# That could turn a target portfolio around 10.5% into a displayed expected scenario
# around 5-6%. Use the same weights and null handling as the calculator's canonical
# planningReturn() function.
old = "function planReturn(f){const vals=[[f.tenYear,.35],[f.fiveYear,.35],[f.threeYear,.2],[f.oneYear,.1],[f.sinceInception,.15]].filter(x=>Number.isFinite(Number(x[0])));if(!vals.length)return 0;const tw=vals.reduce((a,x)=>a+x[1],0);return vals.reduce((a,x)=>a+Number(x[0])*x[1],0)/tw}"
new = "function planReturn(f){const vals=[[f.tenYear,.35],[f.fiveYear,.30],[f.threeYear,.20],[f.oneYear,.10],[f.sinceInception,.05]].filter(x=>x[0]!=null&&x[0]!==''&&Number.isFinite(Number(x[0])));if(!vals.length)return 0;const tw=vals.reduce((a,x)=>a+x[1],0);return vals.reduce((a,x)=>a+Number(x[0])*x[1],0)/tw}"
if old in s:
    s = s.replace(old, new, 1)

# When minimum-investment rules rebalance a target-return portfolio, the final
# practical portfolio can differ slightly from the theoretical search result.
# Keep the validation message tied to the FINAL practical portfolio so the target
# message, scenario fields, graph and monthly plan all describe the same model.
old_wrap = "window.displayRecommendation=function(title,p,detail){const total=Math.max(0,+byId('monthly')?.value||0),q=practicalize(p,total);const extra=q?.practicalAdjusted?' The monthly plan was rebalanced to respect known R500 recurring minimums for applicable unit-trust funds.':'';return oldDisplay(title,q,(detail||'')+extra)};"
new_wrap = "window.displayRecommendation=function(title,p,detail){const total=Math.max(0,+byId('monthly')?.value||0),q=practicalize(p,total);const extra=q?.practicalAdjusted?' The monthly plan was rebalanced to respect known R500 recurring minimums for applicable unit-trust funds.':'';const result=oldDisplay(title,q,(detail||'')+extra);if(title==='Target-return search'){const target=Math.max(0,Math.min(30,+byId('targetReturn')?.value||0)),distance=Math.abs(Number(q?.estimate||0)-target),v=byId('targetValidation');if(v){const exact=distance<=.35;v.innerHTML=exact?`<span class=\"ok\">Final practical portfolio is within ${distance.toFixed(2)} percentage points of your target.</span>`:`<span class=\"warn\">Closest practical portfolio is ${Number(q?.estimate||0).toFixed(2)}%, ${distance.toFixed(2)} points from your target.</span>`}}return result};"
if old_wrap in s:
    s = s.replace(old_wrap, new_wrap, 1)

# Add a lightweight consistency guard. Whenever a selected portfolio exists,
# its estimate is the source of truth for the scenario fields unless the user
# subsequently edits those fields manually.
marker = "/* scenario-sync-v1 */"
if marker not in s:
    guard = r'''
<script>
/* scenario-sync-v1 */
(function(){
  const byId=id=>document.getElementById(id);
  function syncFromSelected(){
    try{
      if(!window.selectedPortfolio || !Number.isFinite(Number(window.selectedPortfolio.estimate))) return;
      const expected=Number(window.selectedPortfolio.estimate);
      const vals=[Math.max(0,expected-2),expected,expected+2];
      ['r1','r2','r3'].forEach((id,i)=>{const el=byId(id);if(el)el.value=vals[i].toFixed(1)});
      const src=byId('scenarioSource');
      if(src){const title=window.selectedPortfolioTitle||'Current portfolio model';src.innerHTML=`Linked to <b>${title}</b>: Cautious ${vals[0].toFixed(1)}% • Expected ${vals[1].toFixed(1)}% • Optimistic ${vals[2].toFixed(1)}%. You can edit these assumptions manually.`}
    }catch(e){}
  }
  ['buildRisk','buildTarget','buildAdvisable'].forEach(id=>byId(id)?.addEventListener('click',()=>queueMicrotask(syncFromSelected)));
})();
</script>
'''
    s = s.replace('</body>', guard + '\n</body>', 1)

p.write_text(s, encoding='utf-8')
print('Fixed target-return scenario sync and missing-return handling')

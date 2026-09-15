#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'docs' / 'index.html'
s = p.read_text(encoding='utf-8')

if 'function renderSelectedMonthlyPlan' in s:
    print('Selected portfolio monthly plan already present; no changes needed.')
    raise SystemExit(0)

# Make the journey vertical and identify the two key sections.
s = s.replace('.inputs{grid-column:span 5}.summary{grid-column:span 7}', '.inputs{grid-column:1/-1}.summary{grid-column:1/-1}', 1)
s = s.replace('<section class="card summary">', '<section class="card summary" id="monthlyPlanSection">', 1)
s = s.replace('<section class="card full">\n<div class="sectiontitle"><h2>Portfolio Builder</h2>', '<section class="card full" id="portfolioBuilderSection">\n<div class="sectiontitle"><h2>Portfolio Builder</h2>', 1)
s = s.replace('<div class="sectiontitle"><h2>Suggested monthly split — Year 1</h2>', '<div class="sectiontitle"><h2>Your monthly investment plan — Year 1</h2>', 1)
s = s.replace('<p class="note">Allocation percentages are saved only in this browser. Suggested defaults are planning assumptions, not personal financial advice.</p>', '<p class="note" id="monthlyPlanNote">Choose a Portfolio Builder option first. Until then, the allocations above are only starter assumptions.</p>', 1)

# Store selected portfolio separately from the recommendation result.
s = s.replace('let feed=FALLBACK,weights={},lastRecommendation=null;', 'let feed=FALLBACK,weights={},lastRecommendation=null,selectedPortfolio=null,selectedPortfolioTitle="";', 1)

anchor = "function renderMetrics(){const a=weightedMetric('TFSA','oneYear'),b=weightedMetric('TFSA','ter'),c=weightedMetric('Non-TFSA','fiveYear'),d=weightedMetric('Non-TFSA','ter');$('tfsa1y').textContent=pct(a.value);$('tfsa1yCov').textContent=`${a.coverage.toFixed(0)}% data coverage`;$('tfsaTer').textContent=pct(b.value);$('tfsaTerCov').textContent=`${b.coverage.toFixed(0)}% fee coverage`;$('mixed5y').textContent=pct(c.value);$('mixed5yCov').textContent=`${c.coverage.toFixed(0)}% data coverage`;$('mixedTer').textContent=pct(d.value);$('mixedTerCov').textContent=`${d.coverage.toFixed(0)}% fee coverage`}"
extra = r'''
const TFSA_ELIGIBLE=new Set(['satrix-msci-world-islamic-etf','satrix-shariah-top-40-etf','old-mutual-albaraka-balanced','old-mutual-albaraka-equity','27four-shariah-income','27four-shariah-balanced']);
function selectedAccountPlan(p,total,tfsaTarget){const rows=p.rows.map(r=>({fund:r.fund,band:r.band,weight:r.weight,total:total*r.weight,tfsa:0,non:total*r.weight}));let left=tfsaTarget;for(const r of rows.filter(x=>TFSA_ELIGIBLE.has(x.fund.id)).sort((a,b)=>b.total-a.total)){const move=Math.min(r.non,left);r.tfsa+=move;r.non-=move;left-=move;if(left<=.01)break}return{rows,unfilled:Math.max(0,left)}}
function renderPlanRows(rows,kind,amount){const vals=rows.filter(r=>r[kind]>.01).sort((a,b)=>b[kind]-a[kind]);if(!vals.length)return '<span class="muted">No allocation in this account.</span>';return vals.map(r=>`<div class="fundrow"><span class="fundname" title="Click for fund details">${fundNameLink(r.fund)}</span><span>${(r[kind]/Math.max(1,amount)*100).toFixed(1)}%</span><b>${money(r[kind])}</b></div>`).join('')}
function renderSelectedMonthlyPlan(p){if(!p)return;const total=Math.max(0,+$('monthly').value||0),annualCap=+$('annualTfsa').value||0,life=+$('lifetimeTfsa').value||0,tfsaTarget=Math.min(total,annualCap/12,life/12||0),plan=selectedAccountPlan(p,total,tfsaTarget),actualTfsa=tfsaTarget-plan.unfilled,actualNon=total-actualTfsa;$('tfsaMonth').textContent=money(actualTfsa);$('mixedMonth').textContent=money(actualNon);$('tfsaSplit').innerHTML=renderPlanRows(plan.rows,'tfsa',actualTfsa);$('mixedSplit').innerHTML=renderPlanRows(plan.rows,'non',actualNon);$('tfsaTotal').innerHTML=`Total: <span class="ok">${money(actualTfsa)}</span>`;$('mixedTotal').innerHTML=`Total: <span class="ok">${money(actualNon)}</span>`;const note=$('monthlyPlanNote');if(note)note.innerHTML=`Based on <b>${selectedPortfolioTitle}</b>. The calculator first uses the TFSA allowance for funds we have verified as TFSA-eligible, then places the balance outside TFSA.${plan.unfilled>.01?` <span class="warn">${money(plan.unfilled)} of this month's TFSA allowance could not be filled without changing the selected portfolio because we have not verified enough selected funds as TFSA-eligible.</span>`:''}`;const reset=$('resetWeights');if(reset)reset.textContent='Return to starter allocations'}
'''
if anchor not in s:
    raise SystemExit('Could not find renderMetrics anchor')
s = s.replace(anchor, anchor + extra, 1)

# Selecting any builder result immediately becomes the active portfolio.
old = 'function displayRecommendation(title,p,detail){lastRecommendation=p;applyPortfolioScenarios(p,title);const start=Math.max(0,+$(\'monthly\').value||0),mix=p.mix;'
new = 'function displayRecommendation(title,p,detail){lastRecommendation=p;selectedPortfolio=p;selectedPortfolioTitle=title;applyPortfolioScenarios(p,title);const start=Math.max(0,+$(\'monthly\').value||0),mix=p.mix;'
if old not in s:
    raise SystemExit('Could not find displayRecommendation start')
s = s.replace(old, new, 1)

# In recalc, render either selected plan or starter split.
old2 = "renderSplit($('tfsaSplit'),'TFSA',tfsaMonthly,$('tfsaTotal'));renderSplit($('mixedSplit'),'Non-TFSA',mixed,$('mixedTotal'));renderMetrics();"
new2 = "if(selectedPortfolio){renderSelectedMonthlyPlan(selectedPortfolio)}else{renderSplit($('tfsaSplit'),'TFSA',tfsaMonthly,$('tfsaTotal'));renderSplit($('mixedSplit'),'Non-TFSA',mixed,$('mixedTotal'))}renderMetrics();"
if old2 not in s:
    raise SystemExit('Could not find recalc split rendering')
s = s.replace(old2, new2, 1)

# Reset now returns to starter allocations and clears selected portfolio.
s = s.replace("$('resetWeights').addEventListener('click',()=>{weights={};saveWeights();recalc()});", "$('resetWeights').addEventListener('click',()=>{selectedPortfolio=null;selectedPortfolioTitle='';weights={};saveWeights();const note=$('monthlyPlanNote');if(note)note.textContent='Choose a Portfolio Builder option first. Until then, the allocations above are only starter assumptions.';recalc()});", 1)

# Reorder the live DOM: contribution -> builder -> monthly plan -> everything else.
insert = "const grid=document.querySelector('.grid'),builderSection=$('portfolioBuilderSection'),monthlySection=$('monthlyPlanSection'),inputsSection=document.querySelector('.inputs');if(grid&&builderSection&&monthlySection&&inputsSection){grid.insertBefore(builderSection,inputsSection.nextElementSibling);grid.insertBefore(monthlySection,builderSection.nextElementSibling)};"
marker = "async function loadFeed()"
if marker not in s:
    raise SystemExit('Could not find loadFeed marker')
s = s.replace(marker, insert + "\n" + marker, 1)

p.write_text(s, encoding='utf-8')
print('Selected Portfolio Builder result now drives the monthly investment plan')

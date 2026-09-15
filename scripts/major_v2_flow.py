#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'docs' / 'index.html'
s = p.read_text(encoding='utf-8')

if 'major-v2-guided-flow' in s:
    print('Major V2 flow already present; no changes needed.')
    raise SystemExit(0)

# Friendly wording and slider label.
s = s.replace('<h2>Contribution assumptions</h2>', '<h2>Your Investment Goal</h2>', 1)
s = s.replace('South African TFSA planning assumption: R46,000 annual contribution limit from 1 March 2026 and R500,000 lifetime contribution limit. Each projection year is treated as a full contribution year.', 'TFSA limits used by the calculator: R46,000 per year from 1 March 2026 and R500,000 over your lifetime. Investment growth does not count towards these contribution limits.')
s = s.replace('<span id="yearLabel">20</span>y', '<span id="yearLabel">20</span> years', 1)

# Add site navigation under the hero.
nav = '''\n<nav class="siteNav" aria-label="Main navigation"><a class="active" href="./">Calculator</a><a href="./fund-explorer.html">Fund Explorer</a><a href="./add-fund.html">Add Fund</a></nav>\n'''
hero_end = '</div></div>\n<div class="beginner">'
if hero_end in s:
    s = s.replace(hero_end, '</div></div>' + nav + '<div class="beginner">', 1)

# Add the two-angle goal selector before the existing fields.
goal_ui = '''\n<div class="goalModes" id="goalModes">\n  <button type="button" class="goalMode active" data-mode="contribution"><span class="modeKicker">OPTION A</span><b>I know what I can invest</b><small>Tell us what you can invest each month and see what it could grow to.</small></button>\n  <button type="button" class="goalMode" data-mode="target"><span class="modeKicker">OPTION B</span><b>I know what I want to reach</b><small>Tell us the portfolio value you want and we will work backwards to the monthly amount.</small></button>\n</div>\n<div class="targetGoalPanel" id="targetGoalPanel" hidden>\n  <div class="fieldgrid">\n    <div class="field"><label>Target portfolio value (R)</label><input id="targetValue" type="number" min="10000" step="10000" value="5000000"></div>\n    <div class="field"><label>Increase my monthly investment each year by (%)</label><input id="targetIncrease" type="number" min="0" step="0.1" value="5"></div>\n  </div>\n  <div class="requiredGrid" id="requiredGrid"><div class="requiredCard"><small>Cautious scenario</small><b id="requiredCautious">—</b><span>starting monthly amount</span></div><div class="requiredCard expected"><small>Expected scenario</small><b id="requiredExpected">—</b><span>starting monthly amount</span></div><div class="requiredCard"><small>Optimistic scenario</small><b id="requiredOptimistic">—</b><span>starting monthly amount</span></div></div>\n  <p class="note" id="targetGoalNote">The calculator works backwards from your target using the selected portfolio's planning scenarios. These are illustrations, not guaranteed returns.</p>\n</div>\n'''
needle = '<div class="fieldgrid">\n<div class="field"><label>Starting monthly contribution (R)</label>'
if needle in s:
    s = s.replace(needle, goal_ui + '<div class="fieldgrid" id="contributionFields">\n<div class="field"><label>Starting monthly contribution (R)</label>', 1)

# Add CSS.
css = r'''
/* major-v2-guided-flow */
.siteNav{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 18px}.siteNav a{padding:9px 12px;border:1px solid var(--line);border-radius:10px;color:var(--text);text-decoration:none;font-weight:750}.siteNav a.active,.siteNav a:hover{background:var(--soft);color:var(--accent)}
.goalModes{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:4px 0 16px}.goalMode{border:1px solid var(--line);border-radius:14px;background:transparent;color:inherit;text-align:left;padding:15px;cursor:pointer}.goalMode.active{border-color:var(--accent);background:var(--soft)}.goalMode b{display:block;font-size:18px;margin:3px 0 5px}.goalMode small{display:block;color:var(--muted);line-height:1.45}.modeKicker{font-size:11px;color:var(--muted);font-weight:800;letter-spacing:.05em}.targetGoalPanel{border:1px solid var(--line);border-radius:14px;padding:14px;margin-bottom:16px;background:var(--soft)}.requiredGrid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:12px}.requiredCard{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:12px}.requiredCard small,.requiredCard span{display:block;color:var(--muted);font-size:12px}.requiredCard b{display:block;font-size:22px;margin:4px 0}.requiredCard.expected{border-color:var(--accent)}
.simpleMilestones table{table-layout:fixed}.simpleMilestones th,.simpleMilestones td{text-align:left}.simpleMilestones .scenarioValue{font-weight:800}.simpleMilestones .scenarioProfit{display:block;color:var(--muted);font-size:11px;margin-top:3px}.expectedCol{background:var(--soft)}.technicalDetails{margin-top:12px}.technicalDetails summary{cursor:pointer;font-weight:700;color:var(--accent)}
.chartLegend{display:flex;gap:14px;flex-wrap:wrap;margin:8px 0 0;font-size:12px;color:var(--muted)}.chartLegend span::before{content:'';display:inline-block;width:18px;height:3px;border-radius:9px;margin-right:6px;vertical-align:middle;background:currentColor}.chartLegend .c1{color:#7ca7ff}.chartLegend .c2{color:#65d0b4}.chartLegend .c3{color:#d5a35d}
.secondaryToggle{margin-left:auto}.hiddenResearch{display:none!important}.compactHistory .metricgrid,.compactHistory .note{display:none}.compactHistory.open .metricgrid,.compactHistory.open .note{display:grid}.compactHistory.open .note{display:block}
@media(max-width:760px){.goalModes,.requiredGrid{grid-template-columns:1fr}.simpleMilestones table,.simpleMilestones tbody,.simpleMilestones tr,.simpleMilestones td,.simpleMilestones th{display:block}.simpleMilestones thead{display:none}.simpleMilestones tr{border:1px solid var(--line);border-radius:12px;padding:10px;margin-bottom:10px}.simpleMilestones td{border:0;padding:5px 0}.simpleMilestones td:first-child{font-weight:800;font-size:18px}.expectedCol{background:transparent}}
'''
s = s.replace('</style>', css + '\n</style>', 1)

# Append JS enhancements after existing calculator JS.
js = r'''
<script>
(function(){
  const byId=id=>document.getElementById(id);
  const money2=n=>new Intl.NumberFormat('en-ZA',{style:'currency',currency:'ZAR',maximumFractionDigits:0}).format(Number(n)||0);
  const MIN_MONTHLY={
    'camissa-islamic-balanced':500,
    'camissa-islamic-high-yield':500,
    'old-mutual-albaraka-balanced':500,
    'old-mutual-albaraka-income':500,
    'old-mutual-albaraka-equity':500,
    '27four-shariah-income':500,
    '27four-shariah-balanced':500
  };

  function fv(startMonthly,annualIncrease,years,annualReturn){let bal=0;const mr=Math.pow(1+annualReturn/100,1/12)-1;for(let m=0;m<years*12;m++){bal*=1+mr;const yr=Math.floor(m/12);bal+=startMonthly*Math.pow(1+annualIncrease/100,yr)}return bal}
  function requiredMonthly(target,annualIncrease,years,annualReturn){let lo=0,hi=1000000;for(let i=0;i<70;i++){const mid=(lo+hi)/2;if(fv(mid,annualIncrease,years,annualReturn)>=target)hi=mid;else lo=mid}return hi}
  function updateGoalMode(){const mode=document.querySelector('.goalMode.active')?.dataset.mode||'contribution';const targetPanel=byId('targetGoalPanel');const contribution=byId('contributionFields');if(targetPanel)targetPanel.hidden=mode!=='target';if(contribution)contribution.style.display=mode==='target'?'none':'grid';if(mode==='target')updateTargetAmounts()}
  function updateTargetAmounts(){if(!byId('targetValue'))return;const target=Math.max(0,+byId('targetValue').value||0),inc=Math.max(0,+byId('targetIncrease').value||0),years=Math.max(1,+byId('years').value||20),rates=[+byId('r1').value||0,+byId('r2').value||0,+byId('r3').value||0];const vals=rates.map(r=>requiredMonthly(target,inc,years,r));byId('requiredCautious').textContent=money2(vals[0]);byId('requiredExpected').textContent=money2(vals[1]);byId('requiredOptimistic').textContent=money2(vals[2]);const m=byId('monthly');const i=byId('increase');if(m&&Math.abs((+m.value||0)-vals[1])>1){m.value=Math.round(vals[1]);m.dispatchEvent(new Event('input',{bubbles:true}))}if(i&&Math.abs((+i.value||0)-inc)>.01){i.value=inc;i.dispatchEvent(new Event('input',{bubbles:true}))}}
  document.querySelectorAll('.goalMode').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.goalMode').forEach(x=>x.classList.toggle('active',x===b));updateGoalMode()}));
  ['targetValue','targetIncrease','years','r1','r2','r3'].forEach(id=>byId(id)?.addEventListener('input',()=>{if(document.querySelector('.goalMode.active')?.dataset.mode==='target')updateTargetAmounts()}));

  function planReturn(f){const vals=[[f.tenYear,.35],[f.fiveYear,.35],[f.threeYear,.2],[f.oneYear,.1],[f.sinceInception,.15]].filter(x=>Number.isFinite(Number(x[0])));if(!vals.length)return 0;const tw=vals.reduce((a,x)=>a+x[1],0);return vals.reduce((a,x)=>a+Number(x[0])*x[1],0)/tw}
  function practicalize(p,total){if(!p||!Array.isArray(p.rows)||!total)return p;let rows=p.rows.map(r=>({...r,amount:Math.max(0,total*Number(r.weight||0))})).filter(r=>r.amount>.01);let changed=false;for(let guard=0;guard<20;guard++){const bad=rows.filter(r=>{const min=MIN_MONTHLY[r.fund.id]||0;return min>0&&r.amount>0&&r.amount<min-.01}).sort((a,b)=>a.amount-b.amount)[0];if(!bad)break;changed=true;const removed=bad.amount;rows=rows.filter(r=>r!==bad);if(!rows.length)break;let recipients=rows.filter(r=>r.band===bad.band);if(!recipients.length)recipients=rows;const base=recipients.reduce((a,r)=>a+r.amount,0)||recipients.length;recipients.forEach(r=>r.amount+=removed*(base? r.amount/base : 1/recipients.length))}
    const sum=rows.reduce((a,r)=>a+r.amount,0)||1;rows.forEach(r=>r.weight=r.amount/sum);const mix={Low:0,Medium:0,High:0};rows.forEach(r=>mix[r.band]=(mix[r.band]||0)+r.weight*100);const estimate=rows.reduce((a,r)=>a+r.weight*planReturn(r.fund),0);return {...p,rows,mix,estimate,practicalAdjusted:changed}}

  if(typeof window.displayRecommendation==='function'){
    const oldDisplay=window.displayRecommendation;
    window.displayRecommendation=function(title,p,detail){const total=Math.max(0,+byId('monthly')?.value||0),q=practicalize(p,total);const extra=q?.practicalAdjusted?' The monthly plan was rebalanced to respect known R500 recurring minimums for applicable unit-trust funds.':'';return oldDisplay(title,q,(detail||'')+extra)};
  }
  if(typeof window.renderSelectedMonthlyPlan==='function'){
    const oldRender=window.renderSelectedMonthlyPlan;
    window.renderSelectedMonthlyPlan=function(p){const total=Math.max(0,+byId('monthly')?.value||0),q=practicalize(p,total);selectedPortfolio=q;return oldRender(q)};
  }

  function findSection(title){return [...document.querySelectorAll('section')].find(sec=>(sec.querySelector('h2')?.textContent||'').trim()===title)}
  const liveSec=findSection('Live Shariah fund data');if(liveSec)liveSec.classList.add('hiddenResearch');
  const histSec=findSection('How the selected funds have performed historically');if(histSec){histSec.classList.add('compactHistory');const head=histSec.querySelector('.sectiontitle');if(head){const b=document.createElement('button');b.className='btn secondaryToggle';b.type='button';b.textContent='Show portfolio history';b.onclick=()=>{histSec.classList.toggle('open');b.textContent=histSec.classList.contains('open')?'Hide portfolio history':'Show portfolio history'};head.appendChild(b)}}

  function simplifyMilestones(){const sec=findSection('Projection milestones');if(!sec)return;const raw=sec.querySelector('table');if(!raw||raw.dataset.simpleSource==='1')return;raw.dataset.simpleSource='1';const wrap=raw.parentElement;const simple=document.createElement('div');simple.className='simpleMilestones';wrap.parentElement.insertBefore(simple,wrap);const details=document.createElement('details');details.className='technicalDetails';const summary=document.createElement('summary');summary.textContent='Show detailed TFSA / non-TFSA breakdown';details.appendChild(summary);wrap.parentElement.insertBefore(details,wrap);details.appendChild(wrap);
    const render=()=>{const rows=[...raw.querySelectorAll('tbody tr')];simple.innerHTML='<table><thead><tr><th>Year</th><th>Capital invested</th><th>Cautious</th><th class="expectedCol">Expected</th><th>Optimistic</th></tr></thead><tbody>'+rows.map(tr=>{const c=[...tr.children].map(x=>x.textContent.trim());if(c.length<10)return '';return `<tr><td>Year ${c[0]}</td><td>${c[1]}</td><td><span class="scenarioValue">${c[5]}</span><span class="scenarioProfit">Profit ${c[4]}</span></td><td class="expectedCol"><span class="scenarioValue">${c[7]}</span><span class="scenarioProfit">Profit ${c[6]}</span></td><td><span class="scenarioValue">${c[9]}</span><span class="scenarioProfit">Profit ${c[8]}</span></td></tr>`}).join('')+'</tbody></table>'};render();new MutationObserver(render).observe(raw.querySelector('tbody')||raw,{childList:true,subtree:true,characterData:true})}
  simplifyMilestones();

  function drawGrowth(){const sec=findSection('Portfolio growth');if(!sec)return;const canvas=sec.querySelector('canvas');if(!canvas)return;const years=Math.max(1,+byId('years')?.value||20),start=Math.max(0,+byId('monthly')?.value||0),inc=+byId('increase')?.value||0,rates=[+byId('r1')?.value||0,+byId('r2')?.value||0,+byId('r3')?.value||0];const dpr=window.devicePixelRatio||1,w=Math.max(600,canvas.clientWidth||sec.clientWidth-36),h=330;canvas.width=w*dpr;canvas.height=h*dpr;canvas.style.height=h+'px';const ctx=canvas.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);const series=rates.map(r=>{const a=[];for(let y=0;y<=years;y++)a.push(fv(start,inc,y,r));return a});const max=Math.max(1,...series.flat()),pad={l:64,r:20,t:24,b:38};const plotW=w-pad.l-pad.r,plotH=h-pad.t-pad.b;const style=getComputedStyle(document.documentElement),grid=style.getPropertyValue('--line').trim()||'#334044',text=style.getPropertyValue('--muted').trim()||'#9eacab',cols=['#7ca7ff','#65d0b4','#d5a35d'];ctx.font='12px system-ui';ctx.strokeStyle=grid;ctx.fillStyle=text;ctx.lineWidth=1;for(let i=0;i<=4;i++){const y=pad.t+plotH*i/4;ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(w-pad.r,y);ctx.stroke();const val=max*(1-i/4);ctx.fillText('R '+new Intl.NumberFormat('en-ZA',{notation:'compact',maximumFractionDigits:1}).format(val),4,y+4)}for(let i=0;i<=4;i++){const yr=Math.round(years*i/4),x=pad.l+plotW*i/4;ctx.fillText(String(yr)+'y',x-8,h-12)}series.forEach((arr,si)=>{ctx.strokeStyle=cols[si];ctx.lineWidth=3;ctx.beginPath();arr.forEach((v,idx)=>{const x=pad.l+plotW*(idx/years),y=pad.t+plotH*(1-v/max);idx?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.stroke()});let lg=sec.querySelector('.chartLegend');if(!lg){lg=document.createElement('div');lg.className='chartLegend';lg.innerHTML='<span class="c1">Cautious</span><span class="c2">Expected</span><span class="c3">Optimistic</span>';canvas.insertAdjacentElement('afterend',lg)}}
  ['monthly','increase','years','r1','r2','r3'].forEach(id=>byId(id)?.addEventListener('input',()=>setTimeout(drawGrowth,0)));window.addEventListener('resize',drawGrowth);setTimeout(drawGrowth,150);
  updateGoalMode();
})();
</script>
'''
s = s.replace('</body>', js + '\n</body>', 1)

p.write_text(s, encoding='utf-8')
print('Applied major V2 guided-flow enhancements')

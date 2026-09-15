#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'docs' / 'index.html'
s = p.read_text(encoding='utf-8')

# Replace the expensive binary-search reverse calculator. Because portfolio value is
# linear in the starting monthly contribution, one FV calculation is sufficient.
old = "function requiredMonthly(target,annualIncrease,years,annualReturn){let lo=0,hi=1000000;for(let i=0;i<70;i++){const mid=(lo+hi)/2;if(fv(mid,annualIncrease,years,annualReturn)>=target)hi=mid;else lo=mid}return hi}"
new = "function requiredMonthly(target,annualIncrease,years,annualReturn){const unit=fv(1,annualIncrease,years,annualReturn);return unit>0?target/unit:0}"
if old in s:
    s = s.replace(old, new, 1)

# Throttle graph redraws to one per browser animation frame instead of queuing a
# setTimeout for every tiny slider movement.
old2 = "['monthly','increase','years','r1','r2','r3'].forEach(id=>byId(id)?.addEventListener('input',()=>setTimeout(drawGrowth,0)));window.addEventListener('resize',drawGrowth);setTimeout(drawGrowth,150);"
new2 = "let growthFrame=0;function requestGrowthDraw(){if(growthFrame)return;growthFrame=requestAnimationFrame(()=>{growthFrame=0;drawGrowth()})}['monthly','increase','years','r1','r2','r3'].forEach(id=>byId(id)?.addEventListener('input',requestGrowthDraw));window.addEventListener('resize',requestGrowthDraw);setTimeout(drawGrowth,150);"
if old2 in s:
    s = s.replace(old2, new2, 1)

# Keep the visible year label immediate while dragging. Heavy dependent work can
# still occur, but the thumb/label remain responsive.
marker = "updateGoalMode();\n})();"
insert = "const yearSlider=byId('years');if(yearSlider){yearSlider.addEventListener('input',()=>{const yl=byId('yearLabel');if(yl)yl.textContent=yearSlider.value},{passive:true})}\n  updateGoalMode();\n})();"
if marker in s and "passive:true" not in s:
    s = s.replace(marker, insert, 1)

p.write_text(s, encoding='utf-8')
print('Optimised projection slider and reverse-goal calculation')

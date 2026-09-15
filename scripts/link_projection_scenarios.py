#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'docs' / 'index.html'
s = p.read_text(encoding='utf-8')

if 'Portfolio-linked scenarios' in s:
    print('Portfolio-linked scenarios already present; no changes needed.')
    raise SystemExit(0)

old = '''<h3>Future return scenarios</h3><div class="plainlabel">These are examples for planning, not guaranteed returns.</div>
<div class="rates"><div class="field"><label>Lower %</label><input id="r1" type="number" step="0.1" value="8"></div><div class="field"><label>Middle %</label><input id="r2" type="number" step="0.1" value="10"></div><div class="field"><label>Higher %</label><input id="r3" type="number" step="0.1" value="12"></div></div>'''
new = '''<h3>Future return scenarios</h3><div class="plainlabel"><b>Portfolio-linked scenarios:</b> after you build a portfolio below, these update automatically from its historical planning return. You can still edit them yourself.</div>
<div class="rates"><div class="field"><label><span class="term" tabindex="0" data-tip="A more cautious planning scenario, automatically set 2 percentage points below the selected portfolio's planning return. It is not a prediction.">Cautious %</span></label><input id="r1" type="number" step="0.1" value="8"></div><div class="field"><label><span class="term" tabindex="0" data-tip="The selected portfolio's blended historical planning return. This is used for illustration only and is not a guaranteed future return.">Expected %</span></label><input id="r2" type="number" step="0.1" value="10"></div><div class="field"><label><span class="term" tabindex="0" data-tip="A more optimistic planning scenario, automatically set 2 percentage points above the selected portfolio's planning return. It is not a prediction.">Optimistic %</span></label><input id="r3" type="number" step="0.1" value="12"></div></div>
<div class="plainlabel" id="scenarioSource">No portfolio selected yet — using the editable starter assumptions above.</div>'''
if old not in s:
    raise SystemExit('Could not find future scenario block')
s = s.replace(old, new, 1)

old_fn = "function displayRecommendation(title,p,detail){lastRecommendation=p;const start=Math.max(0,+$('monthly').value||0),mix=p.mix;$('portfolioResult').innerHTML=`"
new_fn = "function applyPortfolioScenarios(p,title){if(!p||!Number.isFinite(Number(p.estimate)))return;const expected=Number(p.estimate),cautious=Math.max(0,expected-2),optimistic=expected+2;$('r1').value=cautious.toFixed(1);$('r2').value=expected.toFixed(1);$('r3').value=optimistic.toFixed(1);const src=$('scenarioSource');if(src)src.innerHTML=`Linked to <b>${title}</b>: Cautious ${cautious.toFixed(1)}% • Expected ${expected.toFixed(1)}% • Optimistic ${optimistic.toFixed(1)}%. You can edit these assumptions manually.`;recalc()}\nfunction displayRecommendation(title,p,detail){lastRecommendation=p;applyPortfolioScenarios(p,title);const start=Math.max(0,+$('monthly').value||0),mix=p.mix;$('portfolioResult').innerHTML=`"
if old_fn not in s:
    raise SystemExit('Could not find displayRecommendation function')
s = s.replace(old_fn, new_fn, 1)

s = s.replace("<button class=\"btn\" id=\"useReturn\" type=\"button\">Use ${p.estimate.toFixed(1)}% as middle projection</button>", "<button class=\"btn\" id=\"useReturn\" type=\"button\">Reset scenarios from this portfolio</button>")
s = s.replace("const b=$('useReturn');if(b)b.addEventListener('click',()=>{$('r2').value=p.estimate.toFixed(1);recalc()})", "const b=$('useReturn');if(b)b.addEventListener('click',()=>applyPortfolioScenarios(p,title))")

s = s.replace('Profit @ lower</th><th>Total @ lower</th><th>Profit @ middle</th><th>Total @ middle</th><th>Profit @ higher</th><th>Total @ higher', 'Profit @ cautious</th><th>Total @ cautious</th><th>Profit @ expected</th><th>Total @ expected</th><th>Profit @ optimistic</th><th>Total @ optimistic')

p.write_text(s, encoding='utf-8')
print('Linked Cautious / Expected / Optimistic scenarios to Portfolio Builder')

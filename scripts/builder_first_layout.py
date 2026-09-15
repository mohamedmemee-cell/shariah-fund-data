#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'docs' / 'index.html'
s = p.read_text(encoding='utf-8')

marker = '/* portfolio-builder-first-layout */'
if marker not in s:
    css = '''\n/* portfolio-builder-first-layout */\n.builderbox{display:flex;flex-direction:column;min-height:360px}\n.builderbox .help{min-height:58px}\n.builderbox .validation{min-height:22px}\n.builderbox .btn.primary{width:290px;max-width:100%;min-height:54px;display:inline-flex;align-items:center;justify-content:center;font-size:16px;margin-top:auto}\n.builderbox .inlinefields{display:flex;flex-direction:column;align-items:stretch;gap:10px;flex:1}\n.builderbox #buildTarget{align-self:flex-start}\n.builderbox #buildRisk{align-self:flex-start}\n.builderbox #buildAdvisable{align-self:flex-start}\n.builderbox>div[style*="margin-top:12px"]{margin-top:auto!important}\n@media(max-width:900px){.builderbox{min-height:0}.builderbox .help{min-height:0}.builderbox .btn.primary{width:100%}}\n'''
    s = s.replace('</style>', css + '\n</style>', 1)

# Reorder the DOM at runtime so Portfolio Builder appears immediately after the quick guide.
old = "const grid=document.querySelector('.grid'),builderSection=$('portfolioBuilderSection'),monthlySection=$('monthlyPlanSection'),inputsSection=document.querySelector('.inputs');if(grid&&builderSection&&monthlySection&&inputsSection){grid.insertBefore(builderSection,inputsSection.nextElementSibling);grid.insertBefore(monthlySection,builderSection.nextElementSibling)};"
new = "const grid=document.querySelector('.grid'),builderSection=$('portfolioBuilderSection'),monthlySection=$('monthlyPlanSection'),inputsSection=document.querySelector('.inputs');if(grid&&builderSection&&monthlySection&&inputsSection){grid.insertBefore(builderSection,grid.firstElementChild);grid.insertBefore(inputsSection,builderSection.nextElementSibling);grid.insertBefore(monthlySection,inputsSection.nextElementSibling)};"
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('Could not find section reorder logic')

# Option 2: put the target field above the button, matching the other cards.
old2 = '<div class="inlinefields"><div class="field"><label>Target annual return %</label><input id="targetReturn" type="number" min="0" max="30" step="0.1" value="10.5"></div><button class="btn primary" id="buildTarget" type="button">Find closest</button></div>\n<div id="targetValidation" class="validation"></div>'
new2 = '<div class="inlinefields"><div class="field"><label>Target annual return %</label><input id="targetReturn" type="number" min="0" max="30" step="0.1" value="10.5"></div><div id="targetValidation" class="validation"></div><button class="btn primary" id="buildTarget" type="button">Find closest</button></div>'
if old2 in s:
    s = s.replace(old2, new2, 1)

p.write_text(s, encoding='utf-8')
print('Portfolio Builder moved first; action buttons aligned and sized consistently')

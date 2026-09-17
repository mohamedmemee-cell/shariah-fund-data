#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'docs'/'index.html'
DETAILS=ROOT/'docs'/'fund-details.html'

marker='risk-normalisation-v12'

# Shared browser-side function. Published manager labels remain unchanged;
# this only maps them into the calculator's common Low / Medium / High bands.
risk_fn="""function riskBand(f){
  const c=(f.category||'').toLowerCase();
  const raw=(f.risk_level||'').toLowerCase().trim();
  const r=raw.replace(/[–—_-]+/g,' ').replace(/\s+/g,' ');
  if(/aggressive|very high|moderate\s*(to\s*)?high|medium\s*(to\s*)?high/.test(r) || r==='high') return 'High';
  if(/very low|conservative|low\s*(to\s*)?(moderate|medium)/.test(r) || r==='low') return 'Low';
  if(r==='moderate' || r==='medium' || /(^|\s)moderate risk($|\s)/.test(r)) return 'Medium';
  if(c.includes('equity')) return 'High';
  if(c.includes('income')) return 'Low';
  return 'Medium';
}"""

# Calculator page.
s=INDEX.read_text(encoding='utf-8')
old="function riskBand(f){const c=(f.category||'').toLowerCase(),r=(f.risk_level||'').toLowerCase();if(c.includes('equity')||r.includes('aggressive')||(r.includes('high')&&!c.includes('balanced')))return'High';if(c.includes('income')&&(r.includes('low')||!r))return'Low';if(r==='low')return'Low';return'Medium'}"
if old in s:
    s=s.replace(old,risk_fn,1)

if marker not in s:
    css="""
/* risk-normalisation-v12 */
.riskNormalisationV12{margin:0 0 14px;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:color-mix(in srgb,var(--card) 88%,var(--brand-soft));font-size:12px;line-height:1.5;color:var(--muted)}
.riskNormalisationV12 b{color:var(--text)}
"""
    s=s.replace('</style>',css+'\n</style>',1)
    anchor='<div class="builder">'
    explainer='''<div class="riskNormalisationV12"><b>How fund risk labels are standardised</b><br>Fund managers use different wording. The calculator keeps the manager’s original risk label, then maps it into one common Portfolio Builder band: <b>Low / Conservative / Low-Moderate / Low-Medium → Low</b>; <b>Moderate / Medium → Medium</b>; <b>Moderate-High / Medium-High / High / Aggressive → High</b>. If a manager label is missing, fund category is used only as a fallback.</div>'''
    if anchor in s:
        s=s.replace(anchor,explainer+anchor,1)

INDEX.write_text(s,encoding='utf-8')

# Fund detail page: show original manager wording and calculator band side by side.
d=DETAILS.read_text(encoding='utf-8')
if marker not in d:
    # Rename the existing card label to make provenance obvious.
    d=d.replace('<div class="stat"><small>Risk</small><b id="risk">—</b></div>','<div class="stat"><small>Manager risk</small><b id="risk">—</b></div><div class="stat"><small>Calculator risk band</small><b id="calcRiskBandV12">—</b></div>',1)
    js=f'''\n<script>\n/* {marker} */\n(function(){{\n {risk_fn}\n const id=new URLSearchParams(location.search).get('id');\n fetch('./shariah-funds.json?ts='+Date.now(),{{cache:'no-store'}}).then(r=>r.json()).then(j=>{{const f=(j.funds||[]).find(x=>x.id===id);const el=document.getElementById('calcRiskBandV12');if(f&&el)el.textContent=riskBand(f)}}).catch(()=>{{}});\n}})();\n</script>\n'''
    d=d.replace('</body>',js+'</body>',1)
DETAILS.write_text(d,encoding='utf-8')
print('Applied risk normalisation V12')

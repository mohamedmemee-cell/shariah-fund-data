#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / 'docs' / 'index.html'
s = p.read_text(encoding='utf-8')
marker = 'plan-name-reference-v10'
if marker in s:
    print('Plan name/reference V10 already present')
    raise SystemExit(0)

# 1) Add an optional plan identity field before the Portfolio Builder.
anchor = '<section class="card full" id="portfolioBuilderSection">'
identity = '''<section class="card full planIdentitySection" id="planIdentitySection">
<div class="sectiontitle"><h2>Who is this calculation for?</h2><span class="muted">Optional</span></div>
<div class="field planNameField"><label for="planName">Name or reference</label><input id="planName" type="text" maxlength="80" autocomplete="off" placeholder="e.g. Ahmed, Dad, Client A, Retirement Plan"></div>
<p class="note">This helps identify a calculation when you share the link, QR code or PDF. You can use a first name or a non-personal reference instead of a full name.</p>
</section>'''
if anchor not in s:
    raise SystemExit('Could not find Portfolio Builder anchor; refusing partial patch')
s = s.replace(anchor, identity + '\n' + anchor, 1)

# 2) Include the name/reference in the existing compact shared-plan payload.
old_payload = "function payload(){const p=window.selectedPortfolio;return {v:1,created:new Date().toISOString().slice(0,10),"
new_payload = "function payload(){const p=window.selectedPortfolio;return {v:2,created:new Date().toISOString().slice(0,10),planName:(byId('planName')?.value||'').trim(),"
if old_payload not in s:
    raise SystemExit('Could not find share payload; refusing partial patch')
s = s.replace(old_payload, new_payload, 1)

# 3) Restore the name/reference when a shared link is opened.
old_restore = "[['monthly',o.monthly],['increase',o.increase],['years',o.years]"
new_restore = "[['planName',o.planName],['monthly',o.monthly],['increase',o.increase],['years',o.years]"
if old_restore not in s:
    raise SystemExit('Could not find shared-plan restore fields; refusing partial patch')
s = s.replace(old_restore, new_restore, 1)

# Make the existing share restore/change dispatch and summary refresh react to the new field.
s = s.replace("document.querySelectorAll('#monthly,#increase,#years,#riskLow,#riskMedium,#riskHigh,#targetReturn,#maxFunds,#r1,#r2,#r3')",
              "document.querySelectorAll('#planName,#monthly,#increase,#years,#riskLow,#riskMedium,#riskHigh,#targetReturn,#maxFunds,#r1,#r2,#r3')", 1)
s = s.replace("['monthly','increase','years','riskLow','riskMedium','riskHigh','targetReturn','maxFunds','r1','r2','r3'].forEach",
              "['planName','monthly','increase','years','riskLow','riskMedium','riskHigh','targetReturn','maxFunds','r1','r2','r3'].forEach", 1)

# 4) Put a dedicated identity line in Step 6 so it also appears in print/PDF.
summary_anchor = '<div class="planSummaryGrid" id="planSummaryGrid"></div>'
summary_identity = '<div class="planIdentitySummary" id="planIdentitySummary" aria-live="polite"></div>' + summary_anchor
if summary_anchor not in s:
    raise SystemExit('Could not find Step 6 summary grid; refusing partial patch')
s = s.replace(summary_anchor, summary_identity, 1)

# 5) Styling and print treatment.
css = r'''
/* plan-name-reference-v10 */
.planIdentitySection{border-color:color-mix(in srgb,var(--brand) 22%,var(--line));background:linear-gradient(120deg,color-mix(in srgb,var(--brand-soft) 55%,var(--card)),var(--card) 70%)}
.planNameField{max-width:620px}.planNameField input{font-weight:700}
.planIdentitySummary{display:none;margin:0 0 14px;padding:12px 14px;border:1px solid color-mix(in srgb,var(--brand) 28%,var(--line));border-radius:12px;background:var(--brand-soft);font-size:15px}
.planIdentitySummary.show{display:block}.planIdentitySummary strong{font-size:18px;color:var(--brand-strong)}
@media print{#planIdentitySection{display:none!important}#planIdentitySummary{display:block!important;border:1px solid #bbb!important;background:#fff!important;color:#111!important;margin-bottom:14px!important}#planIdentitySummary strong{color:#111!important}}
'''
s = s.replace('</style>', css + '\n</style>', 1)

# 6) Keep the visible context in sync. Text is assigned with textContent so a name cannot inject markup.
js = r'''
<script>
/* plan-name-reference-v10 */
(function(){
 const byId=id=>document.getElementById(id);
 const input=byId('planName'), box=byId('planIdentitySummary'), note=byId('shareDataNote');
 if(!input||!box)return;
 function clean(){return String(input.value||'').trim().replace(/\s+/g,' ').slice(0,80)}
 function render(){
   const name=clean();
   box.textContent='';
   if(name){
     const label=document.createElement('span'); label.textContent='Investment plan for ';
     const strong=document.createElement('strong'); strong.textContent=name;
     box.append(label,strong); box.classList.add('show');
     document.title=`Investment plan for ${name} · Shariah Investment Calculator`;
   }else{
     box.classList.remove('show');
     document.title='Shariah Investment Calculator';
   }
   if(note && location.hash.includes('plan=')){
     const base=note.textContent.replace(/^Shared plan for .*?\. /,'').replace(/^Shared plan\. /,'');
     note.textContent=name?`Shared plan for ${name}. ${base}`:`Shared plan. ${base}`;
   }
 }
 input.addEventListener('input',render);
 input.addEventListener('change',render);
 // Existing shared-link restore runs earlier during page setup; defer once so restored value is visible.
 setTimeout(render,0);
})();
</script>
'''
s = s.replace('</body>', js + '\n</body>', 1)

p.write_text(s, encoding='utf-8')
print('Applied plan name/reference V10')

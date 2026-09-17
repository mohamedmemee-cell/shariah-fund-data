#!/usr/bin/env python3
import json, re
from pathlib import Path
from datetime import date

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'docs'/'index.html'
SCRIPTS=ROOT/'scripts'
APP_VERSION=ROOT/'docs'/'app-version.json'
s=INDEX.read_text(encoding='utf-8')
marker='pdf-name-reference-v16'

# Keep the visible calculator version synchronized automatically with the highest
# numbered release script in the repository. This prevents the badge getting
# stuck at v16 when later V17+ changes are deployed.
versions=[]
for p in SCRIPTS.glob('*.py'):
    m=re.search(r'_v(\d+)\.py$',p.name,re.I)
    if m:
        versions.append(int(m.group(1)))
latest=max(versions) if versions else 16
version_label=f'v{latest}'

# Update any existing calculator version element regardless of its previous text.
s=re.sub(r'(<div\s+id="calcVersionV15"\s+class="calcVersionV14">)v\d+(</div>)',rf'\g<1>{version_label}\2',s,count=1)
# Fallback if the historical id/class changed but a calc-version badge remains.
s=re.sub(r'(<[^>]+class="[^"]*calcVersionV14[^"]*"[^>]*>)v\d+(</[^>]+>)',rf'\g<1>{version_label}\2',s,count=1)
APP_VERSION.write_text(json.dumps({'version':version_label,'build_date':date.today().isoformat()},indent=2)+'\n',encoding='utf-8')

if marker in s:
    INDEX.write_text(s,encoding='utf-8')
    print(f'PDF name/reference already present; synced visible app version to {version_label}')
    raise SystemExit(0)

# Add a dedicated print-only identity line inside Step 6. This is separate from
# the on-screen identity summary so later print/layout patches cannot hide it.
anchor='<div class="planIdentitySummary" id="planIdentitySummary" aria-live="polite"></div><div class="planSummaryGrid" id="planSummaryGrid"></div>'
if anchor in s:
    repl='<div class="planIdentitySummary" id="planIdentitySummary" aria-live="polite"></div><div id="pdfPlanIdentityV16" class="pdfPlanIdentityV16"></div><div class="planSummaryGrid" id="planSummaryGrid"></div>'
    s=s.replace(anchor,repl,1)
else:
    anchor2='<div class="planSummaryGrid" id="planSummaryGrid"></div>'
    if anchor2 not in s:
        raise SystemExit('Could not find Step 6 summary grid; refusing partial patch')
    s=s.replace(anchor2,'<div id="pdfPlanIdentityV16" class="pdfPlanIdentityV16"></div>'+anchor2,1)

css=r'''
/* pdf-name-reference-v16 */
.pdfPlanIdentityV16{display:none}
@media print{
  #pdfPlanIdentityV16{display:block!important;margin:0 0 14px!important;padding:10px 12px!important;border:1px solid #bbb!important;border-radius:8px!important;background:#fff!important;color:#111!important;font-size:14px!important;line-height:1.35!important}
  #pdfPlanIdentityV16 strong{font-size:18px!important;color:#111!important}
}
'''
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
<script>
/* pdf-name-reference-v16 */
(function(){
 const byId=id=>document.getElementById(id);
 function clean(){return String(byId('planName')?.value||'').trim().replace(/\s+/g,' ').slice(0,80)}
 function syncPdfName(){
   const box=byId('pdfPlanIdentityV16');if(!box)return;
   const name=clean();box.textContent='';
   if(!name){box.style.display='none';return}
   const label=document.createElement('span');label.textContent='Investment plan for ';
   const strong=document.createElement('strong');strong.textContent=name;
   box.append(label,strong);
   box.style.display='none';
 }
 byId('planName')?.addEventListener('input',syncPdfName);
 byId('planName')?.addEventListener('change',syncPdfName);
 addEventListener('beforeprint',syncPdfName);
 setTimeout(syncPdfName,0);
})();
</script>
'''
s=s.replace('</body>',js+'\n</body>',1)
INDEX.write_text(s,encoding='utf-8')
print(f'Applied PDF name/reference V16 and synced visible app version to {version_label}')

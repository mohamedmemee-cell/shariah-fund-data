#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'docs'/'index.html'
s=INDEX.read_text(encoding='utf-8')
marker='pdf-name-reference-v16'
if marker in s:
    print('PDF name/reference V16 already present')
    raise SystemExit(0)

# Add a dedicated print-only identity line inside Step 6. This is separate from
# the on-screen identity summary so later print/layout patches cannot hide it.
anchor='<div class="planIdentitySummary" id="planIdentitySummary" aria-live="polite"></div><div class="planSummaryGrid" id="planSummaryGrid"></div>'
if anchor in s:
    repl='<div class="planIdentitySummary" id="planIdentitySummary" aria-live="polite"></div><div id="pdfPlanIdentityV16" class="pdfPlanIdentityV16"></div><div class="planSummaryGrid" id="planSummaryGrid"></div>'
    s=s.replace(anchor,repl,1)
else:
    # Fallback in case later patches changed the exact identity markup.
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
   // Inline style is only a screen fallback; @media print forces display when printing.
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

# Bump the visible build label so it is easy to confirm this fix is deployed.
s=s.replace('id="calcVersionV15" class="calcVersionV14">v15</div>','id="calcVersionV15" class="calcVersionV14">v16</div>',1)

INDEX.write_text(s,encoding='utf-8')
print('Applied PDF name/reference V16')

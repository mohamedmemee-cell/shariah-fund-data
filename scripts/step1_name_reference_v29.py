#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'docs'/'index.html'
p=INDEX
s=p.read_text(encoding='utf-8')
MARKER='step1-name-reference-v29'
if MARKER in s:
    print('Step 1 name/reference V29 already present')
    raise SystemExit(0)

css=r'''
/* step1-name-reference-v29 */
#portfolioBuilderSection #planIdentitySection{margin:0 0 16px;padding:14px 16px;border:1px solid color-mix(in srgb,var(--brand) 22%,var(--line));border-radius:13px;background:color-mix(in srgb,var(--brand-soft) 45%,var(--card));box-shadow:none}
#portfolioBuilderSection #planIdentitySection .sectiontitle{margin-bottom:9px}
#portfolioBuilderSection #planIdentitySection .sectiontitle h2{font-size:17px}
#portfolioBuilderSection #planIdentitySection .sectiontitle h2::before{content:none!important}
#portfolioBuilderSection #planIdentitySection .planNameField{max-width:700px}
#portfolioBuilderSection #planIdentitySection .note{margin-bottom:0}
'''
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
<script>
/* step1-name-reference-v29 */
(function(){
 const identity=document.getElementById('planIdentitySection');
 const step1=document.getElementById('portfolioBuilderSection');
 if(!identity||!step1)return;
 const header=step1.querySelector(':scope > .wizardHeaderV28');
 const title=step1.querySelector(':scope > .sectiontitle');
 // Keep the wizard header first. The name/reference block then becomes the first
 // editable content inside Step 1, before the Portfolio Builder options.
 const anchor=header?.nextSibling||title||step1.firstChild;
 step1.insertBefore(identity,anchor);
 identity.classList.remove('full');
 identity.classList.add('step1IdentityV29');
})();
</script>
<!-- step1-name-reference-v29 -->
'''
s=s.replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Moved name/reference block to the top of Step 1')

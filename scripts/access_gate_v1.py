#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'docs'/'index.html'
s=p.read_text(encoding='utf-8')
if 'calculator-access-gate-v1' in s:
    print('calculator access gate already present')
    raise SystemExit(0)

css=r'''
/* calculator-access-gate-v1 */
.accessGateV1{margin:12px 0 18px;padding:16px 18px;border:1px solid color-mix(in srgb,var(--brand) 30%,var(--line));border-radius:16px;background:linear-gradient(135deg,color-mix(in srgb,var(--brand-soft) 85%,var(--card)),var(--card));box-shadow:0 8px 24px rgba(0,0,0,.05)}
.accessGateV1.shared{border-left:5px solid var(--brand)}.accessGateV1.unlocked{border-color:color-mix(in srgb,var(--green) 45%,var(--line));background:color-mix(in srgb,var(--green-soft) 80%,var(--card))}
.accessGateHead{display:flex;justify-content:space-between;gap:14px;align-items:flex-start;flex-wrap:wrap}.accessGateTitle{font-size:17px;font-weight:850;color:var(--brand-strong);margin:0 0 4px}.accessGateText{margin:0;color:var(--muted);font-size:13px;line-height:1.5;max-width:760px}.accessGateForm{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:12px}.accessGateForm input{min-width:220px;padding:10px 12px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--text);font:inherit;text-transform:uppercase;letter-spacing:.08em}.accessGateError{min-height:18px;margin-top:6px;color:var(--danger);font-size:12px;font-weight:700}.accessGateStatus{display:inline-flex;align-items:center;gap:6px;padding:5px 9px;border-radius:999px;background:var(--soft);font-size:12px;font-weight:800}.lockedFieldV1{cursor:not-allowed!important}.accessLockedNoteV1{font-size:12px;color:var(--muted);margin-top:7px}.accessLockBtnV1{display:none}.accessGateV1.unlocked .accessLockBtnV1{display:inline-flex}
@media(max-width:600px){.accessGateForm{align-items:stretch}.accessGateForm input,.accessGateForm .btn{width:100%;min-width:0}}
'''
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
<script>
/* calculator-access-gate-v1 */
(function(){
 const ACCESS_HASH='137b7af84f7f1bc2904e3970c90595f8963a3b2629ae6d810062861765052600';
 const byId=id=>document.getElementById(id);
 const hasSharedPlan=()=>/(?:^#|&)plan=/.test(location.hash);
 const allowedIds=new Set(['themeMode','backTopV4','downloadPlanPdf','copyPlanLink','showPlanQr','accessCodeV1','accessUnlockV1','accessLockV1']);
 function protectedControls(){return [...document.querySelectorAll('main input,main select,main button')].filter(el=>!allowedIds.has(el.id)&&!el.closest('#calculatorAccessGateV1'))}
 function setLocked(locked){
   document.documentElement.dataset.calculatorLocked=locked?'true':'false';
   protectedControls().forEach(el=>{if(locked){if(!el.dataset.wasDisabledV1)el.dataset.wasDisabledV1=el.disabled?'1':'0';el.disabled=true;el.classList.add('lockedFieldV1')}else{el.disabled=el.dataset.wasDisabledV1==='1';el.classList.remove('lockedFieldV1');delete el.dataset.wasDisabledV1}});
   const gate=byId('calculatorAccessGateV1'),status=byId('accessStatusV1'),title=byId('accessTitleV1'),text=byId('accessTextV1'),form=byId('accessFormV1');
   if(!gate)return;
   gate.classList.toggle('unlocked',!locked);gate.classList.toggle('shared',hasSharedPlan());
   if(locked){status.textContent=hasSharedPlan()?'View only':'Locked';title.textContent=hasSharedPlan()?'Shared investment plan — view only':'Calculator access required';text.textContent=hasSharedPlan()?'You can review this shared plan and download its report. Enter the access code to edit the plan or use the calculator.':'Enter the access code to use the Shariah Investment Calculator.';form.style.display='flex'}
   else{status.textContent='Unlocked';title.textContent=hasSharedPlan()?'Shared plan unlocked':'Calculator unlocked';text.textContent='You can now use all calculator controls for this browser session.';form.style.display='none'}
 }
 async function sha256(value){const data=new TextEncoder().encode(value.trim().toUpperCase());const buf=await crypto.subtle.digest('SHA-256',data);return [...new Uint8Array(buf)].map(b=>b.toString(16).padStart(2,'0')).join('')}
 function ensureGate(){
   if(byId('calculatorAccessGateV1'))return;
   const gate=document.createElement('section');gate.id='calculatorAccessGateV1';gate.className='accessGateV1';gate.innerHTML=`<div class="accessGateHead"><div><div class="accessGateTitle" id="accessTitleV1">Calculator access required</div><p class="accessGateText" id="accessTextV1">Enter the access code to use the Shariah Investment Calculator.</p></div><span class="accessGateStatus" id="accessStatusV1">Locked</span></div><div class="accessGateForm" id="accessFormV1"><input id="accessCodeV1" type="password" autocomplete="off" spellcheck="false" placeholder="Enter access code" aria-label="Calculator access code"><button class="btn primary" id="accessUnlockV1" type="button">Unlock calculator</button></div><div class="accessGateError" id="accessErrorV1"></div><div class="accessLockedNoteV1">Shared-plan viewing remains available while locked. Calculator editing and new calculations require the access code.</div><button class="btn accessLockBtnV1" id="accessLockV1" type="button" style="margin-top:10px">Lock calculator</button>`;
   const nav=document.querySelector('.siteNav')||document.querySelector('nav');
   if(nav)nav.insertAdjacentElement('afterend',gate);else document.querySelector('main')?.prepend(gate);
   byId('accessUnlockV1').addEventListener('click',unlock);
   byId('accessCodeV1').addEventListener('keydown',e=>{if(e.key==='Enter')unlock()});
   byId('accessLockV1').addEventListener('click',()=>{sessionStorage.removeItem('shariahCalculatorUnlocked');byId('accessCodeV1').value='';setLocked(true)});
 }
 async function unlock(){const input=byId('accessCodeV1'),err=byId('accessErrorV1');err.textContent='';const h=await sha256(input.value);if(h!==ACCESS_HASH){err.textContent='That access code is not correct.';input.select();return}sessionStorage.setItem('shariahCalculatorUnlocked','1');input.value='';setLocked(false)}
 function apply(){ensureGate();setLocked(sessionStorage.getItem('shariahCalculatorUnlocked')!=='1')}
 document.addEventListener('DOMContentLoaded',()=>setTimeout(apply,650));
 if(document.readyState!=='loading')setTimeout(apply,650);
 new MutationObserver(()=>{if(document.documentElement.dataset.calculatorLocked==='true')protectedControls().forEach(el=>{if(!el.disabled){el.dataset.wasDisabledV1='0';el.disabled=true;el.classList.add('lockedFieldV1')}})}).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>
'''
s=s.replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Applied calculator access gate V1')

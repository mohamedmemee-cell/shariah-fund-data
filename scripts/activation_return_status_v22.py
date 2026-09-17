#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'docs'/'fund-details.html'
s=p.read_text(encoding='utf-8')
marker='activation-return-status-v22'
if marker in s:
    print('Activation return status V22 already present')
    raise SystemExit(0)

css=r'''
/* activation-return-status-v22 */
.activationStatusV22{margin-top:12px;padding:13px 14px;border:1px solid var(--line);border-radius:11px;background:var(--soft);line-height:1.45}.activationStatusV22 strong{display:block;margin-bottom:3px}.activationStatusV22.ok{border-color:color-mix(in srgb,var(--accent) 45%,var(--line))}.activationStatusV22.warn{border-color:color-mix(in srgb,var(--warn) 45%,var(--line));background:color-mix(in srgb,var(--warn) 8%,var(--card))}.activationStatusV22 .miniActions{display:flex;gap:8px;flex-wrap:wrap;margin-top:9px}.activationStatusV22 .miniActions a{padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--text);text-decoration:none;font-weight:750}
'''
s=s.replace('</style>',css+'\n</style>',1)
js=r'''
<script>
/* activation-return-status-v22 */
(function(){
 const repo='mohamedmemee-cell/shariah-fund-data',api='https://api.github.com/repos/'+repo;
 const params=new URLSearchParams(location.search),fundId=params.get('id');
 const btn=document.getElementById('activationBtn');if(!btn||!fundId)return;
 let status=document.getElementById('activationStatusV22');if(!status){status=document.createElement('div');status.id='activationStatusV22';status.className='activationStatusV22';status.style.display='none';btn.closest('.links')?.insertAdjacentElement('afterend',status)}
 function show(title,text,kind='',issueUrl=''){status.style.display='block';status.className='activationStatusV22 '+kind;status.innerHTML=`<strong>${title}</strong><span>${text}</span>${issueUrl?`<div class="miniActions"><a href="${issueUrl}" target="_blank" rel="noopener">Open GitHub request</a></div>`:''}`}
 async function current(){const [fr,dr]=await Promise.all([fetch('./shariah-funds.json?ts='+Date.now(),{cache:'no-store'}),fetch('./fund-directory.json?ts='+Date.now(),{cache:'no-store'})]);const feed=await fr.json(),dir=await dr.json();return {f:feed.funds.find(x=>x.id===fundId),d:(dir.funds||{})[fundId]||{}}}
 async function issueFor(name){try{const r=await fetch(api+'/issues?state=all&per_page=100&ts='+Date.now(),{cache:'no-store'});if(!r.ok)return null;const rows=await r.json();return rows.find(x=>x.title==='Activate tracked fund: '+name)||null}catch(e){return null}}
 async function check(){try{const {f}=await current();if(!f)return;if(f.bucket!=='Watchlist'){show('Fund activated','This fund is now active for Portfolio Builder calculations.','ok');btn.style.display='none';document.getElementById('activationConfirm')?.style.setProperty('display','none');document.getElementById('fundStatus').textContent='Active';return}const issue=await issueFor(f.name);if(issue){const u=issue.html_url||('https://github.com/'+repo+'/issues/'+issue.number);show('Activation request accepted',`GitHub issue #${issue.number} was created. The fund is being activated and the calculator will update automatically when processing finishes.`,'ok',u);return}show('Ready for activation','Click the button below. GitHub will open once for confirmation. Click the green Create button there, close the GitHub tab and return here.');}catch(e){show('Could not check activation status','Refresh this page and try again.','warn')}}
 const clone=btn.cloneNode(true);btn.replaceWith(clone);clone.textContent='Activate for Portfolio Builder';clone.style.display='inline-block';clone.onclick=async()=>{try{const {f,d}=await current();if(!f)return;const body=`Fund id: ${f.id}\nFund name: ${f.name}\nAccount suitability: ${d.account_suitability||'Not confirmed'}\n\nFinal activation review requested from the fund details page.`;localStorage.setItem('activationRequestV22',JSON.stringify({id:f.id,name:f.name,startedAt:new Date().toISOString()}));show('Confirm activation in GitHub','A GitHub page is opening. Click the green Create button once, then close that tab and return here.');window.open('https://github.com/'+repo+'/issues/new?title='+encodeURIComponent('Activate tracked fund: '+f.name)+'&body='+encodeURIComponent(body),'_blank','noopener');setTimeout(check,1200)}catch(e){show('Could not prepare activation','Refresh and try again.','warn')}};
 document.getElementById('activationConfirm')?.style.setProperty('display','none');window.addEventListener('focus',()=>setTimeout(check,300));document.addEventListener('visibilitychange',()=>{if(!document.hidden)setTimeout(check,300)});setTimeout(check,300);
})();
</script>
'''
s=s.replace('</body>',js+'\n<!-- '+marker+' -->\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Applied activation return status V22')

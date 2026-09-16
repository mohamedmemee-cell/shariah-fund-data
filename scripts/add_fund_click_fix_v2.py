#!/usr/bin/env python3
from pathlib import Path

p=Path(__file__).resolve().parents[1]/'docs'/'add-fund.html'
s=p.read_text(encoding='utf-8')
if 'ADD_FUND_CLICK_FIX_V2' in s:
    print('Add Fund click fix already present')
    raise SystemExit(0)

js=r'''
<script>
/* ADD_FUND_CLICK_FIX_V2 */
(function(){
  const byId=id=>document.getElementById(id);
  const slug=s=>(s||'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,100);
  function value(id){return (byId(id)?.value||'').trim()}
  function buildIssueUrl(){
    const name=value('name');
    if(!name){alert('Please enter the fund name.');return null}
    const manager=value('manager')||'Unknown';
    const website=value('website')||'Not supplied';
    const factsheet=value('factsheet')||'Not supplied';
    const body=[
      'Candidate fund onboarding request','',
      'Fund name: '+name,
      'Fund manager: '+manager,
      'Official fund page: '+website,
      'Factsheet: '+factsheet
    ].join('\n');
    const id=slug(name);
    localStorage.setItem('candidateFundTracking',JSON.stringify({id,name,manager,createdAt:new Date().toISOString()}));
    return 'https://github.com/mohamedmemee-cell/shariah-fund-data/issues/new?title='+encodeURIComponent('Candidate fund: '+name)+'&body='+encodeURIComponent(body);
  }
  function start(){
    const url=buildIssueUrl();if(!url)return;
    const card=byId('confirmCard'),cont=byId('continueConfirm'),status=byId('statusCard');
    if(card){card.classList.remove('hidden');card.scrollIntoView({behavior:'smooth',block:'center'})}
    if(cont){cont.href=url;cont.target='_blank';cont.rel='noopener';cont.onclick=()=>{setTimeout(()=>{card?.classList.add('hidden');status?.classList.remove('hidden');status?.scrollIntoView({behavior:'smooth',block:'start'});location.reload()},600)}}
    byId('cancelConfirm')?.addEventListener('click',()=>card?.classList.add('hidden'),{once:true});
  }
  const btn=byId('submit');
  if(btn){
    const clone=btn.cloneNode(true);
    btn.replaceWith(clone);
    clone.addEventListener('click',start);
  }
})();
</script>
'''
s=s.replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Applied Add Fund click fix V2')

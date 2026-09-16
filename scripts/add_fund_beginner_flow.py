from pathlib import Path

p = Path('docs/add-fund.html')
s = p.read_text(encoding='utf-8')
marker = 'BEGINNER_CONFIRMATION_FLOW_V1'
if marker in s:
    print('Beginner Add Fund confirmation flow already applied')
    raise SystemExit(0)

s = s.replace(
'''<div class="callout"><b>How it works:</b> this site is hosted on GitHub Pages, so GitHub requires one confirmation before a new candidate can be written into the repository. We open that confirmation in a separate tab. After you click <b>Create issue</b> there, come back here — research and tracking continue automatically.</div>
<button class="btn" id="submit" type="button">Start automated onboarding</button>''',
'''<div class="callout"><b>What happens next:</b> we will prepare the fund for research. One quick confirmation is needed before the automated checks can begin.</div>
<button class="btn" id="submit" type="button">Start automated onboarding</button>
<div class="callout hidden" id="confirmCard"><b>One quick confirmation</b><br>This one-time confirmation lets the research process begin. No investment account or payment is created.<div class="actions"><a class="btn" id="continueConfirm" href="#">Continue</a><button class="btn secondary" id="cancelConfirm" type="button">Cancel</button></div></div>''')

s = s.replace('Waiting for GitHub confirmation', 'Waiting for confirmation')
s = s.replace('Create the candidate in the GitHub tab, then return here. This page will detect it automatically.', 'Complete the one-time confirmation, then return here. Research progress will appear automatically.')
s = s.replace('Waiting for the GitHub candidate confirmation. If you already clicked Create issue, this normally appears here shortly.', 'Waiting for your confirmation. Once completed, the research process normally starts shortly.')

old = """const url='https://github.com/'+REPO+'/issues/new?title='+encodeURIComponent('Candidate fund: '+name)+'&body='+encodeURIComponent(body);window.open(url,'_blank','noopener');poll()"""
new = """const url='https://github.com/'+REPO+'/issues/new?title='+encodeURIComponent('Candidate fund: '+name)+'&body='+encodeURIComponent(body);$('confirmCard').classList.remove('hidden');$('continueConfirm').href=url;$('continueConfirm').onclick=()=>{setTimeout(()=>{$('confirmCard').classList.add('hidden');$('statusCard').scrollIntoView({behavior:'smooth',block:'start'});poll()},500)};$('cancelConfirm').onclick=()=>{$('confirmCard').classList.add('hidden')};$('confirmCard').scrollIntoView({behavior:'smooth',block:'center'})"""
if old not in s:
    raise SystemExit('Could not find Add Fund submit action; refusing unsafe partial patch')
s = s.replace(old, new)

s = s.replace('</script></main></body></html>', f'<!-- {marker} -->\n</script></main></body></html>')
p.write_text(s, encoding='utf-8')
print('Applied beginner Add Fund confirmation flow')

#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DETAILS=ROOT/'docs'/'fund-details.html'
marker='editable-shariah-source-v13'

s=DETAILS.read_text(encoding='utf-8')
if marker in s:
    print('Editable Shariah source V13 already present')
    raise SystemExit(0)

# Add a dedicated field for the certificate/governance URL.
anchor='<div><label>Shariah governance verified?</label><select id="vShariah"><option value="">Leave unchanged</option><option value="Yes">Yes</option><option value="No">No</option></select></div>'
field='''<div><label>Shariah governance verified?</label><select id="vShariah"><option value="">Leave unchanged</option><option value="Yes">Yes</option><option value="No">No</option></select></div><div class="verifyWide"><label>Shariah certificate / governance source URL <span class="muted">(optional)</span></label><input id="vShariahSource" type="url" placeholder="https://... official Shariah certificate or governance page"><div class="verificationMeta">Use the official certificate, Shariah board page or other reliable governance source. This is the link shown by the Shariah source button.</div></div>'''
if anchor in s:
    s=s.replace(anchor,field,1)
else:
    print('Warning: Shariah verification field anchor not found')

# Prefill the dedicated field with the currently stored source.
old="byId('vTer').value=currentFund?.ter??'';byId('vDate').value=new Date().toISOString().slice(0,10);"
new="byId('vTer').value=currentFund?.ter??'';if(byId('vShariahSource'))byId('vShariahSource').value=currentDir.shariah_source||'';byId('vDate').value=new Date().toISOString().slice(0,10);"
if old in s:
    s=s.replace(old,new,1)
else:
    print('Warning: verification form prefill anchor not found')

# Either a general verification source/contact OR a dedicated Shariah source is enough
# to trace a Shariah-certificate update.
old="byId('saveVerification')?.addEventListener('click',()=>{if(!byId('vSource').value.trim()){alert('Please record the source or person contacted so the information can be traced later.');return}byId('manualConfirm').style.display='block'});"
new="byId('saveVerification')?.addEventListener('click',()=>{const general=(byId('vSource')?.value||'').trim(),shariah=(byId('vShariahSource')?.value||'').trim();if(!general&&!shariah){alert('Please record a source/contact or the Shariah certificate/governance URL so the information can be traced later.');return}byId('manualConfirm').style.display='block'});"
if old in s:
    s=s.replace(old,new,1)
else:
    print('Warning: save validation anchor not found')

# Include the dedicated source in the GitHub verification request so it can be
# written into fund-directory.json as shariah_source.
old="line('Shariah governance verified','vShariah'),line('1Y return','v1y')"
new="line('Shariah governance verified','vShariah'),line('Shariah certificate/governance source URL','vShariahSource'),line('1Y return','v1y')"
if old in s:
    s=s.replace(old,new,1)
else:
    print('Warning: issue body anchor not found')

# Add marker for idempotence.
s=s.replace('</body>',f'\n<!-- {marker} -->\n</body>',1)
DETAILS.write_text(s,encoding='utf-8')
print('Applied editable Shariah source V13')

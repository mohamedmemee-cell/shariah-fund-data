#!/usr/bin/env python3
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"docs"/"fund-details.html"
MARK="single-activation-controller-v38"
s=P.read_text(encoding="utf-8")

# Remove the obsolete V22 activation JavaScript controller. Its status box styles
# are intentionally retained because the V36 controller reuses that presentation.
patterns=[
    r'\n?<script>\s*/\* activation-return-status-v22 \*/.*?</script>\s*\n?<!-- activation-return-status-v22 -->',
    r'\n?<script[^>]*>\s*/\* activation-return-status-v22 \*/.*?</script>\s*\n?<!-- activation-return-status-v22 -->'
]
for pat in patterns:
    s=re.sub(pat,'\n',s,flags=re.S)

if MARK not in s:
    s=s.replace("</body>","<!-- "+MARK+" -->\n</body>",1)

P.write_text(s,encoding="utf-8")
print("Removed obsolete V22 activation controller; V36 is now authoritative")

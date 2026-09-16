#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / 'docs' / 'index.html'
s = p.read_text(encoding='utf-8')

# Remove the access-gate CSS block inserted by access_gate_v1.py.
s = re.sub(r'\n?/\* calculator-access-gate-v1 \*/\n\.accessGateV1\{.*?@media\(max-width:600px\)\{\.accessGateForm\{align-items:stretch\}\.accessGateForm input,\.accessGateForm \.btn\{width:100%;min-width:0\}\}\n?', '', s, count=1, flags=re.S)

# Remove the complete access-gate script inserted near </body>.
s = re.sub(r'\n?<script>\n/\* calculator-access-gate-v1 \*/.*?</script>\n?', '\n', s, count=1, flags=re.S)

# Defensive cleanup in case a generated page already contains the gate markup.
s = re.sub(r'<section id="calculatorAccessGateV1".*?</section>', '', s, count=1, flags=re.S)

p.write_text(s, encoding='utf-8')
print('Removed calculator access-code gate')

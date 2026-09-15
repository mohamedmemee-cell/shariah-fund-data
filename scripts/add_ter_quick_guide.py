#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'docs' / 'index.html'
s = p.read_text(encoding='utf-8')

if '4. Fees (TER)' in s:
    print('TER quick-guide explanation already present; no changes needed.')
    raise SystemExit(0)

old = '<div class="beginner"><h3>Quick guide — no investment knowledge needed</h3><div class="beginnergrid"><div class="beginneritem"><b>1. Contribution</b><span>How much money you put in each month.</span></div><div class="beginneritem"><b>2. Risk</b><span>How much the value may move up and down. Higher risk can mean bigger gains, but also bigger losses.</span></div><div class="beginneritem"><b>3. Return</b><span>The growth you hope the investment earns. Historical returns are useful clues, not promises.</span></div></div></div>'
new = '<div class="beginner"><h3>Quick guide — no investment knowledge needed</h3><div class="beginnergrid"><div class="beginneritem"><b>1. Contribution</b><span>How much money you put in each month.</span></div><div class="beginneritem"><b>2. Risk</b><span>How much the value may move up and down. Higher risk can mean bigger gains, but also bigger losses.</span></div><div class="beginneritem"><b>3. Return</b><span>The growth you hope the investment earns. Historical returns are useful clues, not promises.</span></div><div class="beginneritem"><b>4. Fees (TER)</b><span>TER means Total Expense Ratio — the approximate yearly cost of running a fund, shown as a percentage. For example, a 1.00% TER is roughly R100 per year for every R10,000 invested. Lower fees help, but they are only one part of choosing a fund.</span></div></div></div>'

if old not in s:
    raise SystemExit('Could not find beginner quick-guide block')
s = s.replace(old, new, 1)
s = s.replace('.beginnergrid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}', '.beginnergrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}', 1)

p.write_text(s, encoding='utf-8')
print('Added TER definition to beginner quick guide')

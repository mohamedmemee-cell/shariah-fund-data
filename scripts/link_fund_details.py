#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'docs' / 'index.html'
s = p.read_text(encoding='utf-8')

if 'function fundHref(f)' not in s:
    anchor = "const $=id=>document.getElementById(id),money=n=>new Intl.NumberFormat('en-ZA',{style:'currency',currency:'ZAR',maximumFractionDigits:0}).format(n||0),pct=n=>n==null?'—':Number(n).toFixed(2)+'%';"
    repl = anchor + "\nfunction fundHref(f){return './fund-details.html?id='+encodeURIComponent(f.id)}\nfunction fundNameLink(f){return `<a href=\"${fundHref(f)}\" style=\"color:inherit;text-decoration:underline;text-decoration-style:dotted;text-underline-offset:3px\">${f.name}</a>`}"
    if anchor not in s:
        raise SystemExit('Could not find JS helper anchor')
    s = s.replace(anchor, repl, 1)

s = s.replace('<span class="fundname" title="${f.name}">${f.name}</span>', '<span class="fundname" title="Click for fund details">${fundNameLink(f)}</span>')
s = s.replace('<tr><td>${f.name}</td><td>${f.bucket}</td>', '<tr><td>${fundNameLink(f)}</td><td>${f.bucket}</td>')
s = s.replace('<tr><td>${r.fund.name}</td><td>${r.band}</td>', '<tr><td>${fundNameLink(r.fund)}</td><td>${r.band}</td>')

p.write_text(s, encoding='utf-8')
print('Linked fund names to fund-details.html')

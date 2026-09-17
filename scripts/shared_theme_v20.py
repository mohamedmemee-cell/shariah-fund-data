#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
FILES = [
    'discovery.html',
    'add-fund.html',
    'fund-explorer.html',
    'fund-details.html',
    'ranking.html',
]
MARKER = 'shared-theme-v20'

CSS = r'''
/* shared-theme-v20 */
html[data-theme="light"]{
  color-scheme:light;
  --bg:#f4f7f7;--card:#fff;--text:#172022;--muted:#667276;--line:#d8e1e2;
  --accent:#16715d;--accent2:#0f5b4b;--soft:#e7f3ef;--warn:#a86200;
  --brand:#0f766e;--brand-strong:#0b5f59;--brand-soft:#e8f6f3;
}
html[data-theme="dark"]{
  color-scheme:dark;
  --bg:#101718;--card:#182123;--text:#edf3f1;--muted:#9eacab;--line:#334044;
  --accent:#66d1b5;--accent2:#92e4cf;--soft:#203532;--warn:#e2ad5e;
  --brand:#64d6bd;--brand-strong:#8ee8d3;--brand-soft:#1f3c37;
}
'''

JS = r'''
<script>
/* shared-theme-v20 */
(function(){
  const key='shariahTheme';
  const saved=localStorage.getItem(key)||'system';
  if(saved==='light'||saved==='dark') document.documentElement.dataset.theme=saved;
  else document.documentElement.removeAttribute('data-theme');

  // Theme is selected once for the whole application from the Calculator page.
  // Remove page-specific selectors from secondary pages so there is only one setting.
  document.querySelectorAll('#themeMode,.themeSelect').forEach(el=>{
    const parent=el.closest('label,.planTools,.themeControl,.theme-control');
    if(parent && /theme/i.test(parent.textContent||'')) parent.remove();
    else el.remove();
  });
})();
</script>
'''

for name in FILES:
    p = DOCS / name
    if not p.exists():
        continue
    s = p.read_text(encoding='utf-8')
    if MARKER in s:
        print(f'{name}: shared theme already present')
        continue
    if '</style>' in s:
        s = s.replace('</style>', CSS + '\n</style>', 1)
    else:
        s = s.replace('</head>', '<style>' + CSS + '</style></head>', 1)
    s = s.replace('</body>', JS + '\n</body>', 1)
    p.write_text(s, encoding='utf-8')
    print(f'{name}: shared theme applied')

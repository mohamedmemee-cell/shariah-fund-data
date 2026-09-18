#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "docs" / "index.html"
s = p.read_text(encoding="utf-8")

MARKER = 'id="quickGuideV35"'

if MARKER in s:
    print("Compact beginner quick guide already present; no changes needed.")
    raise SystemExit(0)

old = '''<div class="beginner"><h3>Quick guide — no investment knowledge needed</h3><div class="beginnergrid"><div class="beginneritem"><b>1. Contribution</b><span>How much money you put in each month.</span></div><div class="beginneritem"><b>2. Risk</b><span>How much the value may move up and down. Higher risk can mean bigger gains, but also bigger losses.</span></div><div class="beginneritem"><b>3. Return</b><span>The growth you hope the investment earns. Historical returns are useful clues, not promises.</span></div><div class="beginneritem"><b>4. Fees (TER)</b><span>TER means Total Expense Ratio — the approximate yearly cost of running a fund, shown as a percentage. For example, a 1.00% TER is roughly R100 per year for every R10,000 invested. Lower fees help, but they are only one part of choosing a fund.</span></div></div></div>'''

new = '''<details class="beginnerGuideV35" id="quickGuideV35">
  <summary>
    <span class="guideSummaryText"><b>Quick Guide — New to investing? Start here</b><small>Understand risk, returns, fees and how this calculator works.</small></span>
    <span class="guideToggleV35" aria-hidden="true">Open guide</span>
  </summary>
  <div class="guideBodyV35">
    <section class="guideSectionV35 guideIntroV35">
      <h3>What this calculator does</h3>
      <p>You tell us how much you want to invest, how comfortable you are with risk and how long you plan to invest. The calculator uses the Shariah-compliant funds it tracks to build a possible mix, show where your monthly money could go and illustrate how the plan could grow over time.</p>
      <p class="guideNoteV35"><strong>Important:</strong> projections and historical returns are planning illustrations, not promises or guaranteed future returns.</p>
    </section>

    <section class="guideSectionV35">
      <h3>Investment basics</h3>
      <div class="guideCardsV35">
        <div class="guideCardV35"><b>Contribution</b><span>How much money you put into the investment each month.</span></div>
        <div class="guideCardV35"><b>Risk</b><span>How much the value may move up and down. More risk can mean stronger long-term growth potential, but also bigger losses.</span></div>
        <div class="guideCardV35"><b>Return</b><span>The growth an investment has earned or may earn. Historical returns help us compare funds, but they do not predict the future.</span></div>
        <div class="guideCardV35"><b>Fees (TER)</b><span>TER is the Total Expense Ratio — the approximate yearly cost of running a fund. A 1.00% TER is roughly R100 per year for every R10,000 invested.</span></div>
        <div class="guideCardV35"><b>TFSA</b><span>A Tax-Free Savings Account. Investment growth and withdrawals are generally tax-free under South African rules, but annual and lifetime contribution limits apply.</span></div>
      </div>
    </section>

    <section class="guideSectionV35">
      <h3>Understanding the risk mix</h3>
      <div class="riskGuideV35">
        <div><b>Low risk</b><span>Usually aims for steadier returns with smaller ups and downs. Growth potential is normally lower than higher-risk investments.</span></div>
        <div><b>Medium risk</b><span>Balances stability and growth. It can still fall in value, but usually moves less dramatically than a high-risk portfolio.</span></div>
        <div><b>High risk</b><span>Can move up and down much more. It may offer stronger long-term growth potential, but losses can also be larger.</span></div>
      </div>
      <p class="guideMixV35"><strong>What does “risk mix” mean?</strong> Your portfolio does not have to be all low, all medium or all high risk. The calculator can combine different risk bands — for example, mostly medium risk with some low-risk stability and some higher-risk growth — to create one overall portfolio.</p>
    </section>

    <section class="guideSectionV35">
      <h3>How to use the calculator</h3>
      <ol class="guideStepsV35">
        <li><b>Choose your portfolio approach.</b><span>Tell the calculator what kind of investment mix you want.</span></li>
        <li><b>Enter your contribution.</b><span>Add what you can invest monthly and any annual increase.</span></li>
        <li><b>Review the monthly split.</b><span>See how the contribution is divided between the selected funds and account types.</span></li>
        <li><b>Look at the projection.</b><span>Compare cautious, expected and optimistic planning scenarios.</span></li>
        <li><b>Review milestones.</b><span>See how the plan may develop at different points in time.</span></li>
        <li><b>Check the summary.</b><span>Review the final fund mix, risk, fees and assumptions before making any investment decision.</span></li>
      </ol>
    </section>

    <section class="guideSectionV35 shariahGuideV35">
      <h3>Shariah-compliant investing</h3>
      <p>The calculator is designed to use investments tracked as Shariah-compliant or still undergoing verification. Fund structures, governance and certificates can change, so review the latest Shariah information in Fund Explorer before investing.</p>
    </section>
  </div>
</details>'''

if old not in s:
    raise SystemExit("Could not find the current beginner quick-guide block in docs/index.html")

s = s.replace(old, new, 1)

css = r'''
/* v35 compact beginner quick guide */
.beginnerGuideV35{border:1px solid var(--line);background:var(--soft);border-radius:13px;margin-bottom:16px;overflow:hidden}
.beginnerGuideV35 summary{list-style:none;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:12px 16px;cursor:pointer;user-select:none}
.beginnerGuideV35 summary::-webkit-details-marker{display:none}
.beginnerGuideV35 summary:focus-visible{outline:2px solid var(--accent);outline-offset:-3px}
.guideSummaryText{display:flex;align-items:baseline;gap:10px;min-width:0}
.guideSummaryText b{font-size:15px}
.guideSummaryText small{font-size:12px;color:var(--muted);font-weight:500}
.guideToggleV35{flex:0 0 auto;font-size:12px;font-weight:800;color:var(--accent);white-space:nowrap}
.beginnerGuideV35[open] .guideToggleV35{font-size:0}
.beginnerGuideV35[open] .guideToggleV35::after{content:'Close guide';font-size:12px}
.guideBodyV35{border-top:1px solid var(--line);padding:16px;display:grid;gap:14px;background:var(--card)}
.guideSectionV35{border:1px solid var(--line);border-radius:11px;padding:14px;background:var(--soft)}
.guideSectionV35 h3{margin:0 0 8px;font-size:16px}
.guideSectionV35 p{margin:0;color:var(--muted);line-height:1.55}
.guideSectionV35 p+p{margin-top:8px}
.guideNoteV35{padding:9px 10px;border-radius:9px;background:var(--card);border:1px solid var(--line)}
.guideCardsV35{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:9px}
.guideCardV35,.riskGuideV35>div{border:1px solid var(--line);border-radius:9px;padding:10px;background:var(--card)}
.guideCardV35 b,.riskGuideV35 b{display:block;margin-bottom:4px}
.guideCardV35 span,.riskGuideV35 span{display:block;font-size:12px;color:var(--muted);line-height:1.45}
.riskGuideV35{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px}
.guideMixV35{margin-top:10px!important}
.guideStepsV35{margin:0;padding:0;list-style:none;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;counter-reset:guideStep}
.guideStepsV35 li{counter-increment:guideStep;position:relative;border:1px solid var(--line);border-radius:9px;padding:10px 10px 10px 38px;background:var(--card);min-height:58px}
.guideStepsV35 li::before{content:counter(guideStep);position:absolute;left:10px;top:10px;width:20px;height:20px;border-radius:50%;display:grid;place-items:center;background:var(--accent);color:var(--card);font-size:11px;font-weight:900}
.guideStepsV35 li b{display:block;font-size:12px;margin-bottom:3px}
.guideStepsV35 li span{display:block;font-size:12px;color:var(--muted);line-height:1.4}
.shariahGuideV35{border-color:color-mix(in srgb,var(--accent) 35%,var(--line));background:color-mix(in srgb,var(--accent) 5%,var(--soft))}
@media(max-width:900px){.guideCardsV35{grid-template-columns:repeat(2,minmax(0,1fr))}.guideStepsV35{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:650px){.beginnerGuideV35 summary{align-items:flex-start}.guideSummaryText{display:block}.guideSummaryText small{display:block;margin-top:3px}.riskGuideV35,.guideCardsV35,.guideStepsV35{grid-template-columns:1fr}.guideBodyV35{padding:11px}.guideSectionV35{padding:11px}}
'''

if '</style>' not in s:
    raise SystemExit("Could not find </style> in docs/index.html")
s = s.replace('</style>', css + '\n</style>', 1)

js = r'''
<script id="quickGuidePrefsV35">
(function(){
  const guide=document.getElementById('quickGuideV35');
  if(!guide) return;
  const key='shariahCalcQuickGuideOpenV35';
  try{
    if(localStorage.getItem(key)==='1') guide.open=true;
    guide.addEventListener('toggle',()=>localStorage.setItem(key,guide.open?'1':'0'));
  }catch(e){}
})();
</script>
'''

if '</body>' not in s:
    raise SystemExit("Could not find </body> in docs/index.html")
s = s.replace('</body>', js + '\n</body>', 1)

p.write_text(s, encoding="utf-8")
print("Replaced large beginner cards with compact expandable Quick Guide v35")

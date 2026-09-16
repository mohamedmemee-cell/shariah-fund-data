#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'docs' / 'index.html'
s = p.read_text(encoding='utf-8')

if 'ui-polish-v1-beginner-friendly' in s:
    print('UI polish already present; no changes needed.')
    raise SystemExit(0)

# Give the lower sections stable IDs so they can be styled without runtime JS.
s = s.replace('<section class="card full"><div class="sectiontitle"><h2>How the selected funds have performed historically</h2>', '<section class="card full" id="historySection"><div class="sectiontitle"><h2>How the selected funds have performed historically</h2>', 1)
s = s.replace('<section class="card full"><div class="sectiontitle"><h2>Portfolio growth</h2>', '<section class="card full" id="growthSection"><div class="sectiontitle"><h2>Portfolio growth</h2>', 1)
s = s.replace('<section class="card full"><div class="sectiontitle"><h2>Projection milestones</h2>', '<section class="card full" id="milestonesSection"><div class="sectiontitle"><h2>Projection milestones</h2>', 1)

# Friendlier top-level copy for non-investors.
s = s.replace('Maximise TFSA first, choose your preferred risk mix, compare target-return portfolios, and model long-term outcomes using live Shariah fund information.', 'Build a Shariah-compliant investment plan in plain English. Choose how much risk feels comfortable, see where your monthly money goes, and explore what it could grow to over time.', 1)

css = r'''
/* ui-polish-v1-beginner-friendly */
:root{
  --brand:#0f766e;--brand-strong:#0b5f59;--brand-soft:#e8f6f3;
  --blue:#3b82f6;--blue-soft:#edf5ff;
  --green:#16865f;--green-soft:#eaf7f1;
  --amber:#b96d08;--amber-soft:#fff6e7;
  --violet:#7c5cc4;--violet-soft:#f4f0ff;
  --coral:#b95d54;--coral-soft:#fff0ee;
}
body{background:linear-gradient(180deg,var(--bg) 0%,var(--bg) 72%,color-mix(in srgb,var(--brand-soft) 35%,var(--bg)) 100%)}
main{padding-top:22px}
.hero{position:relative;overflow:hidden;align-items:center;padding:24px 26px;border:1px solid color-mix(in srgb,var(--brand) 24%,var(--line));border-radius:22px;background:linear-gradient(120deg,color-mix(in srgb,var(--brand-soft) 92%,var(--card)),var(--card) 58%);box-shadow:0 10px 30px rgba(15,118,110,.06)}
.hero::after{content:'';position:absolute;width:220px;height:220px;border-radius:50%;right:-92px;top:-118px;background:color-mix(in srgb,var(--brand) 10%,transparent);pointer-events:none}
.hero h1{color:color-mix(in srgb,var(--text) 90%,var(--brand));line-height:1.05}.hero p{font-size:15px;line-height:1.55}.badge{border:1px solid color-mix(in srgb,var(--brand) 22%,var(--line));background:color-mix(in srgb,var(--brand-soft) 92%,var(--card));color:var(--brand-strong)}
.siteNav{margin:14px 0 18px;padding:4px;width:max-content;max-width:100%;border:1px solid var(--line);border-radius:12px;background:color-mix(in srgb,var(--card) 92%,var(--brand-soft))}.siteNav a{border:0;border-radius:8px;padding:9px 14px}.siteNav a.active{background:var(--brand);color:#fff;box-shadow:0 2px 6px rgba(15,118,110,.16)}
.beginner{padding:15px;border-color:color-mix(in srgb,var(--brand) 20%,var(--line));background:color-mix(in srgb,var(--brand-soft) 72%,var(--card));border-radius:16px}.beginner h3{font-size:17px}.beginneritem{position:relative;overflow:hidden;padding:12px 12px 12px 14px;background:var(--card);transition:border-color .12s ease,transform .12s ease}.beginneritem::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--brand)}.beginneritem:nth-child(2)::before{background:var(--amber)}.beginneritem:nth-child(3)::before{background:var(--blue)}.beginneritem:nth-child(4)::before{background:var(--violet)}.beginneritem:hover{transform:translateY(-1px);border-color:color-mix(in srgb,var(--brand) 26%,var(--line))}
.card{border-color:color-mix(in srgb,var(--brand) 9%,var(--line));box-shadow:0 6px 20px rgba(22,45,43,.035)}
#portfolioBuilderSection,.inputs,#monthlyPlanSection,#growthSection,#milestonesSection,#historySection{position:relative;overflow:hidden}
#portfolioBuilderSection::before,.inputs::before,#monthlyPlanSection::before,#growthSection::before,#milestonesSection::before,#historySection::before{content:'';position:absolute;left:0;right:0;top:0;height:4px;background:var(--brand)}
.inputs::before{background:var(--blue)}#monthlyPlanSection::before{background:var(--green)}#growthSection::before{background:var(--violet)}#milestonesSection::before{background:var(--amber)}#historySection::before{background:var(--blue)}
.sectiontitle{align-items:flex-start}.sectiontitle h2{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:21px;letter-spacing:-.01em}.sectiontitle h2::before{font-size:10px;letter-spacing:.07em;font-weight:850;padding:4px 7px;border-radius:999px;background:var(--brand-soft);color:var(--brand-strong)}
#portfolioBuilderSection .sectiontitle h2::before{content:'STEP 1'}.inputs .sectiontitle h2::before{content:'STEP 2';background:var(--blue-soft);color:#245fb4}#monthlyPlanSection .sectiontitle h2::before{content:'STEP 3';background:var(--green-soft);color:var(--green)}#growthSection .sectiontitle h2::before{content:'STEP 4';background:var(--violet-soft);color:var(--violet)}#milestonesSection .sectiontitle h2::before{content:'STEP 5';background:var(--amber-soft);color:var(--amber)}
.builder{gap:14px}.builderbox{position:relative;border-radius:15px;border-top:4px solid var(--blue);background:linear-gradient(180deg,var(--blue-soft),var(--card) 32%);transition:border-color .12s ease,transform .12s ease,box-shadow .12s ease}.builderbox:nth-child(2){border-top-color:var(--violet);background:linear-gradient(180deg,var(--violet-soft),var(--card) 32%)}.builderbox:nth-child(3){border-top-color:var(--green);background:linear-gradient(180deg,var(--green-soft),var(--card) 32%)}.builderbox:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(30,60,55,.07)}.builderbox .modeLabel{width:max-content;padding:4px 7px;border-radius:999px;background:var(--card);border:1px solid var(--line);font-size:10px}.builderbox h3{font-size:18px;margin-top:8px}.builderbox .btn.primary{border-radius:11px;box-shadow:0 3px 8px rgba(15,118,110,.12)}.builderbox:nth-child(1) .btn.primary{background:var(--blue);border-color:var(--blue)}.builderbox:nth-child(2) .btn.primary{background:var(--violet);border-color:var(--violet)}.builderbox:nth-child(3) .btn.primary{background:var(--green);border-color:var(--green)}
.riskinputs .field{padding:8px;border-radius:10px}.riskinputs .field:nth-child(1){background:var(--green-soft)}.riskinputs .field:nth-child(2){background:var(--amber-soft)}.riskinputs .field:nth-child(3){background:var(--coral-soft)}.riskinputs .field:nth-child(1) input{border-color:color-mix(in srgb,var(--green) 40%,var(--line))}.riskinputs .field:nth-child(2) input{border-color:color-mix(in srgb,var(--amber) 40%,var(--line))}.riskinputs .field:nth-child(3) input{border-color:color-mix(in srgb,var(--coral) 40%,var(--line))}
.goalModes{gap:14px}.goalMode{position:relative;min-height:112px;border-width:2px;border-radius:15px;background:linear-gradient(180deg,color-mix(in srgb,var(--blue-soft) 65%,var(--card)),var(--card));transition:border-color .12s ease,transform .12s ease,background .12s ease}.goalMode:nth-child(2){background:linear-gradient(180deg,color-mix(in srgb,var(--violet-soft) 72%,var(--card)),var(--card))}.goalMode:hover{transform:translateY(-1px)}.goalMode.active{border-color:var(--brand);background:linear-gradient(180deg,var(--brand-soft),var(--card))}.goalMode.active::after{content:'✓';position:absolute;right:12px;top:12px;width:24px;height:24px;border-radius:50%;display:grid;place-items:center;background:var(--brand);color:#fff;font-size:13px;font-weight:900}.modeKicker{color:var(--brand-strong)}
.field input{min-height:44px;transition:border-color .12s ease,box-shadow .12s ease,background .12s ease}.field input:hover{border-color:color-mix(in srgb,var(--brand) 35%,var(--line))}.field input:focus{outline:none;border-color:var(--brand);box-shadow:0 0 0 3px color-mix(in srgb,var(--brand) 14%,transparent);background:color-mix(in srgb,var(--brand-soft) 34%,transparent)}
.rates{gap:12px}.rates>.field{padding:10px;border-radius:12px;border:1px solid var(--line);background:var(--card)}.rates>.field:nth-child(1){background:var(--blue-soft);border-color:color-mix(in srgb,var(--blue) 25%,var(--line))}.rates>.field:nth-child(2){background:var(--green-soft);border-color:color-mix(in srgb,var(--green) 28%,var(--line))}.rates>.field:nth-child(3){background:var(--amber-soft);border-color:color-mix(in srgb,var(--amber) 28%,var(--line))}.rates>.field:nth-child(1) label{color:#245fb4}.rates>.field:nth-child(2) label{color:var(--green)}.rates>.field:nth-child(3) label{color:var(--amber)}
.sliderrow{padding:8px 0 2px}.sliderrow input[type=range]{appearance:none;height:8px;border-radius:999px;background:linear-gradient(90deg,color-mix(in srgb,var(--blue) 80%,#fff),var(--brand),color-mix(in srgb,var(--amber) 78%,#fff));outline:none}.sliderrow input[type=range]::-webkit-slider-thumb{appearance:none;width:24px;height:24px;border-radius:50%;background:var(--card);border:4px solid var(--brand);box-shadow:0 2px 7px rgba(0,0,0,.16);cursor:grab}.sliderrow input[type=range]::-moz-range-thumb{width:18px;height:18px;border-radius:50%;background:var(--card);border:4px solid var(--brand);box-shadow:0 2px 7px rgba(0,0,0,.16);cursor:grab}.sliderrow input[type=range]:active::-webkit-slider-thumb{cursor:grabbing}.sliderrow .big{min-width:112px;text-align:right;font-size:27px;color:var(--brand-strong)}
.stats{gap:12px}.stat{border:1px solid transparent}.stat:nth-child(1){background:var(--green-soft);border-color:color-mix(in srgb,var(--green) 22%,var(--line))}.stat:nth-child(2){background:var(--blue-soft);border-color:color-mix(in srgb,var(--blue) 22%,var(--line))}.stat:nth-child(3){background:var(--violet-soft);border-color:color-mix(in srgb,var(--violet) 22%,var(--line))}.stat b{font-size:20px}
.split{gap:14px}.splitbox{border-radius:14px;background:linear-gradient(180deg,color-mix(in srgb,var(--green-soft) 50%,var(--card)),var(--card) 34%)}.splitbox:nth-child(2){background:linear-gradient(180deg,color-mix(in srgb,var(--blue-soft) 50%,var(--card)),var(--card) 34%)}.pill{background:var(--brand-soft);color:var(--brand-strong);border:1px solid color-mix(in srgb,var(--brand) 18%,var(--line))}
.resultbox{border-left:4px solid var(--brand);background:linear-gradient(120deg,var(--brand-soft),var(--card) 58%)}
.btn{transition:border-color .12s ease,background .12s ease,transform .12s ease}.btn:hover{transform:translateY(-1px)}.btn.primary{background:var(--brand);border-color:var(--brand)}
#growthSection{background:linear-gradient(180deg,color-mix(in srgb,var(--violet-soft) 32%,var(--card)),var(--card) 30%)}#growthSection canvas{border-radius:12px}
.chartLegend{padding-top:6px}.chartLegend span{font-weight:700}
.simpleMilestones{overflow:hidden;border:1px solid var(--line);border-radius:13px}.simpleMilestones table{margin:0}.simpleMilestones th{background:color-mix(in srgb,var(--brand-soft) 60%,var(--card));font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.03em}.simpleMilestones td,.simpleMilestones th{padding:12px}.simpleMilestones tbody tr:hover td{background:color-mix(in srgb,var(--brand-soft) 28%,transparent)}.simpleMilestones .expectedCol{background:var(--green-soft)!important}.scenarioValue{font-size:15px}.technicalDetails summary{padding:7px 0}
#historySection{background:linear-gradient(180deg,color-mix(in srgb,var(--blue-soft) 24%,var(--card)),var(--card) 34%)}
.term::after{background:var(--card)}
@media(prefers-color-scheme:dark){
  :root{--brand:#64d6bd;--brand-strong:#8ee8d3;--brand-soft:#1f3c37;--blue:#79aaff;--blue-soft:#1d2e46;--green:#66d1a8;--green-soft:#1d3930;--amber:#e2ad5e;--amber-soft:#40321f;--violet:#b09aee;--violet-soft:#302a48;--coral:#e29389;--coral-soft:#472b2a}
  body{background:var(--bg)}.hero{box-shadow:none}.builderbox:hover{box-shadow:none}.siteNav a.active{color:#10211d}.goalMode.active::after{color:#10211d}.builderbox .btn.primary{color:#10211d}.sliderrow input[type=range]::-webkit-slider-thumb,.sliderrow input[type=range]::-moz-range-thumb{background:var(--card)}
}
@media(max-width:760px){
  main{padding-left:12px;padding-right:12px}.hero{padding:18px;border-radius:17px}.hero::after{display:none}.siteNav{width:100%;display:grid;grid-template-columns:repeat(3,1fr);gap:3px}.siteNav a{text-align:center;padding:9px 6px;font-size:12px}.beginner{padding:12px}.builderbox{min-height:0}.sectiontitle{gap:8px}.sectiontitle>span.muted{font-size:12px}.sliderrow{align-items:center}.sliderrow .big{min-width:92px;font-size:22px}.simpleMilestones{border:0}.simpleMilestones tr{background:var(--card)}
}
@media(prefers-reduced-motion:reduce){.beginneritem,.builderbox,.goalMode,.field input,.btn{transition:none!important}.beginneritem:hover,.builderbox:hover,.goalMode:hover,.btn:hover{transform:none!important}}
'''

s = s.replace('</style>', css + '\n</style>', 1)

p.write_text(s, encoding='utf-8')
print('Applied beginner-friendly UI polish without adding runtime work')

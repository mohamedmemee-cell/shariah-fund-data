#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'docs' / 'index.html'
s = p.read_text(encoding='utf-8')

if 'performance-v3-ultra-responsive' in s:
    print('Performance V3 already present; no changes needed.')
    raise SystemExit(0)

# Cache the main currency formatter instead of constructing Intl.NumberFormat on every render.
old_money = "const $=id=>document.getElementById(id),money=n=>new Intl.NumberFormat('en-ZA',{style:'currency',currency:'ZAR',maximumFractionDigits:0}).format(n||0),pct=n=>n==null?'—':Number(n).toFixed(2)+'%';"
new_money = "const moneyFormatter=new Intl.NumberFormat('en-ZA',{style:'currency',currency:'ZAR',maximumFractionDigits:0});const $=id=>document.getElementById(id),money=n=>moneyFormatter.format(n||0),pct=n=>n==null?'—':Number(n).toFixed(2)+'%';"
if old_money in s:
    s = s.replace(old_money, new_money, 1)

# Let the browser defer layout/paint work for below-the-fold full-width cards.
perf_css = r'''
/* performance-v3-ultra-responsive */
.card.full{content-visibility:auto;contain-intrinsic-size:1px 520px}
#portfolioBuilderSection,.inputs,#monthlyPlanSection{content-visibility:visible;contain-intrinsic-size:auto}
@media(max-width:760px){.card.full{contain-intrinsic-size:1px 680px}}
'''
s = s.replace('</style>', perf_css + '\n</style>', 1)

# The existing calculator intentionally performs full recalculation on input events.
# That is appropriate for text/number inputs, but too expensive for a continuously-dragged
# range control. Replace only the years slider node at runtime, which cleanly removes all
# legacy high-frequency listeners, then use a two-phase interaction:
#   input  -> immediate label + lightweight target cards + lightweight chart
#   change -> one full calculator recalc when the user releases/commits the slider
# This preserves correctness while making dragging frame-rate friendly.
perf_js = r'''
<script>
/* performance-v3-ultra-responsive */
(function(){
  const $p=id=>document.getElementById(id);
  const moneyFast=new Intl.NumberFormat('en-ZA',{style:'currency',currency:'ZAR',maximumFractionDigits:0});
  const compactFast=new Intl.NumberFormat('en-ZA',{notation:'compact',maximumFractionDigits:1});
  const activeTargetMode=()=>document.querySelector('.goalMode.active')?.dataset.mode==='target';

  function projectionSeries(start,annualIncrease,years,annualReturn){
    const out=[0];
    let balance=0;
    const mr=Math.pow(1+annualReturn/100,1/12)-1;
    const growth=1+annualIncrease/100;
    let monthly=start;
    for(let y=0;y<years;y++){
      for(let m=0;m<12;m++) balance=balance*(1+mr)+monthly;
      out.push(balance);
      monthly*=growth;
    }
    return out;
  }

  function requiredStart(target,annualIncrease,years,annualReturn){
    const unit=projectionSeries(1,annualIncrease,years,annualReturn)[years]||0;
    return unit>0?target/unit:0;
  }

  function getTargetAmounts(years){
    const target=Math.max(0,+$p('targetValue')?.value||0);
    const inc=Math.max(0,+$p('targetIncrease')?.value||0);
    const rates=[+$p('r1')?.value||0,+$p('r2')?.value||0,+$p('r3')?.value||0];
    return {inc,values:rates.map(r=>requiredStart(target,inc,years,r))};
  }

  function updateTargetCards(years){
    if(!activeTargetMode()) return null;
    const data=getTargetAmounts(years);
    const ids=['requiredCautious','requiredExpected','requiredOptimistic'];
    ids.forEach((id,i)=>{const el=$p(id);if(el)el.textContent=moneyFast.format(data.values[i]||0)});
    return data;
  }

  let chartVisible=false,chartDirty=true,chartFrame=0;
  function findGrowthSection(){return [...document.querySelectorAll('section')].find(sec=>(sec.querySelector('h2')?.textContent||'').trim()==='Portfolio growth')}
  const growthSec=findGrowthSection();
  const growthCanvas=growthSec?.querySelector('canvas')||null;

  function drawFastGrowth(years,startOverride=null,incOverride=null){
    if(!growthCanvas||!growthSec){return}
    if(!chartVisible){chartDirty=true;return}
    chartDirty=false;
    const start=Math.max(0,startOverride==null?(+$p('monthly')?.value||0):startOverride);
    const inc=incOverride==null?(+$p('increase')?.value||0):incOverride;
    const rates=[+$p('r1')?.value||0,+$p('r2')?.value||0,+$p('r3')?.value||0];
    const series=rates.map(r=>projectionSeries(start,inc,years,r));
    const max=Math.max(1,...series[0],...series[1],...series[2]);
    const dpr=Math.min(window.devicePixelRatio||1,2);
    const w=Math.max(280,Math.round(growthCanvas.clientWidth||growthSec.clientWidth-36));
    const h=330;
    const pxW=Math.round(w*dpr),pxH=Math.round(h*dpr);
    if(growthCanvas.width!==pxW)growthCanvas.width=pxW;
    if(growthCanvas.height!==pxH)growthCanvas.height=pxH;
    growthCanvas.style.height=h+'px';
    const ctx=growthCanvas.getContext('2d');
    if(!ctx)return;
    ctx.setTransform(dpr,0,0,dpr,0,0);
    ctx.clearRect(0,0,w,h);
    const pad={l:64,r:20,t:24,b:38},plotW=w-pad.l-pad.r,plotH=h-pad.t-pad.b;
    const style=getComputedStyle(document.documentElement);
    const grid=style.getPropertyValue('--line').trim()||'#334044';
    const text=style.getPropertyValue('--muted').trim()||'#9eacab';
    const cols=['#7ca7ff','#65d0b4','#d5a35d'];
    ctx.font='12px system-ui';ctx.strokeStyle=grid;ctx.fillStyle=text;ctx.lineWidth=1;
    for(let i=0;i<=4;i++){
      const y=pad.t+plotH*i/4;
      ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(w-pad.r,y);ctx.stroke();
      ctx.fillText('R '+compactFast.format(max*(1-i/4)),4,y+4);
    }
    for(let i=0;i<=4;i++){
      const yr=Math.round(years*i/4),x=pad.l+plotW*i/4;
      ctx.fillText(String(yr)+'y',x-8,h-12);
    }
    series.forEach((arr,si)=>{
      ctx.strokeStyle=cols[si];ctx.lineWidth=3;ctx.beginPath();
      for(let idx=0;idx<arr.length;idx++){
        const x=pad.l+plotW*(idx/years),y=pad.t+plotH*(1-arr[idx]/max);
        idx?ctx.lineTo(x,y):ctx.moveTo(x,y);
      }
      ctx.stroke();
    });
  }

  function requestFastGrowth(years,startOverride=null,incOverride=null){
    if(chartFrame)return;
    chartFrame=requestAnimationFrame(()=>{chartFrame=0;drawFastGrowth(years,startOverride,incOverride)});
  }

  if(growthSec&&'IntersectionObserver' in window){
    new IntersectionObserver(entries=>{
      chartVisible=!!entries[0]?.isIntersecting;
      if(chartVisible&&chartDirty){
        const years=Math.max(1,+$p('years')?.value||20);
        requestFastGrowth(years);
      }
    },{rootMargin:'250px 0px'}).observe(growthSec);
  }else chartVisible=true;

  const oldSlider=$p('years');
  if(oldSlider){
    const slider=oldSlider.cloneNode(true);
    oldSlider.replaceWith(slider);
    const label=$p('yearLabel');
    let pendingExpected=null,pendingInc=null;

    slider.addEventListener('input',()=>{
      const years=Math.max(1,+slider.value||1);
      if(label)label.textContent=slider.value;
      if(activeTargetMode()){
        const t=updateTargetCards(years);
        pendingExpected=t?.values?.[1]??null;
        pendingInc=t?.inc??null;
        requestFastGrowth(years,pendingExpected,pendingInc);
      }else{
        pendingExpected=null;pendingInc=null;
        requestFastGrowth(years);
      }
    },{passive:true});

    slider.addEventListener('change',()=>{
      const years=Math.max(1,+slider.value||1);
      if(activeTargetMode()){
        const t=getTargetAmounts(years);
        const monthly=$p('monthly'),increase=$p('increase');
        if(monthly)monthly.value=Math.round(t.values[1]||0);
        if(increase)increase.value=t.inc;
      }
      // One expensive recalculation per completed interaction, never per drag frame.
      if(typeof window.recalc==='function')window.recalc();
      else{
        const monthly=$p('monthly');
        if(monthly)monthly.dispatchEvent(new Event('input',{bubbles:true}));
      }
      requestFastGrowth(years);
    });
  }

  // Resize only the graph itself, not every window event. ResizeObserver is much cheaper
  // on responsive layouts and avoids redraw storms during browser resize/zoom.
  if(growthSec&&'ResizeObserver' in window){
    let resizeFrame=0;
    new ResizeObserver(()=>{
      if(resizeFrame)return;
      resizeFrame=requestAnimationFrame(()=>{
        resizeFrame=0;chartDirty=true;
        if(chartVisible)drawFastGrowth(Math.max(1,+$p('years')?.value||20));
      });
    }).observe(growthSec);
  }

  // Defer non-critical work until the browser is idle. This improves first interaction
  // latency on slower phones without changing visible calculator behaviour.
  const idle=window.requestIdleCallback||((fn)=>setTimeout(fn,120));
  idle(()=>{
    document.querySelectorAll('a[target="_blank"]').forEach(a=>{
      if(!a.rel)a.rel='noopener noreferrer';
    });
  });
})();
</script>
'''
s = s.replace('</body>', perf_js + '\n</body>', 1)

p.write_text(s, encoding='utf-8')
print('Applied Performance V3: frame-friendly slider, cached formatters, deferred rendering and lightweight charting')

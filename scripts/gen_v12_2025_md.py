"""Generate back test result/v1.2_2025_result.md from baskets2025.csv."""
import csv, os, datetime, collections, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
rows = list(csv.DictReader(open(os.path.join(HERE, 'baskets2025.csv'), encoding='utf-8')))
for r in rows:
    r['level'] = int(r['level'])
    r['net_pips'] = float(r['net_pips'])
    r['usd'] = float(r['usd'])
    r['lot_pips'] = float(r['lot_pips'])

def pt(s):
    return datetime.datetime.strptime(s, '%Y.%m.%d %H:%M:%S')

START, FINAL = 50000.00, 56567.29
lvl1 = [r for r in rows if r['level'] == 1]
ladder = [r for r in rows if r['level'] >= 2]
neg = [r for r in rows if r['net_pips'] < 0]
durs = {r['idx']: (pt(r['close_dt']) - pt(r['open_dt'])).total_seconds() / 3600 for r in rows}
lvl_dist = collections.Counter(r['level'] for r in ladder)
dirc = collections.Counter(r['dir'] for r in rows)
mon = collections.Counter(r['open_dt'][:7] for r in rows)

L = []
w = L.append
w("# AUDCAD M15 v1.2 — 2025 Backtest Result")
w("")
w("Source log: [back test result/v1.2_2025_result.log](v1.2_2025_result.log) · "
  "EA: [EA/AUDCAD_M15_v1_2.mq5](../EA/AUDCAD_M15_v1_2.mq5)")
w("")
w("> The log file actually contains **two** tester passes: a 2026.01.01–2026.05.12 pass "
  "(final balance 57,179.93) and the **2025.01.01–2025.12.31 full-year pass** "
  "(final balance 56,567.29). This report covers the **2025 full-year pass** only.")
w("")
w("## 1. Summary")
w("")
w("| Item | Value |")
w("|---|---|")
w("| Symbol / TF | AUDCAD, M15 |")
w("| Period | 2025.01.02 → 2025.12.31 |")
w("| Initial deposit | $50,000.00 |")
w("| Final balance | $56,567.29 |")
w(f"| Net profit | **+$6,567.29 (+13.13%)** |")
w("| Inputs | BasketTPPips=10, GridStepPips=22, MaxLegs=10, ProbeLot=0.01, EnableGate=true (D1 EMA20), ShadowMode=false |")
w(f"| 1st entries (probes) opened | 355 (+1 still open at end of test, force-closed by tester) |")
w(f"| Baskets closed by the strategy | 354 |")
w(f"| Total legs (orders) opened | 617 |")
w(f"| Close reason | **354 / 354 = `tp_10.0_pips`** — every basket hit the +10-pip target |")
w(f"| Stop-loss / emergency-DD / blocked-add exits | **0** |")
w(f"| Direction split | {dirc['LONG']} LONG / {dirc['SHORT']} SHORT |")
w(f"| Baskets that laddered (level ≥ 2) | {len(ladder)} ({len(ladder)/len(rows)*100:.1f}%) |")
w(f"| Baskets closed at level 1 (no ladder) | {len(lvl1)} ({len(lvl1)/len(rows)*100:.1f}%) |")
w(f"| Deepest ladder reached | level 8 (1 basket) — MaxLegs=10 never hit |")
w(f"| Basket hold time | min {min(durs.values()):.1f}h · median {sorted(durs.values())[len(durs)//2]:.1f}h · max {max(durs.values()):.1f}h |")
w(f"| Closed below water despite `tp` trigger | {len(neg)} baskets (see Insights) |")
w("")
w("**Profit attribution**")
w("")
w("| Group | Baskets | Net result | Share of profit |")
w("|---|--:|--:|--:|")
w(f"| Level-1 only (0.01 lot) | {len(lvl1)} | +${sum(r['usd'] for r in lvl1):,.2f} | {sum(r['usd'] for r in lvl1)/6567.29*100:.1f}% |")
w(f"| Laddered (level ≥ 2) | {len(ladder)} | +${sum(r['usd'] for r in ladder):,.2f} | {sum(r['usd'] for r in ladder)/6567.29*100:.1f}% |")
w(f"| Open-at-EOT (force-closed) | 1 | -$1.04 | — |")
w("")
w("**Monthly 1st-entry count:** " +
  " · ".join(f"{k[5:]}={v}" for k, v in sorted(mon.items())))
w("")
w("> **Note on the `≈ USD` column.** The EA log records pips, not per-basket USD. "
  "The USD figures below are *derived*: `lot-pips × $6.7743`, where the factor is "
  "calibrated so the sum matches the actual +$6,567.29 balance change (it therefore "
  "absorbs swap and spread). `net_pips` is the EA's own logged figure and is authoritative.")
w("")

# ---------- SECTION 1 ----------
w("## 2. Section 1 — Every 1st Entry: Laddered vs Closed at Level 1")
w("")
w(f"Of the 354 baskets the strategy opened *and closed*: **{len(lvl1)} reached the "
  f"+10-pip target on the probe alone (no ladder)** and **{len(ladder)} required at "
  f"least one grid add (laddered to level 2+)**.")
w("")
w("- `Outcome` = `L1 only` means the probe hit TP before price moved 22 pips adverse.")
w("- `Outcome` = `laddered → Lx` means the basket added grid legs and finally closed at level x.")
w("- `net_pips` is the weighted-average realised pips at close; `≈ USD` is derived (see note above).")
w("")
w("| # | Open (probe) | Dir | Outcome | Final level | net_pips | ≈ USD |")
w("|--:|---|:--:|---|:--:|--:|--:|")
for r in rows:
    if r['level'] == 1:
        outcome = "L1 only — TP, no ladder"
    else:
        outcome = f"laddered → L{r['level']}"
    w(f"| {r['idx']} | {r['open_dt'][:16]} | {r['dir']} | {outcome} | "
      f"L{r['level']} | {r['net_pips']:+.1f} | {r['usd']:+,.2f} |")
w("")
w(f"*(1 further probe — #355 LONG, opened 2025.12.30 09:45 — was still open when the "
  f"test ended and was force-liquidated by the tester at a ~$1 loss; it is excluded "
  f"from the table above.)*")
w("")

# ---------- SECTION 2 ----------
w("## 3. Section 2 — Laddered Baskets (Level 2+): Depth and Close Level")
w("")
w("In v1.2 a basket only ever **grows** (probe → grid adds) and is then **closed in "
  "full** at once. So *levels created* and *level it was closed at* are the same number "
  "— there is no partial de-laddering. **All 152 laddered baskets closed via the "
  "`tp_10.0_pips` target; none closed on a stop-loss or DD exit.**")
w("")
w("### 3a. Ladder-depth distribution")
w("")
w("| Levels created (= close level) | Baskets | Total lots at close | Avg net_pips | Net result |")
w("|:--:|--:|--:|--:|--:|")
lotmap = {2: 0.25, 3: 0.61, 4: 1.09, 5: 1.69, 6: 2.41, 7: 3.25, 8: 4.21}
for lv in sorted(lvl_dist):
    grp = [r for r in ladder if r['level'] == lv]
    w(f"| L{lv} | {len(grp)} | {lotmap[lv]:.2f} | "
      f"{statistics.mean(r['net_pips'] for r in grp):+.1f} | "
      f"+${sum(r['usd'] for r in grp):,.2f} |")
w(f"| **Total** | **{len(ladder)}** | — | — | **+${sum(r['usd'] for r in ladder):,.2f}** |")
w("")
w("### 3b. Every laddered basket")
w("")
w("| # | Open | Close | Dir | Levels created | Closed at level | Close type | wavg | Close px | Total lots | net_pips | ≈ USD |")
w("|--:|---|---|:--:|:--:|:--:|:--:|--:|--:|--:|--:|--:|")
for r in ladder:
    w(f"| {r['idx']} | {r['open_dt'][:16]} | {r['close_dt'][:16]} | {r['dir']} | "
      f"{r['level']} | L{r['level']} | TP | {r['wavg']} | {r['close_p']} | "
      f"{r['total_lots']} | {r['net_pips']:+.1f} | {r['usd']:+,.2f} |")
w("")

# ---------- INSIGHTS ----------
mondays = [r for r in neg if pt(r['close_dt']).weekday() == 0]
w("## 4. Strategy Insights")
w("")
w("**1. The edge is the ladder, not the signal.** Level-1 probes (0.01 lot) won "
  f"{sum(1 for r in lvl1 if r['lot_pips']>0)}/{len(lvl1)} of the time but produced only "
  f"+${sum(r['usd'] for r in lvl1):,.2f} all year — the 0.01 lot is too small to matter. "
  f"**{sum(r['usd'] for r in ladder)/6567.29*100:.0f}% of the year's profit came from the "
  f"{len(ladder)} baskets that laddered.** The strategy is, in effect, a martingale grid: "
  "the signal just picks a direction; the money is made when price runs adverse, the EA "
  "piles in 24×/36×/48×… lots, and the whole basket mean-reverts +10 pips on a now-large "
  "weighted size.")
w("")
w("**2. 100% basket win rate — but that is the martingale signature, not proof of safety.** "
  "Every one of the 354 closed baskets hit its +10-pip target; nothing was stopped out and "
  "the 20% DD cap never fired. That is exactly what a grid-recovery system looks like *while "
  "the market keeps mean-reverting*. The risk is not in the win rate — it is in the one "
  "basket that does not come back.")
w("")
w(f"**3. Tail risk is real and was approached.** The deepest basket reached **level 8 "
  f"(4.21 lots on a $50k account)** before recovering (#215, +$516.92). A level-10 basket "
  f"would carry **6.49 lots** (~$45/pip). The ladder works until it doesn't — 2025 simply "
  f"never produced a move deep and sustained enough to run a basket to MaxLegs or trip the "
  f"DD cap. One trending year against the basket direction is the scenario this backtest "
  f"does not contain.")
w("")
w(f"**4. The `tp` exit can still close underwater — a genuine bug surface.** "
  f"**{len(neg)} baskets** closed with *negative* net_pips even though the close reason was "
  f"`tp_10.0_pips`. `CheckCloseTarget()` decides on the **last closed M15 bar** "
  f"(`iClose(...,1)`), but `CloseBasket()` executes at the **current bid/ask**. When there "
  f"is a gap between the trigger bar and execution — notably weekend gaps "
  f"({len(mondays)} of the {len(neg)} bad closes executed on a Monday) — the realised price "
  f"can be well past the target. Worst case: **#117, a level-3 short, logged "
  f"`tp_10.0_pips` but realised −16.5 pips (≈ −$68)**. Worth fixing: re-check the live "
  f"price inside `CheckCloseTarget` before committing the close, or skip the very first "
  f"M15 bar after a session gap.")
w("")
w("**5. The D1 EMA20 gate is doing heavy filtering.** `GATE_BLOCK` fired ~3,535 times "
  "against only 355 probes opened — the HTF gate vetoed roughly 10 signals for every one "
  "it let through. Combined with the v1.2 single-basket rule, the EA is in the market far "
  "less than the raw signal would suggest. That is good for tail risk but means the result "
  "leans heavily on the gate's direction call being right.")
w("")
w(f"**6. Direction-balanced, but longs carried the year.** {dirc['LONG']} long / "
  f"{dirc['SHORT']} short baskets — well balanced — yet longs returned "
  f"+${sum(r['usd'] for r in rows if r['dir']=='LONG'):,.2f} vs shorts "
  f"+${sum(r['usd'] for r in rows if r['dir']=='SHORT'):,.2f}. AUDCAD spent much of 2025 "
  f"grinding higher, so long ladders recovered faster and shallower while short ladders had "
  f"to fight the drift. A genuinely trending year is when this asymmetry would turn negative.")
w("")
w("**7. Open-ended baskets tie up the account.** Median hold was 7h but the longest "
  "laddered baskets ran **9–12 days** (e.g. #345 ran 2025.11.25 → 12.05). Because v1.2 is "
  "single-basket-at-a-time, a deep basket that sits underwater for over a week blocks every "
  "other signal in that window — visible in the monthly counts (December opened only 9 "
  "probes, partly because late-year baskets ran long).")
w("")
w("### Bottom line")
w("")
w("v1.2 returned **+13.1% in 2025 with a 100% basket win rate and zero stop-outs** — a "
  "clean result, but a *characteristically martingale* one. The backtest confirms the "
  "mechanics work in a mean-reverting / mildly-trending year; it does **not** test the "
  "failure mode (a sustained trend against basket direction running the ladder to level 10 "
  "/ the DD cap). Before any live deployment: (a) fix the gap-driven `tp`-but-negative "
  "close, (b) stress-test against a deliberately adverse trending period, and (c) confirm "
  "the level-8→10 lot sizes are survivable on the intended account size.")
w("")

out = os.path.join(ROOT, 'back test result', 'v1.2_2025_result.md')
open(out, 'w', encoding='utf-8').write("\n".join(L))
print("wrote", out, "—", len(L), "lines")

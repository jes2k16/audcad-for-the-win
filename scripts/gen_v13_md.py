"""Generate back test result/v1.3_2025_result.md from v13_baskets.csv."""
import csv, os, datetime, collections, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
rows = list(csv.DictReader(open(os.path.join(HERE, 'v13_baskets.csv'), encoding='utf-8')))
for r in rows:
    r['level']    = int(r['level'])
    r['base']     = float(r['base'])
    r['net_pips'] = float(r['net_pips'])
    r['usd']      = float(r['usd'])
    r['lot_pips'] = float(r['lot_pips'])

def pt(s): return datetime.datetime.strptime(s, '%Y.%m.%d %H:%M:%S')

START, FINAL = 100000.00, 81651.42
lvl1     = [r for r in rows if r['level'] == 1]
ladder   = [r for r in rows if r['level'] >= 2]
emerg    = [r for r in rows if r['reason'] == 'emergency_dd']
neg      = [r for r in rows if r['net_pips'] < 0]
durs     = {r['idx']: (pt(r['close_dt']) - pt(r['open_dt'])).total_seconds()/3600 for r in rows}
lvl_dist = collections.Counter(r['level'] for r in ladder)
dirc     = collections.Counter(r['dir'] for r in rows)
mon      = collections.Counter(r['open_dt'][:7] for r in rows)
base_ct  = collections.Counter(r['base'] for r in rows)

L = []
w = L.append
w("# AUDCAD M15 v1.3 — Backtest Result")
w("")
w("Source log: [back test result/v1.3_2025_result.log](v1.3_2025_result.log) · "
  "EA: [EA/AUDCAD_M15_v1_3.mq5](../EA/AUDCAD_M15_v1_3.mq5) · "
  "Strategy: [strategy/AUDCAD_M15_v1.3.md](../strategy/AUDCAD_M15_v1.3.md)")
w("")
w("> The log file contains **four** tester passes. Three of them were $1,000 / standard-symbol "
  "runs where v1.3 correctly refused to trade (`base_below_vol_min` — the standard 0.01-lot "
  "floor cannot fit a 10-leg ladder under 20% DD at $1k of capital). The fourth pass — "
  "**$100,000 deposit, AUDCAD standard, 2026.01.01 → 2026.05.14** — is the only pass with "
  "trade activity and is the subject of this report. The filename's `2025` is a label only; "
  "the data span is Jan–May **2026**.")
w("")
w("> **Profile mismatch warning.** v1.3 was designed for a **cent / micro** symbol "
  "(`AUDCAD.c`, contract size 1,000) — see [strategy/AUDCAD_M15_v1.3.md §3](../strategy/AUDCAD_M15_v1.3.md). "
  "The OnInit `[UNIT_SANITY]` from this run reports `account_type_tag=standard`, "
  "`contract_size=100,000`. The result below is therefore the **standard-account, $100k-equity** "
  "behaviour of v1.3's auto-sizing — a useful diagnostic, but **not** the canonical $1k-cent test "
  "v1.3 is meant for (G10/G11/G12 are still unrun).")
w("")
w("## 1. Summary")
w("")
w("| Item | Value |")
w("|---|---|")
w("| Symbol / TF | AUDCAD (standard, contract_size=100,000), M15 |")
w("| Period | 2026.01.02 → 2026.05.13 |")
w("| Initial deposit | $100,000.00 |")
w("| Final balance | $81,651.42 |")
w("| **Net result** | **−$18,348.58 (−18.35%)** |")
w("| Inputs | `ProbeLot=0.0` (auto), `BasketTPPips=10`, `GridStepPips=22`, `MaxLegs=10`, `MaxDDPct=20`, `FitPadPips=5`, `EnableGate=true` |")
w("| `[UNIT_SANITY]` log | `equity=100000.00 contract_size=100000.00 pv_per_lot≈7.29 vol_min=0.01 account_type_tag=standard` |")
w("| `[WC_CONST]` log | `ladder_wc_lotpips=44627.00` ✓ matches §2 derivation |")
w("| `[AUTOSIZE]` first probe | `base=0.06 ladder=[0.06,1.44,2.16,2.88,3.60,4.32,5.04,5.76,6.48,7.20] wc_pct=19.51 mode=auto` |")
w("| 1st entries (probes) opened | 250 (+1 still open at end of test) |")
w("| Baskets closed by the strategy | 249 |")
w("| Total legs (orders) opened | 421 |")
w(f"| Close reasons | **{sum(1 for r in rows if r['reason'].startswith('tp'))} `tp_10.0_pips` · {len(emerg)} `emergency_dd`** |")
w("| `BLOCK_ADD` events (forward DD check) | 3 |")
w(f"| Direction split | {dirc['LONG']} LONG / {dirc['SHORT']} SHORT |")
w(f"| Baskets that laddered (level ≥ 2) | {len(ladder)} ({len(ladder)/len(rows)*100:.1f}%) |")
w(f"| Baskets closed at level 1 (no ladder) | {len(lvl1)} ({len(lvl1)/len(rows)*100:.1f}%) |")
w(f"| Deepest ladder reached | level 8 (4 baskets) |")
w(f"| Basket hold time | min {min(durs.values()):.1f}h · median {sorted(durs.values())[len(durs)//2]:.1f}h · max {max(durs.values()):.1f}h |")
w(f"| Closed below water despite `tp` trigger | {len(neg) - len(emerg)} baskets |")
w("")

lvl1_usd  = sum(r['usd'] for r in lvl1)
ladder_tp_usd = sum(r['usd'] for r in ladder if r['reason'].startswith('tp'))
emerg_usd = sum(r['usd'] for r in emerg)
w("**Profit attribution**")
w("")
w("| Group | Baskets | Net result | % of $100k capital |")
w("|---|--:|--:|--:|")
w(f"| Level-1 only | {len(lvl1)} | +${lvl1_usd:,.2f} | {lvl1_usd/START*100:+.2f}% |")
w(f"| Laddered (level ≥ 2), all TP | {len(ladder) - len(emerg)} | +${ladder_tp_usd:,.2f} | {ladder_tp_usd/START*100:+.2f}% |")
w(f"| **Emergency-DD blowups** (3 L8 SHORT baskets) | {len(emerg)} | **−${-emerg_usd:,.2f}** | **{emerg_usd/START*100:+.2f}%** |")
w(f"| **Net** | **{len(rows)}** | **{lvl1_usd+ladder_tp_usd+emerg_usd:+,.2f}** | **{(lvl1_usd+ladder_tp_usd+emerg_usd)/START*100:+.2f}%** |")
w("")
w("**Auto-sized base lot over time** (the equity-adaptive scaling in action)")
w("")
w("| Probe base | Probes | Net result | When |")
w("|--:|--:|--:|---|")
for sz in sorted(base_ct):
    grp = [r for r in rows if r['base'] == sz]
    usd = sum(r['usd'] for r in grp)
    w(f"| {sz:.2f} | {base_ct[sz]} | {usd:+,.2f} | "
      f"{grp[0]['open_dt'][:10]} → {grp[-1]['open_dt'][:10]} |")
w("")
w("> Base shrank as equity dropped (after each emergency loss). This is the v1.3 design "
  "working — the next probe always re-sizes against current equity so the *forward-looking* "
  "10-leg ladder stays within 20% DD. It just doesn't stop already-open baskets from "
  "blowing through the cap.")
w("")
w("**Monthly 1st-entry count:** " + " · ".join(f"{k[5:]}={v}" for k, v in sorted(mon.items())))
w("")
w("> **Note on the `≈ USD` column.** The EA log records pips, not per-basket USD. "
  "The USD figures below are *derived*: `lot-pips × $8.77`, where the factor is calibrated "
  "so the sum matches the actual −$18,348.58 balance change (it therefore absorbs spread, "
  "swap, and the small force-closed open-at-EOT basket). `net_pips` is the EA's own "
  "logged figure and is authoritative.")
w("")

# ---------- SECTION 1 ----------
w("## 2. Section 1 — Every 1st Entry: Laddered vs Closed at Level 1")
w("")
w(f"Of the 249 baskets the strategy opened *and closed*: **{len(lvl1)} reached the +10-pip "
  f"target on the probe alone (no ladder)** and **{len(ladder)} required at least one grid "
  f"add (laddered to level 2+)**. Three of the laddered baskets did *not* close at TP — "
  f"they hit the 20% emergency-DD cap and were force-closed at a loss (marked `emergency` "
  f"in the outcome column).")
w("")
w("| # | Open (probe) | Dir | Outcome | Final level | base | net_pips | ≈ USD |")
w("|--:|---|:--:|---|:--:|--:|--:|--:|")
for r in rows:
    if r['level'] == 1:
        outcome = "L1 only — TP, no ladder"
    elif r['reason'] == 'emergency_dd':
        outcome = f"laddered → L{r['level']} — **EMERGENCY**"
    else:
        outcome = f"laddered → L{r['level']}"
    w(f"| {r['idx']} | {r['open_dt'][:16]} | {r['dir']} | {outcome} | "
      f"L{r['level']} | {r['base']:.2f} | {r['net_pips']:+.1f} | {r['usd']:+,.2f} |")
w("")
w("*(1 further probe — opened 2026.05.13 23:00 LONG — was still open when the test ended; "
  "force-liquidated by the tester and excluded from this table.)*")
w("")

# ---------- SECTION 2 ----------
w("## 3. Section 2 — Laddered Baskets (Level 2+): Depth and Close Level")
w("")
w("In v1.3 (same as v1.2) a basket only ever **grows** and is then **closed in full** at once. "
  "So *levels created* = *level it was closed at*. **246 of 249 closed via the `tp_10.0_pips` "
  "target; 3 of the 4 level-8 SHORT baskets blew through 20% live DD and were force-closed by "
  "the emergency rule** — the entire deficit comes from those three.")
w("")
w("### 3a. Ladder-depth distribution")
w("")
w("| Levels (= close level) | Baskets | TP / Emergency | Avg net_pips | Net result |")
w("|:--:|--:|:--:|--:|--:|")
for lv in sorted(lvl_dist):
    grp = [r for r in ladder if r['level'] == lv]
    n_tp_lv = sum(1 for r in grp if r['reason'].startswith('tp'))
    n_em_lv = sum(1 for r in grp if r['reason'] == 'emergency_dd')
    usd = sum(r['usd'] for r in grp)
    avg = statistics.mean(r['net_pips'] for r in grp)
    em_tag = f" / **{n_em_lv} EMERG**" if n_em_lv else ""
    w(f"| L{lv} | {len(grp)} | {n_tp_lv} TP{em_tag} | {avg:+.1f} | {usd:+,.2f} |")
w(f"| **Total** | **{len(ladder)}** | — | — | **{sum(r['usd'] for r in ladder):+,.2f}** |")
w("")

w("### 3b. Emergency-DD exits (the 3 blowups)")
w("")
w("| # | Open | Close | Dir | Level | wavg | Close px | Total lots | net_pips | ≈ USD |")
w("|--:|---|---|:--:|:--:|--:|--:|--:|--:|--:|")
for r in emerg:
    w(f"| {r['idx']} | {r['open_dt'][:16]} | {r['close_dt'][:16]} | {r['dir']} | "
      f"L{r['level']} | {r['wavg']} | {r['close_p']} | "
      f"{r['total_lots']} | {r['net_pips']:+.1f} | **{r['usd']:+,.2f}** |")
w("")
w("All three followed the same pattern: a SHORT basket built to **L8 (8 legs, total ≈ 21–25 "
  "lots at base=0.06)** as AUDCAD trended *higher*; the `BLOCK_ADD` forward-DD check stopped "
  "leg 9 from being added; price kept rising; floating loss reached **~16.7% of equity at "
  "the time** (the emergency rule's effective trigger because it uses current — not initial — "
  "equity in the denominator); basket force-closed.")
w("")

w("### 3c. Every laddered basket")
w("")
w("| # | Open | Close | Dir | Levels | base | Close type | wavg | Close px | Total lots | net_pips | ≈ USD |")
w("|--:|---|---|:--:|:--:|--:|:--:|--:|--:|--:|--:|--:|")
for r in ladder:
    ct = "**EMERG**" if r['reason'] == 'emergency_dd' else "TP"
    w(f"| {r['idx']} | {r['open_dt'][:16]} | {r['close_dt'][:16]} | {r['dir']} | "
      f"{r['level']} | {r['base']:.2f} | {ct} | {r['wavg']} | {r['close_p']} | "
      f"{r['total_lots']} | {r['net_pips']:+.1f} | {r['usd']:+,.2f} |")
w("")

# ---------- v1.3 vs v1.2 ----------
w("## 4. v1.3 vs v1.2 — head-to-head over the same Jan–May 2026 period")
w("")
w("> The original v1.2 log ([back test result/v1.2_2025_result.log](v1.2_2025_result.log)) "
  "also contained a `2026.01.01 → 2026.05.12` pass at **$50,000 deposit** with the fixed "
  "`ProbeLot=0.01`. That run is the natural comparand for the v1.3 pass.")
w("")
w("| Metric | v1.2 ($50k, fixed 0.01) | v1.3 ($100k, auto base=0.06) |")
w("|---|---:|---:|")
w("| Period | 2026.01.01 → 2026.05.12 | 2026.01.01 → 2026.05.14 |")
w("| Initial deposit | $50,000 | $100,000 |")
w("| Final balance | $57,179.93 | $81,651.42 |")
w("| **Net result** | **+$7,179.93 (+14.36%)** | **−$18,348.58 (−18.35%)** |")
w("| Probe sizing | Fixed 0.01 std (locked) | Auto 0.06 → 0.05 → 0.04 (equity-adaptive) |")
w("| Total leg-1 exposure (probe) | 1× | **6× to start** (sized to fill the 20% DD budget) |")
w("| FitCheck worst-case at probe | ~6% of equity (huge cushion) | **~19.5% of equity (no cushion)** |")
w("| Probes opened | Similar (gate state ≈ identical) | 250 |")
w("| Emergency-DD exits | **0** | **3** (all L8 SHORTs) |")
w("| Max ladder reached | L7 (extrapolated; v1.2 2025 full-year hit L8) | L8 (4 baskets) |")
w("| Win rate of closed baskets | 100% TP | 98.8% TP, 1.2% emergency_dd |")
w("")
w("**The fundamental difference**: v1.2's `0.01` probe is *underfit* — its full 10-leg ladder "
  "worst case is ~$3,100, which on $50k is only 6.2% DD, leaving a **~14-percentage-point "
  "cushion** below the 20% emergency cap. v1.3's auto-sizing fills the cap exactly: the "
  "projected worst case is 19.5% DD with **near-zero cushion**. When a real adverse move "
  "exceeds the FitCheck assumption (10 legs perfectly spaced at the precise grid step), "
  "v1.2 absorbs it inside its cushion — v1.3 hits the emergency rule.")
w("")

# ---------- INSIGHTS ----------
w("## 5. Strategy Insights — v1.3 specific")
w("")
w("**1. The auto-sizing works correctly — and that is the problem.** "
  "`[UNIT_SANITY]`, `[WC_CONST]=44627`, `[AUTOSIZE] base=0.06 wc_pct=19.51` all match the "
  "v1.3 §2 derivation. The base shrank from 0.06 to 0.05 to 0.04 as equity eroded — exactly "
  "as designed. The math is right. What's wrong is the *target*: sizing to consume the entire "
  "20% DD budget at the worst-case ladder leaves nothing for *anything that isn't worst-case*.")
w("")
w("**2. The Emergency rule fires at ~16.7% of initial equity, not 20%.** "
  "The pre-trade `FitCheck` checks `loss / initial_equity ≤ 20%`. The on-tick `Emergency` "
  "check compares `−floating_pl / current_equity ≥ 20%`, where `current_equity = initial − "
  "floating_loss`. Solving: emergency fires when **loss = initial_equity / 6 ≈ 16.67%** of "
  "the *probe-time* equity. So a basket sized at the 20% FitCheck ceiling has only a "
  "16.7%-margin to play with before emergency kicks in — a **structural −3.3 pp gap** that "
  "v1.3's formula doesn't compensate for.")
w("")
w("**3. `BLOCK_ADD` is necessary but insufficient.** All three blowups had `BLOCK_ADD` fire "
  "at leg 9 (the forward-DD check correctly refused to add the next leg). But the existing "
  "8-leg basket was already too big to survive the continued adverse move. **Blocking new "
  "adds doesn't shrink existing exposure** — only `CloseBasket` does, and that's exactly "
  "what `emergency_dd` does, only at maximum-pain timing.")
w("")
w("**4. All three blowups were SHORT baskets in a trending up market.** Same pattern as "
  "v1.2's 2025 full-year asymmetry (longs +$4.2k, shorts +$2.4k). AUDCAD grinds higher; "
  "shorts have to fight the drift. v1.3 amplifies this: the bigger the lot ladder, the "
  "bigger the blowup when the trend doesn't reverse fast enough.")
w("")
w("**5. The equity-adaptive scaling rescued the run from getting worse.** After the first "
  "emergency on 2026-01-29, the probe base auto-shrank from 0.06 to 0.05 (~$80k equity → "
  "smaller base via the same formula). Without this scaling, the subsequent baskets would "
  "have been the same 0.06 size on smaller equity → bigger relative exposure → likely 4+ "
  "emergencies. The auto-scale capped the bleed; it didn't prevent it.")
w("")
w("**6. The 246 TP closes produced +$38,396, which offset 67% of the −$56,649 emergency "
  "losses.** The strategy *recovers* from emergencies — the 246 good baskets are doing real "
  "work — but it can't outpace blowups of this magnitude in a 4.5-month window.")
w("")
w("### What to fix before live deployment")
w("")
w("Pick one (or stack them):")
w("")
w("- **(a) Soft DD buffer.** Add an input `TargetDDPct` (default 15%) and size with that "
  "instead of `MaxDDPct`. Leaves a 5-point cushion below the 20% emergency. Single-line "
  "change in `ComputeBaseLot()`.")
w("- **(b) Larger `FitPadPips`.** Increase from 5 to 25 pips so the formula assumes a deeper-"
  "than-grid worst case. Shrinks the base proportionally and gives room when price overshoots "
  "the grid.")
w("- **(c) Cap `MaxLegs` lower.** v1.2 2025 full-year hit L8 once; v1.3 hit L8 four times. "
  "Reducing `MaxLegs` to 7 or 8 caps the basket's worst-case exposure (and the WC constant) "
  "directly. Shrinks `g_wc_lotpips`, *enlarges* the auto-base, *reduces* max basket size.")
w("- **(d) Pre-trade pair gate.** If `RSI(D1) > 60` and signal is SHORT, skip the probe "
  "(don't fight a strong daily trend). Pure heuristic but matches the empirical asymmetry.")
w("- **(e) Run on the cent symbol** (the canonical v1.3 target). G10/G11/G12 still unrun. "
  "The cent profile is independent of (a)–(d); those fixes apply to either profile.")
w("")
w("### Bottom line")
w("")
w("v1.3 returned **−18.35% over 4.5 months at $100k standard** vs v1.2's **+14.36% over the "
  "same period at $50k**. Per-dollar-of-capital, v1.3 underperformed v1.2 by **~32 percentage "
  "points** in this run, entirely because v1.3 sizes to use the full 20% DD budget while v1.2 "
  "left a generous cushion. The auto-sizing *machinery* worked correctly — `[UNIT_SANITY]`, "
  "`[WC_CONST]`, `[AUTOSIZE]`, and the post-emergency base-down-scaling are all green. But "
  "**sizing to the cap is the wrong target**; a soft buffer (`TargetDDPct < MaxDDPct`) or a "
  "larger `FitPadPips` is the next move before any live deployment or before treating the "
  "G12 cent-profile run as the green light.")
w("")

out = os.path.join(ROOT, 'back test result', 'v1.3_2025_result.md')
open(out, 'w', encoding='utf-8').write("\n".join(L))
print("wrote", out, "-", len(L), "lines")

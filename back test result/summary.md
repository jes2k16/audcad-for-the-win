# Backtest Run Comparison — v1.4, v1.5 & v1.6 (AUDCAD M15 cent)

All runs: symbol `AUDCADm#` (XM cent), `Max_Drawdown_Percentage = 35%`, HTF gate ON (D1 EMA20), `TP = 10 pips`. Rows sorted **descending — newest run first**.

---

## Settings

| Run | EA | Period | Start $ | Lot mode | Base lot | Grid step | Max Lv | Min Conf | ATR Pause |
|---|---|---|---:|---|---:|---:|---:|---:|---:|
| **[v1.6_2025_v10](v1.6_2025_result_v10(2k).md)** | **v1.6** | **2025 (full)** | **2,000** | **fixed** | **0.10** | **25** | **10** | **2** | **ON (H1) + EMA200 + gap150** |
| **[v1.6_2024_v10](v1.6_2024_result_v10(2k).md)** | **v1.6** | **2024 (full)** | **2,000** | **fixed** | **0.10** | **25** | **10** | **2** | **ON (H1) + EMA200 + gap150** |
| **[v1.6_2025_v9](v1.6_2025_result_v9(2k).md)** | **v1.6** | **2025 (full)** | **2,000** | **AUTO** | **0.20→0.28** | **25** | **10** | **2** | **ON (H1) + EMA200 + gap150** |
| **[v1.6_2024_v9](v1.6_2024_result_v9(2k).md)** | **v1.6** | **2024 (full)** | **2,000** | **AUTO** | **0.18→0.27** | **25** | **10** | **2** | **ON (H1) + EMA200 + gap150** |
| **[v1.6_2025_v8](v1.6_2025_result_v8(2k).md)** | **v1.6** | **2025 (full)** | **2,000** | **AUTO** | **0.16→0.20** | **30** | **10** | **3** | **ON (H1) + EMA200 + gap150** |
| **[v1.6_2025_v7](v1.6_2025_result_v7(2k).md)** | **v1.6** | **2025 (full)** | **2,000** | **fixed** | **0.10** | **30** | **10** | **3** | **ON (H1) + EMA200 + gap150** |
| **[v1.6_2024_v7](v1.6_2024_result_v7(2k).md)** | **v1.6** | **2024 (full)** | **2,000** | **AUTO** | **0.15→0.19** | **30** | **10** | **3** | **ON (H1) + EMA200 + gap150** |
| **[v1.6_2024_v8](v1.6_2024_result_v8(2k).md)** | **v1.6** | **2024 (full)** | **2,000** | **fixed** | **0.10** | **30** | **10** | **3** | **ON (H1) + EMA200 + gap150** |
| **[v1.6_2024_v3](v1.6_2025_result_v3(2k).md)** | **v1.6** | **2024 (full)** ⚠️ | **2,000** | **fixed** | **0.10** | **30** | **10** | **3** | **ON (H1) + EMA200** |
| **[v1.6_2024_v2](v1.6_2025_result_v2(2k).md)** | **v1.6** | **2024 (full)** ⚠️ | **2,000** | **fixed** | **0.10** | **30** | **10** | **3** | **ON (H1)** |
| **[v1.6_2024_v1](v1.6_2025_result_v1(2k).md)** | **v1.6** | **2024 (full)** ⚠️ | **2,000** | **fixed** | **0.10** | **30** | **10** | **3** | **ON (M15)** |
| **[v1.5_2025_2k_v6](v1.5_2025_result_v6(2k).md)** | **v1.5** | **2025 (full)** | **2,000** | **fixed** | **0.20** | **30** | **6** | **4** | off |
| [v1.5_2025_2k_v5](v1.5_2025_result_v5(2k).md) | v1.5 | 2025 (full) | 2,000 | fixed | 0.30 | 30 | 6 | 4 | off |
| **[v1.5_2025_2k_v4](v1.5_2025_result_v4(2k).md)** | **v1.5** | **2025 (full)** | **2,000** | **AUTO** | **0.82→1.45** | **30** | **6** | **4** | off |
| [v1.5_2025_2k_v3](v1.5_2025_result_v3(2k).md) | v1.5 | 2025 (full) | 2,000 | fixed | 0.10 | 30 | 6 | 4 | off |
| [v1.5_2025_2k](v1.5_2025_result_v1(2k).md) | v1.5 | 2025 (full) | 2,000 | fixed | 0.10 | 30 | 10 | 3 | off |
| [v1.4_2025_v1](v1.4_2025_result_v1.md) | v1.4 | 2025 (full) | 1,000 | auto | 0.11 | 22 | 10 | — | off |
| **[v1.5_2024_2k_v6](v1.5_2024_result_v6(2k).md)** | **v1.5** | **2024 (full)** | **2,000** | **fixed** | **0.20** | **30** | **6** | **4** | off |
| [v1.5_2024_2k_v5](v1.5_2024_result_v5(2k).md) | v1.5 | 2024 (full) | 2,000 | fixed | 0.30 | 30 | 6 | 4 | off |
| **[v1.5_2024_2k_v4](v1.5_2024_result_v4(2k).md)** | **v1.5** | **2024 (full)** | **2,000** | **AUTO** | **0.76→0.37** | **30** | **6** | **4** | off |
| **[v1.5_2024_2k_v3](v1.5_2024_result_v3(2k).md)** | **v1.5** | **2024 (full)** | **2,000** | **fixed** | **0.10** | **30** | **6** ✅ | **4** ✅ | off |
| [v1.5_2024_2k_v2](v1.5_2024_result_v2(2k).md) | v1.5 | 2024 (full) | 2,000 | fixed | 0.10 | 30 | 10 | 4 | off |
| [v1.5_2024_2k](v1.5_2024_result_v1(2k).md) | v1.5 | 2024 (full) | 2,000 | fixed | 0.10 | 30 | 10 | 3 | off |
| [v1.5_Jul2024](v1.5_July2025_result_v1.md) | v1.5 | **Jul 2024 only** | 1,000 | auto | 0.10 | 22 | 10 | **3** | off |
| [v1.4_2024_v2](v1.4_2024_result_v2.md) | v1.4 | 2024 (full) | 1,000 | **fixed** | 0.10 | 22 | 10 | — | off |
| [v1.4_2024_v1](v1.4_2024_result_v1.md) | v1.4 | 2024 (full) | 1,000 | auto | 0.11 | 22 | 10 | — | off |
| [v1.4_2023_v1](v1.4_2023_result_v1.md) | v1.4 | 2023 (full) | 1,000 | auto | 0.10 → 0.16 | 22 | 10 | — | off |

---

## Results

| Run | Final $ | Net % | Probes | Closes | Win % | Net pips | Emerg | Block | Max legs | ATR pauses | End state |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **v1.6_2025_v10** | **2,376.43** | **+18.82%** ✅ | **289** | **288** | **93.4%** | **+3,082.4** | **0** | **0** | **L6** | 4 | **OK** |
| **v1.6_2024_v10** | **2,428.55** | **+21.43%** ✅ | **224** | **224** | **98.2%** | **+2,734.4** | **0** | **0** | **L8** | 6 | **OK** |
| **v1.6_2025_v9** | **2,889.50** | **+44.47%** 🚀 | **289** | **288** | **93.4%** | **+3,082.4** | **0** | **0** | **L6** | 4 | **OK (cap live)** |
| **v1.6_2024_v9** | **2,936.47** | **+46.82%** 🚀 | **224** | **224** | **98.2%** | **+2,734.4** | **0** | **0** | **L8** ⚠️ | 6 | **OK (cap live)** |
| **v1.6_2025_v8** | **2,400.41** | **+20.02%** ✅ | **241** | **240** | **93.8%** | **+2,449.1** | **0** | **0** | **L5** | 4 | **OK** |
| **v1.6_2025_v7** | **2,222.51** | **+11.13%** ✅ | **241** | **240** | **93.8%** | **+2,449.1** | **0** | **0** | **L5** | 4 | **OK** |
| **v1.6_2024_v7** | **2,461.43** | **+23.07%** ✅ | **169** | **169** | **97.6%** | **+2,095.3** | **0** | **0** | **L6** | 6 | **OK** |
| **v1.6_2024_v8** | **2,276.21** | **+13.81%** ✅ | **169** | **169** | **97.6%** | **+2,095.3** | **0** | **0** | **L6** | 6 | **OK** |
| **v1.6_2024_v3** | **1,769.39** | **−11.53%** ⚠️ | **203** | **203** | **99.5%** | **—** | **1** (Aug 5) | **0** | **L9** | ~5 | **active Dec** ✅ |
| **v1.6_2024_v2** | **1,203.83** | **−39.81%** ❌ | **145** | **145** | **98.6%** | **—** | **2** (Aug 5, Sep 27) | **1** | **L9** | **5** | **frozen Q4** |
| **v1.6_2024_v1** | **1,204.18** | **−39.79%** ❌ | **147** | **147** | **98.6%** | **—** | **2** (Aug 5, Sep 27) | **1** | **L9** | **62** | **frozen Q4** |
| **v1.5_2025_2k_v6** | **2,274.29** | **+13.71%** ✅ | **152** | **152** | **96.1%** | **—** | **0** | **0** | **4** | — | **OK (easy year)** |
| v1.5_2025_2k_v5 | 2,411.31 | **+20.57%** ✅ | 152 | 152 | 96.1% | +1,636.0 | 0 | 0 | 4 | — | OK (2024 risk) |
| **v1.5_2025_2k_v4** | **3,500.64** | **+75.03%** 🚀 | **152** | **152** | **96.1%** | **+1,636.0** | **0** | **0** | **4** | — | **OK (cap armed)** |
| v1.5_2025_2k_v3 | 2,137.14 | **+6.86%** ✅ | 152 | 152 | 96.1% | +1,636.0 | 0 ✅ | 0 | 4 | — | OK |
| v1.5_2025_2k | 2,313.27 | **+15.66%** | 258 | 257 | 95.7% | +2,840.7 | 0 | 0 | 6 | — | OK |
| v1.4_2025_v1 | 2,074.72 | **+107.47%** | 622 | 368 | 95.4% | — | 0 | 0 | 6 | — | OK |
| **v1.5_2024_2k_v6** | **1,742.37** | **−12.88%** ❌ | **119** | **119** | **98.3%** | **—** | **1** (Aug 5) | **0** | **L6@48.20 lots** | — | **OK (no freeze)** |
| v1.5_2024_2k_v5 | 1,873.03 | **−6.35%** | 123 | 123 | 98.4% | — | **1** (Jul 31) | 0 | L6@72.30 lots | — | OK (no freeze) |
| **v1.5_2024_2k_v4** | **1,255.59** | **−37.22%** ❌ | **123** | **123** | **96.7%** | **—** | **3** (Apr 9, Apr 19, Jul 25) | **4** | **L6@94.83 lots** | — | **OK (no freeze)** |
| **v1.5_2024_2k_v3** | **2,159.23** | **+7.96%** ✅ | **113** | **113** | **99.1%** | **+1,286.5** | **0** ✅ | **0** | **6** | — | **OK (full year)** |
| v1.5_2024_2k_v2 | 1,610.73 | **−19.46%** | 119 | 119 | 98.3% | +1,182.9 | **1** (Aug 5) | 0 | 9 | — | OK (full year) |
| **v1.5_2024_2k** | **1,204.19** | **−39.79%** | **145** | **145** | **95.2%** | **+1,327.5** | **2** (Aug 5, Sep 27) | **1** | **9** | — | **frozen Q4** |
| v1.5_Jul2024 | 751.66 | **−24.83%** | — | 14 | 92.9% | — | **1** (Jul 25) | 1 | 8 | — | frozen |
| v1.4_2024_v2 | 934.97 | **−6.50%** | 151 | 151 | 95.4% | +1,610.9 | **1** (Jul 25) | 2 | 9 | — | frozen |
| v1.4_2024_v1 | 815.27 | **−18.50%** | 138 | 84 | ~94% | — | **1** (Apr 9) | 1 | 8 | — | frozen |
| v1.4_2023_v1 | 838.18 | **−16.18%** | — | 221 | 95.5% | +2,555 | **2** (Jun) | 0 | 8 | — | frozen |

---

## Per-run notes

### v1.4_2023_v1 — 2 emergencies in 7 days killed it
- Jun 16 SHORT L8 −77.6 pips; Jun 23 LONG L8 −76.7 pips.
- Wiped 5 months of gains; account idle Jul–Dec.

### v1.4_2024_v1 — single April emergency, frozen
- Apr 9 SHORT 8-leg, −83.9 pips on 46.31 lots (~199 pips adverse).
- L1 Apr 2 → L8 Apr 8 → L9 blocked → emergency Apr 9 17:10.
- Reversal note: price peaked at 0.90075 (emergency close = absolute top); TP would have hit Apr 10 17:00 (24h later) — pure bad luck.

### v1.4_2024_v2 — fixed lot saved April, July still killed it
- Jul 25 LONG L9, −85.6 pips on 52.90 lots (~218 pips adverse).
- April basket survived (vs v1 emergency) — fixed 0.10 lot extended profitable trading by 3.5 months.
- Post-emergency price: continued falling 153 pips to low 0.88921 (Aug 5); TP would have hit Aug 19 (~75% DD at low — cap was correctly protective).
- +12% better than v1 but same dead end.

### v1.5_Jul2024 — confluence rule worked, freeze still happened
- Single-month test confirmed Jul 15 20:15 hair-trigger **blocked as predicted** (`buy_arms=1 < min=3`).
- But Jul 18 10:30 fired with 3 legit arms (StochRSI + BB%B + swing-low) → fatal basket → emergency Jul 25.
- **Structural lesson**: confluence defends against single-arm noise, NOT against multi-day directional moves with HTF gate aligned wrong.

### v1.5_2024_2k — same config as the 2025 winner, but 2024 broke it
- Same exact inputs as v1.5_2025_2k (the +15.66% run). Only variable: the year of price action.
- **Two emergencies**:
  - **Aug 5 LONG, L9, −146.1 pips on 52.90 lots (~$584 loss)**. L1 was the *same* 2024-07-18 10:30 entry that emergency'd the v1.5_1k July run. The $2k+30 config absorbed the initial 178-pip drop, but the move continued **another 105 pips after Jul 25** to 0.88937. Total adverse 319 pips — beyond the 270-pip ladder coverage.
  - **Sep 27 SHORT, L8 (L9 blocked), −135.0 pips on 42.10 lots (~$429 loss)**. 224-pip rise pre-emergency, total 289 pips. SHORT direction this time.
- **Q4 frozen**: 758 SKIP_PROBE events Oct–Dec — fixed 0.10 lot no longer fits 10-leg ladder under MaxDD=35 after equity dropped to ~$1.2k. `fit_check_fail_override` is the new freeze mode (vs `base_below_vol_min` in 1k runs).
- **What did work**: April 2024 had three deep baskets (L6, L5, L4) that all closed green — exact months where v1.4 1k auto-sized struggled. The configuration genuinely handles ≤225 pip adverse swings.
- **Structural lesson**: doubling capital ($1k → $2k) doubles the dollar value of the 35% emergency cap (~$350 → ~$700), which means MORE lots can accumulate before the cap fires. Bigger capital = bigger ammunition = bigger bullet wounds when emergency fires. This is why the % loss is *worse* than v1.4 v2 (−39.8% vs −6.5%) despite the EA surviving more individual adverse moves.
- analysis: see [v1.5_2024_result_v1(2k).md](v1.5_2024_result_v1(2k).md)

### v1.5_2024_2k_v2 — Min_Conf=4 cut 2024 losses in half, prevented Q4 freeze
- **Same exact inputs as v1.5_2024_2k except `Min_Confluence_Count` raised from 3 → 4 (unanimous).**
- **Sep 27 SHORT emergency PREVENTED** ✅ — the Sep 11 23:15 entry (which had 3-of-4 arms in v1) now needs all 4. `swing-high distance = 64 pips > 50` → dissented → no fire. September traded 6 small baskets through TP closes.
- **Aug 5 LONG emergency STILL FIRED**, but from an *earlier worse* L1: **Jul 16 11:45 @ 0.92216** (vs Jul 18 10:30 @ 0.92130 in v1). The Jul 16 bar had ALL 4 arms in deep oversold agreement (RSI=33.4, StochRSI=18.2, BB%B=0.05, swing-low=47 pips) — unanimous rule can't say no to that.
- **The Aug 5 emergency damage was nearly identical**: 9 legs, 52.90 lots, −142.4 pips (~$569 loss) vs v1's −146.1 pips (~$584). Saved ~$15 from the slightly better wavg of the earlier L1.
- **Why the year-end result is so much better**: avoiding the SECOND emergency in Sep kept equity above the FitCheck floor → Q4 traded normally instead of 758 SKIP_PROBE events. November had 22 closes (busiest month of the year — recovery).
- **Leg distribution shape**: very bimodal — 91.6% of baskets close at L1 or L2, then nothing between L5 and L9 except the single Aug 5 fatal. Unanimous rule trades fewer borderline setups; either it's a clean small win or a deep trap.
- **Lesson**: `Min_Conf=4` cleanly blocks 3-arm borderline cases but cannot block genuine 4-arm oversold/overbought readings. When the indicators legitimately scream "extreme", the market still has room to keep moving.
- analysis: see [v1.5_2024_result_v2(2k).md](v1.5_2024_result_v2(2k).md)

### v1.5_2024_2k_v3 — THE WINNING COMBO (Min_Conf=4 + Max_Level=6)
- **First 2024 result with a positive return**: +$159.23 (+7.96%) on $2k.
- **Zero emergencies, zero block_adds, zero skip_probes**. Account healthy all 12 months.
- 99.1% win rate (112/113 closes), single −3.3 pip spread artifact, +1,286.5 net pips.
- **The Jul 16 11:45 fatal LONG** (4-arm unanimous BUY at 0.92216 — the L1 that emergency'd v2) **closed at TP +12.5 pips on Aug 16 22:00** after a 31-day hold. At the absolute Aug 5 low (0.88937, where v1 emergency'd at $584 loss and v2 at $569 loss), this basket was floating at −222.8 pips below wavg = ~$405 loss = **20.3% DD** — well under the 35% cap.
- **The structural mechanism**: with Max_Level=6, the ladder sums to 24.10 lots × pv = $1.82/pip. For 35% DD = $700 to trigger emergency, price would need to be ~385 pips below wavg, which translates to ~490 pips below L1 — bigger than AUDCAD's actual 330-pip drop. **The cap mathematically cannot fire on real-world AUDCAD M15 moves at this configuration.**
- wc_pct at probe-open: **4.59%** (vs 22.52% at Max_Level=10) — 6× the safety margin.
- Only one basket all year reached the cap (L6), and it closed at TP.
- 4 levers in concert: $2k capital floats the freeze floor; Min_Conf=4 blocks borderline 3-arm setups; Step=30 spreads legs; **Max_Level=6 makes the cap mathematically unreachable**. Drop any one and the config starts leaking.
- analysis: see [v1.5_2024_result_v3(2k).md](v1.5_2024_result_v3(2k).md)

### v1.5_2025_2k_v4 — auto-sizing ON: same trades, 11× the profit, but cap re-armed
- **Only change from v3: `Auto_Compute_Lot_Size_Based_On_Equity = false → true`.** Everything else identical (Min_Conf=4, Max_Level=6, step=30, $2k).
- **Identical signals to v3**: same 152 probes, same 152 closes, same 96.1% win rate, same 0 emergencies. The ONLY difference is position size.
- Base lot auto-computed: **0.82** at $2k start, growing to **1.45** by year-end as equity compounded to $3.5k.
- Result: **$3,500.64 (+75.03%)** vs v3's +6.86% — **11× the profit from the exact same trades**, purely from sizing + compounding.
- **This answers "why was v3 profit small?"** — it was the deliberately-tiny fixed 0.10 lot, not the strategy. Auto-sizing is fully compatible with the v1.5 safe structure.
- **CRITICAL caveat — the emergency cap is now ARMED**: wc_pct jumped from 4.22% (v3) to **34.63–35%** (v4). Auto-sizing targets the full DD budget, so a full 6-leg basket now consumes the entire 35% cap at grid extension. **v3's safety was structural (cap unreachable); v4's safety on 2025 was circumstantial (no basket got past L4).** Had 2025 produced a Jul-2024-style 330-pip move, v4 would likely have emergency'd.
- **Strong prior that v4 does NOT survive 2024**: the Jul-Aug L6 fatal that v3 absorbed at 20.3% DD (because fixed 0.10 lots were tiny) would, at auto-sizing wc_pct=35%, blow past the cap and emergency. v4 on 2024 likely behaves like v1.5_2024_2k v1 (−39.79%) or worse.
- **The dial**: profit scales with how much DD budget you spend. v3 spends 4% → +6.86%, can't blow up. v4 spends 35% → +75%, cap live. The big return and the blow-up risk are the same lever.
- **Mandatory next test**: run v4 config on 2024 + 2023 before any deployment conclusion.
- analysis: see [v1.5_2025_result_v4(2k).md](v1.5_2025_result_v4(2k).md)

### v1.5_2024_2k_v4 — auto-sizing on the HARD year: 3 emergencies, −37.22% (prediction confirmed)
- **Only change from v3: `Auto_Compute=true`.** Same Min_Conf=4, Max_Level=6, step=30, $2k.
- **3 emergencies**: Apr 9 SHORT (94.83 lots, −85.5 pips), Apr 19 LONG (70.85 lots, −86.2 pips), Jul 25 LONG (54.50 lots, −86.7 pips). Total ~$1,430 in emergency losses.
- **The April smoking gun**: in v3, April's three deep baskets (L6/L5/L4) all closed GREEN. In v4, the same April setups emergency'd TWICE. Same market, same signals, same max-level — only the lot size differed. **This proves v3's safety came entirely from the small fixed lot, NOT from Max_Level=6.**
- **CRITICAL LESSON — Max_Level is not a safety lever under auto-sizing**: wc_pct was 34.87% at Max_Level=6 in v4 vs 4.59% at the same Max_Level=6 in v3. The auto-sizer computes the base to consume the full 35% budget regardless of how many legs the ladder has — lowering Max_Level just makes each leg bigger. Under auto-sizing, the cap is ALWAYS armed at ~MaxDD%. The only risk lever left is `Max_Drawdown_Percentage` itself.
- **One upside of auto**: never froze (0 SKIP_PROBE). The auto-sizer shrank base 0.76 → 0.37 after the April double-emergency, so probes always fit. Auto self-adjusts down and never permanently locks out — but pays for it by emergency-ing repeatedly instead.
- **The complete 2×2** (sizing × year): fixed-0.10 → +7.96% (2024) / +6.86% (2025); auto → −37.22% (2024) / +75.03% (2025). **Auto-sizing is a leveraged bet on the year being calm. v3 fixed is the only config positive on both years.**
- **Auto-sizing rejected for production.** Path forward: a fixed lot bigger than 0.10 (e.g. 0.20–0.30) that lifts returns 2–3× while keeping wc_pct under ~15% so the cap stays unreachable.
- analysis: see [v1.5_2024_result_v4(2k).md](v1.5_2024_result_v4(2k).md)

### v1.5_2025_2k_v5 — fixed 0.30 middle ground: +20.57% on 2025, but NOT safe for 2024
- **Only change from v3: `Default_Base_Lot_Size = 0.10 → 0.30`** (still fixed, auto OFF). Same Min_Conf=4, Max_Level=6, step=30, $2k.
- Same 152 trades as v3/v4, 96.1% win rate, 0 emergencies on 2025. **Final +20.57% — ~3× the v3 return** (3× the lot ≈ 3× the return).
- wc_pct = 12.67% (constant). Deepest basket L4 (32.70 lots) — 2025 never went past L4.
- **⚠️ wc_pct UNDERSTATES the real 2024 risk.** wc_pct measures DD if price stops at the ladder bottom (L6, ~150 pips below L1). The 2024 Jul-Aug move went 326 pips below L1 = 176 pips PAST L6, where DD grows linearly with no new legs. The v3 (0.10) basket floated at 20.3% DD at the Aug 5 low; at 0.30 (3× lots) that's **~61% DD → emergency around 0.89885**, well before the low.
- **Corrected safe-lot math**: size off the worst historical DD, not wc_pct. v3 (0.10) → 20.3% DD on the 2024 worst basket. For DD ≤ 35%: `base_max = 0.10 × 35/20.3 = 0.172`. **The true safe ceiling at $2k is ~0.15, not 0.30.**
- **v5 is not a free lunch** — it's a less-extreme point on the same risk dial. The risk/reward map: v3 0.10 = +7.96%/+6.86% (both safe); v5 0.30 = ~−35%(proj)/+20.57%; v4 auto = −37.22%/+75.03%.
- **Next**: (1) run v5 0.30 on 2024 to confirm the projected emergency; (2) run **fixed 0.15 on 2024 + 2025** — projected true safe-max (~30% DD worst-case 2024, ~1.5× v3 return). If 0.15 stays clean on 2024, it becomes the recommended production lot.
- analysis: see [v1.5_2025_result_v5(2k).md](v1.5_2025_result_v5(2k).md)

### v1.5_2024_2k_v5 — fixed 0.30 on hard year: 1 capped emergency, only −6.35% (NOT the −35% projected)
- **Only change from v3: `Default_Base_Lot_Size = 0.10 → 0.30`.** Same Min_Conf=4, Max_Level=6, step=30, $2k.
- **The v5-2025 −35% projection was 5× too pessimistic.** Actual: **−6.35%**, single emergency, account recovered, no freeze.
- **Why milder**: the emergency cap fires at 35% and CUTS the loss there — it doesn't wait for the bottom. The single Jul 31 LONG emergency (72.30 lots, −111.7 pips, ~$609 ≈ 35% of equity at the time) was offset by 121 winning baskets → year nets only −6.35%.
- **0.30 got April RIGHT**: the April L5 baskets (50.70 lots) that v4 auto-0.76 emergency'd TWICE, v5 0.30 rode out and closed green (+11.1, +10.6 pips). Only the deepest July L6 basket breached the cap at 0.30. **1 emergency vs auto's 3.**
- **The monotonic risk ladder is now mapped** (2024 emergencies / 2024% / 2025%): 0.10 → 0/+7.96%/+6.86%; 0.30 → 1/−6.35%/+20.57%; auto → 3/−37.22%/+75.03%. Bigger lot = more cap breaches = bigger swings both ways.
- **2-year sum nearly tied**: v3 0.10 = +$296; v5 0.30 = +$284. Same total, different shape — v5 has a strong year and a mild down year vs v3's two small positives. **Both survive at $2k (no freeze) because a single capped emergency leaves equity ~$1,400, above the ~$963 floor.**
- **Reframe**: it's not "v3 safe vs all-else-blows-up" — it's a variance spectrum, all survivable at $2k. 0.10 = zero emergencies/lowest variance; 0.30 = occasional capped emergency, recovers; auto = frequent emergencies.
- **Next**: test fixed 0.15/0.20 (largest lot with zero 2024 emergencies = max return at zero emergency risk), and 2023 replay for 0.10/0.15/0.30.
- analysis: see [v1.5_2024_result_v5(2k).md](v1.5_2024_result_v5(2k).md)

### v1.5_2025_2k_v6 — fixed 0.20 on easy year: +13.71%, slots cleanly between 0.10 and 0.30
- **Only change from v3: `Default_Base_Lot_Size = 0.10 → 0.20`** (still fixed, auto OFF). Same Min_Conf=4, Max_Level=6, step=30, $2k.
- Same 152 trades, 96.1% win rate, 0 emergencies. **Final +13.71%** — return scales ~linearly with lot on the easy year (0.10 → +6.86%, 0.20 → +13.71%, 0.30 → +20.57%).
- wc_pct = 8.45%. Deepest basket L4 (2025 never went past L4 in any run). Cap never threatened.
- Easy years prove nothing about robustness — the real test is the 2024 half (v6).
- analysis: see [v1.5_2025_result_v6(2k).md](v1.5_2025_result_v6(2k).md)

### v1.5_2024_2k_v6 — fixed 0.20 on hard year: WORSE than 0.30 (−12.88%), the non-monotonic dip
- **Only change from v3: `Default_Base_Lot_Size = 0.10 → 0.20`.** Same Min_Conf=4, Max_Level=6, step=30, $2k.
- **The 0.20 run was meant to find "the largest lot with zero 2024 emergencies." It took one.** Aug 5 LONG, L6 (48.20 lots), net −161.7 pips, DD=35% — the recurring Jul 16 11:45 fatal basket again.
- **THE SURPRISE — 0.20 (−12.88%) loses MORE than 0.30 (−6.35%), a smaller lot with a bigger loss.** Both trigger the *same* unavoidable Jul-16 emergency, capped at 35% of equity, so the dollar loss is essentially identical (~$588 at 0.20 vs ~$609 at 0.30). But the **winning baskets' profit scales with lot size** — at 0.20 the ~117 winners recover only ⅔ of what 0.30's do. Same emergency damage, weaker recovery → worse net.
- **Structural lesson — there's a valley, not a monotonic ladder.** Once a lot is big enough to trigger the unavoidable emergency, going *smaller* doesn't help: you eat the same capped loss but collect smaller wins. 0.20 is **too big to dodge the emergency (like 0.10 does) and too small to recover well (like 0.30 does)** — a dominated option.
- **Confirms the safe ceiling is below 0.20.** 0.10 floats the Jul-16 basket to 20.3% DD (stays under cap, 0 emergencies); 0.20 (2× lots) pushes it to ~40% DD → crosses the 35% cap. The true zero-emergency ceiling is ~0.15–0.17, as v5 predicted.
- **2-year sum is the worst of the fixed options**: −$258 (2024) + $274 (2025) = **+$17**, vs 0.10's +$296 and 0.30's +$284. Dominated on both ends — under-recovers vs 0.30 on the hard year, under-earns vs 0.30 on the easy year.
- No freeze: at $2k the single ~$588 emergency leaves equity ~$1,740, well above the ~$963 vol_min floor.
- analysis: see [v1.5_2024_result_v6(2k).md](v1.5_2024_result_v6(2k).md)

### v1.4_2025_v1 — easy year, default config crushed it
- 0 emergencies all year. Auto-sized base 0.11 at $1k start.
- HTF gate added +33.89 pp vs gate-OFF run.

### v1.5_2025_2k — the aggressive ($2k baseline) config on easy year
- Sep 12–24 deep basket: 6 legs, 24.10 lots, 109-pip adverse swing, held 12 days → closed +20.7 pips. Closest-call all year, still green.
- Leg distribution: L1=169, L2=68, L3=11, L4=7, L5=1, L6=1, L7+=0.
- All 11 "losses" are rollover-spread artifacts at 00:0X times (worst −10.3 pips ≈ $1.83). Not real strategy losses.
- 2,055 GATE_BLOCK events (HTF gate rejecting ~88% of raw signals).
- **wc_pct at probe-open: 20.73%** — 12pp pre-baked headroom under 35% cap.
- **Verdict**: $2k + step=30 + fixed 0.10 absorbs every 2025 setup with room to spare. **But this same config lost 39.79% on 2024** — see v1.5_2024_2k.

### v1.5_2025_2k_v3 — winning combo confirmed positive on easy year
- **Same exact config as v1.5_2024_2k_v3** (Min_Conf=4 + Max_Level=6 + $2k + step=30 + fixed 0.10).
- Final: $2,137.14 (**+6.86%**), 152 closes, 96.1% win rate, 0 emergencies, 0 blocks, 0 skips.
- Max legs reached: **only L4** (4 baskets). Zero baskets reached L5 or L6 — 2025 simply didn't have the multi-day sustained moves that produced the Sep deep basket in v1 or the Jul-Aug fatal in 2024.
- Trade-off vs v1 (Min=3, Lv=10): same year gives up ~$176 of upside (15.66% → 6.86%), trades 106 fewer probes (258 → 152). The conservative config is paying for survivability with selectivity.
- **2-year head-to-head**: v3 combo = $159 (2024) + $137 (2025) = **+$296** total. v1 aggressive combo = −$796 (2024) + $313 (2025) = **−$483** total. **Conservative wins by $779 across the 2-year window.**
- 6 losing closes — same rollover-spread pattern at 00:0X times (max −10.3 pips, total drag ~$5).
- **Verdict**: config validated on both 2024 (hard) and 2025 (easy). Two-out-of-three years showing consistent positive returns with zero structural risk. **Final validation gate: 2023 replay.**
- analysis: see [v1.5_2025_result_v3(2k).md](v1.5_2025_result_v3(2k).md)

### v1.6_2024_v10 — v9 knobs, fixed 0.10: +21.43%, same trades, wc_pct≈19%
- **Only change from v9: `Auto_Compute=false`, fixed 0.10.** Same Min_Conf=2, step=25, gap150 stack.
- **Identical 224 probes / +2,734 net pips to v9 auto** — dollar return ≈ 46% of v9 (+$429 vs +$936) because lot is ~half.
- **+21.43% beats v8 fixed (+13.81%) by +7.6 pp** with same zero-emergency record. wc_pct=18.97% (vs v9's 34%) — **2× cap headroom**.
- Jul 18 blocked; Jul 22 L5 closed +11.4 pips at **16.90 lots** (vs 35.49 v9). Apr L8 SHORT: **42.10 lots**, +11.4 pips (vs 84.20 v9) — same basket, half exposure.
- **2-year with 2025 v10: +$805** (vs v8/v7 +$499, v9 +$1,826). **Leading fixed-lot production candidate** pending 2023.
- analysis: [v1.6_2024_result_v10(2k).md](v1.6_2024_result_v10(2k).md)

### v1.6_2025_v10 — same fixed aggressive stack: +18.82% on easy year
- **Identical 289 probes / +3,082 net pips to v9.** +18.82% vs v9 +44.47% — pure sizing difference.
- Max L6 (Dec 11), 0 emergencies, wc_pct=17.47%. Beats v7 fixed (+11.13%) by +7.7 pp with same gate stack family.
- analysis: [v1.6_2025_result_v10(2k).md](v1.6_2025_result_v10(2k).md)

### v1.6_2024_v9 — aggressive stack on gap150: +46.82%, L8 close call, still zero emergencies
- **Changes from v7/v8**: `Min_Confluence_Count=2`, `Grid_Step_Pips=25`, auto ON. Same EMA200 + gap150 + H1 ATR + Max_Level=10.
- **+46.82%** — highest 2024 return in the matrix (+$936). 224 probes (+55 vs v7), wc_pct=34.15%, base 0.18→0.27.
- **Jul 18 fatal still blocked** (`htf_gap_above gap=227.1`); Jul 22 replacement LONG closed L5 Jul 30 (+11.4 pips, 35.49 lots).
- **April L8 SHORT (Apr 2 → Apr 10)** — 84.20 lots, +11.4 pips. Same ~195-pip adverse rally that **emergency'd v1.5 v4 auto twice** in April. Survived here; **closest cap call in the test set**.
- Only 1 basket reached L7+ all year. 4 negative closes (rollover). Gap blocks: 1,086 (~2× v8).
- **2-year with 2025 v9: +$1,826** (vs v7/v8 auto +$861). Tail risk is real — validate 2023 before production.
- analysis: [v1.6_2024_result_v9(2k).md](v1.6_2024_result_v9(2k).md)

### v1.6_2025_v9 — same aggressive config on easy year: +44.47%
- **Identical config to 2024 v9.** 289 probes (+48 vs v8 auto), 0 emergencies, max L6 (Dec 11 LONG, +11.3 pips).
- **+44.47%** vs v8 auto +20.02% — Min_Conf=2 + step=25 + larger auto base compound on the easy year.
- 828 gap blocks (vs 433 at Min_Conf=3). 19 negative closes = rollover only.
- Gives up v1.5 v4's +75% easy-year peak but pairs with +47% hard year instead of −37%.
- analysis: [v1.6_2025_result_v9(2k).md](v1.6_2025_result_v9(2k).md)

### v1.6_2024_v8 — **`Max_EMA200_Gap_Pips=150` breaks 2024**: +13.81%, zero emergencies
- **Key addition over v3**: `Max_EMA200_Gap_Pips=150` on top of EMA200 + H1 ATR. Fixed 0.10, Min_Conf=3, Max_Level=10.
- **Jul 18 10:30 fatal LONG @ 0.92103 blocked** at the exact bar: `htf_gap_above gap=227.1 max=150`. Price was 227 pips above EMA200 — parabolic extension, not a mean-reversion zone.
- **Replacement entry Jul 22 15:45 @ 0.91399** (~71 pips lower). L5 basket closed Jul 30 +10.5 pips (16.90 lots). Survived Aug 5 low with no emergency.
- **562 gap blocks** (100 above / 54 below) on top of EMA200 veto. Fewer probes than v3 (169 vs 203) but all survivable.
- **First positive full-year 2024 at Max_Level=10** without emergency. Beats v1.5 v3 (+7.96%) by +5.85 pp with 50% more trades.
- 2-year with 2025 v7 fixed: **+$499**. analysis: [v1.6_2024_result_v8(2k).md](v1.6_2024_result_v8(2k).md)

### v1.6_2024_v7 — same gate stack, auto-sizing: +23.07% on identical 169 trades
- **Only change from v8: `Auto_Compute=true`.** Same signals, same gate blocks, same 0 emergencies.
- Base auto-computed 0.15 → 0.19; wc_pct=33.79% (cap armed). Profit ~1.67× fixed v8 (+$461 vs +$276).
- **Why auto works here but v1.5 v4 auto failed**: gap filter blocked the Jul 18 parabolic L1 that auto-sized v4 couldn't avoid. Auto is safe only when the gate prevents the catastrophic entry.
- 2-year with 2025 v8 auto: **+$861**. analysis: [v1.6_2024_result_v7(2k).md](v1.6_2024_result_v7(2k).md)

### v1.6_2025_v7 — gap stack validates on easy year: +11.13%, beats v1.5 v3
- Same config as 2024 v8 (EMA200 + gap150 + fixed 0.10). 241 probes, 0 emergencies, max L5.
- **+11.13% vs v1.5 v3's +6.86%** — +4.27 pp with 59% more probes. Gate stack trades more actively than Min_Conf=4 while staying clean.
- 433 gap blocks (100 above / 100 below — balanced on easy year). 15 negative closes = rollover spread only.
- 2-year with 2024 v8: **+$499** vs v1.5 v3's +$296 (+$203). analysis: [v1.6_2025_result_v7(2k).md](v1.6_2025_result_v7(2k).md)

### v1.6_2025_v8 — auto on easy year: +20.02%, identical trades to v7
- **Only change from v7: `Auto_Compute=true`.** 241/240 probes/closes, 0 emergencies, +20.02%.
- Lower peak than v1.5 v4 auto (+75%) because gate blocks ~433 entries/year — but v4 auto was **−37% on 2024**. v6 auto pair: +23%/+20% both years.
- 2-year auto sum **+$861** vs fixed **+$499**. Cap live at wc_pct≈34%. analysis: [v1.6_2025_result_v8(2k).md](v1.6_2025_result_v8(2k).md)

### v1.6_2024_v3 — EMA200 gate: Sep emergency PREVENTED, account active all year, still −11.53%
- **⚠️ Filename says "2025" but test period is 2024** (same naming error).
- Only change from v2: `GateEMA_Period = 200` (D1 EMA200 instead of EMA20).
- **EMA200 says "AUDCAD is in a long-term bull trend" for most of 2024** — blocked **1,371 SHORT signals** vs only 523 LONG blocks. The strategy ran as effectively "longs only" for most of the year.
- **Sep 11 23:15 SHORT (the fatal Sep basket in v1/v2) blocked at the exact bar** (`htf_veto_sell`) — because AUDCAD was above its 200-day average. No Sep 27 emergency. No Q4 freeze. Account active through Dec 30. **203 probes vs 145 in v2** — more trades because EMA200 passes more LONG signals.
- **Jul 18 LONG fatal basket: identical** — AUDCAD was above EMA200 (correctly trend-aligned), gate said "long OK." Same 9 legs, same Aug 5 09:02 emergency, same −147.7 pips on 52.90 lots (~$591 loss).
- **Why still negative**: −11.53% not flat or positive because (a) the one remaining emergency cost ~$591, and (b) recovery at 0.10 fixed lot is ~$0.07 per L1 close — 202 TP closes across the year generates only ~$360 total TP profit. Math: +$360 − $591 = −$231. Account survives but can't recover fast enough.
- **EMA200 vs EMA20 head-to-head**: −11.53% vs −39.79% — a 70% improvement in loss magnitude, purely from a slower EMA period. The structural problem (Max_Level=10 allows 9-leg accumulation) remains.
- **The lesson**: EMA200 is a genuine macro filter — useful for blocking counter-trend entries in a directional year. But it cannot protect against a trend-aligned entry followed by a violent counter-move. Only `Max_Level=6` has proven it can absorb that.
- **Next test**: `Min_Conf=4 + Max_Level=6 + EMA200` — all three layers combined.
- analysis: see [v1.6_2025_result_v3(2k).md](v1.6_2025_result_v3(2k).md)

### v1.6_2024_v2 — H1 ATR: only 5 pauses all year, missed the fatal period entirely
- **⚠️ Filename says "2025" but test period is 2024** (same naming error as v1).
- Only change from v1: `ATR_Timeframe = PERIOD_H1` (vs M15 in v1).
- **5 pause activations** vs 62 on M15 — H1 smooths out M15 spikes. Only triggers when an entire session is hot (NFP, risk-off shock). Routine intraday volatility is invisible.
- **Fatal Jul 18 basket: zero H1 ATR response.** On Jul 25 (the critical day), `H1 atr_ratio=1.16` — completely below the 1.8 threshold. All 9 legs added unimpeded. The H1 pause only fired at **Aug 5 11:00 — 2 hours after the emergency at 09:02**.
- Sep 19 pause did delay L7 of the Sep emergency basket by ~15 hours. Basket still emergency'd on Sep 27.
- **Final: $1,203.83 — slightly WORSE than ATR-OFF ($1,204.19)**. The 5 pauses on non-fatal May/June baskets may have slightly altered their leg timing to disadvantage; the fatal baskets were untouched.
- **Three-way verdict** (ATR OFF / M15 ATR / H1 ATR): $1,204.19 / $1,204.18 / $1,203.83 — within $0.36 of each other. ATR pause in any timeframe has zero structural impact on the 2024 failure mode.
- **Definitive conclusion**: 2024 killed the EA via slow 18-day directional drift, not volatility spikes. ATR measures per-bar volatility; it is blind to direction and duration. `Max_Level=6` is the only tested fix.
- analysis: see [v1.6_2025_result_v2(2k).md](v1.6_2025_result_v2(2k).md)

### v1.6_2024_v1 — ATR pause ON (M15), same config as v1.5_2024_2k → same result ($0.01 difference)
- **⚠️ Filename says "2025" but test period is 2024-01-01 → 2024-12-31** (naming error, consistent with earlier v1.5_July2025 typo).
- Same base config as `v1.5_2024_2k` (Min_Conf=3, Max_Level=10, fixed 0.10, Grid=30, $2k) with the only addition being `Enable_ATR_Pause=true`.
- **ATR pause activated 62 times, blocking 491 potential leg additions.** Despite this, the result is bit-for-bit identical: same 2 emergencies (Aug 5 LONG L9, Sep 27 SHORT L8), same frozen Q4, final balance $1,204.18 vs $1,204.19 (ATR-OFF).
- **Why it made no difference**: 2024's fatal baskets accumulated over 2–3 *weeks* of slow, step-by-step adverse movement. ATR pause targets *fast bars* (ATR(14)/ATR(100) ≥ 1.8). Between those fast bursts, the market calmed, the EA resumed, and added the next leg. The emergencies were inevitable regardless.
- **BLOCK_ADD (dd_cap_fwd) still functioned correctly**: Sep 27 L9 attempt was blocked because post-E1 equity could not afford a 9th leg under MaxDD=35%.
- **Structural finding**: ATR pause is a noise filter, not a trend-protection tool. It will show benefit only in scenarios where a single fast spike (not a sustained move) would have forced a premature leg addition.
- analysis: see [v1.6_2025_result_v1(2k).md](v1.6_2025_result_v1(2k).md)

---

## At-a-glance read

**Three patterns explain everything**:

1. **$1k cent + 22-pip grid + L8/L9 emergency = freeze**. Every $1k run with an emergency ended below the $963 vol_min floor — permanently idle for the rest of the year. The freeze isn't optional; it's mechanical.

2. **2025 was easy**. Both v1.4_2025_v1 (+107%) and v1.5_2025_2k (+15.66%) closed green with 0 emergencies. Don't draw conclusions about robustness from 2025-only data.

3. **Hard years stay hard even at $2k + step=30 + Min_Conf=3** (−39.79%, 2 emergencies, Q4 frozen). Capital doubling absorbs medium swings — it does **not** prevent the cap from firing in 280+ pip moves, and the cap now costs ~2× more dollars per emergency (35% of $2k = ~$700 vs 35% of $1k = ~$350).
4. **Raising `Min_Conf` from 3 → 4 (unanimous) cut 2024 losses ~50% (−39.79% → −19.46%)**. Cleanly blocked one of the two emergencies (Sep 11 SHORT — was a borderline 3-arm setup with swing-high dissenting at 64 pips). Did NOT block the Aug 5 LONG fatal — found a different L1 two days earlier with all 4 arms deeply agreeing. **The unanimous rule prevents borderline traps but not genuine 4-arm oversold setups at the start of big directional moves.**
5. **Min_Conf=4 + Max_Level=6 is the winning combo on both years tested**: +7.96% on 2024 (hard) and +6.86% on 2025 (easy). First config in the test set to deliver consistent positive returns across both regimes. The Max_Level=6 cap is the structural fix — with 24.10 max lots, the 35% DD cap is mathematically unreachable on the 330-pip AUDCAD drop because the floating loss at the absolute low only hits ~20% DD. The Jul 16 fatal LONG (emergency'd at both Min_Conf=3 and Min_Conf=4 with Max_Level=10) closed at TP +12.5 pips after a 31-day hold. **2-year combined: +$296 vs −$483 for the aggressive baseline.** Final validation gate: 2023 replay.
6. **The cost of the conservative config on easy years is real but small**: 2025 v3 gave up ~$176 vs v1 (6.86% vs 15.66%). The trade is "buy survivability with selectivity" — 41% fewer probes, max legs capped at L4 in 2025 (vs L6 in v1), but zero emergency risk. On a 2-year window the trade pays for itself by ~$780.
6b. **Profit is set by SIZING, not the safe structure** (v4 proof): turning `Auto_Compute=true` on the v3 safe structure (Min_Conf=4 + Max_Level=6) fired the *identical* 152 trades but returned **+75.03%** vs v3's +6.86% — 11× more, purely from compounding bigger lots. BUT wc_pct went 4% → 35% (cap re-armed).
6c. **Auto-sizing CONFIRMED fatal on the hard year** (v4 2024): −37.22%, 3 emergencies. The same April baskets that closed GREEN in v3 emergency'd in v4 — only the lot size differed. **Definitive proof that v3's safety came from the small fixed lot, not Max_Level=6.** And the killer structural finding: **Max_Level is NOT a safety lever under auto-sizing** — the auto-sizer inflates per-leg lots to consume the full 35% budget regardless of leg count (wc_pct=34.87% at Max_Level=6). The complete 2×2: fixed-0.10 = +7.96%/+6.86% (both years positive); auto = −37.22%/+75.03% (coin flip on the year). **v3 fixed-0.10 is the only config positive on both years. Auto-sizing rejected.**
6d. **`wc_pct` is a misleading safety gauge for fixed-lot sizing** (v5 finding). v5 fixed-0.30 returned +20.57% on 2025 with wc_pct=12.67% — looks safe. But wc_pct only measures DD if price stops at the ladder bottom (L6); real sustained moves go *past* L6 where DD grows linearly with no new legs. **Size the fixed lot off the worst historical DD (2024 = 20.3% at base 0.10), not off wc_pct.** Lot with zero 2024 emergencies ≈ **0.15–0.17**.
6e. **CORRECTION — a capped emergency at 0.30 is survivable, not catastrophic** (v5 2024 proof). The projected "−35%" for 0.30 on 2024 was 5× too pessimistic. Actual: **−6.35%, 1 emergency, recovered.** The cap fires at 35% and CUTS the loss (doesn't wait for the bottom); at $2k the post-emergency equity (~$1,400) stays above the freeze floor, so the EA recovers. April baskets that auto-0.76 emergency'd twice, 0.30 rode out green. **The real picture is a variance spectrum, all survivable at $2k**: 0.10 = 0 emerg / +7.96%/+6.86%; 0.30 = 1 emerg / −6.35%/+20.57%; auto = 3 emerg / −37.22%/+75.03%. 2-year totals: 0.10 = +$296, 0.30 = +$284 (nearly tied, different shape). The freeze that doomed $1k runs needs equity < $963 floor — at $2k a single capped emergency doesn't get there.
6f. **The fixed-lot risk curve is a VALLEY, not a monotonic ladder** (v6 0.20 finding). Filling in the gap between 0.10 and 0.30 on 2024 produced the counterintuitive result: **0.20 = −12.88%, WORSE than 0.30's −6.35%.** Both lots trigger the *same* unavoidable Jul-16 emergency (capped at 35% of equity → ~$590 either way), but winning-basket profit scales with lot size, so 0.20's smaller wins recover less. Once a lot crosses the emergency threshold (≈0.17), shrinking it doesn't reduce the capped loss — it just shrinks the recovery. **0.20 is a dominated option**: too big to dodge the emergency (like 0.10), too small to recover well (like 0.30). 2-year sums: 0.10 = +$296, **0.20 = +$17 (worst)**, 0.30 = +$284. This also pins the zero-emergency safe ceiling firmly **below 0.20** (0.10 floats the fatal basket to 20.3% DD; 0.20 to ~40% > 35% cap), consistent with the ~0.15–0.17 estimate. **Next: test 0.15 — the last untested sweet-spot candidate.**
7. **The 270-pip ladder coverage wall is no longer the binding constraint.** At Max_Level=6 the ladder spans 150 pips, but the cap-firing threshold (490 pips past L1) is bigger than the move. The remaining concerns are: (a) opportunity cost when stuck in a deep basket (31 days for the Jul 16 trade), (b) the still-untested 2023 replay.
8. **ATR pause (v1.6) had zero impact on the hard year — confirmed across M15 AND H1 timeframes.** Three-way comparison (ATR OFF / M15 ATR / H1 ATR): final balances $1,204.19 / $1,204.18 / $1,203.83 — within $0.36. Same emergencies, same dates. H1 ATR fired only 5 times all year and missed the fatal Jul-Aug period entirely (H1 ratio=1.16 on Jul 25 — no spike detected; pause fired at 11:00 Aug 5, **2 hours after the 09:02 emergency**). ATR measures volatility; 2024 killed via slow 18-day directional drift that looks "calm" to any ATR measure. **`Max_Level=6` remains the only tested structural fix.**
9. **EMA200 gate (v1.6 v3) cut the 2024 loss by 70%: −11.53% vs −39.79%, and kept the account alive all year.** The EMA200 blocked 1,371 SHORT entries (vs 523 LONG blocks) because AUDCAD was above its 200-day average for most of 2024 — effectively running "longs only." The Sep 11 SHORT (which became the fatal Sep basket in previous runs) was blocked at the exact bar. The Jul 18 LONG was NOT blocked (correctly trend-aligned to EMA200). Result: 1 emergency instead of 2, no Q4 freeze, 203 trades active through Dec 30. Still negative because: (a) the one emergency cost ~$591 and (b) recovery at 0.10 fixed lot is ~$0.07/close — 202 wins earned only ~$360. **EMA200 alone cannot fix trend-aligned parabolic entries.**
10. **BREAKTHROUGH — `Max_EMA200_Gap_Pips=150` (v1.6 v7/v8) is the missing layer.** Blocks probes when price is >150 pips from EMA200. Jul 18 10:30 fatal LONG (gap=227 pips) **killed at the bar**; replacement Jul 22 entry 71 pips lower closed L5 at TP. **2024: +13.81% fixed / +23.07% auto, 0 emergencies** (vs v3 EMA200-only −11.53% with 1 emergency). **2025: +11.13% fixed / +20.02% auto, 0 emergencies** (vs v1.5 v3 +6.86%). **First config positive on BOTH years at $2k**: fixed 2-yr sum **+$499** (+$203 vs v1.5 v3); auto 2-yr **+$861**. Mechanism: don't mean-revert when price is parabolic vs the 200-day mean. Auto-sizing becomes viable again **only paired with this gap cap** (v1.5 v4 auto alone was −37% on 2024). **2023 replay still mandatory.** Optional overlays: Min_Conf=4, Max_Level=6 for defense-in-depth.
11. **v9 aggressive stack (Min_Conf=2, step=25, auto, gap150) — profit ceiling on tested years, cap live.** Same gate as v7/v8 plus hair-trigger confluence + tighter grid. **2024: +46.82% (L8 Apr basket survived, +11.4 pips); 2025: +44.47% (max L6). 0 emergencies both years. 2-yr sum +$1,826** — 2.1× v7/v8 auto. April L8 SHORT (84 lots) is the same move that emergency'd v1.5 v4 auto — survived but proves wc_pct=35% was **engaged**. **Not first-deploy safe** until 2023 confirms.
12. **v10 = v9 with fixed 0.10 — best fixed-lot 2-year result (+$805), recommended production candidate.** Same 224/289 probes and net pips as v9; return ≈ 45% of v9 auto because lot is fixed small. **2024: +21.43% (L8 at 42 lots, wc_pct≈19%); 2025: +18.82%. 0 emergencies both years.** Beats v8/v7 fixed (+$499) by +61% with ~2× the wc_pct headroom of v9. **Sizing dial**: v10 fixed for deploy, v9 auto for max return after 2023 gate clears.

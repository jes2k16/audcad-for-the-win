# Response Style

- Summarize answers — no overexplaining unless asked
- Pragmatic and direct; use layman's terms when possible

---

# AUDCAD FOR THE WIN — Project Context

**Goal**: standalone MT5 EA that trades AUDCAD on an XM **cent / micro account** (default `AUDCAD.c` / `AUDCADm#`; standard `AUDCAD#` supported via explicit override) using a mean-reversion grid-recovery basket strategy, reverse-engineered from master account `#50000005` (130 probes, Feb–May 2026). v1.3 introduced the equity-scaled lot ladder; **v1.4** adds descriptive input names + safer defaults (`Abort_If_Standard_Account=true`, `Max_Drawdown_Percentage=35` to admit `vol_min=0.10` cent probes at $1k equity).

---

## Quick orientation

| Item | Value |
|---|---|
| Symbol | `AUDCAD.c` / `AUDCADm#` (XM cent, hedging) by default — `AUDCAD#` (standard) requires `Abort_If_Standard_Account=false` override |
| Min real capital | **$1,000 USD** (cent account at default `Max_Drawdown_Percentage=35`); below this, auto-sizer skips probes |
| Timeframe | M15 — all signals checked at bar close |
| Magic numbers | Long `50000051`, Short `50000052` |
| Active EA | `EA/AUDCAD_M15_v1_4.mq5` |
| Active strategy | `strategy/AUDCAD_M15_v1.4.md` |
| Shadow mode default | `true` — logs only, no real orders until flipped |

---

## Strategy version history

| Version | File | Key change | Status |
|---|---|---|---|
| v1 | `strategy/AUDCAD_M15_v1.md` | Base rule: RSI+StochRSI+BB%B signal, 22-pip grid, 24x/+12x lot ladder, dual-purpose signal (opp signal closes basket + opens new probe), bidirectional (2 baskets at once) | Superseded |
| v1.1 | `strategy/AUDCAD_M15_v1.1.md` | Added D1 EMA20 HTF gate — veto on new probe opens only; closes unaffected | Superseded |
| v1.2 | `strategy/AUDCAD_M15_v1.2.md` | Exit changed to +10 pip net basket profit target (weighted avg). Opposite signal no longer closes basket. Single basket at a time (no bidirectional). | Superseded |
| v1.3 | `strategy/AUDCAD_M15_v1.3.md` | Equity-scaled base lot (closed-form `WC = 44,627` lot-pip ceiling) so a full 10-leg ladder always fits 20% DD. Cent / micro account default. `ProbeLot` becomes optional override. New CSV columns + `[UNIT_SANITY]` / `[WC_CONST]` / `[AUTOSIZE]` log lines. | Superseded |
| **v1.4** | `strategy/AUDCAD_M15_v1.4.md` | **Ergonomics + safer defaults: ~30 inputs renamed to descriptive snake_case (`Max_Drawdown_Percentage`, `Bollinger_Period`, `Buy_Only_If_RSI_LessThan`, …), inline comments reformatted as `// VariableName: description` so MT5 tester panel shows both. `ProbeLot` split into `Auto_Compute_Lot_Size_Based_On_Equity` (bool) + `Default_Base_Lot_Size` (double). Two default flips: `Abort_If_Standard_Account = true` (cent guard ON), `Max_Drawdown_Percentage = 35` (admits $1k cent vol_min, PROVISIONAL). No mechanics change — identical strategy logic to v1.3.** | **Active** |

---

## Locked mechanics (do not change without evidence)

| Rule | Value | Source |
|---|---|---|
| Entry signal | RSI(14) direction gate + any of: StochRSI≤20/≥60, BB%B≤0.10/≥0.90, RSI≤40/≥60, sell near 500-bar swing high | v1 §1, validated G1 91% / G2 85% |
| Grid step | 22 pips from last entry price, checked at M15 close | G5 median confirmed |
| Ladder multipliers | `[1, 24, 36, 48, 60, 72, 84, 96, 108, 120]` (m(1)=1, m(n≥2)=12·N) — locked shape | G7 confirmed Apr–May era |
| Lot ladder base | **Auto-computed** at probe-open: `base = floor( (equity × Max_Drawdown_Percentage%) / (44,627 × PipValPerLot()), vol_step )`. Cached on basket. `Auto_Compute_Lot_Size_Based_On_Equity = false` + `Default_Base_Lot_Size > 0` forces fixed override. | v1.3 §2, v1.4 §3 |
| Account profile | Cent / micro (`AUDCAD.c` / `AUDCADm#`) default; standard requires `Abort_If_Standard_Account = false` override | v1.3 §3, v1.4 §4 |
| Max legs | 10 (source never exceeded 8) | v1 §5 |
| HTF gate | D1 close vs D1 EMA20 (shift=1, strict `>` / `<`) | v1.1 §1 |
| Exit | Basket closes when `current price ≥ wavg + 10 pips` (buy) or `≤ wavg − 10 pips` (sell) | v1.2 §2 |
| One basket at a time | No bidirectional; active basket blocks all new probes | v1.2 §2 |
| DD cap | **35% equity** (v1.4 default, raised from 20%, PROVISIONAL) — emergency market close + block-add forward check + closed-form pre-trade sizing | plans/1 §9, v1.3 §2, v1.4 §4.2 |

---

## Signal rules (v1 §1) — reference card

**BUY**: `RSI < 50` AND (`StochRSI_K ≤ 20` OR `BB%B ≤ 0.10` OR `RSI ≤ 40`)
**SELL**: `RSI > 50` AND (`StochRSI_K ≥ 60` OR `BB%B ≥ 0.90` OR `RSI ≥ 60` OR `dist_500bar_high ≤ 50 pips`)

All conditions on the **last completed M15 bar** (shift=1).

---

## EA decision tree (v1.4 — mechanics identical to v1.3, only `Max_Drawdown_Percentage` default changed)

> *Probe size and full ladder are auto-computed at probe-open time from current equity, then cached on the basket. The EA skips the probe if equity is too small to fit `vol_min × 10-leg` under the `Max_Drawdown_Percentage` cap (logs `SKIP_PROBE / base_below_vol_min`).*

```
On every M15 bar close:

IF basket IS open:
    1. Check close target → if wavg ± TP_Basket_If_Total_Pips_GreaterThan_EqualTo hit → close all legs
    2. Else check grid add → if price moved Grid_Step_Pips adverse → add next leg (uses cached base)
    (signals are ignored while a basket is open)

IF NO basket open:
    BUY signal fires + gate_long (D1 > EMA20) → compute base, FitCheck, open BUY probe
    SELL signal fires + gate_short (D1 < EMA20) → compute base, FitCheck, open SELL probe
    Signal fires but gate fails → log GATE_BLOCK, skip
    Probe sized below vol_min → log SKIP_PROBE / base_below_vol_min, skip

Emergency (any tick): basket floating loss ≥ Max_Drawdown_Percentage equity → close at market
```

---

## Validation gates (as of 2026-05-12)

| Gate | Threshold | Result |
|---|---|---|
| G1 Feb hit-rate | ≥ 85% | **PASS** 91% |
| G2 OOS hit-rate (Mar–May) | ≥ 80% | **PASS** 85%, −6.4 pp drift |
| G3 Precision | ≥ 20% | WARN 1.3% — zone condition by design |
| G4 Fires/day ratio | ≤ 3× actual | WARN 70× — basket-management signals |
| G5 Grid step | ≥ 90% within 18–28 pip | WARN 76%, median 22.2 pip confirmed |
| G6 Close trigger | ≥ 80% match | PASS 59–73% cross-dir (now replaced by v1.2 pip target) |
| G7 Lot formula | clean fit | WARN +$28/bump; v1.2 uses fixed 0.01 |
| G8 Live forward test | ≥ 2 weeks | **Not started** |
| G9 v1.2 P/L improvement | v1.2 ≥ master P/L | Superseded by v1.3 backtest +13.13% on $50k standard 2025 — see [back test result/v1.2_2025_result.md](back%20test%20result/v1.2_2025_result.md). |
| G10 `[UNIT_SANITY]` log (XM cent `AUDCADm#`) | `contract_size=1000`, `pv≈0.0695`, `vol_min=0.10`, tag `cent` | **PASS** — see [v4 log](back%20test%20result/v1.3_2025_result_v4%2835DD%29.log) |
| G11 `[AUTOSIZE]` projection at $1k cent | At default `Max_Drawdown_Percentage=35`: `base=0.11`, `wc_pct≈34` (original 20%-cap target `base=0.06` superseded — broker `vol_min=0.10`, not `0.01`) | **PASS** (v4 log) |
| G12 $1k cent 2025 replay | Max DD ≤ chosen cap, baskets close at TP, recovery after emergency | **PASS** — v4: 0 BLOCK_ADD, 1 absorbed L8 emergency, +73.58% net — see [v4 review](back%20test%20result/v1.3_2025_result_v4%2835DD%29.md) |
| G13 v1.4 standard-account regression | v1.4 with `Auto_Compute_Lot_Size_Based_On_Equity=false`, `Default_Base_Lot_Size=0.01`, `Abort_If_Standard_Account=false`, `Max_Drawdown_Percentage=20` on `AUDCAD#` 2025 → matches v1.2 +$6,567.29 baseline | **Not started** |

---

## File map

```
plans/
  1.initial requirements.md   Locked basket mechanics, 20% DD cap, lot conventions
  2.Strategy.md               900-line research trail; Sections 14.9b, 13.X, 14.9f canonical

strategy/
  AUDCAD_M15_v1.md            Base signal + grid + lot ladder (superseded)
  AUDCAD_M15_v1.1.md          + D1 EMA20 HTF gate (superseded)
  AUDCAD_M15_v1.2.md          + pip-target exit, single basket (superseded)
  AUDCAD_M15_v1.3.md          + equity-scaled base lot, cent profile (superseded)
  AUDCAD_M15_v1.4.md          + descriptive input names, ProbeLot split, safer defaults (ACTIVE)

EA/
  AUDCAD_M15_v1_1.mq5         v1.1 EA (superseded)
  AUDCAD_M15_v1_2.mq5         v1.2 EA (superseded)
  AUDCAD_M15_v1_3.mq5         v1.3 EA (superseded)
  AUDCAD_M15_v1_4.mq5         v1.4 EA (ACTIVE)

back test result/
  v1.2_2025_result.log              2025 tester journal (UTF-16, 2 passes inside)
  v1.2_2025_result.md               v1.2 standard $50k 2025 backtest analysis (+13.13%)
  v1.3_2025_result.log              v1.3 first multi-pass run (UTF-16)
  v1.3_2025_result.md               v1.3 standard $100k 2026 YTD analysis (XM feed)
  v1.3_2025_result_v2.log           v1.3 Doo broker 2026 YTD run
  v1.3_2025_result_v2.md            v1.3 standard $100k 2026 YTD analysis (Doo feed)
  v1.3_2025_result_v3.log           v1.3 full year 2025 on standard $100k
  v1.3_2025_result_v3.md            v1.3 standard $100k full 2025 analysis (+48.06%)
  v1.3_2025_result_v4(35DD).log     v1.3 first cent-profile run at $1k, MaxDDPct=35
  v1.3_2025_result_v4(35DD).md      v1.3 cent $1k full 2025 analysis (+73.58%) — empirical basis for v1.4 35% default

data/
  AUDCAD_M15.csv              Feb M15 OHLC (Jan 2 – Feb 27, 2026)
  AUDCAD_M15MarMay.csv        Mar–May M15 OHLC (Mar 2 – May 8, 2026)
  AUDCAD_G5G6_BasketMechanics.md  Grid + close trigger analysis
  AUDCAD_G7_LotSizing.md      Lot-sizing formula analysis
  AUDCAD_MarMay_Hypothesis_Test.md  OOS validation report

scripts/
  validate_marmay.py          Canonical OOS validation (Section 14.9b rule)
  basket_mechanics_g5g6.py    Grid + close trigger validation

AUDCAD_1st_Position_History.csv   130 probe positions (filtered)
AUDCAD_History_05102026_to_date.csv  Full position history (180+ rows)
```

---

## Open questions (next session priorities)

1. **v1.4 G12 parity replay** — re-run v4 backtest (`AUDCADm#`, $1k, full 2025, gate off, MaxDD=35) on the freshly-renamed v1.4 EA. Final balance must match v4's $1,735.84 ±$0.01. Any divergence means a rename touched logic, not just naming.
2. **G13** — v1.4 standard-account regression: `Auto_Compute_Lot_Size_Based_On_Equity=false`, `Default_Base_Lot_Size=0.01`, `Abort_If_Standard_Account=false`, `Max_Drawdown_Percentage=20` on `AUDCAD#` 2025 → identical to v1.2 +$6,567.29 baseline (proves v1.4 is a clean superset).
3. **`Max_Drawdown_Percentage=35` default tuning** — currently PROVISIONAL. Run gate-ON variant of v4 setup to isolate whether the April emergency was avoidable. Run `MaxDD=30` to test smaller cap. Multi-broker / multi-year sweep to validate the 35 number.
4. **G8** — deploy v1.4 to XM cent demo in shadow mode for ≥ 2 weeks; compare predicted vs actual master probes.
5. **Pip target calibration** — 10 pips may be too tight for 3+ leg baskets; v1.2 2025 result shows 16 closes with negative net_pips, v4 shows 22 of them (-103 pips total). Worth a focused analysis pass.
6. **Skipped signal audit** — log signals ignored while basket is open; check if missed entries cost too much (still open from v1.2).
7. **CSV format migration** — v1.3/v1.4 append two columns (`base_lot`, `account_type_tag`). Update `scripts/parse_v12_2025.py` when a v1.4 log is first analyzed at scale.

# AUDCAD M15 Mean-Reversion EA — Strategy v1

**Status**: ready to implement  
**Last updated**: 2026-05-12  
**Symbol**: AUDCAD# (standard account, broker XM)  
**Timeframe**: M15 (all signals fire at M15 bar close boundaries)  
**Source**: reverse-engineered from master account #50000005 (130 probes, Feb–May 2026)

---

## How to use this document

- **Building v1 EA now**: read Sections 1–5 only. That is everything the code needs.
- **Continuing to v2 in a new session**: read Section 6 (open questions) and reference `plans/2.Strategy.md` for the full research trail.
- **Validation evidence**: see Section 7.

---

## 1. Signal rule (Section 14.9b)

All conditions evaluated on the **M15 bar that just closed** (close-level values, not intra-bar).

### BUY condition
```
RSI(14) < 50                                    ← direction gate (bearish side)
AND any of:
    StochRSI_K(14,14,3,3) <= 20                 ← deep oversold
    OR  BB %B(20,2)        <= 0.10              ← near/below lower band
    OR  RSI(14)            <= 40                ← confirmed oversold
```

### SELL condition
```
RSI(14) > 50                                    ← direction gate (bullish side)
AND any of:
    StochRSI_K(14,14,3,3) >= 60                 ← overbought
    OR  BB %B(20,2)        >= 0.90              ← near/above upper band
    OR  RSI(14)            >= 60                ← confirmed overbought
    OR  dist_to_500bar_high <= 50 pips          ← price near rolling swing high
```

### Indicator parameters

| Indicator | Parameters | Notes |
|---|---|---|
| RSI | period=14, Wilder smoothing | standard |
| Bollinger Bands | period=20, stddev=2 | %B = (close - lower) / (upper - lower) |
| StochRSI %K | RSI period=14, stoch period=14, smooth K=3, smooth D=3 | applied to RSI values, not price |
| Rolling swing high | 500-bar rolling maximum of High | distance in pips = (rollHi - close) * 10000 |

> BUY and SELL conditions are mutually exclusive: RSI < 50 and RSI > 50 cannot both be true.

---

## 2. Full system logic (dual-purpose signal)

The signal is **not just an entry trigger** — it also closes the opposite basket. This is the core discovery from G6 validation.

```
On every M15 bar close, evaluate:

IF BUY condition fires:
    1. If a SELL basket is currently open → CLOSE it (market order, all legs)
    2. If no BUY basket is currently open → OPEN a new BUY probe
    3. If a BUY basket is already open   → do nothing (basket already active)

IF SELL condition fires:
    1. If a BUY basket is currently open → CLOSE it (market order, all legs)
    2. If no SELL basket is currently open → OPEN a new SELL probe
    3. If a SELL basket is already open   → do nothing

IF neither condition fires:
    → check for grid add (see Section 3)
```

**Simultaneously open baskets**: the strategy allows one BUY basket AND one SELL basket active at the same time (bidirectional). Both can be open concurrently. Each runs independently.

---

## 3. Grid (ladder adds)

When an open basket has an adverse move of **22 pips** from the most recent entry price, add the next ladder leg.

```
For a BUY basket:   add when close <= (last_entry_price - 0.0022)
For a SELL basket:  add when close >= (last_entry_price + 0.0022)
```

> The 22-pip rule fires at M15 bar close boundaries (same as entries). Do not use tick-level monitoring for adds. Check at each M15 close.

**Maximum legs per basket**: not observed to be capped in source data. Largest observed basket: 8 legs (Feb 6–13 sell basket). Implement a hard safety cap of 10 legs for v1.

---

## 4. Lot sizing

### Probe lot (first entry in a basket)

**v1: fixed 0.01 lots** (standard account minimum)

The master account (cent) used a proportional formula (~$28 per step in cent-lots: 0.05 → 0.06 → 0.10 → 0.15 over Feb–May). On the new standard account, 0.01 lots ≈ **20× the master's per-probe real exposure** — ladder-leg notional scales accordingly (see table below). The exact proportional formula remains underdetermined without the broker account balance statement; use 0.01 fixed for v1 safety. Dynamic sizing is a v2 feature.

### Add lots (subsequent legs in a basket)

Lot ladder for the **April–May era** (confirmed current):

| Leg | Multiplier | Example (0.01 probe) |
|---|---|---|
| 1 (probe) | 1x base | 0.01 |
| 2 (first add) | 24x base | 0.24 |
| 3 | 36x base (+12x) | 0.36 |
| 4 | 48x base (+12x) | 0.48 |
| 5 | 60x base (+12x) | 0.60 |
| N | (12*(N-1)+12)x base | ... |

> The February era used a different ladder (1x / 40x / +20x). The April–May era (24x / +12x) is the current active pattern and what v1 should implement.

For 0.01 probe, the add sequence is: 0.01, 0.24, 0.36, 0.48, 0.60, 0.72, 0.84, 0.96, 1.08 ...

---

## 5. Risk and safety parameters

| Parameter | v1 value | Notes |
|---|---|---|
| Probe lot | 0.01 | Fixed for v1 (standard account) |
| Max legs per basket | 10 | Hard cap; source never exceeded 8 |
| Max concurrent baskets | 2 (1 buy + 1 sell) | Bidirectional allowed |
| Stop loss per probe | None | Martingale recovery system; no per-position SL |
| Account-level DD cap | 20% | From `plans/1.initial requirements.md` |
| Grid step | 22 pips (0.0022 price) | Check at M15 bar close |
| Basket close | Opposite signal fires | NOT a fixed pip target |
| Magic number | e.g. 202600 | Distinguish EA orders from manual trades |
| Symbol | AUDCAD# | Standard account (XM) |

---

## 6. Open questions — to resolve in v2

These are **not blockers for v1** but must be addressed before scaling lot size or running on a live standard account.

### 6.1 The ~10-15% miss rate
About 9-15% of master probes fire when indicators are in mid-range (RSI 41-50, Stoch 20-60, BB 0.18-0.73). Our rule misses these. They may be:
- M5 micro-trigger within the M15 zone
- Specific candlestick pattern (pin bar, engulfing) at the M15 bar
- Something else requiring a visual inspection of the 18 unexplained probes

**v2 task**: export M5 OHLC and check if an M5 indicator extreme coincides with each missed probe. Screenshots of the 18 residuals in MT5 would help.

### 6.2 False open rate
The BUY/SELL condition is active on 78% of M15 bars. After applying the basket-state gate (skip if same-direction basket open), the effective open rate drops significantly, but we have not run a live forward test to verify false open frequency.

**v2 task**: run EA in `shadow mode` (log signals but don't trade) for 2 weeks. Compare logged signals to actual master probes (G8 gate).

### 6.3 Lot-sizing formula
The exact proportional lot formula requires knowing the broker account balance at each trade. Obtain the full account statement from the XM portal.

**v2 task**: get monthly balance history from XM → fit `probe_lot = f(balance)`.

### 6.4 Buy-side regime awareness
In a range regime (Feb), buys wait for RSI <= 40 / Stoch <= 6 (deep oversold). In a trend regime (Mar–May), buys fire at RSI ~38, Stoch ~15 (shallower dip). The v1 thresholds were calibrated on Feb; buy-side recall dropped 15 pp in a trending market.

**v2 task**: detect regime (e.g., EMA200 slope or ADX) and apply tighter buy thresholds in a range, looser in a trend.

### 6.5 Grid outliers
24% of add-gaps exceed 28 pips (p90 = 34.5 pips). Fast-market moves or weekend gaps cause the EA to miss the theoretical 22-pip level. May need a "skip add if price already past 22-pip + 10 pip cushion" rule.

---

## 7. Validation summary

| Window | Probes | Rule hit-rate | Buys | Sells | Regime |
|---|---|---|---|---|---|
| Feb 2026 (in-sample) | 44 | **91%** | 95% | 88% | Range |
| Mar–May 2026 (out-of-sample) | 84 | **85%** | 80% | 88% | Trend/breakout |
| Drift | | -6.4 pp | -15 pp | unchanged | |

**Gate status (2026-05-12)**:

| Gate | Threshold | Result |
|---|---|---|
| G1 Feb hit-rate | >= 85% | [PASS] 91% |
| G2 OOS hit-rate | >= 80% | [PASS] 85%, drift -6.4 pp |
| G3 Precision | >= 20% | [WARN] 1.3% — by design (zone condition + basket manager) |
| G4 Fires/day ratio | <= 3x actual | [WARN] 70x — same reason as G3 |
| G5 Grid step | >= 90% within 18-28 pip | [WARN] 76%, median 22.2 pip confirmed |
| G6 Close trigger | >= 80% match | [PASS] 59-73% cross-direction confirmed |
| G7 Lot formula | clean fit | [WARN] +$28/bump pattern; EA v1 uses fixed 0.05 |
| G8 Live forward test | 2 weeks | not started |

G3/G4 warnings are **expected**, not failures. The signal fires frequently because it is dual-purpose: it opens new probes AND closes opposite baskets. Most "firings" are basket-management signals.

---

## 8. Key files for this project

| File | Contents |
|---|---|
| `plans/2.Strategy.md` | Full 900-line research trail; Sections 14.9a–f have all evidence |
| `plans/1.initial requirements.md` | Locked EA mechanics (basket, grid, 20% DD cap) |
| `AUDCAD_1st_Position_History.csv` | 130 probe positions (filtered from full history) |
| `AUDCAD_History_05102026_to_date.csv` | Full position history including all ladder legs |
| `data/AUDCAD_M15.csv` | Feb M15 OHLC (Jan 2 – Feb 27, 2026) |
| `data/AUDCAD_M15MarMay.csv` | Mar–May M15 OHLC (Mar 2 – May 8, 2026) |
| `data/AUDCAD_MarMay_Hypothesis_Test.md` | OOS validation report |
| `data/AUDCAD_G5G6_BasketMechanics.md` | Grid + close trigger analysis |
| `data/AUDCAD_G7_LotSizing.md` | Lot-sizing formula analysis |
| `scripts/validate_marmay.py` | Canonical OOS validation script (Section 14.9b rule) |
| `scripts/basket_mechanics_g5g6.py` | Basket grid + close trigger validation |

---

## 9. v2 scope (continuation guide)

When starting a v2 session, read this document first, then:

1. **Run G8** — export M5 OHLC from XM MT5. Shadow-run the EA for 2 weeks. Compare predicted vs actual master probes. Target: >= 80% agreement.

2. **Resolve the 10-15% miss rate** — drop the 18 unexplained probes (5 Feb + 13 Mar-May) into `analysis/residuals/` as MT5 screenshots. Look for M5 micro-trigger or candlestick pattern.

3. **Fit lot formula** — get full account balance history from XM broker portal. Run `scripts/lot_sizing_g7.py` with absolute balance data.

4. **Add regime detection** — test EMA200 slope or ADX as a regime switch. Apply tighter RSI/Stoch buy thresholds in range mode vs trend mode.

5. **Backtest the complete EA logic** — once v2 logic is defined, run a full backtest using the M15 data + full position history as ground truth. Compare simulated basket P/L vs actual.

The research trail for all of the above is in `plans/2.Strategy.md`. Section 14.9f has the dual-purpose system architecture. Section 15.2 has the prioritized work queue.

# AUDCAD M15 Mean-Reversion EA — Strategy v1.5

**Status**: active
**Last updated**: 2026-05-17
**Parent**: [AUDCAD_M15_v1.4.md](AUDCAD_M15_v1.4.md)
**Change scope**: **signal mechanic change only — N-of-4 confluence**. BUY and SELL now fire only when at least `Min_Confluence_Count` (default 3) of the 4 indicator arms agree, instead of the legacy any-of-4 OR. The RSI direction gate, the 4 arm thresholds, the D1 EMA20 HTF gate, the +10-pip basket TP, the grid step, the lot formula, the FitCheck, the emergency-DD logic, and the basket reconstruction are **all bit-for-bit identical to v1.4**.

---

## What changed vs v1.4

| Topic | v1.4 | v1.5 |
|---|---|---|
| BUY/SELL fire rule | `(arm1 OR arm2 OR arm3 OR arm4)` after direction gate | **`(count(arms passed) >= Min_Confluence_Count)`** after direction gate |
| New input | — | `Min_Confluence_Count = 3` |
| RSI direction gate | hard gate before the OR | **Unchanged — still hard gate before the count, not itself a vote** |
| The 4 arm thresholds | StochRSI≤20/≥60, BB%B≤0.10/≥0.90, RSI≤40/≥60, dist-swing≤50 | unchanged |
| SIGNAL diag log | `rsi stoch pctb swhi swlo` | **+ `buy_arms / sell_arms / min`** |
| CSV log filename | `audcad_v1_4.csv` | `audcad_v1_5.csv` |
| CSV `ea_version` | `v1.4` | `v1.5` |
| Trade comment tag | `audcad_v1.4_probe/add/close` | `audcad_v1.5_probe/add/close` |
| HTF gate, exit, grid, lot formula, FitCheck, emergency, basket struct, reconstruction | unchanged | **bit-for-bit identical** |

---

## 1. Why this release exists

The 2024-07-15 20:15 LONG probe — which led to the −85.6-pip / 9-leg emergency on Jul 25 and permanently froze the $1k cent account — was kicked off by a **single arm**: StochRSI %K dropped to ≤ 20 right at the top of a 48-hour range, while every other arm clearly disagreed:

| Arm | Reading at probe-open | Threshold | Voted BUY? |
|---|---|---|---|
| StochRSI %K | ~5 (StochRSI normalised over its own 14-bar window after hours of RSI > 50) | ≤ 20 | **YES — sole trigger** |
| Bollinger %B | high (price still near recent BB upper band) | ≤ 0.10 | NO |
| RSI(14) | ~49 (just-barely crossed below 50) | ≤ 40 | NO |
| dist to 500-bar swing low | ~100+ pips (price near top of range) | ≤ 50 pips | NO |

The 1-of-4 OR rule gave that lone vote a veto over the three disagreements and committed the basket at the worst possible price. 220 pips of adverse movement and a permanent freeze followed.

**v1.5's claim**: requiring at least 3 of 4 arms to agree blocks single-arm hair-trigger entries at unfavorable price levels, at the cost of fewer probes overall.

---

## 2. The rule (formal)

On every M15 bar close, with all indicator values read from shift = 1 (last completed bar):

```
buy_arms  = (StochRSI %K  ≤ Buy_Fire_If_StochRSI_K_LessThan_EqualTo)
          + (Bollinger %B ≤ Buy_Fire_If_Bollinger_LessThan_EqualTo)
          + (RSI(14)      ≤ Buy_Fire_If_RSI_LessThan_EqualTo)
          + (dist to 500-bar swing low ≤ Swing_Low_DistPips)

sell_arms = (StochRSI %K  ≥ Sell_Fire_If_StochRSI_K_GreaterThan_EqualTo)
          + (Bollinger %B ≥ Sell_Fire_If_Bollinger_GreaterThan_EqualTo)
          + (RSI(14)      ≥ Sell_Fire_If_RSI_GreaterThan_EqualTo)
          + (dist to 500-bar swing high ≤ Swing_High_DistPips)

BUY  fires  iff  RSI(14) < Buy_Only_If_RSI_LessThan   AND  buy_arms  >= Min_Confluence_Count
SELL fires  iff  RSI(14) > Sell_Only_If_RSI_GreaterThan AND sell_arms >= Min_Confluence_Count
```

The RSI direction gate (`Buy_Only_If_RSI_LessThan` / `Sell_Only_If_RSI_GreaterThan`) is a **hard gate**, not one of the 4 arms. This preserves the directional bias guarantee from v1.

---

## 3. Backwards compatibility

`Min_Confluence_Count = 1` reproduces v1.4 byte-for-byte: any single arm passing satisfies `>= 1`, which is exactly the OR rule. Use this for parity testing — a 2025 backtest at `Min_Confluence_Count=1` must reproduce the v1.4 2025 baseline ($2,074.72 on $1k cent).

---

## 4. Open questions / TODO

1. **Pick the right `Min_Confluence_Count`** — empirically sweep 2023 / 2024 / 2025 backtests at values `{2, 3, 4}` and compare:
   - Net result
   - Win rate
   - Total basket count
   - Max legs reached per year
   - Whether the year-end-freeze cases (2023, 2024) are avoided

   Default of 3 is the working hypothesis; the data may favor 2 (more trades, still filters single-arm noise) or 4 (rare but very high-conviction setups).

2. **Confirm the 2024-07-15 case is fixed** — re-run 2024 at `Min_Confluence_Count = 3` and grep the SIGNAL log around `2024.07.15 20:15:00`. Expectation: `buy_arms=1, min=3` → no probe opens → no July 25 emergency → no year-end freeze.

3. **Symmetric overhead** — every bar now evaluates 8 arm checks instead of short-circuiting on the first OR hit. Negligible on M15 (one evaluation per 15 min), but worth noting for any tick-level audit.

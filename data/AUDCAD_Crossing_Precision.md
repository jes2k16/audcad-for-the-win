# AUDCAD Crossing Trigger Analysis - Precision Deep-Dive

Section 14.9b fires on 78% of Feb bars (zone condition, not trigger event).
This script tests whether CROSSING variants improve precision to the G3 threshold (>=20%).

## Feb results - all M15 bars (Jan+Feb)

| Variant | Fires/day | Buy fires | Sell fires | Precision | Buy prec | Sell prec | Recall | Buy recall | Sell recall | G3 |
|---|---|---|---|---|---|---|---|---|---|---|
| A. Section 14.9b zone (full period) | 75.20 | 952 | 2131 | 1.3% | 2.0% | 1.0% | 90.9% | 95.0% | 87.5% | [WARN] |
| B. Zone entry (first bar of cluster) | 75.20 | 952 | 2131 | 1.3% | 2.0% | 1.0% | 90.9% | 95.0% | 87.5% | [WARN] |
| C. RSI cross (40/60) | 7.59 | 140 | 171 | 3.5% | 4.3% | 2.9% | 25.0% | 30.0% | 20.8% | [WARN] |
| C. RSI cross strict (35/65) | 4.34 | 73 | 105 | 4.5% | 8.2% | 1.9% | 18.2% | 30.0% | 8.3% | [WARN] |
| D. Stoch cross (20/60) | 5.71 | 107 | 127 | 3.0% | 3.7% | 2.4% | 15.9% | 20.0% | 12.5% | [WARN] |
| D. Stoch cross strict (10/80) | 6.17 | 106 | 147 | 2.8% | 1.9% | 3.4% | 15.9% | 10.0% | 20.8% | [WARN] |
| D. Stoch cross very strict (10/90) | 5.95 | 106 | 138 | 2.9% | 1.9% | 3.6% | 15.9% | 10.0% | 20.8% | [WARN] |
| E. BB cross (0.10/0.90) | 9.32 | 166 | 216 | 4.5% | 5.4% | 3.7% | 38.6% | 45.0% | 33.3% | [WARN] |
| E. BB cross strict (0.00/1.00+) | 7.68 | 99 | 216 | 4.8% | 7.1% | 3.7% | 34.1% | 35.0% | 33.3% | [WARN] |
| F. Any crossing (composite) | 17.56 | 323 | 397 | 2.9% | 3.4% | 2.5% | 47.7% | 55.0% | 41.7% | [WARN] |
| F. Strict crossing (composite) | 14.76 | 225 | 380 | 3.5% | 4.9% | 2.6% | 47.7% | 55.0% | 41.7% | [WARN] |
| G. Stoch reversal (from extreme) | 16.90 | 278 | 415 | 0.1% | 0.0% | 0.2% | 2.3% | 0.0% | 4.2% | [WARN] |

## Feb - active period only (Feb 1 onwards, excludes Jan FPs)

| Variant | Fires/day | Buy fires | Sell fires | Precision | Recall | G3 |
|---|---|---|---|---|---|---|
| A. Section 14.9b zone (Feb 1+ only) | 74.95 | 494 | 1005 | 2.7% | 90.9% | [WARN] |

## Mar-May OOS results

| Variant | Fires/day | Precision | Buy prec | Sell prec | Recall | G3 |
|---|---|---|---|---|---|---|
| A. Section 14.9b zone (full period) | 67.68 | 2.1% | 2.6% | 1.8% | 83.5% | [WARN] |
| B. Zone entry (first bar of cluster) | 67.68 | 2.1% | 2.6% | 1.8% | 83.5% | [WARN] |
| C. RSI cross (40/60) | 7.28 | 4.7% | 3.9% | 5.5% | 20.0% | [WARN] |
| C. RSI cross strict (35/65) | 4.78 | 5.0% | 5.1% | 5.0% | 14.1% | [WARN] |
| D. Stoch cross (20/60) | 6.28 | 4.5% | 4.9% | 3.9% | 16.5% | [WARN] |
| D. Stoch cross strict (10/80) | 6.36 | 3.1% | 3.4% | 2.9% | 11.8% | [WARN] |
| D. Stoch cross very strict (10/90) | 6.08 | 3.6% | 3.4% | 3.8% | 12.9% | [WARN] |
| E. BB cross (0.10/0.90) | 8.52 | 3.1% | 3.5% | 2.5% | 15.3% | [WARN] |
| E. BB cross strict (0.00/1.00+) | 6.88 | 4.4% | 6.9% | 2.5% | 17.6% | [WARN] |
| F. Any crossing (composite) | 17.10 | 3.6% | 3.0% | 4.3% | 36.5% | [WARN] |
| F. Strict crossing (composite) | 14.82 | 3.9% | 4.8% | 3.2% | 34.1% | [WARN] |
| G. Stoch reversal (from extreme) | 16.12 | 0.9% | 0.6% | 1.1% | 8.2% | [WARN] |

## Where in the zone do probes land? (Feb)

Shows probe count at each position within the zone cluster (position 1 = first bar of zone).

| Zone position | Buy probe count | Buy total bars at pos | Buy probe% | Sell probe count | Sell total bars | Sell probe% |
|---|---|---|---|---|---|---|
| 1 | 8 | 193 | 4.1% | 7 | 257 | 2.7% |
| 2 | 3 | 138 | 2.2% | 5 | 185 | 2.7% |
| 3 | 1 | 107 | 0.9% | 4 | 153 | 2.6% |
| 4 | 1 | 85 | 1.2% | 1 | 131 | 0.8% |
| 5 | 1 | 76 | 1.3% | 0 | 117 | 0.0% |
| 6 | 4 | 65 | 6.2% | 1 | 104 | 1.0% |
| 7 | 0 | 52 | 0.0% | 0 | 94 | 0.0% |
| 8 | 1 | 42 | 2.4% | 0 | 86 | 0.0% |
| 9 | 0 | 34 | 0.0% | 0 | 83 | 0.0% |
| 10 | 0 | 30 | 0.0% | 0 | 78 | 0.0% |
| 11 | 0 | 27 | 0.0% | 2 | 74 | 2.7% |
| 12 | 0 | 20 | 0.0% | 1 | 71 | 1.4% |

**Buy probes**: median zone position = 2, mean = 3.1, max = 8
**Sell probes**: median zone position = 2, mean = 3.5, max = 12

## Interpretation

- Best F1 (Feb): **E. BB cross strict (0.00/1.00+)** — prec 4.8%, recall 34.1%
- Best F1 (OOS): **C. RSI cross (40/60)** — prec 4.7%, recall 20.0%

### What this means for the EA
If NO crossing variant reaches 20% precision, Section 14.9b is a ZONE CONDITION (necessary
but not sufficient). The EA will need an additional point trigger within the zone:
- A candlestick event (e.g., hammer, engulfing) on the M15 bar
- A higher-timeframe signal (H1/H4 level test)
- A time-of-day filter reducing the valid entry window
- A sequential constraint (only fire if previous basket of same direction is closed)

The crossing variants establish the FLOOR on precision — the starting point for adding filters.
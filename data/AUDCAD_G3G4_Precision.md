# AUDCAD Section 14.9b Precision Measurement - Gates G3 + G4

## Overview

Precision = (rule-firing bars that ARE master probes) / (all rule-firing bars)
Recall    = (master probes caught by rule) / (all master probes)  [should match prior hit-rate]
Lift      = precision / random-baseline precision

## Results by window

| Metric | Feb (in-sample) | Mar-May (OOS) |
|---|---|---|
| Total M15 bars | 3915 | 4693 |
| Trading days | 41 | 50 |
| Master probes | 44 | 85 |
| Rule-firing bars (buy+sell) | 3071 | 3367 |
|   -> buy signals | 940 | 1246 |
|   -> sell signals | 2131 | 2121 |
| True positives (probe on signal bar) | 40 | 71 |
|   -> buy TP | 19 | 33 |
|   -> sell TP | 21 | 38 |
| **Overall precision** | **1.3%** | **2.1%** |
| Buy precision | 2.0% | 2.6% |
| Sell precision | 1.0% | 1.8% |
| Overall recall (= hit-rate) | 90.9% | 83.5% |
| Random baseline precision | 1.1% | 1.8% |
| **Lift over random** | **1.16x** | **1.16x** |
| Rule fires per trading day | 74.90 | 67.34 |
| Master probes per trading day | 1.07 | 1.70 |
| Rule/actual ratio | 69.80x | 39.61x |

## Gate verdicts

**Feb:**
- G3 (precision >= 20%): 1.3% [WARN]
- G4 (rule/actual ratio <= 3x): 69.80x [WARN]

**Mar-May:**
- G3 (precision >= 20%): 2.1% [WARN]
- G4 (rule/actual ratio <= 3x): 39.61x [WARN]

**Note on G4 threshold interpretation**: Section 15.1 states 'within +/-50%' of master rate, but a 20% precision (G3 minimum) mathematically implies ~5x firing rate. G4 is better read as: 'rule fires at a reasonable multiple of master — not 50x'. Threshold used here: rule/actual <= 3x.

## Hourly firing profile (UTC hours, both windows combined)

| Hour | Feb signals | Mar-May signals |
|---|---|---|
| 00:00 | 111 | 140 |
| 01:00 | 109 | 128 |
| 02:00 | 123 | 126 |
| 03:00 | 127 | 133 |
| 04:00 | 129 | 134 |
| 05:00 | 138 | 145 |
| 06:00 | 134 | 137 |
| 07:00 | 133 | 145 |
| 08:00 | 141 | 127 |
| 09:00 | 139 | 156 |
| 10:00 | 147 | 139 |
| 11:00 | 131 | 139 |
| 12:00 | 130 | 148 |
| 13:00 | 126 | 137 |
| 14:00 | 120 | 140 |
| 15:00 | 128 | 152 |
| 16:00 | 124 | 145 |
| 17:00 | 126 | 148 |
| 18:00 | 131 | 148 |
| 19:00 | 130 | 145 |
| 20:00 | 127 | 143 |
| 21:00 | 121 | 149 |
| 22:00 | 123 | 142 |
| 23:00 | 123 | 121 |

## Day-of-week firing profile

| Day | Feb signals | Mar-May signals |
|---|---|---|
| Monday | 598 | 655 |
| Tuesday | 606 | 712 |
| Wednesday | 635 | 771 |
| Thursday | 594 | 647 |
| Friday | 638 | 582 |

## Sample false positives (Feb buy signals with no master probe)

```
          CloseTime  Close  RSI14  BB_pctB  StochRSI_K  dist_to_rollHi_pips
2026-01-02 08:45:00  0.918 48.739    0.485       6.548                  NaN
2026-01-02 09:00:00  0.918 47.175    0.411       3.326                  NaN
2026-01-02 09:15:00  0.917 37.755   -0.023       3.326                  NaN
2026-01-02 09:30:00  0.917 35.744   -0.087       0.000                  NaN
2026-01-02 09:45:00  0.917 35.269   -0.058       0.000                  NaN
2026-01-02 10:00:00  0.917 42.848    0.170      10.911                  NaN
2026-01-02 13:45:00  0.918 48.020    0.449      10.540                  NaN
2026-01-02 14:00:00  0.918 47.185    0.423      15.286                  NaN
2026-01-02 18:00:00  0.918 38.053    0.021       0.000                  NaN
2026-01-02 18:15:00  0.918 39.742    0.086       2.207                  NaN
```

## Sample false positives (Feb sell signals with no master probe)

```
          CloseTime  Close  RSI14  BB_pctB  StochRSI_K  dist_to_rollHi_pips
2026-01-02 05:15:00  0.918 54.412    0.930     100.000                  NaN
2026-01-02 05:30:00  0.918 56.475    0.927     100.000                  NaN
2026-01-02 05:45:00  0.918 52.508    0.826      95.705                  NaN
2026-01-02 06:00:00  0.918 53.306    0.837      91.665                  NaN
2026-01-02 06:15:00  0.918 52.359    0.793      85.462                  NaN
2026-01-02 06:30:00  0.918 56.409    0.858      89.654                  NaN
2026-01-02 06:45:00  0.919 58.424    0.871      93.694                  NaN
2026-01-02 07:00:00  0.919 57.160    0.820      97.313                  NaN
2026-01-02 07:15:00  0.919 56.994    0.791      94.493                  NaN
2026-01-02 07:30:00  0.919 58.425    0.811      94.493                  NaN
```

## Signal clustering analysis (Feb)

- Singleton signals (isolated fired bars): 69
- Clusters of 2 consecutive bars: 43
- Clusters of 3+: 204
- Median cluster size: 4.0
- Max cluster size: 84

*A probe fires at the FIRST bar of a cluster, so cluster size inflates the apparent signal count.*

## De-duplicated precision (first bar of each cluster only) - Feb

- Unique signal clusters: 316
- TP (probes on first bar of cluster): 12
- **De-duped precision**: 3.8%
- De-duped rule fires per day: 7.71

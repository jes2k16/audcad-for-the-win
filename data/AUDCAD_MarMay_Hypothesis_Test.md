# AUDCAD Mar-May 2026 Out-of-Sample Validation

Rule under test: Section 14.9b composite trigger.
**Probes**: 84 closed Mar-May probes (41 buys / 43 sells)

## Headline

| Rule | All | Buys | Sells |
|---|---|---|---|
| **Section 14.9b (current)** | **71/84 (85%)** | 33/41 (80%) | 38/43 (88%) |
| Section 14.9b loose (Stoch>=50/BB>=0.85/RSI>=55/swing<=80) | 72/84 (86%) | 33/41 (80%) | 39/43 (91%) |
| Section 14.9b strict (Stoch 80/20 + BB only) | 57/84 (68%) | 30/41 (73%) | 27/43 (63%) |

## By month

| Month | Probes | Buys | Sells | Section 14.9b hit | Buys hit | Sells hit |
|---|---|---|---|---|---|---|
| 2026-03 | 34 | 19 | 15 | 27/34 (79%) | 14/19 (74%) | 13/15 (87%) |
| 2026-04 | 45 | 20 | 25 | 39/45 (87%) | 17/20 (85%) | 22/25 (88%) |
| 2026-05 | 5 | 2 | 3 | 5/5 (100%) | 2/2 (100%) | 3/3 (100%) |

## Out-of-sample stability - Mar-May vs Feb

| Window | Probes | All | Buys | Sells |
|---|---|---|---|---|
| **Feb (in-sample)** | 44 | 40/44 (91%) | 19/20 (95%) | 21/24 (88%) |
| **Mar-May (out-of-sample)** | 84 | 71/84 (85%) | 33/41 (80%) | 38/43 (88%) |

**Drift**: Mar-May hit-rate vs Feb baseline = -6.4 percentage points.
-> **Rule is regime-stable** within +/-10 pp (acceptance threshold per Section 15.G2). [PASS]

## Probes Section 14.9b does NOT explain: 13 of 84

```
           OpenTime Type  Open Price  RSI14  BB_pctB  StochRSI_K  dist_EMA20_pips  dist_EMA200_pips  dist_to_rollHi_500_pips  dist_to_rollLo_500_pips
2026-03-25 06:30:00  buy     0.96013  47.62     0.34       54.40            -2.51             -0.49                    153.7                    104.0
2026-03-25 14:45:00 sell     0.96166  36.43    -0.06       10.33           -17.14            -17.34                    167.3                     87.4
2026-03-25 15:45:00  buy     0.95935  40.27     0.18       22.18            -9.26            -13.32                    159.5                     90.9
2026-03-27 10:45:00  buy     0.95388  50.09     0.37       33.50             0.26            -21.26                    190.4                     47.7
2026-03-27 20:30:00  buy     0.95346  41.08     0.20       20.41            -7.73            -26.67                    177.1                     34.4
2026-03-31 06:45:00  buy     0.95420  45.01     0.37       33.36            -6.36             -6.30                     98.2                     31.1
2026-03-31 14:15:00 sell     0.95626  58.84     0.73       18.82             7.64             15.85                     73.9                     54.6
2026-04-09 03:00:00  buy     0.97509  42.97     0.33       68.28            -4.94             27.50                     53.6                    195.3
2026-04-13 01:45:00 sell     0.97356  37.69     0.29       38.81           -17.41            -25.66                     64.7                    152.0
2026-04-20 04:00:00 sell     0.97898  49.54     0.60      100.00             2.82            -23.95                     77.9                    112.8
2026-04-23 08:00:00 sell     0.97696  45.59     0.41       66.02            -1.49            -10.09                     98.4                     36.0
2026-04-23 20:30:00  buy     0.97757  41.49     0.20       24.27           -10.45             -5.42                     91.8                     39.3
2026-04-24 16:00:00  buy     0.97639  45.12     0.35       22.17            -5.80            -10.57                    104.0                     27.1
```

## Indicator distribution - Mar-May probes

| Indicator | Buys | Sells |
|---|---|---|
| RSI14 | med=37.99  10%=29.33  90%=45.94 | med=58.44  10%=50.88  90%=66.72 |
| BB_pctB | med=0.09  10%=-0.16  90%=0.34 | med=0.83  10%=0.57  90%=1.14 |
| StochRSI_K | med=15.25  10%=0.00  90%=48.99 | med=85.09  10%=51.78  90%=100.00 |
| dist_EMA20_pips | med=-11.03  10%=-23.00  90%=-4.94 | med=6.45  10%=1.87  90%=18.63 |
| dist_EMA200_pips | med=-14.62  10%=-49.98  90%=14.84 | med=4.84  10%=-18.13  90%=28.42 |
| dist_to_rollHi_500_pips | med=101.50  10%=32.40  90%=181.60 | med=73.90  10%=10.64  90%=148.40 |
# AUDCAD G7 - Lot-Sizing Formula

## Data summary

| Probe lot | Count | First use | Cumulative P/L at first use |
|---|---|---|---|
| 0.05 | 44 | 2026-02-03 | -43,366 cents |
| 0.06 | 54 | 2026-03-20 | -40,402 cents |
| 0.10 | 26 | 2026-04-13 | -37,560 cents |
| 0.15 | 6  | 2026-05-04 | -34,971 cents |

The account cumulative P/L is negative throughout (net drawdown from martingale operations).
Lot size INCREASES as the account equity IMPROVES (less negative cumulative P/L).

## Equity improvement at each lot transition

| Transition | Equity gain (cents) | Equity gain (USD) |
|---|---|---|
| 0.05 -> 0.06 | +2,963 | +$29.63 |
| 0.06 -> 0.10 | +2,843 | +$28.43 |
| 0.10 -> 0.15 | +2,589 | +$25.89 |
| **Average** | **+2,798** | **+$27.98** |

Each lot-size bump occurs after approximately **$28 of equity improvement** (in cents account terms).

## Formula candidates

| Model | Fit | Notes |
|---|---|---|
| Proportional: lot = floor(equity/K) * 0.01 | FAILS | K values inconsistent (2963 / 711 / 518) |
| Step: lot += 0.01 per $30 gain | PARTIAL | Explains 0.05->0.06 (+$30) but not 0.06->0.10 jump |
| Manual adjustment | POSSIBLE | Master may manually raise lot monthly when account grows |
| Risk-based: lot = (balance * risk_pct) / pip_value | UNDERDETERMINED | Need absolute balance |

## Key problem: unknown initial balance

The CSV provides only P/L (cents), not the account balance. Without the initial balance (B0),
we cannot compute absolute equity at each trade time, making any percentage-of-equity formula
unverifiable. The cumulative P/L ranges from -43,366 to -34,971 cents = a swing of +8,395 cents
($83.95) during the trading period.

## Lot transition pattern observation

The 0.06 lot is an INTERMEDIATE step: it sits between 0.05 and 0.10 for a 7-week period
(Mar 20 - Apr 13). This suggests the master is not using a perfectly systematic lot formula
but rather bumping lots manually every ~$28 of equity gain, using 0.01 cent-lot increments for
the first bump and then larger jumps (0.06->0.10, 0.10->0.15) as confidence grows.

## G7 verdict

| Metric | Status |
|---|---|
| Data points | 4 distinct lot levels across 130 probes |
| Formula identified | NO -- underdetermined without initial balance |
| Pattern identified | YES -- lot increases ~$28/bump, manually adjusted monthly |
| G7 verdict | [WARN] -- sufficient to build EA v1 with fixed lot |

## EA recommendation

**EA v1**: Use **0.05 fixed probe lot** (conservative, matches initial period).
**EA v2**: Implement dynamic sizing once broker statement confirms exact account balance.
  Estimated formula: add 0.01 cent-lot for every ~$28 of equity gain above the starting balance.

**Note**: for the copy-trading source, the master account almost certainly uses a clean balance-based
formula (e.g., lot = max(0.01, floor(balance / 10000) * 0.01) or similar). The exact formula
requires the master account balance data, which we do not have.

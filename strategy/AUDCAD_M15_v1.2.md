# AUDCAD M15 Mean-Reversion EA — Strategy v1.2

**Status**: ready to implement (delta over v1.1)
**Last updated**: 2026-05-12
**Parent**: [AUDCAD_M15_v1.1.md](AUDCAD_M15_v1.1.md)
**Change scope**: replace dual-purpose signal with a net-basket profit target exit; remove bidirectional concurrency.

---

## What changed vs v1.1

| Topic | v1 / v1.1 | v1.2 |
|---|---|---|
| Exit trigger | Opposite signal closes the basket | Basket closes when net profit ≥ +10 pips (weighted avg) |
| Opposite signal while basket open | Closes the basket + opens new probe | Ignored — active basket takes priority |
| Concurrent baskets | Up to 2 (1 buy + 1 sell simultaneously) | 1 at a time only |
| HTF gate | v1.1 D1 EMA20 gate on opens | Unchanged — still applies |
| Entry signal rule | v1 §1 oscillator rule | Unchanged |
| Grid adds | 22-pip ladder | Unchanged |
| Lot sizing | 0.01 probe, 24x / +12x ladder | Unchanged |

---

## 1. Signal rule

Unchanged from [strategy/AUDCAD_M15_v1.md §1](AUDCAD_M15_v1.md).

---

## 2. Full system logic

```
On every M15 bar close:

─── IF NO basket is open ───────────────────────────────────────────────
    IF BUY condition fires (v1 §1) AND gate_long (D1 close > D1 EMA20):
        → OPEN a new BUY probe

    IF SELL condition fires (v1 §1) AND gate_short (D1 close < D1 EMA20):
        → OPEN a new SELL probe

─── IF A BASKET IS OPEN ────────────────────────────────────────────────
    1. Check close condition (evaluate first, before grid):
         BUY basket:  current close >= weighted_avg_entry + 0.0010
         SELL basket: current close <= weighted_avg_entry - 0.0010
         → If met: CLOSE all legs at market, basket done.

    2. Check grid add (only if close condition was NOT met):
         BUY basket:  current close <= last_entry_price - 0.0022
         SELL basket: current close >= last_entry_price + 0.0022
         → If met: ADD next ladder leg

    3. Opposite signal fires → do nothing (basket stays open, signal ignored)
    4. Same-direction signal fires → do nothing (basket already open)
```

### Weighted average entry price

```
weighted_avg_entry = Σ(lots_i × entry_price_i) / Σ(lots_i)
                     across all open legs in the basket
```

Recalculate after each new leg is added.

---

## 3. Grid (ladder adds)

Unchanged from [strategy/AUDCAD_M15_v1.md §3](AUDCAD_M15_v1.md).

- 22-pip step from the **most recent entry price** (not the weighted avg)
- Checked at M15 bar close boundaries only
- Hard cap: 10 legs per basket

---

## 4. Lot sizing

Unchanged from [strategy/AUDCAD_M15_v1.md §4](AUDCAD_M15_v1.md).

| Leg | Example (0.01 probe) |
|---|---|
| 1 (probe) | 0.01 |
| 2 | 0.24 |
| 3 | 0.36 |
| 4 | 0.48 |
| 5 | 0.60 |
| N | 0.12 × N lots |

---

## 5. Risk and safety parameters

| Parameter | v1.2 value | Notes |
|---|---|---|
| Probe lot | 0.01 | Fixed for v1.2 (standard account) |
| Basket close target | +10 pips net (weighted avg) | New in v1.2 |
| Max concurrent baskets | **1** | Changed from 2; one direction at a time |
| Max legs per basket | 10 | Hard cap unchanged |
| Stop loss per probe | None | Grid recovery; no per-position SL |
| Account-level DD cap | 20% | Last-resort hard stop, unchanged |
| Grid step | 22 pips (0.0022 price) | Checked at M15 bar close |
| HTF gate | D1 close vs D1 EMA20 (shift=1) | From v1.1; unchanged |
| Magic number | 202600 | Unchanged |
| Symbol | AUDCAD# | Standard account (XM) |

---

## 6. MT5 implementation notes

```mql5
// --- Weighted average entry ---
double WeightedAvgEntry(int magic, ENUM_ORDER_TYPE dir) {
    double sumLots = 0, sumVal = 0;
    for (int i = PositionsTotal() - 1; i >= 0; i--) {
        if (PositionGetTicket(i) <= 0) continue;
        if (PositionGetInteger(POSITION_MAGIC) != magic) continue;
        if ((int)PositionGetInteger(POSITION_TYPE) != (int)dir) continue;
        double lots  = PositionGetDouble(POSITION_VOLUME);
        double price = PositionGetDouble(POSITION_PRICE_OPEN);
        sumLots += lots;
        sumVal  += lots * price;
    }
    return (sumLots > 0) ? sumVal / sumLots : 0.0;
}

// --- Close condition check (call on every M15 bar close) ---
double wae    = WeightedAvgEntry(MAGIC, buyBasketOpen ? ORDER_TYPE_BUY : ORDER_TYPE_SELL);
double target = 10 * _Point * 10; // 10 pips for AUDCAD (5-digit broker: 0.0010)
bool closeNow = buyBasketOpen  ? (close >= wae + target)
                               : (close <= wae - target);
if (closeNow) CloseAllLegs(magic);
```

> **Pip value**: on a 5-digit AUDCAD# broker (XM standard), 1 pip = 0.0001. 10 pips = 0.0010. Confirm with `SymbolInfoDouble(_Symbol, SYMBOL_POINT)` — if POINT = 0.00001 then 10 pips = `10 * 10 * _Point`.

---

## 7. Open questions specific to v1.2

### 7.1 Profit target calibration
The 10-pip target is untested. Key risk: a ladder with 4+ legs may need more than 10 pips net to cover spread and negative legs. Consider logging the actual net pip at close during G8 forward test to see if 10 pips is too tight or too loose.

### 7.2 No forced exit if target is never reached
With the opposite signal no longer closing baskets, a basket can theoretically stay open indefinitely if price drifts sideways and never reaches +10 pips net. The only hard exits are:
- 20% DD cap
- Manual close

**v1.3 candidate**: add a basket age limit (e.g., close at breakeven or loss after N bars / N days if no recovery).

### 7.3 Missed entry opportunities
With only one basket at a time, a strong signal in the opposite direction is ignored while a basket is open. During a trending market this could mean sitting out most of the move.

**Monitor in G8**: log every skipped signal and note the direction + HTF gate state. If skipped signals consistently would have been profitable, revisit concurrency.

### 7.4 Re-validation needed
- **G6** (close trigger match) will no longer apply — the close trigger is now a pip target, not the opposite signal. Replace G6 with a new gate:
- **G9 (P/L improvement vs master)**: replay Feb–May 2026 with v1.2 pip-target exit; compare simulated basket P/L vs master's actual P/L.

---

## 8. Implementation order

1. Implement v1.1 in full (HTF gate, entry signal, grid).
2. Replace the dual-purpose close logic with the weighted-avg +10 pip target.
3. Remove the bidirectional basket namespace — enforce single-basket-at-a-time.
4. Add logging: `[CLOSE] wae=X, close=Y, net_pips=Z` on every M15 bar close so G9 can be audited.
5. Run G9 simulation on Feb–May 2026 OHLC before deploying live.
6. Deploy v1.2 to demo for the 2-week G8 forward test.

---

## 9. Backward compatibility

v1.2 is **not** backward compatible with v1/v1.1 basket state. The dual-purpose close logic is gone. A live v1/v1.1 basket that is waiting for the opposite signal to close it will never close under v1.2 rules — it will only close when price reaches the weighted-avg +10 pip target. Migrate cleanly: close any open v1.1 baskets manually before switching to v1.2.

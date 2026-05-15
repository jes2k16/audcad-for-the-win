# AUDCAD M15 Mean-Reversion EA — Strategy v1.1

**Status**: ready to implement (delta over v1)
**Last updated**: 2026-05-12
**Parent**: [AUDCAD_M15_v1.md](AUDCAD_M15_v1.md)
**Change scope**: add a single HTF directional bias gate; everything else is unchanged.

---

## What changed vs v1

v1 replicates the master account 1:1. v1's hit-rate validation (G1 91%, G2 85%) confirms the §1 oscillator rule is sound, but the master account is a **symmetric mean-reverter** trading an **asymmetric tape** — see Finding F1 in [analysis/AUDCAD_05102026.md:46-50](../analysis/AUDCAD_05102026.md#L46-L50). The result: sell-side baskets fought the 2026 uptrend (1/31 disaster, open 5/8 basket).

v1.1 adds **one rule** to prevent new probes against the higher-timeframe trend:

> **A new BUY probe may only open if D1 closed above its EMA20.
> A new SELL probe may only open if D1 closed below its EMA20.**

This is a **veto on opens**, not a change to the signal rule, not a change to basket mechanics.

---

## 1. The HTF EMA gate

```
EMA20_D1 = EMA(close, 20) on the daily timeframe, last COMPLETED bar
            (in MT5: iMA(symbol, PERIOD_D1, 20, 0, MODE_EMA, PRICE_CLOSE, 1))

gate_long  =  Close_D1[1] > EMA20_D1[1]      ← daily closed above its 20 EMA
gate_short =  Close_D1[1] < EMA20_D1[1]      ← daily closed below its 20 EMA
```

- Re-evaluated on **every M15 bar close** (same cadence as the §1 signal).
- Uses **shift=1** (last completed daily bar), not the in-progress D1.
- Gate state changes at most once per trading day (when the daily bar closes).
- No buffer / hysteresis in v1.1 — strict close-above / close-below. (See §6 for the hysteresis trade-off.)

### Why D1 EMA20 specifically

| Candidate | Why not | Why D1 EMA20 wins |
|---|---|---|
| W1 EMA20 | Too slow — flips ~1× per quarter; useless for tactical timing | — |
| D1 EMA200 | Too slow — captures regime but lags 6-12 months on flips | — |
| H4 EMA20 | Too fast — flips intraday; would let the symmetric problem back in | — |
| **D1 EMA20** | — | Listed in [analysis/AUDCAD_05102026.md:38](../analysis/AUDCAD_05102026.md#L38) as the "first real pullback magnet"; flips on the timescale (1-3 weeks) where the master's losing baskets actually accumulate |

---

## 2. Updated decision tree

The change is two `IF` insertions inside the v1 §2 logic. Everything else is identical.

```
On every M15 bar close, evaluate:

IF BUY condition fires (per v1 §1):
    1. If SELL basket open → CLOSE it (market order, all legs)        ← unchanged
    2. IF gate_long is TRUE:                                          ← NEW
         If no BUY basket open → OPEN a new BUY probe                 ← unchanged inside the gate
       ELSE:
         Skip the open. (Basket-close in step 1 still happened.)      ← NEW
    3. If a BUY basket is already open → do nothing                   ← unchanged

IF SELL condition fires (per v1 §1):
    1. If BUY basket open → CLOSE it                                  ← unchanged
    2. IF gate_short is TRUE:                                         ← NEW
         If no SELL basket open → OPEN a new SELL probe               ← unchanged inside the gate
       ELSE:
         Skip the open.                                               ← NEW
    3. If a SELL basket is already open → do nothing                  ← unchanged

IF neither condition fires:
    → check for grid add (v1 §3)                                      ← unchanged
```

> **Critical design choice — the gate vetoes OPENS, not CLOSES.** A BUY signal still closes an open SELL basket even if the gate forbids new buys. This is intentional: the gate is protective, and forcing early exits from a fighting basket is exactly the behavior we want when HTF trend disagrees.

---

## 3. MT5 implementation notes

```mql5
// Once per OnTick at the M15 close (or in OnInit + cached for the day):
double ema20_d1   = iMA(_Symbol, PERIOD_D1, 20, 0, MODE_EMA, PRICE_CLOSE, 1);
double close_d1   = iClose(_Symbol, PERIOD_D1, 1);
bool   gate_long  = (close_d1 > ema20_d1);
bool   gate_short = (close_d1 < ema20_d1);
```

- **Caching**: D1 values only change at the daily rollover. Optional: cache `gate_long`/`gate_short` and recompute only when a new D1 bar is detected. For a single-symbol EA the saving is trivial; not required.
- **First-bar safety**: at EA startup, ensure `Bars(_Symbol, PERIOD_D1) >= 21` before reading shift=1 EMA20. If not, skip the gate (i.e., default to "blocked" for both sides until enough history is loaded).
- **Symbol suffix**: `AUDCAD#` (standard account, per v1 §5).
- **Broker timezone**: D1 close depends on broker server time. XM's daily roll matches GMT+2/+3 (Athens). No code change needed; just be aware that the gate flips around 00:00 server time, not 00:00 UTC.

---

## 4. What does NOT change

| v1 section | Status in v1.1 |
|---|---|
| §1 Signal rule (RSI, StochRSI, BB %B, 500-bar swing) | **Unchanged** |
| §2 Dual-purpose signal (open + close opposite basket) | **Unchanged** — only the *open* step is now gated |
| §3 Grid (22-pip ladder adds) | **Unchanged** — see §6 for the open question |
| §4 Lot sizing (0.05 probe, 24x / +12x ladder) | **Unchanged** |
| §5 Risk parameters | One row added — see below |
| §6 Open questions | F1 (asymmetric tape) now partially addressed; others unchanged |
| §7 Validation gates G1–G8 | Need re-run for v1.1 (the gate will reduce probe count) |

---

## 5. Risk & safety table — added row

| Parameter | v1.1 value | Notes |
|---|---|---|
| HTF gate timeframe | PERIOD_D1 | Daily |
| HTF gate indicator | EMA(20) on close | Standard EMA, no smoothing variant |
| HTF gate operator | strict (`>` / `<`) | No buffer in v1.1 — see §6 |
| HTF gate shift | 1 (last completed D1) | Never use shift=0 (incomplete bar) |
| HTF gate failure mode | Block new probes both sides | Until `Bars(D1) >= 21` |

All other rows from [strategy/AUDCAD_M15_v1.md §5](AUDCAD_M15_v1.md) remain in effect verbatim.

---

## 6. Open considerations specific to v1.1

### 6.1 Grid adds on legacy "wrong-side" baskets
If v1.1 starts with an existing sell basket from a previous run (or v1.0 deployment), and that basket is now against the HTF trend, **v1.1 still allows grid adds** on it per §3. Rationale: the gate's job is to control *new openings*; basket management is delegated to the dual-purpose close trigger. Forbidding adds on legacy baskets would strand them without their grid-recovery mechanism.

**Decision for v1.1**: do not change grid behavior. Existing baskets manage to close via the opposite signal as in v1.

**Defer to v1.2 if observed**: if back-test shows the gate prevents the opposite signal from firing (because the opposite signal is now also gated from re-opening, so price never reaches a regime where the close trigger goes off), then we need a forced-exit rule. Track this in G8.

### 6.2 Whipsaw at the D1 EMA20 boundary
Strict close-above/close-below means a daily close that wobbles ±2 pips around EMA20 can flip the gate daily. In a sideways regime this is harmless (no new probes either way during chop). In a transitional regime (trend → range) it could whipsaw probe direction.

**v1.1 choice**: accept whipsaw, monitor frequency in G8 shadow logs.
**v1.2 candidate**: hysteresis buffer (e.g., gate_long only flips OFF if close drops > 20 pips below EMA20).

### 6.3 The gate will reduce probe frequency
v1 fires on 78% of M15 bars (most are basket-management). v1.1 will:
- Close opposite baskets at the same rate (gate doesn't affect closes).
- Open new probes **only on the trend-aligned side**.

In the Mar–May 2026 OOS window the D1 was above EMA20 for ~78% of trading days, so:
- BUY probes: ~unchanged (gate is satisfied most of the time)
- SELL probes: ~78% reduction (gate vetoes most)

This is the **intended** behavior. The losing-leg sell baskets from the OOS window are exactly what the gate is designed to refuse.

### 6.4 Re-validation needed
Gates G1, G2, G6 from v1 must be re-run with the v1.1 logic:
- **G1/G2**: hit-rate will *drop* numerically (we now intentionally skip valid master probes that fight HTF). This is correct — we are no longer replicating the master, we are improving on it.
- **G6**: the cross-direction close rate should be **unchanged** (gate doesn't touch closes).

New gate to add:
- **G9 (P/L improvement)**: replay Feb–May 2026 with v1.1; compare simulated basket P/L vs the master's actual P/L. Target: v1.1 ≥ master P/L. If v1.1 underperforms, the gate is too restrictive (or the master's losing trades were rescued by mechanics we haven't modeled).

---

## 7. Implementation order

1. Implement v1 in full (per [strategy/AUDCAD_M15_v1.md](AUDCAD_M15_v1.md) §1–5).
2. Add the gate code from §3 above as a thin wrapper around the probe-open step.
3. Add a logging line: `[GATE] D1 close=X, EMA20=Y, gate_long=true/false, gate_short=true/false` on every M15 close so G8 shadow-mode logs are gate-aware.
4. Run G9 simulation on Feb–May 2026 OHLC before deploying live.
5. Deploy v1.1 to demo for the 2-week G8 forward test, not v1.

---

## 8. Backward compatibility

v1.1 is strictly stricter than v1. Any probe that v1.1 opens, v1 would also have opened. A v1.1 → v1 rollback is safe (just disables the gate; no state migration). Use the same magic number as v1 — there is no need for a parallel basket namespace.

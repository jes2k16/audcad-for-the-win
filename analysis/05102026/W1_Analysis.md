# AUDCAD — Weekly (W1) Chart Analysis — 2026-05-10

**Source:** `charts/05102026/AUDCAD_W1_05102026.jpg`
**Broker:** XM (`AUDCAD#`).

## Snapshot at time of capture

| Field | Value |
|---|---|
| Current candle | O 0.97829 · H 0.99294 · L 0.97121 · **C 0.99088** (+1.31%) |
| Bid / Ask | 0.99088 / 0.99155 |
| EMA 10 (close) | 0.97202 |
| EMA 20 (close) | 0.95884 |
| EMA 50 (close) | 0.93561 |
| EMA 200 (close) | 0.91775 |
| RSI(14) | **72.47** — overbought |
| Stoch RSI(14,14,3,3) | **50.40 / 49.32** — neutral |

## Structural read

- **Trend phase, accelerating.** The weekly came out of an extended 2024–mid-2025 base (0.86 – 0.93) with a clean breakout through 0.93 in late 2025 and has gone almost straight up since. Current weekly candle is pressing 0.99.
- **EMA stack is bullishly fanned and widening** (10 > 20 > 50 > 200). The widening separation is the signature of an established trend, not the early phase.
- **Big anomalous candle** in early 2025 — a long red wick down to ~0.86 followed by recovery. That capitulation low is the structural floor of the entire current move.

## Key levels

| Level | Significance |
|---|---|
| **0.99 – 1.00** | Macro resistance (carried over from M1). Currently being tested. |
| **0.97200** | EMA10 — first dynamic support; close pullbacks should hold here. |
| **0.95884** | EMA20 — the level a healthy trend pulls back to before resuming. |
| **0.95** | Old breakout pivot (range top through 2025). Flip support. |
| **0.93561** | EMA50 — deeper trend support; a break here ends the acceleration phase. |
| **0.93** | Breakout origin pivot; loss of this means the weekly trend is broken. |
| **0.86** | Early-2025 capitulation low. Macro floor. |

## Oscillator read — important divergence

- **RSI(14) = 72.47**: overbought, persistent in trend.
- **Stoch RSI = ~50, neutral**: this is the notable signal. Stoch RSI cooled from extreme to mid-range while price continued higher.

This is **bearish-leaning hidden divergence**: when Stoch RSI works off overbought conditions while price consolidates or pushes slightly higher, it's the textbook setup for one more thrust *or* a sharper pullback. In context (rejection candidate at 0.99 macro resistance) it tilts toward "pullback to EMA10/20 likely before any continuation".

## Implications for the EA strategy

1. **Weekly trend is strongly up — counter-trend shorts have a structural headwind.** This compounds the M1 finding: the master's symmetric mean-reversion shorts in 2026 were fighting BOTH monthly and weekly bias.
2. **Buy-the-dip is the favored side on this timeframe.** Pullbacks into 0.972 (EMA10), 0.959 (EMA20) or 0.95 (former range top) are the high-probability long setups. A v2 trend filter could *promote* probe size on the long side here while *demoting* (or skipping) shorts.
3. **Stoch RSI neutral is a yellow flag for chasing longs at 0.99.** Don't take the macro bull bias as license to ignore the resistance test happening right now. The cleaner long setup is on a pullback, not at the highs.
4. **Weekly directional bias resolves the `LongBias`/`ShortBias` open question** raised in M1: for 2026 to date, the EA should *at minimum* track weekly EMA10 vs EMA50 spread as a "long-trend strength" gauge.

## Risk read

- A weekly close > 0.99 with momentum opens 1.00 / 1.0150 with thin overhead structure. Counter-trend shorts here = adverse trend × adverse momentum.
- A weekly close back below 0.97 from current levels = first sign of a meaningful pullback; mean-reversion shorts get a tactical edge again from there.
- The 2025 capitulation wick to 0.86 is a reminder this pair *can* take ~10% jolts on weekly. Any EA leverage and DD math must stomach a comparable adverse move on the long side too — not just the short side.

## Confidence

**High** for the weekly bull-trend read (price action and EMA fan are unambiguous). **Medium-high** for the "pullback over breakout" near-term tactical read (depends on whether 0.99 holds; Stoch RSI says it likely will, at least short-term).

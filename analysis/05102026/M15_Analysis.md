# AUDCAD — M15 Chart Analysis — 2026-05-10

**Source:** `charts/05102026/AUDCAD_M15_05102026.jpg`
**Broker:** XM (`AUDCAD#`).

## Snapshot at time of capture

| Field | Value |
|---|---|
| Current candle | O 0.99070 · H 0.99088 · L 0.99065 · **C 0.99088** (+0.01%) — very tight range |
| Bid / Ask | 0.99088 / 0.99155 |
| EMA 10 (close) | 0.99109 |
| EMA 20 (close) | 0.99092 |
| EMA 50 (close) | 0.98996 |
| EMA 200 (close) | 0.98723 |
| RSI(14) | **52.02** — neutral |
| Stoch RSI(14,14,3,3) | **22.89 / 41.93** — %K below 30 (**oversold**), %K crossed below %D |

## Structural read

The M15 chart shows roughly the last 2 trading days (5/8 → late 5/9). Three sub-segments:

1. **5/8 morning – 5/8 evening (range/decline)**: chop and slow drift from ~0.990 down to ~0.984. The master's 5/8 03:00 probe (0.98458), 5/8 09:30 add (0.98672), and 5/8 15:45 add (0.99109) were placed across this window.
2. **5/8 late evening – 5/9 mid-day (base + grind up)**: floor around 0.984 → gradual rise back to ~0.988.
3. **5/9 ~13:00 spike**: sharp impulse from ~0.987 to ~0.993 in roughly 2 hours (≈60 pips), then mean-reversion back toward 0.991.
4. **Last several M15 bars**: very narrow consolidation candles near 0.99088 — the market is digesting the spike.

The **price is currently sitting *just below* EMA10/EMA20 (both ~0.991)** — first time since the spike that the M15 EMA10 has been touched from below. That's a tactically meaningful inflection point.

## Key levels (M15)

| Level | Significance |
|---|---|
| **0.99294** | Spike high (also matches D1/H1 high). Resistance. |
| **0.99109 / 0.99092** | EMA10/EMA20 cluster — price now testing this zone from below. |
| **0.98996** | EMA50 — first deeper support. |
| **0.98723** | EMA200 — would mark a real M15 trend break if broken. |
| **0.984** | 5/8 base low — major pivot for any further pullback. |
| **0.99109** | The master's 5/8 15:45 sell add — coincidentally at current EMA10. |

## Momentum read — fresh oversold cross on M15

This is the cleanest oscillator setup currently visible across all timeframes:

- **RSI 52** — squarely neutral. No overbought/oversold edge.
- **Stoch RSI %K = 22.89, %D = 41.93** — %K just dropped below the 30 oversold band and is below %D. The classic Stoch RSI "primed for a long" configuration.

**If — and only if — the master uses Stoch RSI on M15 as an entry trigger, a buy probe is being set up *right now*** (or has just fired in the most recent M15 bar). This is the most concrete real-time test our analysis has produced so far.

## Mapping to recent CSV trades — what was happening at probe times

The 5/8 entries are close enough to be inferred from this chart:

| CSV entry        | Direction | Price   | Inferred M15 context (best read from this chart) |
|------------------|-----------|---------|--------------------------------------------------|
| 5/8 03:00        | sell      | 0.98458 | Likely after a prior overbought rally segment; entry near a local high before drift down. |
| 5/8 09:30 (add)  | sell      | 0.98672 | Mid-range during the 5/8 chop; ladder logic, not entry-trigger. |
| 5/8 15:45 (add)  | sell      | 0.99109 | At the start of the spike; ladder logic again, but the price level coincided with what later became the EMA10. |

The chart **does not** clearly show classic textbook overbought signals on M15 right at the 5/8 03:00 probe — which weakens H2 (RSI extreme on M15) as the master's trigger and **strengthens H1 (BB touch) or H4 (BB+RSI combo)**. The earlier-dated probes in the CSV (4/21, 4/13, etc.) cannot be resolved from this chart's window — those need the screenshot sample from `plans/2`.

## Implications for the EA strategy

1. **M15 is the right execution timeframe.** Earlier observation from CSV (every entry on a 15-minute boundary) is consistent with what M15 momentum signals would produce. We should keep `Timeframe = PERIOD_M15` as the EA default in the design phase.
2. **Stoch RSI on M15 is a viable component of the trigger.** A %K cross below 20 (or above 80) with %D agreeing is a standard mean-reversion signal that fits the CSV's probe-win profile (8–18 pip targets in 30 min – 5 h).
3. **There is a *live test* unfolding right now**: M15 is oversold, HTFs are bullish-trending. If the master's strategy fires a long probe in the next few hours, that's strong evidence the trigger is M15-oscillator based. If no probe fires, the trigger is conditional on something else (HTF agreement, time-of-session, range-vs-trend filter).
4. **The 5/9 spike + mean-reversion sequence** is the kind of pattern where the master might *expect* shorts to work — but on a single-TF basis only. The H4/D1 trend overrides.
5. **Don't overweight a single oscillator.** The cleanest M15 buy setup right now still happens against an HTF trend that says "long bias". If `plans/2` lands on a single-indicator trigger we should at minimum surface a HTF-trend-filter parameter even if disabled by default.

## Risk read

- Entering a long probe on the current M15 oversold cross while HTFs are bullish = **trend-aligned mean-reversion**, the highest-quality kind of probe. If the EA fires here, it's the right kind of signal.
- Entering a short probe on the recent 5/9 spike high = trend-fighting; the kind of trade that historically built the deepest baskets.
- The current 5/8 sell basket (3 legs open) is currently on the "wrong" side of M15 as well as HTFs. It needs the M15 mean-reversion *to fail and continue lower* to get back toward breakeven.

## Confidence

**High** that M15 is the execution timeframe. **Medium-high** that an M15 oscillator (RSI or Stoch RSI) is part of the probe trigger — but we cannot confirm which from this chart alone; the `plans/2` screenshot sample is still required to discriminate H1 vs H2 vs H3 vs H4. **Medium** that price will mean-revert short-term — Stoch RSI oversold + neutral RSI is constructive but not a guarantee against more chop.

# AUDCAD — Monthly (M1) Chart Analysis — 2026-05-10

**Source:** `charts/05102026/AUDCAD_M1_05102026.jpg`
**Broker:** XM (`AUDCAD#` symbol — note the `#` suffix; cent symbol elsewhere is `AUDCAD.c`).

## Snapshot at time of capture

| Field | Value |
|---|---|
| Current candle (May 2026) | O 0.97753 · H 0.99294 · L 0.97121 · **C 0.99088** (+1.36%) |
| Bid / Ask | 0.99088 / 0.99155 (~6.7 pip spread on M1 — informational, not actionable on this TF) |
| EMA 10 (close) | 0.94922 |
| EMA 20 (close) | 0.93924 |
| EMA 50 (close) | 0.91775 |
| EMA 200 (close) | not labelled, but the deep-blue line near 0.92 |
| RSI(14) | **71.23** — overbought |
| Stoch RSI(14,14,3,3) | **92.95 / 93.23** — extreme overbought |

## Structural read

- **Multi-year range broken to the upside.** From mid-2021 through end-2025 AUDCAD oscillated ~0.86 – 0.95. In the last few monthly candles price has **broken hard above 0.95** and is pressing the **0.99 multi-year resistance** (last tagged in late 2020).
- **EMA stack is fully bullish**: price > EMA10 > EMA20 > EMA50 > EMA200, with all EMAs sloping up. This is a textbook trending bull configuration on the highest timeframe we have.
- **Pace of the move is unusual**: the rally from ~0.91 to ~0.99 happened in a small number of monthly candles. Strong momentum, but stretched.

## Key levels

| Level | Significance |
|---|---|
| **0.99 – 1.00** | Major multi-year resistance / round number. Current price is leaning into it. |
| **0.95** | Old range top (2021–2025). Now flips to support on a pullback. |
| **0.93 – 0.94** | EMA10 / EMA20 cluster — likely first dynamic support. |
| **0.91 – 0.92** | EMA50 / EMA200 cluster — deeper structural support. |
| **0.86** | Range-low pivot of the multi-year consolidation. Hard floor. |

## Oscillator read

- RSI 71 in a breakout is **not** a counter-signal — momentum overbought can persist for many months in a real breakout. Treat it as confirmation, not exhaustion.
- Stoch RSI > 90 is more sensitive and can flag pullbacks even in strong trends. Worth watching for a roll-down as the first warning of a breather.

## Implications for the EA strategy

1. **Macro bias is strongly LONG.** Any mean-reversion *short* on lower timeframes is a counter-trend trade against the dominant direction.
2. **Why 1/31/2026's "order compression" hurt so much, in hindsight:** the master copy strategy is symmetric mean-reversion. AUDCAD broke its multi-year range early in 2026 and started trending up. Symmetric short probes got steamrolled because the higher timeframes were no longer balanced.
3. **HTF trend filter is justified:** even a simple "skip shorts when monthly EMA10 > EMA50 by more than X%" filter would likely have avoided the worst basket of the period. This is exactly the candidate for `plans/2` D2 (HTF trend filter, deferred to v2).
4. **Symmetry assumption needs review.** The CSV's strategy treats long and short as equally weighted. Monthly tells us 2026 is **not** symmetric. The EA should at minimum log a "directional skew" indicator and may want a configurable `LongBias` / `ShortBias` weighting.

## Risk read

- A monthly close above 0.99 opens room toward 1.00 / 1.0150 with no overhead structure. Counter-trend shorts in this window are objectively higher-risk than counter-trend longs.
- A monthly bearish reversal candle off 0.99 would be the first technical signal that mean-reversion shorts have a tactical edge again. Until then, expect continued long-side bias.

## Confidence

**High** for the structural read (range break + EMA stack are unambiguous on this timeframe). **Medium** for the "near 0.99 resistance reaction" call — that depends on whether 0.99 holds or fails on the monthly close.

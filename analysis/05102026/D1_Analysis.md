# AUDCAD — Daily (D1) Chart Analysis — 2026-05-10

**Source:** `charts/05102026/AUDCAD_D1_05102026.jpg`
**Broker:** XM (`AUDCAD#`).

## Snapshot at time of capture

| Field | Value |
|---|---|
| Current candle | O 0.98433 · H 0.99294 · L 0.98280 · **C 0.99088** (+0.65%) |
| Bid / Ask | 0.99088 / 0.99155 |
| EMA 10 (close) | 0.98199 |
| EMA 20 (close) | 0.97675 |
| EMA 50 (close) | 0.97068 |
| EMA 200 (close) | 0.94141 |
| RSI(14) | **65.84** — bullish, room to run |
| Stoch RSI(14,14,3,3) | **90.54 / 67.87** — %K crossing up into overbought |

## Structural read

- **Clean, ongoing daily uptrend** since the early-2025 low. The chart shows a stair-stepping advance: rally → tight pullback to EMA10/EMA20 → resumption.
- **Each pullback in 2026 has held the EMA20.** The EMA20 (0.97675) has effectively been the trend's spine for the last several months.
- **Today's candle is a clean breakout candle** above the prior swing high near 0.985, pushing into 0.99294 intraday before settling at 0.99088.
- **EMA200 (0.94141) is now ~5 big figures below price** — the trend is well established, not nascent.

## Key levels (D1)

| Level | Significance |
|---|---|
| **0.99294** | Today's high — local resistance / breakout candle high. |
| **0.99 / 1.00** | Macro resistance carried from W1/M1. |
| **0.985** | Prior daily swing high — now flipped support. |
| **0.98199** | EMA10 — first daily dynamic support. |
| **0.97675** | EMA20 — the "trend is broken if lost" line. |
| **0.97068** | EMA50 — deeper trend support. |
| **0.94141** | EMA200 — macro structural floor (very far off). |

## Momentum read

- **RSI 65.84** is a *constructive* bullish reading — still room before the 70+ overbought band that often coincides with daily reversals. This is different from W1/M1 which are already at 71–72.
- **Stoch RSI %K crossing up** at 90.54 with %D at 67.87: classic momentum-thrust signal. In a trending market this typically precedes another push, not a top.

Net momentum read: **bullish, with fuel left**. No daily-timeframe sell signal.

## Mapping to recent CSV trades

The CSV's most recent baskets land directly on this chart:

- 5/5 11:30 sell probe @ 0.97469 → 7-leg basket → closed 5/8 01:02 @ 0.98466. The chart shows price spiking from ~0.974 to ~0.989 across 5/5–5/7 — that's exactly the leg that built and then partially recovered the basket.
- 5/8 03:00 sell probe @ 0.98458 (still open per CSV).
- 5/8 09:30 sell add @ 0.98672 (still open).
- 5/8 15:45 sell add @ 0.99109 (still open).

At capture (price 0.99088), those three open shorts sit roughly:
- Probe (0.98458): **~63 pips against** on 0.0015 std lots ≈ -$0.95 USD floating.
- Add 1 (0.98672): **~42 pips against** on 0.036 std lots ≈ -$15 USD floating.
- Add 2 (0.99109): **~2 pips in profit** on 0.054 std lots ≈ +$1 USD floating.
- Weighted-avg basket entry ≈ **0.98927**, current 0.99088 → **~16 pips against the basket**, basket P/L roughly **-$15 USD floating** at chart time.

The next ladder add at +22 pips from 0.99109 would fire near **0.99329**. That sits *above* the macro 0.99 resistance and *above* today's high — possible but requires breaking key resistance first.

## Implications for the EA strategy

1. **Daily trend confirms the W1/M1 read.** Three timeframes agree: AUDCAD is in a clean uptrend, and counter-trend shorts face structural resistance.
2. **The EMA20 daily (0.97675) is the right line to define "trend intact" vs "trend broken"** for an HTF filter. A simple v2 rule: `if D1 close < D1 EMA20 → re-enable shorts; else demote/skip shorts`. Cheap to implement, anchors the bias to actual structure rather than an arbitrary indicator threshold.
3. **The 5/5–5/8 basket is a perfect post-mortem case study** for the EA: probe was placed *near* the daily breakout, ladder added into the breakout, recovery only happened because price retraced briefly to 0.985. The EA's 20% DD cap from `plans/1` should keep this kind of basket survivable.
4. **The currently-open 5/8 sell basket is the live test.** If price grinds higher to 0.99329 and triggers a 4th add (and beyond), the basket goes deep into both the daily and weekly trend — exactly the failure mode we want to redesign around. Watch how it resolves; that data will inform whether the trend filter is needed in v1, not v2.

## Risk read

- Bullish bias on daily plus momentum still loaded means **shorts above 0.99 carry trend risk**. Don't size them as if symmetric to longs.
- A daily close back below 0.98 (today's open area) would invalidate the latest breakout and re-introduce range conditions — that's when symmetric mean-reversion becomes safer again.

## Confidence

**High** for the daily uptrend read. **High** that today's breakout is bullish-momentum (RSI 65 + Stoch RSI crossing up) rather than exhaustion. **Medium** that 0.99 macro resistance produces *some* short-term reaction (because Stoch RSI %D at 67 still has space, the macro level may pause but not reverse the daily trend).

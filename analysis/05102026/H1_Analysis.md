# AUDCAD — H1 Chart Analysis — 2026-05-10

**Source:** `charts/05102026/AUDCAD_H1_05102026.jpg`
**Broker:** XM (`AUDCAD#`).

## Snapshot at time of capture

| Field | Value |
|---|---|
| Current candle | O 0.99128 · H 0.99140 · L 0.99053 · **C 0.99088** (-0.04%) — narrow range below recent high |
| Bid / Ask | 0.99088 / 0.99155 |
| EMA 10 (close) | 0.99031 |
| EMA 20 (close) | 0.98916 |
| EMA 50 (close) | 0.98721 |
| EMA 200 (close) | 0.98227 |
| RSI(14) | **62.13** — bullish but mid-range |
| Stoch RSI(14,14,3,3) | **41.57 / 47.15** — %K below %D, **first bearish cross visible across all higher TFs** |

## Structural read

H1 covers roughly the last ~10 days (4/29 → 5/9). Three sub-segments:

1. **4/29 – 5/4 (range/base)**: chop between 0.973 and 0.979 with a hot wick down to ~0.973 around 5/5 morning. Master placed the 5/5 11:30 sell probe (0.97469) right inside this base.
2. **5/5 → 5/7 (rally)**: ~170 pips up from ~0.973 to ~0.992. Clean trend candles mostly above EMA10 H1. This is the leg that built the master's 7-leg sell ladder.
3. **5/7 → 5/9 (volatile two-touch of 0.99)**: spike high ~0.99294 on 5/7, pullback to ~0.984 on 5/8 (where the master closed the 7-leg basket at 0.98466), then rally back to 0.99 on 5/8–5/9. Currently consolidating just below 0.99.

**Possible double-top forming at 0.99**: two pushes (5/7, 5/9) into the same band, both stalling. Higher TFs (D1/H4) say "trend, expect continuation"; H1 momentum says "near-term pause/pullback".

## Key levels (H1)

| Level | Significance |
|---|---|
| **0.99294** | 5/7 spike high; 5/9 retest. Active double-top candidate. |
| **0.99088 – 0.99140** | Current consolidation band (last 2 H1 candles). |
| **0.99031** | EMA10 — price hugging it from above. First crack of the local trend. |
| **0.98916** | EMA20 — would be the first "real" pullback target. |
| **0.98721** | EMA50 — deeper pullback. Coincides with the 5/8 basket-close zone (0.98466). |
| **0.98227** | EMA200 — only reached in a true H1 trend break. |
| **0.984** | 5/8 swing low — first lower-low to watch. A close below this prints lower-low / lower-high structure. |

## Momentum read — divergence vs. higher TFs

This is the first place in the top-down where bullish unanimity *cracks*:

- M1, W1, D1, H4: all bullish, momentum supportive of more upside.
- **H1: RSI mid (62), Stoch RSI %K below %D in the 40s** — first bearish-leaning cross.

A Stoch RSI bear cross under 50 from an overbought turn is a classic H1 "exhaustion" signal that often precedes a 30–60 pip pullback toward EMA20/50 in trend continuations.

## Mapping to recent CSV trades

The H1 chart is the **highest** timeframe at which we can clearly see each ladder leg:

- **5/5 11:30 probe @ 0.97469** — H1 was at the bottom of a 6-day range; the probe was a textbook range-fade short. *In a range, this works; in a coming breakout, it fails.* The master couldn't tell the difference.
- **Adds 5/5 → 5/7 (0.97758 → 0.98867)** — each placed during a clean trending rally after the breakout above 0.978. The grid step (~22 pips) matched roughly 1–2 H1 candles per add.
- **Basket close 5/8 01:02 @ 0.98466** — coincided with the H1 retracement low at the EMA50/EMA20 cluster. A favorable pullback bailed the basket out.
- **New 5/8 ladder (probe + 2 adds)**: probe 0.98458 sat near where the prior basket closed (range fade attempt again), then adds at 0.98672 / 0.99109 chased the rebound up. The 0.99109 add lands at the H1 double-top zone — coincidentally a reasonable short location, but only if the double-top resolves bearishly.

## Implications for the EA strategy

1. **H1 is the highest timeframe where the *range vs trend* distinction is decision-relevant for the EA.** Above H1, the trend is clearly up — but on H1 the market alternates between range and trend phases (visible 4/29–5/4 vs 5/5–5/7).
2. **The probe-trigger reverse-engineering needs an H1 context check.** Possible v2 rule: only allow shorts when H1 EMA10 < EMA20 (range/pullback regime) and only allow longs when H1 EMA10 > EMA20 (trend regime). Trivially cheap to add.
3. **Current momentum favors a 5/8 basket recovery scenario** — if H1 Stoch RSI continues unwinding bearishly, price should pull back toward 0.987–0.989 (EMA20–EMA50), which would put the master's 5/8 basket back near its weighted-average breakeven. This is the *short-term* read; HTF says it'll likely resume up after.
4. **The double-top at 0.99 deserves a tactical alert.** A confirmed H1 close below 0.984 (the 5/8 swing low) would print a lower-low and validate the top short-term. Without that, treat the consolidation as a pause within an HTF uptrend.

## Risk read

- For the open 5/8 sell basket: the H1 momentum signal is **the first thing in our top-down that helps it**. If it works, basket recovers and closes near breakeven. If it doesn't, an H1 close back above 0.99294 with momentum opens the path to 1.00 and the basket goes to the next ladder add at ~0.99329.
- For new probes today: H1 says "don't initiate fresh longs at the highs" and "shorts have a tactical setup but a strong HTF headwind".

## Confidence

**High** that H1 is in a near-term consolidation/pause. **Medium** that the consolidation resolves as a pullback (Stoch RSI bear cross supports it; HTF trend pressure works against it). **Low** that this is the start of a meaningful reversal — would need H1 close < 0.984 plus H4 close < EMA10.

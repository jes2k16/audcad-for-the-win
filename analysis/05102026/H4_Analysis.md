# AUDCAD — H4 Chart Analysis — 2026-05-10

**Source:** `charts/05102026/AUDCAD_H4_05102026.jpg`
**Broker:** XM (`AUDCAD#`).

## Snapshot at time of capture

| Field | Value |
|---|---|
| Current candle | O 0.99103 · H 0.99150 · L 0.99053 · **C 0.99088** (-0.02%) — near-doji at resistance |
| Bid / Ask | 0.99088 / 0.99155 |
| EMA 10 (close) | 0.98872 |
| EMA 20 (close) | 0.98591 |
| EMA 50 (close) | 0.98241 |
| EMA 200 (close) | 0.97475 |
| RSI(14) | **66.91** — bullish |
| Stoch RSI(14,14,3,3) | **82.70 / 67.70** — overbought, %K above %D |

## Structural read

- The H4 covers roughly the last six weeks (late March → 2026-05-10). Three regimes are visible:
  1. **Mid-April rally and rejection at 0.99** (around 4/16–4/17): a sharp spike to ~0.99 was forcefully sold, producing the chart's tallest red candle and the visible 4/18–4/20 leg down.
  2. **Late-April base and shakeout** (~4/22–4/30): consolidation 0.973 – 0.978 with a deep wick low near **0.965** (the V-shaped capitulation visible just before May).
  3. **May breakout / V-recovery**: from ~0.975 on 5/4 to **0.993 on 5/9**, ~180 pips in five days. The current H4 candle is the first one that has printed a small range (near-doji) right at 0.99 — the first hint of a pause.
- **EMA stack is fully bullish and tightly fanned** (10 > 20 > 50 > 200). Pullbacks during the May rally have all held EMA10.
- **Macro context**: prior 0.99 rejection (4/16) is the ghost of resistance. Today's near-doji at the same level says the market hasn't decided yet whether it's a re-test (rejection again) or a base for breakout (clean break to 1.00).

## Key levels (H4)

| Level | Significance |
|---|---|
| **0.99294** | Today's daily high — local resistance. |
| **0.99 / 1.00** | Macro resistance + the 4/16/2026 rejection point on H4. |
| **0.98872** | EMA10 — first dynamic support, and where most May pullbacks have held. |
| **0.98591** | EMA20 — secondary dynamic support. |
| **0.98241** | EMA50 — tertiary support; structural rather than tactical. |
| **0.97475** | EMA200 — where the late-April capitulation reversed; major support. |
| **0.965** | Late-April wick low — last "true" cleared low. |

## Momentum read

- **RSI 66.91** is bullish but mid-range; not extreme, room before the 75–80 H4 overbought band.
- **Stoch RSI 82.70 / 67.70**: %K firmly in overbought; %D still climbing. In a strong trend this configuration usually unwinds via *time*-correction (sideways) rather than *price*-correction.

The H4 near-doji at resistance + Stoch RSI overbought = **conditions for a tactical pause**, not a reversal. Until an H4 close back below ~0.988 (EMA10), bullish bias dominates.

## Mapping to recent CSV trades

The recent CSV behavior is highly visible on this timeframe:

- **5/5 11:30 probe @ 0.97469**: placed in the consolidation base — an aggressive *short* entry just as the H4 was forming the higher low that became the launchpad of the V-rally. Looks like classic mean-reversion thinking that fought the structural turn.
- **Ladder 5/5 → 5/7 (0.97758 → 0.98867)**: each add fired roughly every ~4 H4 bars during the rally. The 22-pip grid step on M15 corresponded to ~half an H4 candle each.
- **Closed 5/8 01:02 @ 0.98466**: caught the brief consolidation pullback before the next leg up. Lucky timing — without that pullback the basket would have approached the 20% DD cap.
- **5/8 sell probes @ 0.98458 / 0.98672 / 0.99109 (still open)**: placed continuously into the May breakout; on H4 they look like fading a confirmed bullish leg, into the prior resistance at 0.99.

The H4 makes the failure mode of symmetric mean-reversion **visible**: the strategy keeps fading exhaustion that *isn't* exhaustion in trending phases.

## Implications for the EA strategy

1. **H4 confirms the trend bias of W1/D1.** Counter-trend probes need a tighter filter on this timeframe specifically.
2. **EMA10 H4 (0.98872) is a useful "tactical trend line"**: probes against the H4 trend should be size-discounted or skipped while price > H4 EMA10 by a meaningful margin.
3. **The 4/16 vs 5/9 retest of 0.99** is the kind of context an EA can exploit: when price tests prior rejection level with overbought oscillators, a *short-term* short scalp has historical precedent — but only one — and it's a thin edge versus the prevailing trend.
4. **Probe-trigger reverse-engineering** (`plans/2`) needs to look closely at the M15/M5 charts at the 5/5 11:30 entry: was the master fading the H4 doji's predecessor, or the M15 RSI extreme? The H4 alone shows nothing structural at that entry — so the trigger must be a lower-TF oscillator signal rather than an H4-level pattern.

## Risk read

- An H4 close > 0.992 with momentum opens a clean run at 0.995 / 0.99 (round) / 1.00.
- An H4 close back below 0.988 and into 0.985 would be the first tactical "trend pause/pullback in progress" signal — at that point fresh mean-reversion shorts get a tighter stop and a closer target.
- No bearish-structure signal yet on H4. Pause/consolidate is more likely than reverse.

## Confidence

**High** that H4 trend is up. **Medium-high** that 0.99 produces a short-term pause/consolidation rather than an immediate breakout (Stoch RSI extreme + near-doji at resistance). **Low** that 0.99 produces an outright reversal — momentum and structure both argue against it.

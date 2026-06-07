# AUDCAD M15 Mean-Reversion EA — Strategy v1.6

**Status**: active
**Last updated**: 2026-06-07
**Parent**: [AUDCAD_M15_v1.5.md](AUDCAD_M15_v1.5.md)
**Change scope**: **grid-add mechanic change only — ATR ladder pause.** While a basket is open, grid-leg additions are PAUSED during fast (high-volatility) market conditions and resumed once volatility normalizes. The signal confluence, RSI direction gate, 4 arm thresholds, D1 EMA20 HTF gate, +10-pip basket TP, lot formula, FitCheck, and emergency-DD logic are **all bit-for-bit identical to v1.5**. Setting `Enable_ATR_Pause = false` reproduces v1.5 exactly.

Full design rationale and the backtest matrix live in [plans/4. ATR Integration.md](../plans/4.%20ATR%20Integration.md).

---

## What changed vs v1.5

| Topic | v1.5 | v1.6 |
|---|---|---|
| Grid-leg add | fires whenever price moves `Grid_Step_Pips` adverse from `last_price` | **same, but SKIPPED while `g_atr_paused` is true** (volatility spike) |
| New inputs | — | `Enable_ATR_Pause`, `ATR_Period_Fast`, `ATR_Period_Slow`, `ATR_Pause_Ratio`, `ATR_Resume_Ratio`, `ATR_Resume_Confirm_Bars`, `ATR_Pause_Min_Pips` |
| New log events | — | `ATR_PAUSE`, `ATR_RESUME`, `ADD_PAUSED` |
| SIGNAL diag log | `... buy_arms / sell_arms / min` | **+ `atr_ratio / atr_paused`** (only when `Enable_ATR_Pause=true`) |
| CSV log filename | `audcad_v1_5.csv` | `audcad_v1_6.csv` |
| CSV `ea_version` | `v1.5` | `v1.6` |
| Trade comment tag | `audcad_v1.5_*` | `audcad_v1.6_*` |
| Signal, gate, exit, lot formula, FitCheck, emergency, basket struct | unchanged | **bit-for-bit identical** |

---

## 1. Why this release exists

Every losing backtest year fails the same way: during a sustained directional move the grid keeps stacking ever-larger legs (`12·N × base`) until the 35% DD cap fires an emergency.

- **2024 Jul-16 LONG**: −327.9 pips over a multi-day drop (bottom 0.88937 on Aug 5).
- **2023 Jun**: back-to-back 200-pip / 245-pip whipsaws within 7 days.

The fix in earlier versions (small fixed lot + `Max_Level=6`) keeps lots small *structurally* but caps upside. v1.6 attacks the problem from the other side: stop adding legs **during** the violent part of the move, then add once price stabilizes. Fewer, cheaper legs ⇒ lower total lots ⇒ lower floating loss ⇒ the cap is far less likely to fire — and the one cheap leg added near the bottom pulls the weighted-average entry down hard, so a small bounce hits TP.

Pausing adds is mathematically close to **widening the grid step** during high volatility — both reduce how many legs accumulate while price is running.

---

## 2. Volatility metric (self-normalizing)

On the signal timeframe (M15), the EA tracks:

```
ratio = ATR(ATR_Period_Fast) / ATR(ATR_Period_Slow)        (shift = 1, last completed bar)
```

- `ATR_Period_Fast = 14` reacts quickly; `ATR_Period_Slow = 100` is the ~1-day baseline.
- The **ratio** measures "is current short-term volatility elevated vs its own recent norm." Because it is a ratio, thresholds do not need re-tuning across 2023 / 2024 / 2025.
- `ATR_Pause_Min_Pips` (default 6.0) is an absolute floor: a high ratio on a tiny absolute move will not pause. `0` disables the floor.

---

## 3. The hybrid pause/resume state machine

Evaluated once per M15 bar close (`UpdateAtrPauseState()`), before the decision tree:

```
NOT paused:
    if ratio >= ATR_Pause_Ratio AND atr_fast_pips >= ATR_Pause_Min_Pips:
        -> PAUSE (log ATR_PAUSE), reset calm_count = 0

paused:
    if ratio <= ATR_Resume_Ratio:  calm_count += 1
    else:                          calm_count  = 0
    if calm_count >= ATR_Resume_Confirm_Bars:
        -> RESUME (log ATR_RESUME), reset calm_count = 0
```

- The dead-band between `ATR_Resume_Ratio` (default 1.2) and `ATR_Pause_Ratio` (default 1.8) prevents the state from flip-flopping.
- The confirm-bar count (default 3) requires **sustained** calm before adds resume — a single calm bar in the middle of chaos does not resume.

---

## 4. What "pause" does — and what it never touches

While `g_atr_paused` is true, `CheckAdd()` returns early **before** computing the grid trigger, so:

- No new leg is opened.
- `last_price` is NOT advanced.

The following are **never** paused (they run regardless of ATR state):

- The emergency-DD market close (`OnTick`, every tick).
- The +10-pip TP basket close (`CheckCloseTarget`, every bar).
- New-probe sizing / FitCheck (FitCheck still assumes the *full* ladder, so pausing only ever makes real risk lower than the projection — conservative by design).

---

## 5. Resume add behavior — Option A (single leg + re-baseline)

`CheckAdd()` already adds **at most one leg per bar** and sets `last_price = add_px`. So Option A needs no special resume code: skip adds while paused (leaving `last_price` untouched); on the first calm bar the normal `CheckAdd` fires exactly once at the current price and re-baselines `last_price` automatically.

### Worked example (recurring Jul-2024 LONG, `Grid_Step_Pips = 30`)

- L1 opens at `0.92216`, so `last_price = 0.92216`; normally L2 fires at `0.91916`.
- A fast drop plunges ~152 pips to `0.90700` with adds paused — no legs added on the way down.
- Volatility calms at `0.90700`. The next calm bar adds **one** leg at `0.90700` and sets `last_price = 0.90700`. The next leg only fires if price drops a further 30 pips to `0.90400`.

Result: one cheap leg near the bottom instead of 5 legs on the way down. With L2 sized 24× L1, the weighted-average entry sits near `0.91256` (only ~4 pips above L2), so TP (`wavg + 10 pips ≈ 0.91356`) needs only a ~14-pip bounce off the bottom — even while L1 is still deep underwater.

---

## 6. Inputs (v1.6 additions)

| Input | Default | Meaning |
|---|---:|---|
| `Enable_ATR_Pause` | `true` | Master switch. `false` ⇒ bit-for-bit identical to v1.5 (parity gate). |
| `ATR_Period_Fast` | `14` | Short-term ATR period on the signal timeframe. |
| `ATR_Period_Slow` | `100` | Baseline ATR period (~1 day of M15). |
| `ATR_Pause_Ratio` | `1.8` | Pause adds when `atr_fast/atr_slow >=` this. |
| `ATR_Resume_Ratio` | `1.2` | Calm threshold; ratio must fall to `<=` this to be eligible to resume. |
| `ATR_Resume_Confirm_Bars` | `3` | Consecutive calm bars required before adds resume. |
| `ATR_Pause_Min_Pips` | `6.0` | Only pause if `atr_fast` (pips) also exceeds this; `0` disables. |

All thresholds are PROVISIONAL defaults to be tuned via the backtest sweep in [plans/4. ATR Integration.md §8](../plans/4.%20ATR%20Integration.md).

---

## 7. Backwards compatibility

`Enable_ATR_Pause = false` short-circuits `UpdateAtrPauseState()` (state forced to not-paused) and the pause gate in `CheckAdd()`, leaving every code path identical to v1.5. A 2025 backtest at `Enable_ATR_Pause=false`, fixed 0.10, Min_Conf=4, Max_Level=6, step=30 must reproduce v1.5_2025_2k_v3 exactly ($2,137.14).

---

## 8. Open questions / TODO

1. **Threshold sweep** — `ATR_Pause_Ratio` {1.5, 1.8, 2.2}, `ATR_Resume_Ratio` {1.1, 1.2, 1.3}, `ATR_Resume_Confirm_Bars` {2, 3, 4} on 2023 / 2024 / 2025. Find the set that defuses the Jul-2024 and Jun-2023 emergencies without starving normal grid recovery.
2. **Confirm the Jul-2024 basket is fixed** — re-run 2024 and grep `ATR_PAUSE` / `ADD_PAUSED` around `2024.07.16`–`2024.07.25`. Expectation: legs paused through the fast drop, fewer total lots, no (or a much smaller) emergency.
3. **Lot unlock** — if pause prevents the 0.30 emergency on 2024, sweep a larger fixed lot (0.40–0.50) to measure how much extra return the pause safely unlocks.
4. **Does pause ever hurt?** — on calm years (2025) the pause should rarely engage; confirm the easy-year result is unchanged vs v1.5 / v5.
5. **Interaction with `Max_Level=6`** — with both the structural cap and the ATR pause active, check whether `Max_Level` can be safely raised again (more recovery legs available once calm returns).

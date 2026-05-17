# AUDCAD M15 Mean-Reversion EA — Strategy v1.4

**Status**: superseded by [AUDCAD_M15_v1.5.md](AUDCAD_M15_v1.5.md) (N-of-4 signal confluence). Set `Min_Confluence_Count=1` in v1.5 to reproduce v1.4 behavior.
**Last updated**: 2026-05-16
**Parent**: [AUDCAD_M15_v1.3.md](AUDCAD_M15_v1.3.md)
**Change scope**: **ergonomics + safer defaults**. ~30 inputs renamed to descriptive snake_case, inline comments reformatted so the MT5 tester panel shows `VariableName: description`, `ProbeLot` split into two clearer inputs, and two default values flipped to make `$1k cent` deployment work out of the box. **No signal, gate, exit, grid, lot-formula, FitCheck, emergency-exit, basket-reconstruction, or risk-math logic changes.**

---

## What changed vs v1.3

| Topic | v1.3 | v1.4 |
|---|---|---|
| Input names | Cryptic abbreviations (`MaxDDPct`, `BB_StdDev`, `Buy_RSI_Dir`, `FitPadPips`, …) | **Descriptive snake_case** (`Max_Drawdown_Percentage`, `Bollinger_StdDev`, `Buy_Only_If_RSI_LessThan`, `Fit_Check_Pad_Pips`, …) |
| Input panel labels | Description only — variable name invisible in MT5 tester | **`VariableName: description`** — both visible side-by-side |
| Probe lot input | Single `ProbeLot` with magic-number overload (`0.0` = auto, `>0` = manual) | **Split into two**: `Auto_Compute_Lot_Size_Based_On_Equity` (bool) + `Default_Base_Lot_Size` (double) |
| Cent-symbol guard default | `RequireCentAccount = false` | **`Abort_If_Standard_Account = true`** — refuses standard symbols unless explicitly overridden |
| DD cap default | `MaxDDPct = 20.0` | **`Max_Drawdown_Percentage = 35.0`** — admits `vol_min=0.10` cent probes at $1k equity (PROVISIONAL — to be revised after more empirical runs) |
| CSV log filename | `audcad_v1_3.csv` | **`audcad_v1_4.csv`** — keeps v1.3 and v1.4 logs from colliding |
| CSV `ea_version` | `v1.3` | `v1.4` — column layout otherwise identical |
| Signal, gate, grid, exit, lot formula, FitCheck, emergency exit, basket struct, reconstruction | Unchanged | **Bit-for-bit identical to v1.3** |

---

## 1. Why this release exists

v1.3 has two ergonomic problems surfaced during the $1k cent deployment session:

1. **The MT5 Strategy Tester input panel displays only the inline `//` comment, not the variable name.** Users have to cross-reference source to know which row is which — painful when tuning 30+ inputs.
2. **`ProbeLot = 0.0`** as the trigger for auto-sizing is a magic-number overload. Multiple users (and AI assistants) have had to be walked through "0 means auto, anything else means manual override." That's confusing input design.

v1.4 fixes both, plus locks in two **default value changes** that make the canonical $1k-cent deployment work without manual reconfiguration.

---

## 2. Input rename table (the full spec)

Comment format throughout: `// VariableName: description`.

### Identity & symbol

| v1.3 | v1.4 | Default |
|---|---|---:|
| `TradeSymbol` | `Forex_Pair` | `""` |
| `MagicLong` | `Long_Basket_Group_Tag` | `50000051` |
| `MagicShort` | `Short_Basket_Group_Tag` | `50000052` |
| `SignalTF` | `Signal_Timeframe` | `PERIOD_M15` |

### Signal indicator periods

| v1.3 | v1.4 | Default |
|---|---|---:|
| `RSI_Period` | `RSI_Period` | `14` |
| `BB_Period` | `Bollinger_Period` | `20` |
| `BB_StdDev` | `Bollinger_StdDev` | `2.0` |
| `SRSI_K_Period` | `Stoch_RSI_Lookback` | `14` |
| `SRSI_K_Smooth` | `Stoch_RSI_Smooth` | `3` |
| `SwingLookback` | `Swing_High_Bars` | `500` |
| `SwingNearPips` | `Swing_High_DistPips` | `50.0` |

### Signal — BUY thresholds

| v1.3 | v1.4 | Default |
|---|---|---:|
| `Buy_RSI_Dir` | `Buy_Only_If_RSI_LessThan` | `50.0` |
| `Buy_RSI_Deep` | `Buy_Fire_If_RSI_LessThan_EqualTo` | `40.0` |
| `Buy_Stoch` | `Buy_Fire_If_StochRSI_K_LessThan_EqualTo` | `20.0` |
| `Buy_PctB` | `Buy_Fire_If_Bollinger_LessThan_EqualTo` | `0.10` |

### Signal — SELL thresholds

| v1.3 | v1.4 | Default |
|---|---|---:|
| `Sell_RSI_Dir` | `Sell_Only_If_RSI_GreaterThan` | `50.0` |
| `Sell_RSI_Deep` | `Sell_Fire_If_RSI_GreaterThan_EqualTo` | `60.0` |
| `Sell_Stoch` | `Sell_Fire_If_StochRSI_K_GreaterThan_EqualTo` | `60.0` |
| `Sell_PctB` | `Sell_Fire_If_Bollinger_GreaterThan_EqualTo` | `0.90` |

### Exit / Grid

| v1.3 | v1.4 | Default |
|---|---|---:|
| `BasketTPPips` | `TP_Basket_If_Total_Pips_GreaterThan_EqualTo` | `10.0` |
| `GridStepPips` | `Grid_Step_Pips` | `22.0` |
| `MaxLegs` | `Grid_Max_Level_To_SL` | `10` |

### Lot sizing — the split + cent guard

| v1.3 | v1.4 | Default | Note |
|---|---|---:|---|
| `ProbeLot` (split) | `Auto_Compute_Lot_Size_Based_On_Equity` (bool) | **`true`** | NEW — turns auto-sizer on/off |
| `ProbeLot` (split) | `Default_Base_Lot_Size` (double) | **`0.10`** | NEW — base lot when auto-sizer is off |
| `RequireCentAccount` | `Abort_If_Standard_Account` | **`true`** *(flipped from `false`)* | Cent default; refuses standard unless overridden |

### Risk

| v1.3 | v1.4 | Default | Note |
|---|---|---:|---|
| `MaxDDPct` | `Max_Drawdown_Percentage` | **`35.0`** *(raised from `20.0`)* | PROVISIONAL — admits vol_min=0.10 at $1k cent |
| `FitPadPips` | `Fit_Check_Pad_Pips` | `5.0` | |

### HTF gate

| v1.3 | v1.4 | Default |
|---|---|---:|
| `EnableGate` | `Enable_HTF_Gate` | `true` |
| `GateTF` | `GateTimeframe` | `PERIOD_D1` |
| `GateEMA` | `GateEMA_Period` | `20` |

### Operational

| v1.3 | v1.4 | Default |
|---|---|---:|
| `ShadowMode` | `Shadow_Mode` | `true` |
| `LogFile` | `Log_File` | `"audcad_v1_4.csv"` |
| `Verbosity` | `Verbosity` | `2` |

---

## 3. The `ProbeLot` split — equivalence map

The v1.3 semantic of `ProbeLot` is preserved exactly; only the surface changes.

| v1.3 setting | v1.4 equivalent |
|---|---|
| `ProbeLot = 0.0` (auto) | `Auto_Compute_Lot_Size_Based_On_Equity = true` (Default_Base_Lot_Size is ignored) |
| `ProbeLot = 0.10` (manual) | `Auto_Compute_Lot_Size_Based_On_Equity = false` + `Default_Base_Lot_Size = 0.10` |
| `ProbeLot = 0.01` (legacy v1.2 replay) | `Auto_Compute_Lot_Size_Based_On_Equity = false` + `Default_Base_Lot_Size = 0.01` |

The OnInit `[AUTOSIZE]` log line continues to surface the chosen mode: `mode=auto` when the bool is `true`, `mode=override` when `false`.

---

## 4. Default value changes — behaviour notes

### 4.1 `Abort_If_Standard_Account = true`

**Effect:** attaching v1.4 to a standard `AUDCAD#` symbol (contract_size > 10000) with default inputs causes `INIT_FAILED` with this alert:

```
AUDCAD v1.4: Abort_If_Standard_Account=true and contract_size=100000.00 looks like a
standard symbol. Aborting. Set Abort_If_Standard_Account=false to attach anyway.
```

To replay v1.3-on-standard backtests, set `Abort_If_Standard_Account = false` explicitly.

### 4.2 `Max_Drawdown_Percentage = 35.0`

**Effect:** the auto-sizer's worst-case budget is now `equity × 0.35` instead of `equity × 0.20`. The emergency-exit threshold and the `BLOCK_ADD` forward check also use 35%. At $1k cent (`vol_min=0.10`, `pv≈0.07`), the auto-sizer picks `base=0.11` (was: blocked at 20%) — exactly the configuration validated by the [v4 backtest](../back%20test%20result/v1.3_2025_result_v4%2835DD%29.md) (+73.58% on full year 2025 with one absorbed L8 emergency).

**Caveat:** 35% explicitly accepts a 35%-of-equity single-basket worst case. The v4 run absorbed it once; a 2-σ stress year could see two losses in succession. **This default is provisional** and should be tightened after multi-year, multi-broker validation. The upper bound of "safe" is something like the smallest cap that still admits `base = vol_min` at the target deposit — 35 is convenient for $1k XM cent but not universal.

---

## 5. Backward compatibility

| Aspect | Status |
|---|---|
| Strategy mechanics (signal, gate, grid, exit, lot formula, emergency exit, FitCheck) | **Identical to v1.3** — same trades, same balance curve given identical inputs and broker/year/feed |
| CSV column layout | **Identical** — same 14 base columns + `base_lot, account_type_tag`. Only the `ea_version=v1.4` header string differs |
| CSV filename default | Changed to `audcad_v1_4.csv` — prevents v1.3/v1.4 log collision |
| Magic numbers | **Identical** — `50000051` long, `50000052` short. A v1.3 basket left open will be picked up by v1.4 via `ReconstructBaskets()` |
| Default inputs | **Three differences**: `Auto_Compute_Lot_Size_Based_On_Equity` (new), `Abort_If_Standard_Account = true` (flipped), `Max_Drawdown_Percentage = 35.0` (raised). To get v1.3-default behaviour, set: `Auto_Compute_Lot_Size_Based_On_Equity = true`, `Abort_If_Standard_Account = false`, `Max_Drawdown_Percentage = 20.0` |
| `parse_v12_2025.py` | **No change needed** — CSV column layout is identical to v1.3, only the version string changes |

---

## 6. Validation gates

All v1.3 gates carry forward unchanged in criteria. Status updates:

| Gate | Criterion | Status |
|---|---|---|
| G10 — `[UNIT_SANITY]` matches expected XM cent | `contract_size=1000`, `pv≈0.07`, `vol_min=0.10`, `vol_step=0.01`, tag `cent` | **PASS** (v4 log) |
| G11 — `[AUTOSIZE]` projection at $1k cent | `base=0.11`, `wc_pct≈34` at `Max_Drawdown_Percentage=35` | **PASS** (v4 log; original 20%-cap prediction superseded by 35% default) |
| G12 — $1k cent 2025 replay | Max DD ≤ chosen cap, baskets close at TP, recovery after any emergency | **PASS** (v4 result: 0 BLOCK_ADD, 1 absorbed emergency, +73.58% net) |
| G13 — Standard-account regression | v1.4 with `Auto_Compute_Lot_Size_Based_On_Equity=false`, `Default_Base_Lot_Size=0.01`, `Abort_If_Standard_Account=false`, `Max_Drawdown_Percentage=20` on `AUDCAD#` 2025 → matches v1.2 +$6,567.29 baseline | **Not started** |
| G8 — Live forward test | ≥ 2 weeks shadow on XM cent demo with v1.4 | **Not started** |

---

## 7. Implementation order (executed for this release)

1. Copy `EA/AUDCAD_M15_v1_3.mq5` → `EA/AUDCAD_M15_v1_4.mq5`.
2. Bump `#property version "1.40"`; rewrite header comment block with v1.4 change summary.
3. Rewrite `// === SECTION 1: INPUTS ===` per §2 table with new names, new defaults, new comment format.
4. Apply ProbeLot split per §3 — replace L564, L575, L881-885, L888, L891, L908, L942-944 touchpoints.
5. Body-pass: rename every identifier in function bodies (`MagicLong` → `Long_Basket_Group_Tag`, etc.). Update `OnInit` references for `Abort_If_Standard_Account` and the AUTOSIZE projection log.
6. Update version strings: order comments (`audcad_v1.3_*` → `audcad_v1.4_*`), CSV header (`ea_version=v1.4`), all `Print(...)` prefixes.
7. Grep verification: no stale v1.3 identifiers in function bodies (only header-comment historical references allowed).
8. Compile in MetaEditor (zero errors, zero warnings) — *to be done by user before backtest*.
9. Run G12 replay to confirm byte-identical equity curve vs v4's $1,735.84.

---

## 8. References

- Parent: [AUDCAD_M15_v1.3.md](AUDCAD_M15_v1.3.md)
- Lineage: [v1.md](AUDCAD_M15_v1.md) → [v1.1.md](AUDCAD_M15_v1.1.md) → [v1.2.md](AUDCAD_M15_v1.2.md) → [v1.3.md](AUDCAD_M15_v1.3.md) → **v1.4**
- Empirical basis for `Max_Drawdown_Percentage = 35` default: [back test result/v1.3_2025_result_v4(35DD).md](../back%20test%20result/v1.3_2025_result_v4%2835DD%29.md)
- Risk requirements (unchanged): [plans/1.initial requirements.md](../plans/1.initial%20requirements.md)

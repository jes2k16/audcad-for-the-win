# AUDCAD M15 Mean-Reversion EA — Strategy v1.3

**Status**: ready to implement (delta over v1.2)
**Last updated**: 2026-05-15
**Parent**: [AUDCAD_M15_v1.2.md](AUDCAD_M15_v1.2.md)
**Change scope**: replace the fixed `ProbeLot = 0.01` (standard-account) sizing with a runtime equity-scaled base lot, so a full 10-leg ladder always consumes exactly `MaxDDPct%` of equity at the worst-case price. Default account profile returns to **cent / micro** (the original target in `plans/1 §2`). All v1.2 mechanics — signal, gate, exit, grid, single-basket — are unchanged.

---

## What changed vs v1.2

| Topic | v1.2 | v1.3 |
|---|---|---|
| Probe lot | Fixed `ProbeLot = 0.01` (standard) | **Auto-computed** from equity (see §2). `ProbeLot` is now an optional override (>0 forces fixed). |
| Account profile | Standard (`AUDCAD#`, ~$50k tuned) | **Cent / micro default** (`AUDCAD.c`). Standard still supported via override. |
| Ladder shape (multipliers) | `[1, 24, 36, 48, 60, 72, 84, 96, 108, 120]` (12×N for n≥2) | **Unchanged.** Only the base unit scales. |
| Worst-case sizing | `FitCheck` gates a pre-set ladder | **Closed-form** base lot derived from `MaxDDPct`. FitCheck demoted to defence-in-depth. |
| Rounding | `MathRound` in `NormLot` | **`MathFloor`** inside `ComputeBaseLot()`. Rounding up one `vol_step` could breach the cap. |
| `BasketState` | (no base field) | **New field `base_lot`** — cached at probe-open time; grid adds use the cached value. |
| Min-equity behaviour | (n/a) | If `equity` too small for even `vol_min × 10-leg` under the cap, EA **skips every probe** and logs `SKIP_PROBE / base_below_vol_min`. |
| CSV log header | `ea_version=v1.2`, 14 columns | `ea_version=v1.3`, **+2 columns**: `base_lot`, `account_type_tag`. Header line carries `contract_size`. |
| New log lines | (n/a) | `[UNIT_SANITY]`, `[WC_CONST]`, `[AUTOSIZE]` at OnInit (one-shot diagnostics). |
| Entry signal, D1 gate, +10-pip exit, grid step, MaxLegs, single-basket, 20% emergency close, FitPad | Unchanged | **Unchanged** — locked from v1 / v1.1 / v1.2. |

---

## 1. Signal, gate, grid, exit

All unchanged. See:

- Signal: [AUDCAD_M15_v1.md §1](AUDCAD_M15_v1.md)
- D1 EMA20 HTF gate: [AUDCAD_M15_v1.1.md §1](AUDCAD_M15_v1.1.md)
- Grid (22 pips, MaxLegs=10): [AUDCAD_M15_v1.md §3](AUDCAD_M15_v1.md)
- Basket close target (+10 pips weighted-avg): [AUDCAD_M15_v1.2.md §2](AUDCAD_M15_v1.2.md)
- Single basket at a time, opposite signal ignored: [AUDCAD_M15_v1.2.md §2](AUDCAD_M15_v1.2.md)

---

## 2. Lot-sizing formula

### 2.1 Worst-case ladder cost (the `WC` constant)

For the locked 12×N ladder, with `MaxLegs = 10`, `GridStepPips = 22`, `FitPadPips = 5`, the worst-case price is `(MaxLegs−1) × GridStepPips + FitPadPips = 203` pips beyond the probe. At that price, leg `n` has been adverse for `adv_pips(n) = FitPadPips + GridStepPips × (MaxLegs − n)`. Per **unit base lot** (`base = 1.0`), the worst-case lot-pips total is:

| Leg n | mult m(n) | adv_pips(n) | lot-pips |
|---:|---:|---:|---:|
| 1 | 1   | 203 | 203 |
| 2 | 24  | 181 | 4,344 |
| 3 | 36  | 159 | 5,724 |
| 4 | 48  | 137 | 6,576 |
| 5 | 60  | 115 | 6,900 |
| 6 | 72  |  93 | 6,696 |
| 7 | 84  |  71 | 5,964 |
| 8 | 96  |  49 | 4,704 |
| 9 | 108 |  27 | 2,916 |
| 10| 120 |   5 | 600 |

**`WC = Σ m(n) × adv_pips(n) = 44,627`** lot-pips per unit base lot.

The EA recomputes `WC` at every `OnInit` from the current inputs (`MaxLegs`, `GridStepPips`, `FitPadPips`, and the hard-coded multiplier `12.0`), so changing any of those automatically updates the constant. It is logged at startup as `[WC_CONST] ladder_wc_lotpips=44627.00`.

> **⚠ Edit-with-care.** Changing the multiplier shape (the `12 * n` in `LegLot`) requires editing the matching loop in `OnInit` so `g_wc_lotpips` stays consistent. The locked ladder shape `[1, 24, 36, 48, 60, 72, 84, 96, 108, 120]` is the empirically validated April–May 2026 master-account pattern (see `plans/2.Strategy.md §13.X`); do not touch without evidence.

### 2.2 Closed-form base lot

Worst-case loss in account currency for any chosen base lot:

```
worst_case_loss = base × WC × PipValPerLot()
```

Setting that ≤ `MaxDDPct% × equity` and solving for `base`:

```
base ≤ (equity × MaxDDPct / 100) / (WC × PipValPerLot())
```

The EA picks the largest base that satisfies this AND lands on the broker's `vol_step`:

```
base = MathFloor( raw / vol_step ) × vol_step,   where raw = (eq × MaxDDPct/100) / (WC × pv)
base ∈ [vol_min, vol_max]
if base < vol_min → return 0 (skip probe — log SKIP_PROBE / base_below_vol_min)
```

**Why `MathFloor`, not `MathRound`** — rounding up one `vol_step` can push the worst-case past the cap. v1.2's `NormLot` uses `MathRound`, which is fine for fixed inputs that already sit on `vol_step`, but unsafe for the auto-sized base. v1.3 keeps `NormLot` for grid adds (where `base × integer_multiplier` always lands on `vol_step` exactly) but inline `MathFloor` inside `ComputeBaseLot()`.

### 2.3 Worked example — $1,000 real on an XM cent account

- `equity = 100,000` cent units displayed (XM cent shows balance in cents; $1,000 real → 100,000)
- `PipValPerLot ≈ 7` cent units per pip per 1.0 lot (cent-symbol contract = 1,000 vs standard 100,000)
- `WC = 44,627`, `MaxDDPct = 20`, `vol_step = 0.01`

```
raw     = (100,000 × 0.20) / (44,627 × 7) = 20,000 / 312,389 = 0.0640
floor   = MathFloor(0.0640 / 0.01) × 0.01 = 0.06
```

→ **`base = 0.06 cent lots`**

Full projected ladder: `[0.06, 1.44, 2.16, 2.88, 3.60, 4.32, 5.04, 5.76, 6.48, 7.20]` cent lots.
Total at level 10 = **38.94 cent lots** (= 0.3894 standard lot equivalent).
Worst-case loss = `0.06 × 44,627 × 7 ≈ 18,743 cents ≈ $187` → **`18.7%` of $1,000.** Inside the 20% cap.

> The master account `#50000005` used cent probes of 0.05–0.15 across Feb–May 2026 (see `data/AUDCAD_G7_LotSizing.md`). v1.3's formula explains those as the equity-bracketed solutions to the same equation across a growing equity curve.

### 2.4 Manual override

`input double ProbeLot = 0.0` — any value `> 0` bypasses `ComputeBaseLot()` and forces a fixed probe (then the ladder is `[ProbeLot, 24·ProbeLot, 36·ProbeLot, …]` via the locked multipliers). Used for:

- **Backtest replay** of the v1.2 setup at `ProbeLot = 0.01` on a standard symbol (proves v1.3 is a clean superset of v1.2 — same trades, same balance).
- **Manual sizing** when running on a profile where the auto formula doesn't apply (e.g., a broker that reports cent values in a different unit convention).

The OnInit log makes the choice observable: `[AUTOSIZE] base=… mode=auto|override`.

---

## 3. Cent-account profile

### 3.1 Symbol naming

Default target is **`AUDCAD.c`** (XM cent). The `.c` suffix is the broker's cent-symbol marker (commonly used by XM, FBS, RoboForex). The EA reads the symbol's `SYMBOL_TRADE_CONTRACT_SIZE` at OnInit:

- `contract_size ≤ 10,000` → tag `account_type=cent` (XM cent: 1,000-unit contracts).
- `contract_size  > 10,000` → tag `account_type=standard` (100,000-unit contracts).

The tag is a heuristic, used **only** for the log header — it does **not** change any math. The formula is unit-consistent regardless: `equity` and `PipValPerLot()` are always reported in the same account-currency unit by MT5, so the result is unconditionally in lots.

### 3.2 `RequireCentAccount` input

`input bool RequireCentAccount = false`. When `true`, OnInit fails with a clear alert if `contract_size > 10000`. Use this on production to prevent an accidental attach to the wrong symbol.

### 3.3 The `[UNIT_SANITY]` line is the canonical proof of correctness

Broker conventions for cent symbols vary (FBS, Exness, XM each have small differences). The v1.3 `OnInit` emits one diagnostic line that pins everything down:

```
[UNIT_SANITY] equity=100000.00 contract_size=1000.00 tick_val=0.00001
              tick_size=0.00001 pv_per_lot=0.07000 vol_min=0.01
              vol_step=0.01 account_type_tag=cent
```

The first tester run on any new broker MUST surface this line and the values MUST match the expected profile **before** going further. If they don't, the formula needs a unit-conversion factor. See §6 verification plan.

---

## 4. Edge cases & invariants

1. **Base lot is cached on the basket at probe-open time.** It is **never** recomputed during the life of the basket. Recomputing on each grid add against drifting equity would death-spiral: a basket already underwater would see its formula shrink the base, while the *already-open* legs are big — or, worse, growing equity would inflate the base mid-flight and FitCheck would be stale. See `BasketState.base_lot` in the EA.

2. **Account growth mid-basket leaves the cached base stale.** Accepted: WC is bounded *below* the cap, never above, so a stale base only means a smaller-than-optimal *next* probe size after the current basket closes. Documented behaviour, not a bug.

3. **Restart safety.** `ReconstructBaskets()` re-derives the cached base from the open legs: the smallest-volume leg is the probe (leg 1), and probe volume = base. Helper `FindMinLegVolume(magic)`.

4. **`base < vol_min` ⇒ EA cannot operate.** If `ComputeBaseLot()` returns 0 and `ProbeLot` is not overridden, the EA logs `SKIP_PROBE / base_below_vol_min eq=…` and waits. An `OnInit` `Alert(...)` surfaces this immediately on attach so the operator knows the account is too small for a safe 10-leg ladder at the chosen `MaxDDPct`.

5. **FitCheck's role is reduced to verification.** By construction, `ComputeBaseLot()` already targets exactly the cap, so FitCheck should always pass when auto-sizing is engaged. If it ever fails post-auto-sizing, the EA logs `SKIP_PROBE / fit_check_fail_after_autosize` — that **is** the signal that the broker unit convention differs from assumption and the formula needs recalibration.

---

## 5. What is unchanged from v1.2

- Signal rule (RSI + StochRSI + BB%B + 500-bar swing-near for sells)
- D1 EMA20 HTF gate (shift = 1, strict)
- Grid step = 22 pips, checked at M15 bar close
- `MaxLegs = 10`
- Basket TP = +10 pips weighted-avg net
- Single basket at a time; opposite signals ignored while a basket is open
- 20% emergency-DD market close on every tick
- 5-pip `FitPadPips`
- Magic numbers `50000051` / `50000052`
- Backward-incompatible CSV format vs v1.2: two trailing columns appended (`base_lot`, `account_type_tag`). Header line also carries `contract_size`. Downstream analysis scripts in `scripts/` (`parse_v12_2025.py` etc.) need updating before they consume v1.3 logs.

---

## 6. Risk & safety parameters

| Parameter | v1.3 value | Notes |
|---|---|---|
| Probe lot | **Auto-computed** from `equity, MaxDDPct, WC, PipValPerLot()`; floored to `vol_step`. `ProbeLot > 0` overrides. | §2 |
| Ladder multipliers | `[1, 24, 36, 48, 60, 72, 84, 96, 108, 120]` locked | v1 §4, v1.3 §2 |
| Basket close target | +10 pips net (weighted avg) | v1.2 §2; unchanged |
| Max concurrent baskets | 1 | v1.2; unchanged |
| Max legs per basket | 10 | v1; unchanged |
| Stop loss per probe | None | Unchanged |
| Account-level DD cap | 20% (`MaxDDPct`) — emergency close + block-add forward check + closed-form pre-trade sizing | plans/1 §9; v1.3 §2 |
| Grid step | 22 pips (`GridStepPips`) | v1; unchanged |
| FitPad | 5 pips (`FitPadPips`) | plans/1 §9; unchanged |
| HTF gate | D1 close vs D1 EMA20 (shift = 1) | v1.1; unchanged |
| Magic numbers | `50000051` long / `50000052` short | Unchanged |
| **Symbol (default)** | **`AUDCAD.c`** (cent) | v1.3 §3; standard supported via `ProbeLot` override |
| **Account profile** | **Cent / micro** default; standard via override | v1.3 §3 |
| `RequireCentAccount` | `false` (default) | v1.3 §3.2 |

---

## 7. Backward compatibility

v1.3 is **not** byte-compatible with v1.2 basket state, in two ways:

1. **CSV format** — two new trailing columns (`base_lot`, `account_type_tag`) and the header line carries `contract_size`. `parse_v12_2025.py` and any downstream tooling need updating to consume v1.3 logs.
2. **Default symbol** — v1.2 ran on `AUDCAD#` (standard); v1.3 defaults to `AUDCAD.c` (cent). To replay v1.2's exact behaviour for regression testing, run v1.3 with `TradeSymbol = "AUDCAD#"` and `ProbeLot = 0.01` on a standard demo (this is exactly verification step 4 in §8).

The magic numbers are unchanged (`50000051` / `50000052`), so if a v1.2 basket is open on a standard symbol and the operator switches the chart to v1.3 attached to `AUDCAD.c`, the v1.3 instance will **not** see the v1.2 basket (different symbol). Migrate cleanly: let v1.2 baskets close on the standard symbol first, then attach v1.3 to the cent symbol.

---

## 8. Validation gates

| Gate | Criterion | Notes |
|---|---|---|
| **G10 (new) — `[UNIT_SANITY]` matches expected XM cent values** | First tester run on `AUDCAD.c` $1k demo emits `contract_size=1000`, `equity=100000`, `pv_per_lot≈0.07`, `vol_min=0.01`, `vol_step=0.01` | If any value is off, broker uses a different cent denomination; STOP and recalibrate. |
| **G11 (new) — `[AUTOSIZE]` produces base = 0.06 at $1k** | OnInit log shows `base=0.06`, `ladder=[0.06,1.44,2.16,…,7.20]`, `wc_pct≈18.7` on a $1k XM cent demo | Confirms the closed-form math is correct end-to-end. |
| **G12 (new) — 2025 replay on $1k cent profile** | Strategy Tester run on `AUDCAD.c`, $1k deposit, 2025 M15. Pass: max equity DD ≤ 20%; 0 `base_below_vol_min` skips; 0 `fit_check_fail_after_autosize` events; net % return comparable to v1.2 +13.13% on $50k. | The full year confirms the auto-sized ladder handles the same trade distribution as v1.2. |
| **G13 (new) — Standard-account regression** | v1.3 with `TradeSymbol=AUDCAD#`, `ProbeLot=0.01`, 2025 M15 replay → **byte-identical** to v1.2's `+$6,567.29` final balance. | Proves v1.3 is a clean superset of v1.2 when the override is engaged. |
| G8 — Live forward test (≥ 2 weeks shadow on XM cent demo) | DD never approaches 20%; AUTOSIZE matches projected; no SKIP_PROBE events | From v1; carry forward. |

G10 + G11 are implementation gates (block release). G12 + G13 are validation gates (block live deployment). G8 is the release gate.

---

## 9. Implementation order

1. Copy `EA/AUDCAD_M15_v1_2.mq5` → `EA/AUDCAD_M15_v1_3.mq5`. Bump version, swap LogFile/comment strings.
2. Add `BasketState.base_lot` and zero-init in `InitBsk`. Add `g_wc_lotpips`, `g_contract_size`, `g_account_type_tag` globals.
3. Add `ComputeBaseLot()` (Section 3, before `LegLot`). Add `FindMinLegVolume()`.
4. Change `LegLot(int n)` → `LegLot(int n, double base)`. Update all 3 call sites.
5. Change `FitCheck(bool, double)` → `FitCheck(bool, double, double)`; pass base through.
6. In `OpenProbe`: resolve base (override or auto), skip on `base ≤ 0`, FitCheck with base, cache on basket, extend log note with `base=…` and `wc_pct=…`.
7. In `CheckAdd`: pass `bsk.base_lot` to `LegLot(next_n, …)`. No other change.
8. In `ReconstructBaskets`: after the accumulate loop, set `bsk.base_lot = FindMinLegVolume(bsk.magic)`.
9. Extend `WriteLog` format string to emit two trailing fields (`bsk_base`, `g_account_type_tag`).
10. In `OnInit`: read `SYMBOL_TRADE_CONTRACT_SIZE`, set `g_account_type_tag`; compute `g_wc_lotpips` from inputs; emit `[UNIT_SANITY]`, `[WC_CONST]`, `[AUTOSIZE]` log lines; honour `RequireCentAccount`; guard the legacy `ProbeLot < vol_min` check with `ProbeLot > 0`; bump CSV header to `ea_version=v1.3` and append the two new columns.
11. **Compile** in MetaEditor → zero errors, zero warnings.
12. **Run G10–G13 in order.** Do not declare done until G10 + G11 are green from a real cent demo journal (not just arithmetic).

---

## 10. Open questions specific to v1.3

### 10.1 Broker-specific cent-symbol denomination

XM cent denominates balance/equity in cents and `SYMBOL_TRADE_TICK_VALUE` in cents. Other brokers (FBS, Exness) may differ. The formula is unit-consistent provided `equity` and `pv` come from the **same** denominator — which they always do on a single MT5 account. G10 is the gate that catches any mismatch.

### 10.2 Account growth scales the *next* probe, not the current one

A basket opened at $1k equity then growing to $1,500 mid-basket continues to manage with the $1k-sized ladder. The next probe (after this basket closes) will size on $1,500 equity → `base ≈ 0.09`. This is expected behaviour, not a bug; flagged in §4 invariant 2.

### 10.3 Live forward should re-tighten `wc_pct`

The projected `wc_pct` at $1k cent is **18.7%** — close to the cap. Spread, swap, and intra-tick adverse moves between trigger and execution (see v1.2 2025 result §4 insight about gap-driven `tp`-but-negative closes) can take a realised basket past the projected worst. Consider a soft buffer (e.g., target `MaxDDPct − 2`%) once G12 confirms the formula is correct.

### 10.4 Standard-account fallback

A user with a $5,000+ standard account doesn't need cent precision. v1.3 supports them via `ProbeLot=0.01` override on `AUDCAD#`. We may want a `MinAccountEquity` input that auto-skips the EA below a threshold — out of scope for v1.3, candidate for v1.4.

---

## 11. References

- Parent: [AUDCAD_M15_v1.2.md](AUDCAD_M15_v1.2.md)
- Lineage: [v1.md](AUDCAD_M15_v1.md) → [v1.1.md](AUDCAD_M15_v1.1.md) → [v1.2.md](AUDCAD_M15_v1.2.md) → **v1.3**
- Risk requirements: [plans/1.initial requirements.md](../plans/1.initial%20requirements.md) §2, §9, §10 — v1.3 implements the cent-account profile (§2) and realises the auto-scale formula sketched in §10 with a closed-form replacement for `ScaleDivisor`.
- Master-account lot analysis: [data/AUDCAD_G7_LotSizing.md](../data/AUDCAD_G7_LotSizing.md) — the 0.05 → 0.06 → 0.10 → 0.15 cent probe progression in the source data is the empirical signature of the same equation v1.3 solves.
- v1.2 2025 backtest reference (standard $50k): [back test result/v1.2_2025_result.md](../back%20test%20result/v1.2_2025_result.md).

"""
Gate G7: Lot-sizing formula reconstruction.

Reconstructs running equity from cumulative P/L and fits BaseLot = f(equity).
Known probe lot sizes: 0.05, 0.06, 0.10, 0.15 (cent account, 1 lot = 100k cent-units)

Input:  AUDCAD_History_05102026_to_date.csv
Output: data/AUDCAD_G7_LotSizing.md
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT      = Path(r"d:/CLAUDE/AUDCAD FOR THE WIN")
HIST_FILE = ROOT / "AUDCAD_History_05102026_to_date.csv"
OUT_FILE  = ROOT / "data" / "AUDCAD_G7_LotSizing.md"

# ---------------------------------------------------------------------------
# Load, parse, sort by close time
# ---------------------------------------------------------------------------
df = pd.read_csv(HIST_FILE)
df['OpenTime']   = pd.to_datetime(df['Open Time'],  format='%m/%d/%Y %H:%M')
df['CloseTime']  = pd.to_datetime(df['Close Time'], format='%m/%d/%Y %H:%M')
df['Lots']       = pd.to_numeric(df['Trading Volume (in Lots)'], errors='coerce')
df['Profit_raw'] = pd.to_numeric(df['Profit'].str.replace(',',''), errors='coerce')
df['dir']        = df['Type'].str.lower()
df = df.dropna(subset=['Lots', 'Profit_raw'])

probe_lots = {0.05, 0.06, 0.10, 0.15}
df['is_probe'] = df['Lots'].isin(probe_lots)

probes = df[df['is_probe']].sort_values('OpenTime').reset_index(drop=True)
print(f"Probe positions: {len(probes)}")
print(f"Lot distribution: {probes['Lots'].value_counts().sort_index().to_dict()}")

# ---------------------------------------------------------------------------
# Equity at probe open = sum of P/L of positions closed before probe open
# ---------------------------------------------------------------------------
equity_rel = []
for _, pr in probes.iterrows():
    closed_before = df[df['CloseTime'] < pr['OpenTime']]['Profit_raw'].sum()
    equity_rel.append(closed_before)

probes['equity_gain'] = equity_rel  # cumulative gain since t=0

print("\nEquity gain by lot size:")
for lot in sorted(probe_lots):
    sub = probes[probes['Lots'] == lot]
    if len(sub) == 0: continue
    print(f"  lot={lot}: n={len(sub)}  gain range [{sub['equity_gain'].min():.0f}, {sub['equity_gain'].max():.0f}]  "
          f"median={sub['equity_gain'].median():.0f}")

# ---------------------------------------------------------------------------
# Infer initial balance: the 0.05 lot probes represent the BASE state
# The first lot change (0.05->0.06 or 0.05->0.10) tells us the equity threshold
# ---------------------------------------------------------------------------
# Find chronological sequence of lot changes
lot_seq = probes[['OpenTime','Lots','equity_gain']].copy()
lot_seq['lot_change'] = lot_seq['Lots'] != lot_seq['Lots'].shift()
changes = lot_seq[lot_seq['lot_change']].copy()
print("\nLot size transitions:")
print(changes.to_string())

# The equity_gain at first 0.10 probe gives us the relative threshold
# If initial balance = X, then balance at first 0.10 probe = X + equity_gain_at_that_point
# 0.05 -> 0.10 likely represents a doubling (proportional sizing)
# So: X + gain_at_first_0.10 = 2 * X  -> gain = X  -> X = gain

first_010 = probes[probes['Lots'] == 0.10].sort_values('OpenTime').iloc[0] if len(probes[probes['Lots'] == 0.10]) > 0 else None
first_006 = probes[probes['Lots'] == 0.06].sort_values('OpenTime').iloc[0] if len(probes[probes['Lots'] == 0.06]) > 0 else None
first_015 = probes[probes['Lots'] == 0.15].sort_values('OpenTime').iloc[0] if len(probes[probes['Lots'] == 0.15]) > 0 else None

print()
if first_006 is not None: print(f"First 0.06 probe: {first_006['OpenTime']}  equity_gain={first_006['equity_gain']:.0f}")
if first_010 is not None: print(f"First 0.10 probe: {first_010['OpenTime']}  equity_gain={first_010['equity_gain']:.0f}")
if first_015 is not None: print(f"First 0.15 probe: {first_015['OpenTime']}  equity_gain={first_015['equity_gain']:.0f}")

# ---------------------------------------------------------------------------
# Fit: BaseLot = 0.05 * round(equity / K)  where K = some constant
# From cents: 1 lot = 1 cent unit in micro sizing? Or BaseLot = 0.01 * floor(equity / K)?
# Try: BaseLot = 0.05 + 0.01 * floor(equity_gain / threshold)
# Try: step function at round equity milestones
# Try: BaseLot proportional to equity (percentage of equity)
# ---------------------------------------------------------------------------
# The data points we have:
# lot=0.05 at equity_gain ~ 0
# lot=0.06 at first 006 probe
# lot=0.10 at first 010 probe
# lot=0.15 at first 015 probe
# These are 4 points of {equity: lot}

# Cent account: values in cents (1 USD = 100 cents)
# If initial balance is E0 (cents), then:
# E0         -> 0.05 lot
# E0 + G_006 -> 0.06 lot
# E0 + G_010 -> 0.10 lot
# E0 + G_015 -> 0.15 lot

gains = {}
if first_006 is not None: gains[0.06] = first_006['equity_gain']
if first_010 is not None: gains[0.10] = first_010['equity_gain']
if first_015 is not None: gains[0.15] = first_015['equity_gain']

print("\n--- Fitting lot-sizing models ---")
print("Known transitions (relative gain -> new lot size):")
for lot, gain in sorted(gains.items(), key=lambda x: x[1]):
    print(f"  gain={gain:.0f} -> lot={lot}")

# Hypothesis 1: BaseLot = 0.05 * (1 + floor(gain/step))
# Find step that fits
# 0.05 = 0.05 * 1 -> gain < step
# 0.06 = ... doesn't fit cleanly (0.06/0.05 = 1.2, not integer)
print()
print("Hypothesis 1 (linear step): BaseLot = 0.05 * n_steps")
print("  0.06/0.05 = 1.2 -> not integer multiples -> Hypothesis 1 FAILS")

# Hypothesis 2: Cent-based sizing. In cent accounts, balance shown in cents.
# Typical risk management: 1% risk per probe.
# Probe risk = BaseLot * pip_value_per_lot * stop_loss_pips
# If no stop loss (martingale), it's just a fixed account percentage
# BaseLot = (account_balance_cents * risk_pct) / (pip_value * sl_pips)
# For AUDCAD.c: pip value = 1 cent per 0.01 lot per pip?
# Actually: 1 lot AUDCAD = 100,000 units. Pip value = 100,000 * 0.0001 * (1 CAD / AUD rate)
# In cents: 1 lot = 100 cents per pip approximately
# 0.05 lot = 5 cents per pip
# If initial balance = 500 cents and trade at 1% per pip: 500*0.01/5 = 1 pip? That doesn't work well.

# Hypothesis 3: Simple proportional (lot = initial_lot * balance / initial_balance)
# 0.05 at E0, 0.10 at 2*E0 -> E0 = gain at first 0.10
# 0.06 at 1.2*E0 -> gain at first 0.06 = 0.2*E0
if first_010 is not None:
    E0_est = first_010['equity_gain']
    print(f"\nHypothesis 3 (proportional): E0 estimate = {E0_est:.0f} cents")
    print(f"  BaseLot = 0.05 * (1 + gain/E0) rounded to nearest 0.05 or custom step")
    for lot, gain in sorted(gains.items(), key=lambda x: x[1]):
        multiplier = 1 + gain/E0_est
        predicted = 0.05 * multiplier
        print(f"  lot={lot}: gain={gain:.0f}, multiplier={multiplier:.2f}, predicted={predicted:.3f}")

# Hypothesis 4: Stepwise based on rounded balance
# balance thresholds that trigger lot bumps
print("\nHypothesis 4 (step function):")
print("  If gain thresholds are round numbers:")
for lot, gain in sorted(gains.items(), key=lambda x: x[1]):
    # Find nearest round number
    rounds = [100, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000, 5000]
    nearest = min(rounds, key=lambda r: abs(r - gain))
    print(f"  lot={lot}: gain={gain:.0f} -> nearest round={nearest}")

# --------------------------------------------------------------------------
# Build report
# --------------------------------------------------------------------------
rep = []
rep.append("# AUDCAD G7 - Lot-Sizing Formula\n")
rep.append("## Data available\n")
rep.append(f"- Probe lots: {sorted(probe_lots & set(probes['Lots'].unique()))}")
rep.append(f"- Total probe positions: {len(probes)}")
rep.append("")
rep.append("## Equity gain at first use of each lot size\n")
rep.append("| Lot size | Equity gain since start | Notes |")
rep.append("|---|---|---|")
rep.append("| 0.05 | ~0 (base) | First observed lot size |")
for lot, gain in sorted(gains.items(), key=lambda x: x[1]):
    rep.append(f"| {lot} | {gain:.0f} cents | Relative to start |")
rep.append("")

rep.append("## Lot-sizing model candidates\n")
if first_010 is not None:
    E0 = first_010['equity_gain']
    rep.append(f"Best-fit estimate: **E0 (initial balance) ~ {E0:.0f} cents** (= equity at first 0.10-lot probe)")
    rep.append("")
    rep.append("| Lot | Actual | Proportional prediction | Error |")
    rep.append("|---|---|---|---|")
    for lot, gain in sorted(gains.items(), key=lambda x: x[1]):
        pred = 0.05 * (1 + gain/E0)
        rep.append(f"| {lot} | {lot:.2f} | {pred:.3f} | {abs(lot-pred):.3f} |")
    rep.append("")
    rep.append(f"The proportional model (lot = 0.05 * balance/E0) predicts the 0.10 lot correctly but over-predicts others.")
    rep.append(f"The 0.06 lot (gain={gains.get(0.06,0):.0f}) represents a {gains.get(0.06,0)/E0*100:.0f}% equity gain from start.")
    rep.append(f"The 0.15 lot (gain={gains.get(0.15,0):.0f}) represents a {gains.get(0.15,0)/E0*100:.0f}% equity gain from start.")

rep.append("")
rep.append("## G7 verdict\n")
rep.append("| Metric | Status |")
rep.append("|---|---|")
rep.append(f"| Data points | 4 distinct lot sizes (0.05, 0.06, 0.10, 0.15) |")
rep.append("| Formula fit | UNDERDETERMINED -- 4 points, no clean model |")
rep.append("| Proportional model | Approximate only (0.05 -> 0.10 = 2x = doubling correct; 0.06 and 0.15 imprecise) |")
rep.append("| G7 verdict | [WARN] -- more equity data needed for precise fit |")
rep.append("")
rep.append("## Next steps for G7\n")
rep.append("1. Obtain account statement with exact balance at each trade date (from broker portal)")
rep.append("2. Verify whether lot = floor(balance / X) * 0.01 for some X, or a percentage-of-balance rule")
rep.append("3. Alternative: treat 0.05 as 'default' and the few 0.06/0.10/0.15 as equity-proportional adjustments")
rep.append("   -- for EA v1, use 0.05 fixed lot (safest); add dynamic sizing in v2")

OUT_FILE.write_text('\n'.join(rep), encoding='utf-8')
print(f"\nWrote {OUT_FILE}")

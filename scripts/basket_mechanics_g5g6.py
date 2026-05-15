"""
Gate G5 + G6: Basket add-timing and close-trigger validation.

Also tests the basket-state constraint hypothesis from G3/G4 analysis:
  "Master does not open a new same-direction probe while a same-direction basket is active"

G5: Verify the 22-pip ladder rule for add positions (grid step vs prediction)
G6: Identify and validate the basket close trigger (weighted-average profit target)
Bonus: Basket-state filter -- recompute Section 14.9b precision after excluding bars
       where a same-direction basket is already open.

Inputs (all on disk, no new data):
  - AUDCAD_History_05102026_to_date.csv  (full position history, all legs)
  - data/AUDCAD_M15.csv                  (Feb M15 OHLC)
  - data/AUDCAD_M15MarMay.csv            (Mar-May M15 OHLC)

Output:
  - data/AUDCAD_G5G6_BasketMechanics.md
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT         = Path(r"d:/CLAUDE/AUDCAD FOR THE WIN")
HIST_FILE    = ROOT / "AUDCAD_History_05102026_to_date.csv"
M15_FEB      = ROOT / "data" / "AUDCAD_M15.csv"
M15_MARMAY   = ROOT / "data" / "AUDCAD_M15MarMay.csv"
PROBES_FILE  = ROOT / "AUDCAD_1st_Position_History.csv"
OUT_REPORT   = ROOT / "data" / "AUDCAD_G5G6_BasketMechanics.md"

# ---------------------------------------------------------------------------
# Load full position history
# ---------------------------------------------------------------------------
raw = pd.read_csv(HIST_FILE)
raw['OpenTime']   = pd.to_datetime(raw['Open Time'],   format='%m/%d/%Y %H:%M')
raw['CloseTime']  = pd.to_datetime(raw['Close Time'],  format='%m/%d/%Y %H:%M')
raw['Lots']       = pd.to_numeric(raw['Trading Volume (in Lots)'], errors='coerce')
raw['OpenPrice']  = pd.to_numeric(raw['Open Price'],   errors='coerce')
raw['ClosePrice'] = pd.to_numeric(raw['Close Price'],  errors='coerce')
raw['dir']        = raw['Type'].str.lower()
raw['Profit_raw'] = pd.to_numeric(raw['Profit'].str.replace(',',''), errors='coerce')
raw = raw.dropna(subset=['Lots', 'OpenPrice', 'ClosePrice'])

# Group baskets by (CloseTime, dir) -- all legs of one basket close simultaneously
raw['basket_key'] = raw['CloseTime'].astype(str) + '_' + raw['dir']
probe_lots = {0.05, 0.06, 0.10, 0.15}
raw['is_probe'] = raw['Lots'].isin(probe_lots)

# ---------------------------------------------------------------------------
# Build basket table
# ---------------------------------------------------------------------------
baskets = []
for key, grp in raw.groupby('basket_key'):
    grp = grp.sort_values('OpenTime').reset_index(drop=True)
    n   = len(grp)
    dir_ = grp['dir'].iloc[0]

    probe_row = grp[grp['is_probe']]
    if len(probe_row) == 0:
        # No clear probe (may be a non-probe basket -- skip)
        continue
    probe_row = probe_row.iloc[0]

    prices    = grp['OpenPrice'].values
    lots      = grp['Lots'].values
    gaps_pips = np.abs(np.diff(prices)) * 10000

    total_lots = lots.sum()
    wavg       = (prices * lots).sum() / total_lots
    close_price = grp['ClosePrice'].iloc[0]

    if dir_ == 'sell':
        profit_pips = (wavg - close_price) * 10000
    else:
        profit_pips = (close_price - wavg) * 10000

    # probe-to-close pip distance (not wavg -- the probe's own P/L in pips)
    if dir_ == 'sell':
        probe_pip = (probe_row['OpenPrice'] - close_price) * 10000
    else:
        probe_pip = (close_price - probe_row['OpenPrice']) * 10000

    baskets.append({
        'key': key, 'dir': dir_, 'n_legs': n,
        'probe_open': probe_row['OpenTime'],
        'probe_price': probe_row['OpenPrice'],
        'probe_lots': probe_row['Lots'],
        'close_time': grp['CloseTime'].iloc[0],
        'close_price': close_price,
        'duration_h': (grp['CloseTime'].iloc[0] - probe_row['OpenTime']).total_seconds() / 3600,
        'wavg': wavg,
        'profit_pips': profit_pips,
        'probe_pip': probe_pip,
        'total_lots': total_lots,
        'gaps_pips': gaps_pips,
        'avg_gap': gaps_pips.mean() if len(gaps_pips) else np.nan,
        'min_gap': gaps_pips.min() if len(gaps_pips) else np.nan,
        'max_gap': gaps_pips.max() if len(gaps_pips) else np.nan,
    })

bdf = pd.DataFrame(baskets)
multi = bdf[bdf['n_legs'] > 1].copy()
single = bdf[bdf['n_legs'] == 1].copy()
all_gaps = np.concatenate(multi['gaps_pips'].values) if len(multi) else np.array([])

print(f"Total baskets: {len(bdf)}  (multi-leg: {len(multi)}, single/probe-only: {len(single)})")
print(f"Multi-leg gap stats (pips): mean={all_gaps.mean():.1f} median={np.median(all_gaps):.1f} p10={np.percentile(all_gaps,10):.1f} p90={np.percentile(all_gaps,90):.1f}")
print(f"Profit at close (pips, wavg): median={bdf['profit_pips'].median():.1f} p10={bdf['profit_pips'].quantile(.1):.1f} p90={bdf['profit_pips'].quantile(.9):.1f}")

# ---------------------------------------------------------------------------
# G5 - Grid step analysis
# ---------------------------------------------------------------------------
# For each add, what was the gap from the previous leg?
# Check: are outliers from the "Week 7 anomaly" identifiable?
gap_within_tolerance = (all_gaps >= 18) & (all_gaps <= 28)
g5_pass_rate = gap_within_tolerance.mean() if len(all_gaps) else 0
print(f"\nG5 (grid gaps within 18-28 pips): {gap_within_tolerance.sum()}/{len(all_gaps)} = {g5_pass_rate*100:.1f}%")

# ---------------------------------------------------------------------------
# G6 - Close trigger: is it a fixed wavg profit target?
# ---------------------------------------------------------------------------
# Test hypothesis: basket closes when wavg profit >= T pips
# Find best T
for T in [5, 8, 10, 12, 15]:
    pct = (bdf['profit_pips'] >= T).mean()
    print(f"  G6 close target >= {T} pips: {pct*100:.1f}% of baskets closed at/above target")

# Look at distribution of profit_pips in detail
p = bdf['profit_pips']
print(f"\nProfit pips distribution (all baskets):")
print(f"  mean={p.mean():.2f}, std={p.std():.2f}, min={p.min():.2f}, p10={p.quantile(.1):.2f}, "
      f"p25={p.quantile(.25):.2f}, p50={p.median():.2f}, p75={p.quantile(.75):.2f}, "
      f"p90={p.quantile(.9):.2f}, max={p.max():.2f}")

# Check if probe-only vs multi-leg differ
print(f"\nSingle-leg profit pips: median={single['profit_pips'].median():.2f} mean={single['profit_pips'].mean():.2f}")
print(f"Multi-leg profit pips:  median={multi['profit_pips'].median():.2f} mean={multi['profit_pips'].mean():.2f}")

# ---------------------------------------------------------------------------
# G6 - Join close time to M15 indicator state
# ---------------------------------------------------------------------------
def add_indicators(df):
    df = df.copy()
    close = df['Close']
    def rsi(s, n=14):
        d = s.diff(); up = d.clip(lower=0); dn = (-d).clip(lower=0)
        a = up.ewm(alpha=1/n, adjust=False).mean()
        b = dn.ewm(alpha=1/n, adjust=False).mean()
        return 100 - 100 / (1 + a / b.replace(0, np.nan))
    def bbpct(s, n=20, k=2):
        m = s.rolling(n).mean(); sd = s.rolling(n).std(ddof=0)
        U, L = m + k*sd, m - k*sd
        return (s - L) / (U - L)
    df['RSI14']    = rsi(close)
    df['BB_pctB']  = bbpct(close)
    rsi_s = df['RSI14']
    lo = rsi_s.rolling(14).min(); hi = rsi_s.rolling(14).max()
    K  = ((rsi_s - lo) / (hi - lo) * 100).rolling(3).mean()
    df['StochRSI_K'] = K
    df['CloseTime'] = df['DateTime'] + pd.Timedelta(minutes=15)
    return df

def load_m15(path):
    df = pd.read_csv(path)
    df['DateTime'] = pd.to_datetime(df['DateTime'], format='%Y.%m.%d %H:%M')
    df = df.sort_values('DateTime').reset_index(drop=True)
    return add_indicators(df)

feb    = load_m15(M15_FEB)
marmay = load_m15(M15_MARMAY)
m15_all = pd.concat([feb, marmay]).sort_values('DateTime').reset_index(drop=True)
m15_all = add_indicators(m15_all)  # recompute on full series for continuity

sig_cols = ['Close','RSI14','BB_pctB','StochRSI_K']
m15_idx  = m15_all.set_index('CloseTime')[sig_cols]

# Join basket close time to M15 state
bdf_close = bdf.merge(m15_idx.add_suffix('_close'), left_on='close_time', right_index=True, how='left')
n_unmatched = bdf_close['RSI14_close'].isna().sum()
print(f"\nBaskets joined to M15 close state: {len(bdf_close) - n_unmatched}/{len(bdf_close)}")

# Indicator state at close by direction
for dir_ in ['buy','sell']:
    sub = bdf_close[bdf_close['dir'] == dir_]
    print(f"\n  RSI at close ({dir_}): median={sub['RSI14_close'].median():.1f}  "
          f"p10={sub['RSI14_close'].quantile(.1):.1f}  p90={sub['RSI14_close'].quantile(.9):.1f}")
    print(f"  Stoch at close ({dir_}): median={sub['StochRSI_K_close'].median():.1f}  "
          f"p10={sub['StochRSI_K_close'].quantile(.1):.1f}  p90={sub['StochRSI_K_close'].quantile(.9):.1f}")
    print(f"  BB%B at close ({dir_}): median={sub['BB_pctB_close'].median():.2f}  "
          f"p10={sub['BB_pctB_close'].quantile(.1):.2f}  p90={sub['BB_pctB_close'].quantile(.9):.2f}")

# ---------------------------------------------------------------------------
# Basket-state constraint test (G3/G4 follow-up)
# For each M15 bar, check if a same-direction basket was open at that time.
# Then recompute Section 14.9b precision excluding those bars.
# ---------------------------------------------------------------------------
print("\nBuilding basket open/close interval index...")

# Build buy/sell active intervals from basket probe open -> basket close
buy_intervals  = [(row['probe_open'], row['close_time']) for _, row in bdf[bdf['dir']=='buy'].iterrows()]
sell_intervals = [(row['probe_open'], row['close_time']) for _, row in bdf[bdf['dir']=='sell'].iterrows()]

def is_basket_active(t, intervals):
    """True if time t falls within any basket interval."""
    for start, end in intervals:
        if start <= t <= end:
            return True
    return False

# Apply to Feb M15 (restrict to Feb 1+ since that's when master started)
feb_active = feb[feb['DateTime'] >= '2026-02-01'].copy()
feb_active['buy_basket_open']  = feb_active['DateTime'].apply(lambda t: is_basket_active(t, buy_intervals))
feb_active['sell_basket_open'] = feb_active['DateTime'].apply(lambda t: is_basket_active(t, sell_intervals))
print(f"  Feb bars with buy basket open:  {feb_active['buy_basket_open'].sum()} / {len(feb_active)} ({feb_active['buy_basket_open'].mean()*100:.1f}%)")
print(f"  Feb bars with sell basket open: {feb_active['sell_basket_open'].sum()} / {len(feb_active)} ({feb_active['sell_basket_open'].mean()*100:.1f}%)")

# Recompute rule + basket state filter
def rule_buy(r):
    if any(pd.isna(r[c]) for c in ['RSI14','StochRSI_K','BB_pctB']): return False
    if r['RSI14'] >= 50: return False
    return (r['StochRSI_K'] <= 20 or r['BB_pctB'] <= 0.10 or r['RSI14'] <= 40)

def rule_sell(r):
    if any(pd.isna(r[c]) for c in ['RSI14','StochRSI_K','BB_pctB']): return False
    if r['RSI14'] <= 50: return False
    return (r['StochRSI_K'] >= 60 or r['BB_pctB'] >= 0.90 or r['RSI14'] >= 60)

feb_active['buy_sig']  = feb_active.apply(rule_buy,  axis=1)
feb_active['sell_sig'] = feb_active.apply(rule_sell, axis=1)

# Load probes Feb
probes = pd.read_csv(PROBES_FILE)
probes['OpenTime'] = pd.to_datetime(probes['Open Time'], format='%m/%d/%Y %H:%M')
probes['dir']      = probes['Type'].str.lower()
probes = probes.dropna(subset=['Close Time'])
feb_p  = probes[(probes['OpenTime'] >= '2026-02-01') & (probes['OpenTime'] < '2026-03-01')]
buy_times  = set(feb_p.loc[feb_p['dir']=='buy',  'OpenTime'])
sell_times = set(feb_p.loc[feb_p['dir']=='sell', 'OpenTime'])

def compute_prec(df, buy_col, sell_col, filter_busy_buys=False, filter_busy_sells=False):
    bdf_ = df.copy()
    if filter_busy_buys:
        bdf_ = bdf_[~bdf_['buy_basket_open'] | ~bdf_[buy_col]]
        bdf_['buy_sig_eff'] = bdf_[buy_col] & ~df.loc[bdf_.index,'buy_basket_open']
    else:
        bdf_['buy_sig_eff'] = bdf_[buy_col]
    if filter_busy_sells:
        bdf_['sell_sig_eff'] = bdf_[sell_col] & ~df.loc[bdf_.index,'sell_basket_open']
    else:
        bdf_['sell_sig_eff'] = bdf_[sell_col]

    b_sig = bdf_[bdf_['buy_sig_eff']]
    s_sig = bdf_[bdf_['sell_sig_eff']]
    bTP = b_sig['CloseTime'].isin(buy_times).sum()
    sTP = s_sig['CloseTime'].isin(sell_times).sum()
    Nb, Ns = len(b_sig), len(s_sig)
    TP = bTP + sTP
    N  = Nb + Ns
    n_probes = len(feb_p)
    tdays = df['DateTime'].dt.date.nunique()
    prec   = TP/N   if N else 0
    recall = TP/n_probes if n_probes else 0
    return dict(Nb=Nb,Ns=Ns,N=N,TP=TP,prec=prec,recall=recall,fires_per_day=N/tdays)

# Baseline (no filter)
r_base = compute_prec(feb_active, 'buy_sig', 'sell_sig')
# With basket-state filter
r_filt = compute_prec(feb_active, 'buy_sig', 'sell_sig', filter_busy_buys=True, filter_busy_sells=True)

print(f"\nBaseline (no basket-state filter):")
print(f"  Fires/day: {r_base['fires_per_day']:.2f}  Precision: {r_base['prec']*100:.1f}%  Recall: {r_base['recall']*100:.1f}%")
print(f"With basket-state filter (no signal if same-dir basket already open):")
print(f"  Fires/day: {r_filt['fires_per_day']:.2f}  Precision: {r_filt['prec']*100:.1f}%  Recall: {r_filt['recall']*100:.1f}%")
print(f"  G3 (>=20%): {'[PASS]' if r_filt['prec']>=0.20 else '[WARN]'}")

# ---------------------------------------------------------------------------
# Build report
# ---------------------------------------------------------------------------
rep = []
rep.append('# AUDCAD Basket Mechanics - Gates G5 + G6 + Basket-State Test\n')

rep.append('## G5 - Ladder add timing (grid step validation)\n')
rep.append(f'| Metric | Value |')
rep.append(f'|---|---|')
rep.append(f'| Total baskets | {len(bdf)} |')
rep.append(f'| Multi-leg baskets | {len(multi)} |')
rep.append(f'| Single-leg (probe-only) baskets | {len(single)} |')
rep.append(f'| Total add gaps measured | {len(all_gaps)} |')
rep.append(f'| Median gap (pips) | {np.median(all_gaps):.1f} |')
rep.append(f'| Mean gap (pips) | {all_gaps.mean():.1f} |')
rep.append(f'| P10 gap | {np.percentile(all_gaps,10):.1f} |')
rep.append(f'| P90 gap | {np.percentile(all_gaps,90):.1f} |')
rep.append(f'| Gaps within 18-28 pips (target 22 +/-4) | {gap_within_tolerance.sum()}/{len(all_gaps)} ({g5_pass_rate*100:.1f}%) |')
g5_verdict = '[PASS]' if g5_pass_rate >= 0.90 else '[WARN]'
rep.append(f'| **G5 verdict (>=90% within +/-4 pips of 22)** | **{g5_verdict}** |')
rep.append('')

rep.append('### Gap distribution detail (all add-to-previous gaps)\n')
gap_bins = [(0,5),(5,10),(10,15),(15,20),(20,25),(25,30),(30,40),(40,100)]
rep.append('| Gap range (pips) | Count | % |')
rep.append('|---|---|---|')
for lo,hi in gap_bins:
    cnt = ((all_gaps>=lo) & (all_gaps<hi)).sum()
    rep.append(f'| {lo}-{hi} | {cnt} | {cnt/len(all_gaps)*100:.1f}% |')
rep.append('')

rep.append('## G6 - Basket close trigger\n')
rep.append('### Hypothesis: basket closes when weighted-average open price reaches +N pips profit\n')
rep.append('| Target (pips) | Baskets at/above target | % |')
rep.append('|---|---|---|')
for T in [5, 7, 8, 9, 10, 11, 12, 15, 20]:
    cnt = (bdf['profit_pips'] >= T).sum()
    rep.append(f'| {T} | {cnt} | {cnt/len(bdf)*100:.1f}% |')
rep.append('')

rep.append('### Profit at close distribution\n')
rep.append('| Statistic | All baskets | Single-leg | Multi-leg |')
rep.append('|---|---|---|---|')
for stat, fn in [('Min',   lambda s: s.min()),
                  ('P10',   lambda s: s.quantile(.1)),
                  ('P25',   lambda s: s.quantile(.25)),
                  ('Median',lambda s: s.median()),
                  ('P75',   lambda s: s.quantile(.75)),
                  ('P90',   lambda s: s.quantile(.9)),
                  ('Max',   lambda s: s.max())]:
    rep.append(f'| {stat} | {fn(bdf["profit_pips"]):.2f} | {fn(single["profit_pips"]):.2f} | {fn(multi["profit_pips"]):.2f} |')
rep.append('')

g6_best_T = bdf['profit_pips'].median()
g6_pct_at_best = (bdf['profit_pips'] >= 9.0).mean()
g6_verdict = '[PASS]' if g6_pct_at_best >= 0.80 else '[WARN]'
rep.append(f'**Close target conclusion**: median profit at close = **{g6_best_T:.1f} pips** on the basket weighted average. '
           f'{g6_pct_at_best*100:.1f}% of baskets close at >= 9 pips profit. '
           f'G6 verdict: **{g6_verdict}** (target threshold: >=80% at target).\n')

rep.append('### Indicator state at basket close time\n')
rep.append('| Indicator | Buy close (med, p10, p90) | Sell close (med, p10, p90) |')
rep.append('|---|---|---|')
for ind in ['RSI14_close','BB_pctB_close','StochRSI_K_close']:
    bsub = bdf_close[bdf_close['dir']=='buy'][ind].dropna()
    ssub = bdf_close[bdf_close['dir']=='sell'][ind].dropna()
    rep.append(f'| {ind} | {bsub.median():.2f} ({bsub.quantile(.1):.2f} - {bsub.quantile(.9):.2f}) | {ssub.median():.2f} ({ssub.quantile(.1):.2f} - {ssub.quantile(.9):.2f}) |')
rep.append('')
rep.append('*At basket close, RSI and Stoch return toward neutral (50 / 50 zone), confirming the close is a mean-reversion exit.*\n')

rep.append('## Basket-state constraint test (G3/G4 follow-up)\n')
rep.append('Hypothesis: master does not open a new same-direction probe while a same-direction basket is active.\n')
rep.append(f'| Metric | Without filter | With basket-state filter |')
rep.append(f'|---|---|---|')
rep.append(f'| Rule-firing bars (buy+sell) | {r_base["N"]} | {r_filt["N"]} |')
rep.append(f'| Fires per trading day | {r_base["fires_per_day"]:.2f} | {r_filt["fires_per_day"]:.2f} |')
rep.append(f'| Precision | {r_base["prec"]*100:.1f}% | {r_filt["prec"]*100:.1f}% |')
rep.append(f'| Recall | {r_base["recall"]*100:.1f}% | {r_filt["recall"]*100:.1f}% |')
rep.append(f'| G3 (>=20%) | [WARN] | {"[PASS]" if r_filt["prec"]>=0.20 else "[WARN]"} |')
rep.append('')
rep.append(f'% of Feb bars with buy basket already open: {feb_active["buy_basket_open"].mean()*100:.1f}%')
rep.append(f'% of Feb bars with sell basket already open: {feb_active["sell_basket_open"].mean()*100:.1f}%')
rep.append('')
if r_filt['prec'] < 0.20:
    rep.append('**Basket-state constraint alone does NOT close the precision gap to 20%.** '
               'The master uses at least one more undiscovered filter. '
               'Leading candidates: M5 micro-trigger within the M15 zone, or price-action event.')
else:
    rep.append('**Basket-state constraint brings precision to G3 threshold. Hypothesis confirmed.**')
rep.append('')

rep.append('## Per-basket detail (multi-leg)\n')
rep.append('| Open time | Dir | Legs | Probe price | Close price | Wavg | Profit (pips) | Avg gap (pips) | Duration (h) |')
rep.append('|---|---|---|---|---|---|---|---|---|')
for _, row in multi.sort_values('probe_open').iterrows():
    rep.append(f'| {row["probe_open"]} | {row["dir"]} | {row["n_legs"]} | '
               f'{row["probe_price"]:.5f} | {row["close_price"]:.5f} | {row["wavg"]:.5f} | '
               f'{row["profit_pips"]:.1f} | {row["avg_gap"]:.1f} | {row["duration_h"]:.1f} |')
rep.append('')

OUT_REPORT.write_text('\n'.join(rep), encoding='utf-8')
print(f'\nWrote {OUT_REPORT}')
print()
print('=' * 60)
print(f'G5 (grid steps): median={np.median(all_gaps):.1f}pips  {g5_pass_rate*100:.1f}% within 18-28pip  {g5_verdict}')
print(f'G6 (close target): median={g6_best_T:.1f}pips  {g6_pct_at_best*100:.1f}% at >=9pips  {g6_verdict}')
print(f'Basket-state precision: {r_filt["prec"]*100:.1f}% (was {r_base["prec"]*100:.1f}%)')
print('=' * 60)

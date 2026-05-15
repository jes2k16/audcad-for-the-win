"""
February probe validation — v3.

User pushback after v2:
  1. v2 ignored the M15 EMAs (10/20/50/200) entirely.
  2. v2 didn't account for HTF resistance — Feb prices were at the top of the
     multi-year 0.86-0.95 range, so sells were structurally HTF-aligned regardless
     of M15 oscillator state.

v3 adds:
  - EMA stack state at probe time (bullish/bearish/mixed)
  - Price-vs-EMA distance (pips) — how stretched is price relative to the MA
  - EMA10/EMA20 cross within last N bars (micro-trend flip)
  - Distance to N-bar swing high / swing low (proxy for HTF level proximity)
  - Re-test the 6 unexplained sells against these new features.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(r"d:/CLAUDE/AUDCAD FOR THE WIN")
M15_FILE   = ROOT / "data" / "AUDCAD_M15.csv"
PROBES_FILE = ROOT / "AUDCAD_1st_Position_History.csv"
OUT_CSV    = ROOT / "data" / "AUDCAD_Feb_Probe_Indicators_v3.csv"
OUT_REPORT = ROOT / "data" / "AUDCAD_Feb_Hypothesis_Test_v3.md"

# ----- Load M15 ---------------------------------------------------------------
m15 = pd.read_csv(M15_FILE)
m15["DateTime"]  = pd.to_datetime(m15["DateTime"], format="%Y.%m.%d %H:%M")
m15 = m15.sort_values("DateTime").reset_index(drop=True)
m15["CloseTime"] = m15["DateTime"] + pd.Timedelta(minutes=15)
close = m15["Close"]

def ema(s, n): return s.ewm(span=n, adjust=False).mean()
def rsi(s, n=14):
    d = s.diff(); up = d.clip(lower=0); dn = (-d).clip(lower=0)
    a = up.ewm(alpha=1/n, adjust=False).mean()
    b = dn.ewm(alpha=1/n, adjust=False).mean()
    rs = a / b.replace(0, np.nan)
    return 100 - 100 / (1 + rs)
def bb(s, n=20, k=2):
    m = s.rolling(n).mean(); sd = s.rolling(n).std(ddof=0)
    return m + k*sd, m, m - k*sd
def stoch(rsi_s, n=14, k=3, d=3):
    lo = rsi_s.rolling(n).min(); hi = rsi_s.rolling(n).max()
    K  = ((rsi_s - lo)/(hi - lo)*100).rolling(k).mean()
    return K, K.rolling(d).mean()

m15["EMA10"]  = ema(close, 10)
m15["EMA20"]  = ema(close, 20)
m15["EMA50"]  = ema(close, 50)
m15["EMA200"] = ema(close, 200)
m15["RSI14"]  = rsi(close, 14)
U, M, L = bb(close, 20, 2)
m15["BB_upper"] = U; m15["BB_mid"] = M; m15["BB_lower"] = L
m15["BB_pctB"] = (close - L) / (U - L)
K, D = stoch(m15["RSI14"], 14, 3, 3)
m15["StochRSI_K"] = K; m15["StochRSI_D"] = D

# EMA stack alignment at each bar
m15["EMA_stack_bull"] = ((m15["EMA10"] > m15["EMA20"]) &
                         (m15["EMA20"] > m15["EMA50"]) &
                         (m15["EMA50"] > m15["EMA200"]))
m15["EMA_stack_bear"] = ((m15["EMA10"] < m15["EMA20"]) &
                         (m15["EMA20"] < m15["EMA50"]) &
                         (m15["EMA50"] < m15["EMA200"]))
m15["EMA10_above_EMA20"] = m15["EMA10"] > m15["EMA20"]
m15["EMA20_above_EMA50"] = m15["EMA20"] > m15["EMA50"]
m15["above_EMA200"]      = close > m15["EMA200"]

# Distance (pips) from each EMA — positive = price above EMA
m15["dist_EMA10_pips"]  = (close - m15["EMA10"])  * 10000
m15["dist_EMA20_pips"]  = (close - m15["EMA20"])  * 10000
m15["dist_EMA50_pips"]  = (close - m15["EMA50"])  * 10000
m15["dist_EMA200_pips"] = (close - m15["EMA200"]) * 10000

# Recent swing high/low — multiple lookbacks (HTF resistance proxy)
# 100 M15 bars  = ~25 hours (~1 day)
# 500 M15 bars  = ~5 days  (~1 week)
# 2000 M15 bars = ~20 days (~1 month, approximates monthly swing)
for n in (100, 500, 2000):
    m15[f"rollHi_{n}"] = m15["High"].rolling(n).max()
    m15[f"rollLo_{n}"] = m15["Low"].rolling(n).min()
    m15[f"dist_to_rollHi_{n}_pips"] = (m15[f"rollHi_{n}"] - close) * 10000  # pips below recent high
    m15[f"dist_to_rollLo_{n}_pips"] = (close - m15[f"rollLo_{n}"]) * 10000  # pips above recent low

# EMA10/EMA20 cross flag — fires when stack flips
m15["EMA10_cross_up"]   = m15["EMA10_above_EMA20"] & ~m15["EMA10_above_EMA20"].shift(1, fill_value=False)
m15["EMA10_cross_down"] = (~m15["EMA10_above_EMA20"]) & m15["EMA10_above_EMA20"].shift(1, fill_value=False)
# Recent cross within last 10 bars
m15["recent_cross_up"]   = m15["EMA10_cross_up"].rolling(10).sum() > 0
m15["recent_cross_down"] = m15["EMA10_cross_down"].rolling(10).sum() > 0

# ----- Join probes ------------------------------------------------------------
probes = pd.read_csv(PROBES_FILE)
probes["OpenTime"] = pd.to_datetime(probes["Open Time"], format="%m/%d/%Y %H:%M")
feb = probes[(probes["OpenTime"] >= "2026-02-01") &
             (probes["OpenTime"] <  "2026-03-01")].copy()
feb = feb.sort_values("OpenTime").reset_index(drop=True)

sig_cols = [c for c in m15.columns if c not in ("DateTime","CloseTime")]
j = feb.merge(m15.set_index("CloseTime")[sig_cols],
              left_on="OpenTime", right_index=True, how="left")
j["dir"] = j["Type"].str.lower()
buys, sells = j["dir"]=="buy", j["dir"]=="sell"
N, NB, NS = len(j), buys.sum(), sells.sum()
def pct(n, d): return f"{n}/{d} ({100*n/d:.0f}%)"

print(f"Joined {N} probes (buys {NB}, sells {NS})")

# ----- Distribution of new features at probe times ----------------------------
def stat_group(col):
    return {
        "buy_med":   round(j.loc[buys,  col].median(), 2),
        "buy_p10":   round(j.loc[buys,  col].quantile(.10), 2),
        "buy_p90":   round(j.loc[buys,  col].quantile(.90), 2),
        "sell_med":  round(j.loc[sells, col].median(), 2),
        "sell_p10":  round(j.loc[sells, col].quantile(.10), 2),
        "sell_p90":  round(j.loc[sells, col].quantile(.90), 2),
    }

ema_features = [
    "dist_EMA10_pips","dist_EMA20_pips","dist_EMA50_pips","dist_EMA200_pips",
]
swing_features = [
    "dist_to_rollHi_100_pips","dist_to_rollLo_100_pips",
    "dist_to_rollHi_500_pips","dist_to_rollLo_500_pips",
    "dist_to_rollHi_2000_pips","dist_to_rollLo_2000_pips",
]

# Boolean features — fraction true by direction
def bool_stat(col):
    return {
        "all_true":  round(j[col].mean()*100, 0),
        "buy_true":  round(j.loc[buys,  col].mean()*100, 0),
        "sell_true": round(j.loc[sells, col].mean()*100, 0),
    }

bool_features = [
    "EMA_stack_bull","EMA_stack_bear",
    "EMA10_above_EMA20","EMA20_above_EMA50","above_EMA200",
    "recent_cross_up","recent_cross_down",
]

# ----- EMA-based hypothesis tests --------------------------------------------
# H8: Trend filter — only buy below EMA200, only sell above EMA200
def h8(row):
    if row["dir"]=="buy":  return not row["above_EMA200"]
    if row["dir"]=="sell": return row["above_EMA200"]
    return False

# H9: Counter-EMA-stack — buy when bearish stack, sell when bullish stack
def h9(row):
    if row["dir"]=="buy":  return row["EMA_stack_bear"]
    if row["dir"]=="sell": return row["EMA_stack_bull"]
    return False

# H10: Price stretched from EMA20 — buy when price < EMA20 by ≥X pips, sell when > by X
def h10(row, pips=10):
    d = row["dist_EMA20_pips"]
    if pd.isna(d): return False
    if row["dir"]=="buy":  return d <= -pips
    if row["dir"]=="sell": return d >=  pips
    return False

# H11: Near recent swing — sells fire near a 500-bar (~1 week) swing high; buys near 500-bar swing low
def h11_proximity(row, prox_pips=20, lookback="500"):
    if row["dir"]=="sell":
        d = row[f"dist_to_rollHi_{lookback}_pips"]
        return (not pd.isna(d)) and d <= prox_pips
    if row["dir"]=="buy":
        d = row[f"dist_to_rollLo_{lookback}_pips"]
        return (not pd.isna(d)) and d <= prox_pips
    return False

# H12: Counter-EMA10 — buy when EMA10 < EMA20 (down micro-trend), sell when EMA10 > EMA20
def h12(row):
    if row["dir"]=="buy":  return not row["EMA10_above_EMA20"]
    if row["dir"]=="sell": return row["EMA10_above_EMA20"]
    return False

# Re-test these
j["H8_above_EMA200"]   = j.apply(h8, axis=1)
j["H9_counter_stack"]  = j.apply(h9, axis=1)
j["H10_stretch_10pip"] = j.apply(lambda r: h10(r, 10), axis=1)
j["H10_stretch_20pip"] = j.apply(lambda r: h10(r, 20), axis=1)
j["H10_stretch_30pip"] = j.apply(lambda r: h10(r, 30), axis=1)
j["H11_swing_500_20pip"] = j.apply(lambda r: h11_proximity(r, 20, "500"), axis=1)
j["H11_swing_500_30pip"] = j.apply(lambda r: h11_proximity(r, 30, "500"), axis=1)
j["H11_swing_500_50pip"] = j.apply(lambda r: h11_proximity(r, 50, "500"), axis=1)
j["H11_swing_2000_30pip"] = j.apply(lambda r: h11_proximity(r, 30, "2000"), axis=1)
j["H11_swing_2000_50pip"] = j.apply(lambda r: h11_proximity(r, 50, "2000"), axis=1)
j["H12_counter_EMA10_20"] = j.apply(h12, axis=1)

# Old composite from v2
def rule_stoch(row, st_sell=80, st_buy=20):
    return (row["dir"]=="sell" and row["StochRSI_K"]>=st_sell) or \
           (row["dir"]=="buy"  and row["StochRSI_K"]<=st_buy)
def rule_bb(row, bb_sell=0.9, bb_buy=0.1):
    return (row["dir"]=="sell" and row["BB_pctB"]>=bb_sell) or \
           (row["dir"]=="buy"  and row["BB_pctB"]<=bb_buy)
def rule_rsi(row, rs_sell=60, rs_buy=40):
    return (row["dir"]=="sell" and row["RSI14"]>=rs_sell) or \
           (row["dir"]=="buy"  and row["RSI14"]<=rs_buy)
j["v2_composite"] = j.apply(lambda r: rule_stoch(r) or rule_bb(r) or rule_rsi(r), axis=1)

# New composite with EMA stretch
j["v3_composite"] = j.apply(lambda r: rule_stoch(r) or rule_bb(r) or rule_rsi(r) or h10(r, 10), axis=1)
j["v3_with_swing"] = j.apply(lambda r: rule_stoch(r) or rule_bb(r) or rule_rsi(r) or h10(r, 10) or h11_proximity(r, 30, "500"), axis=1)

# ----- Build report ----------------------------------------------------------
def hit_table(cols):
    out = []
    for c in cols:
        a = j[c].sum(); b = j.loc[buys, c].sum(); s = j.loc[sells, c].sum()
        out.append(f"| {c} | {pct(a, N)} | {pct(b, NB)} | {pct(s, NS)} |")
    return out

rep = []
rep.append("# AUDCAD February Probe Validation — v3 (EMA + HTF swing tests)\n")
rep.append(f"**Probes**: {N} ({NB} buys / {NS} sells)\n")

# Section A — distributions
rep.append("## A. Indicator distributions at probe times (new features)\n")
rep.append("Distance from EMA in pips (positive = price above EMA):\n")
rep.append("| feature | buy med (10–90%) | sell med (10–90%) |")
rep.append("|---|---|---|")
for f in ema_features:
    s = stat_group(f)
    rep.append(f"| {f} | {s['buy_med']} ({s['buy_p10']} → {s['buy_p90']}) | {s['sell_med']} ({s['sell_p10']} → {s['sell_p90']}) |")

rep.append("\nDistance to recent swing high / low in pips (positive = below the high / above the low):\n")
rep.append("| feature | buy med (10–90%) | sell med (10–90%) |")
rep.append("|---|---|---|")
for f in swing_features:
    s = stat_group(f)
    rep.append(f"| {f} | {s['buy_med']} ({s['buy_p10']} → {s['buy_p90']}) | {s['sell_med']} ({s['sell_p10']} → {s['sell_p90']}) |")

# Section B — boolean state at probe times
rep.append("\n## B. EMA stack / cross state at probe times\n")
rep.append("| state | all probes true | buys true | sells true |")
rep.append("|---|---|---|---|")
for f in bool_features:
    s = bool_stat(f)
    rep.append(f"| {f} | {s['all_true']}% | {s['buy_true']}% | {s['sell_true']}% |")

# Section C — hit-rate of new hypotheses
rep.append("\n## C. New hypothesis hit-rates\n")
rep.append("| Hypothesis | All | Buys | Sells |")
rep.append("|---|---|---|---|")
rep.extend(hit_table([
    "H8_above_EMA200","H9_counter_stack","H12_counter_EMA10_20",
    "H10_stretch_10pip","H10_stretch_20pip","H10_stretch_30pip",
    "H11_swing_500_20pip","H11_swing_500_30pip","H11_swing_500_50pip",
    "H11_swing_2000_30pip","H11_swing_2000_50pip",
    "v2_composite","v3_composite","v3_with_swing",
]))

# Section D — 6 unexplained probes from v2: do any new features explain them?
rep.append("\n## D. The 6 probes v2 couldn't explain — re-tested with new features\n")
unexplained_v2 = j[~j["v2_composite"]]
cols_show = ["OpenTime","Type","Open Price",
             "RSI14","BB_pctB","StochRSI_K",
             "dist_EMA20_pips","dist_EMA50_pips","dist_EMA200_pips",
             "dist_to_rollHi_500_pips","dist_to_rollLo_500_pips",
             "EMA_stack_bull","EMA_stack_bear",
             "H10_stretch_10pip","H11_swing_500_30pip"]
nm = unexplained_v2[cols_show].copy()
for c in cols_show:
    if nm[c].dtype == float:
        nm[c] = nm[c].round(2)
rep.append("```")
rep.append(nm.to_string(index=False))
rep.append("```")

# Section E — full per-probe attribution (which rules fired)
rep.append("\n## E. Per-probe attribution: which Feb probes hit each new test?\n")
rep.append("| OpenTime | Dir | Price | dEMA20 | dEMA200 | toHi500 | toLo500 | Stack | v2 | +H10 | +H11 |")
rep.append("|---|---|---|---|---|---|---|---|---|---|---|")
for _, r in j.iterrows():
    stack = "BULL" if r["EMA_stack_bull"] else ("BEAR" if r["EMA_stack_bear"] else "mix")
    rep.append(f"| {r['OpenTime']} | {r['Type']} | {r['Open Price']:.5f} | "
               f"{r['dist_EMA20_pips']:+.0f} | {r['dist_EMA200_pips']:+.0f} | "
               f"{r['dist_to_rollHi_500_pips']:.0f} | {r['dist_to_rollLo_500_pips']:.0f} | {stack} | "
               f"{'Y' if r['v2_composite'] else '.'} | "
               f"{'Y' if r['H10_stretch_10pip'] else '.'} | "
               f"{'Y' if r['H11_swing_500_30pip'] else '.'} |")

OUT_REPORT.write_text("\n".join(rep), encoding="utf-8")
j.to_csv(OUT_CSV, index=False, float_format="%.5f")
print(f"Wrote {OUT_REPORT}")
print(f"Wrote {OUT_CSV}")
print()
print(f"v2 composite:                   {pct(j['v2_composite'].sum(),    N)}")
print(f"v3 composite (+EMA stretch):    {pct(j['v3_composite'].sum(),    N)}")
print(f"v3 + swing proximity 500/30:    {pct(j['v3_with_swing'].sum(),   N)}")
print()
print("Of the 6 v2-unexplained probes, hits by:")
for r_name, col in [("EMA stretch ≥10 pips", "H10_stretch_10pip"),
                    ("EMA stretch ≥20 pips", "H10_stretch_20pip"),
                    ("Swing 500 within 30 pips", "H11_swing_500_30pip"),
                    ("Swing 500 within 50 pips", "H11_swing_500_50pip"),
                    ("Swing 2000 within 50 pips", "H11_swing_2000_50pip")]:
    n_hit = unexplained_v2[col].sum()
    print(f"  {r_name}: {n_hit}/{len(unexplained_v2)}")

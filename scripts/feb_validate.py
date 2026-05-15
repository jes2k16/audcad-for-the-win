"""
February probe validation.

Joins each February 2026 probe from AUDCAD_1st_Position_History.csv to the M15
indicator state at the bar that closed just before the probe entered (the
"signal bar"), then tests hypotheses H1-H4 against the 44 probes.

Outputs:
  - data/AUDCAD_Feb_Probe_Indicators.csv  (joined table)
  - data/AUDCAD_Feb_Hypothesis_Test.md    (results summary)
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(r"d:/CLAUDE/AUDCAD FOR THE WIN")
M15_FILE     = ROOT / "data" / "AUDCAD_M15.csv"
PROBES_FILE  = ROOT / "AUDCAD_1st_Position_History.csv"
OUT_JOIN_CSV = ROOT / "data" / "AUDCAD_Feb_Probe_Indicators.csv"
OUT_REPORT   = ROOT / "data" / "AUDCAD_Feb_Hypothesis_Test.md"

# ----- Load M15 bars -----------------------------------------------------------
m15 = pd.read_csv(M15_FILE)
m15["DateTime"] = pd.to_datetime(m15["DateTime"], format="%Y.%m.%d %H:%M")
m15 = m15.sort_values("DateTime").reset_index(drop=True)

# Each bar's DateTime is its OPEN time; bar closes at DateTime + 15 min.
# An M15 signal that fires at probe time T came from the bar that closed AT T,
# which has DateTime == T - 15min.
m15["CloseTime"] = m15["DateTime"] + pd.Timedelta(minutes=15)

# ----- Indicators (computed on each bar's close, available at its CloseTime) ----
close = m15["Close"]

def ema(series, n):
    return series.ewm(span=n, adjust=False).mean()

def rsi(series, n=14):
    diff = series.diff()
    up   = diff.clip(lower=0)
    down = (-diff).clip(lower=0)
    # Wilder's smoothing
    avg_up   = up.ewm(alpha=1/n, adjust=False).mean()
    avg_down = down.ewm(alpha=1/n, adjust=False).mean()
    rs = avg_up / avg_down.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def bbands(series, n=20, k=2):
    mid = series.rolling(n).mean()
    sd  = series.rolling(n).std(ddof=0)
    upper = mid + k * sd
    lower = mid - k * sd
    pctB  = (series - lower) / (upper - lower)
    return upper, mid, lower, pctB

def stoch_rsi(rsi_series, n_rsi=14, n_stoch=14, smooth_k=3, smooth_d=3):
    lo = rsi_series.rolling(n_stoch).min()
    hi = rsi_series.rolling(n_stoch).max()
    raw_k = (rsi_series - lo) / (hi - lo) * 100
    pctK  = raw_k.rolling(smooth_k).mean()
    pctD  = pctK.rolling(smooth_d).mean()
    return pctK, pctD

m15["EMA10"]   = ema(close, 10)
m15["EMA20"]   = ema(close, 20)
m15["EMA50"]   = ema(close, 50)
m15["EMA200"] = ema(close, 200)
m15["RSI14"]  = rsi(close, 14)
upper, mid, lower, pctB = bbands(close, 20, 2)
m15["BB_upper"] = upper
m15["BB_mid"]   = mid
m15["BB_lower"] = lower
m15["BB_pctB"]  = pctB
pK, pD = stoch_rsi(m15["RSI14"], 14, 14, 3, 3)
m15["StochRSI_K"] = pK
m15["StochRSI_D"] = pD
m15["StochRSI_K_prev"] = pK.shift(1)
m15["StochRSI_D_prev"] = pD.shift(1)

# Bar range pips (for the MaxBarRangePips check we wanted in Section 9)
m15["BarRangePips"] = (m15["High"] - m15["Low"]) * 10000

# ----- Load probes and filter to February --------------------------------------
probes = pd.read_csv(PROBES_FILE)
probes["OpenTime"] = pd.to_datetime(probes["Open Time"], format="%m/%d/%Y %H:%M")
feb = probes[(probes["OpenTime"] >= "2026-02-01") &
             (probes["OpenTime"] <  "2026-03-01")].copy()
feb = feb.sort_values("OpenTime").reset_index(drop=True)

print(f"Loaded {len(m15)} M15 bars  ({m15['DateTime'].min()} -> {m15['DateTime'].max()})")
print(f"Loaded {len(feb)} February probes  ({feb['OpenTime'].min()} -> {feb['OpenTime'].max()})")

# ----- Join probe -> signal-bar (the bar that closed AT probe time) ------------
signal = m15.set_index("CloseTime")
signal_cols = ["Open","High","Low","Close",
               "EMA10","EMA20","EMA50","EMA200",
               "RSI14","BB_upper","BB_mid","BB_lower","BB_pctB",
               "StochRSI_K","StochRSI_D",
               "StochRSI_K_prev","StochRSI_D_prev",
               "BarRangePips"]

# Try direct join. If a probe's timestamp doesn't match a CloseTime exactly,
# we'll need a timezone adjustment.
def try_join(offset_minutes):
    adj = feb.copy()
    adj["LookupTime"] = adj["OpenTime"] + pd.Timedelta(minutes=offset_minutes)
    joined = adj.merge(signal[signal_cols],
                       left_on="LookupTime", right_index=True,
                       how="left")
    return joined, joined[signal_cols[0]].notna().sum()

# Auto-detect a timezone offset by trying 0, +/-60, +/-120, +/-180 minutes
candidates = [0, 60, -60, 120, -120, 180, -180]
results = [(off, *try_join(off)) for off in candidates]
best = max(results, key=lambda r: r[2])
offset, joined, hits = best
print(f"Best offset: {offset:+d} min -> {hits}/{len(feb)} probes joined")

if hits < len(feb):
    missing = joined[joined["Close"].isna()][["Ticket","OpenTime","Type","Open Price"]]
    print(f"  WARNING: {len(missing)} probes did not align to a bar.")
    print(missing.to_string(index=False))

# ----- Hypothesis tests --------------------------------------------------------
j = joined.copy()
j["dir"] = j["Type"].str.lower()

# Standard thresholds
def h1_bb(row):  # Bollinger touch
    if row["dir"] == "sell": return row["BB_pctB"] >= 1.0
    if row["dir"] == "buy" : return row["BB_pctB"] <= 0.0
    return False

def h2_rsi(row, hi=70, lo=30):
    if row["dir"] == "sell": return row["RSI14"] >= hi
    if row["dir"] == "buy" : return row["RSI14"] <= lo
    return False

def h3_stoch(row):
    K, D, Kp, Dp = row["StochRSI_K"], row["StochRSI_D"], row["StochRSI_K_prev"], row["StochRSI_D_prev"]
    if any(pd.isna(x) for x in (K, D, Kp, Dp)): return False
    if row["dir"] == "sell":
        return (Kp >= 80) and (K < Kp) and (K < D)
    if row["dir"] == "buy":
        return (Kp <= 20) and (K > Kp) and (K > D)
    return False

def h3_stoch_loose(row):  # K in extreme zone, not requiring prior bar
    K, D = row["StochRSI_K"], row["StochRSI_D"]
    if pd.isna(K) or pd.isna(D): return False
    if row["dir"] == "sell": return K >= 80
    if row["dir"] == "buy" : return K <= 20
    return False

j["H1_BB"]            = j.apply(h1_bb, axis=1)
j["H2_RSI_70_30"]     = j.apply(lambda r: h2_rsi(r, 70, 30), axis=1)
j["H2_RSI_65_35"]     = j.apply(lambda r: h2_rsi(r, 65, 35), axis=1)
j["H2_RSI_60_40"]     = j.apply(lambda r: h2_rsi(r, 60, 40), axis=1)
j["H3_StochRSI_cross"]= j.apply(h3_stoch, axis=1)
j["H3_StochRSI_zone"] = j.apply(h3_stoch_loose, axis=1)
j["H4_BB_AND_RSI"]    = j["H1_BB"] & j["H2_RSI_70_30"]

# ----- Output joined table -----------------------------------------------------
out_cols = (["Ticket","OpenTime","Type","Open Price","Profit"] +
            ["Close","EMA10","EMA20","EMA50","EMA200",
             "RSI14","BB_upper","BB_mid","BB_lower","BB_pctB",
             "StochRSI_K","StochRSI_D","StochRSI_K_prev","StochRSI_D_prev",
             "BarRangePips"] +
            ["H1_BB","H2_RSI_70_30","H2_RSI_65_35","H2_RSI_60_40",
             "H3_StochRSI_cross","H3_StochRSI_zone","H4_BB_AND_RSI"])
j[out_cols].to_csv(OUT_JOIN_CSV, index=False, float_format="%.5f")
print(f"\nWrote {OUT_JOIN_CSV}")

# ----- Build hypothesis test report --------------------------------------------
total = len(j)
buys  = (j["dir"] == "buy").sum()
sells = (j["dir"] == "sell").sum()

def pct(n, d):
    return f"{n}/{d} ({100*n/d:.1f}%)" if d else "n/a"

hypotheses = [
    ("H1  BB(20,2) touch (sell >= upper, buy <= lower)",       "H1_BB"),
    ("H2  RSI(14) 70/30",                                    "H2_RSI_70_30"),
    ("H2' RSI(14) 65/35",                                    "H2_RSI_65_35"),
    ("H2'' RSI(14) 60/40",                                   "H2_RSI_60_40"),
    ("H3  Stoch-RSI(14,14,3,3) cross from extreme",          "H3_StochRSI_cross"),
    ("H3' Stoch-RSI %K in extreme zone (no cross required)", "H3_StochRSI_zone"),
    ("H4  BB touch AND RSI 70/30",                           "H4_BB_AND_RSI"),
]

lines = []
lines.append(f"# AUDCAD February Probe Validation - Hypothesis Test\n")
lines.append(f"**Generated**: {pd.Timestamp.now().isoformat(timespec='seconds')}")
lines.append(f"**Data**: {M15_FILE.name} ({m15['DateTime'].min().date()} -> {m15['DateTime'].max().date()})")
lines.append(f"**Probes**: {total} February probes ({buys} buys / {sells} sells)")
lines.append(f"**Timezone offset applied** (probe -> signal bar): {offset:+d} min\n")

lines.append("## Hit rate by hypothesis (signal-bar close, direction-matched)\n")
lines.append("| Hypothesis | All | Buys | Sells |")
lines.append("|---|---|---|---|")
for label, col in hypotheses:
    all_hits   = j[col].sum()
    buy_hits   = j.loc[j["dir"] == "buy",  col].sum()
    sell_hits  = j.loc[j["dir"] == "sell", col].sum()
    lines.append(f"| {label} | {pct(all_hits, total)} | {pct(buy_hits, buys)} | {pct(sell_hits, sells)} |")
lines.append("")

# Distribution stats
lines.append("## Indicator distribution at probe times\n")
def stat(col):
    s = j[col].describe(percentiles=[.1,.25,.5,.75,.9])
    return f"min={s['min']:.2f}  10%={s['10%']:.2f}  25%={s['25%']:.2f}  med={s['50%']:.2f}  75%={s['75%']:.2f}  90%={s['90%']:.2f}  max={s['max']:.2f}"

for col in ["RSI14","BB_pctB","StochRSI_K","StochRSI_D"]:
    lines.append(f"- **{col}**: {stat(col)}")
    lines.append(f"  - Buys:  {stat(col) if False else j.loc[j['dir']=='buy',col].describe(percentiles=[.1,.5,.9]).to_dict()}")
    lines.append(f"  - Sells: {j.loc[j['dir']=='sell',col].describe(percentiles=[.1,.5,.9]).to_dict()}")
lines.append("")

# Worst hits - list probes that no hypothesis explained
no_match = j[~(j["H1_BB"] | j["H2_RSI_70_30"] | j["H3_StochRSI_cross"])]
lines.append(f"## Probes that **no major hypothesis** (H1, H2-70/30, H3-cross) explains: {len(no_match)} of {total}\n")
if len(no_match) > 0:
    nm = no_match[["OpenTime","Type","Open Price","RSI14","BB_pctB","StochRSI_K","StochRSI_D"]].copy()
    for col in ["RSI14","BB_pctB","StochRSI_K","StochRSI_D"]:
        nm[col] = nm[col].round(2)
    lines.append("```")
    lines.append(nm.to_string(index=False))
    lines.append("```")

OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {OUT_REPORT}")

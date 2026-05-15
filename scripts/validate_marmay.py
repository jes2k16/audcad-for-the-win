"""
Out-of-sample validation of the Section 14.9b trigger rule against Mar-May 2026 data.

Section 14.9b rule:
  BUY  fires on M15 close when ALL of:
    - RSI(14) < 50          (direction gate)
    - any of: Stoch %K <= 20  OR  BB %B <= 0.10  OR  RSI <= 40

  SELL fires on M15 close when ALL of:
    - RSI(14) > 50          (direction gate)
    - any of: Stoch %K >= 60  OR  BB %B >= 0.90  OR  RSI >= 60
              OR price within 50 pips of 500-bar rolling swing high

Reports overall Mar-May hit rate, per-month breakdown, comparison vs Feb,
and the probes the rule misses (residuals).
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(r"d:/CLAUDE/AUDCAD FOR THE WIN")
M15_FILE    = ROOT / "data" / "AUDCAD_M15MarMay.csv"
PROBES_FILE = ROOT / "AUDCAD_1st_Position_History.csv"
OUT_CSV     = ROOT / "data" / "AUDCAD_MarMay_Probe_Indicators.csv"
OUT_REPORT  = ROOT / "data" / "AUDCAD_MarMay_Hypothesis_Test.md"
FEB_CSV     = ROOT / "data" / "AUDCAD_Feb_Probe_Indicators_v3.csv"

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
def bbpct(s, n=20, k=2):
    m = s.rolling(n).mean(); sd = s.rolling(n).std(ddof=0)
    U, L = m + k*sd, m - k*sd
    return (s - L) / (U - L)
def stoch(rsi_s, n=14, k=3, d=3):
    lo = rsi_s.rolling(n).min(); hi = rsi_s.rolling(n).max()
    K  = ((rsi_s - lo)/(hi - lo)*100).rolling(k).mean()
    return K, K.rolling(d).mean()

m15["EMA10"]  = ema(close, 10)
m15["EMA20"]  = ema(close, 20)
m15["EMA50"]  = ema(close, 50)
m15["EMA200"] = ema(close, 200)
m15["RSI14"]  = rsi(close, 14)
m15["BB_pctB"] = bbpct(close, 20, 2)
K, D = stoch(m15["RSI14"], 14, 3, 3)
m15["StochRSI_K"] = K; m15["StochRSI_D"] = D
m15["dist_EMA20_pips"]  = (close - m15["EMA20"]) * 10000
m15["dist_EMA200_pips"] = (close - m15["EMA200"]) * 10000
m15["rollHi_500"] = m15["High"].rolling(500).max()
m15["rollLo_500"] = m15["Low"].rolling(500).min()
m15["dist_to_rollHi_500_pips"] = (m15["rollHi_500"] - close) * 10000
m15["dist_to_rollLo_500_pips"] = (close - m15["rollLo_500"]) * 10000

# ----- Load probes and filter to Mar-May -------------------------------------
probes = pd.read_csv(PROBES_FILE)
probes["OpenTime"] = pd.to_datetime(probes["Open Time"], format="%m/%d/%Y %H:%M")
mm = probes[(probes["OpenTime"] >= "2026-03-01") &
            (probes["OpenTime"] <  "2026-05-08")].copy()
# Drop currently-open probes (no Close Time)
mm = mm.dropna(subset=["Close Time"]).copy()
mm = mm.sort_values("OpenTime").reset_index(drop=True)

print(f"Loaded {len(m15)} M15 bars  ({m15['DateTime'].min()} -> {m15['DateTime'].max()})")
print(f"Loaded {len(mm)} Mar-May probes  ({mm['OpenTime'].min()} -> {mm['OpenTime'].max()})")

# ----- Join ------------------------------------------------------------------
sig_cols = ["Close","EMA10","EMA20","EMA50","EMA200",
            "RSI14","BB_pctB","StochRSI_K","StochRSI_D",
            "dist_EMA20_pips","dist_EMA200_pips",
            "dist_to_rollHi_500_pips","dist_to_rollLo_500_pips"]
j = mm.merge(m15.set_index("CloseTime")[sig_cols],
             left_on="OpenTime", right_index=True, how="left")
j["dir"] = j["Type"].str.lower()
j["month"] = j["OpenTime"].dt.to_period("M").astype(str)
n_unmatched = j["Close"].isna().sum()
if n_unmatched > 0:
    print(f"  WARNING: {n_unmatched} probes did not align to a bar (likely weekend / gap):")
    print(j[j["Close"].isna()][["OpenTime","Type","Open Price"]].to_string(index=False))
    j = j.dropna(subset=["Close"]).copy()  # drop unmatched

buys, sells = j["dir"]=="buy", j["dir"]=="sell"
N, NB, NS = len(j), buys.sum(), sells.sum()
def pct(n, d): return f"{n}/{d} ({100*n/d:.0f}%)" if d else "n/a"

# ----- Apply Section 14.9b rule -----------------------------------------------------
def rule_14_9b(row):
    if pd.isna(row["RSI14"]) or pd.isna(row["StochRSI_K"]) or pd.isna(row["BB_pctB"]):
        return False
    if row["dir"] == "buy":
        if row["RSI14"] >= 50: return False  # direction gate
        return (row["StochRSI_K"] <= 20 or
                row["BB_pctB"]    <= 0.10 or
                row["RSI14"]      <= 40)
    if row["dir"] == "sell":
        if row["RSI14"] <= 50: return False  # direction gate
        return (row["StochRSI_K"] >= 60 or
                row["BB_pctB"]    >= 0.90 or
                row["RSI14"]      >= 60 or
                (not pd.isna(row["dist_to_rollHi_500_pips"]) and
                 row["dist_to_rollHi_500_pips"] <= 50))
    return False

j["rule_14_9b"] = j.apply(rule_14_9b, axis=1)

# Also test variant rules to see if any tuning improves OOS
def rule_loose(row):
    """Section 14.9b with wider sell threshold (Stoch >= 50 instead of >= 60)"""
    if pd.isna(row["RSI14"]) or pd.isna(row["StochRSI_K"]): return False
    if row["dir"] == "buy":
        if row["RSI14"] >= 50: return False
        return (row["StochRSI_K"] <= 20 or row["BB_pctB"] <= 0.10 or row["RSI14"] <= 40)
    if row["dir"] == "sell":
        if row["RSI14"] <= 50: return False
        return (row["StochRSI_K"] >= 50 or row["BB_pctB"] >= 0.85 or row["RSI14"] >= 55 or
                (not pd.isna(row["dist_to_rollHi_500_pips"]) and row["dist_to_rollHi_500_pips"] <= 80))
    return False
j["rule_loose"] = j.apply(rule_loose, axis=1)

def rule_strict(row):
    """Section 14.9b with classical extremes only (no swing-prox, no loose RSI)"""
    if pd.isna(row["RSI14"]) or pd.isna(row["StochRSI_K"]): return False
    if row["dir"] == "buy":
        if row["RSI14"] >= 50: return False
        return (row["StochRSI_K"] <= 20 or row["BB_pctB"] <= 0.10)
    if row["dir"] == "sell":
        if row["RSI14"] <= 50: return False
        return (row["StochRSI_K"] >= 80 or row["BB_pctB"] >= 0.90)
    return False
j["rule_strict"] = j.apply(rule_strict, axis=1)

# ----- Build report ----------------------------------------------------------
rep = []
rep.append("# AUDCAD Mar-May 2026 Out-of-Sample Validation\n")
rep.append(f"Rule under test: Section 14.9b composite trigger.")
rep.append(f"**Probes**: {N} closed Mar-May probes ({NB} buys / {NS} sells)\n")

# Headline
hit  = j["rule_14_9b"].sum()
bhit = (j["rule_14_9b"] & buys).sum()
shit = (j["rule_14_9b"] & sells).sum()
rep.append("## Headline\n")
rep.append("| Rule | All | Buys | Sells |")
rep.append("|---|---|---|---|")
rep.append(f"| **Section 14.9b (current)** | **{pct(hit, N)}** | {pct(bhit, NB)} | {pct(shit, NS)} |")
hl = j["rule_loose"].sum(); blhit = (j["rule_loose"] & buys).sum(); slhit = (j["rule_loose"] & sells).sum()
rep.append(f"| Section 14.9b loose (Stoch>=50/BB>=0.85/RSI>=55/swing<=80) | {pct(hl, N)} | {pct(blhit, NB)} | {pct(slhit, NS)} |")
hs = j["rule_strict"].sum(); bshit = (j["rule_strict"] & buys).sum(); sshit = (j["rule_strict"] & sells).sum()
rep.append(f"| Section 14.9b strict (Stoch 80/20 + BB only) | {pct(hs, N)} | {pct(bshit, NB)} | {pct(sshit, NS)} |")
rep.append("")

# By month
rep.append("## By month\n")
rep.append("| Month | Probes | Buys | Sells | Section 14.9b hit | Buys hit | Sells hit |")
rep.append("|---|---|---|---|---|---|---|")
for m, grp in j.groupby("month"):
    gN = len(grp)
    gB = (grp["dir"]=="buy").sum(); gS = (grp["dir"]=="sell").sum()
    gh = grp["rule_14_9b"].sum()
    gbh = (grp["rule_14_9b"] & (grp["dir"]=="buy")).sum()
    gsh = (grp["rule_14_9b"] & (grp["dir"]=="sell")).sum()
    rep.append(f"| {m} | {gN} | {gB} | {gS} | {pct(gh, gN)} | {pct(gbh, gB)} | {pct(gsh, gS)} |")
rep.append("")

# Comparison to Feb
rep.append("## Out-of-sample stability - Mar-May vs Feb\n")
try:
    feb = pd.read_csv(FEB_CSV)
    feb["dir"] = feb["Type"].str.lower()
    febN = len(feb)
    fbuys, fsells = feb["dir"]=="buy", feb["dir"]=="sell"
    # recompute Section 14.9b on feb
    def feb_rule(row):
        if pd.isna(row["RSI14"]) or pd.isna(row["StochRSI_K"]): return False
        if row["dir"] == "buy":
            if row["RSI14"] >= 50: return False
            return (row["StochRSI_K"] <= 20 or row["BB_pctB"] <= 0.10 or row["RSI14"] <= 40)
        if row["dir"] == "sell":
            if row["RSI14"] <= 50: return False
            return (row["StochRSI_K"] >= 60 or row["BB_pctB"] >= 0.90 or row["RSI14"] >= 60 or
                    (not pd.isna(row.get("dist_to_rollHi_500_pips", np.nan)) and
                     row["dist_to_rollHi_500_pips"] <= 50))
        return False
    feb["rule_14_9b"] = feb.apply(feb_rule, axis=1)
    fh = feb["rule_14_9b"].sum()
    fbh = (feb["rule_14_9b"] & fbuys).sum()
    fsh = (feb["rule_14_9b"] & fsells).sum()
    rep.append("| Window | Probes | All | Buys | Sells |")
    rep.append("|---|---|---|---|---|")
    rep.append(f"| **Feb (in-sample)** | {febN} | {pct(fh, febN)} | {pct(fbh, fbuys.sum())} | {pct(fsh, fsells.sum())} |")
    rep.append(f"| **Mar-May (out-of-sample)** | {N} | {pct(hit, N)} | {pct(bhit, NB)} | {pct(shit, NS)} |")
    drift = (hit/N) - (fh/febN)
    rep.append(f"\n**Drift**: Mar-May hit-rate vs Feb baseline = {drift*100:+.1f} percentage points.")
    if abs(drift) < 0.10:
        rep.append(f"-> **Rule is regime-stable** within +/-10 pp (acceptance threshold per Section 15.G2). [PASS]")
    else:
        rep.append(f"-> **Rule drifts beyond +/-10 pp** - needs regime-specific tuning or HTF filter. [WARN]")
except Exception as e:
    rep.append(f"(could not load Feb comparison: {e})")
rep.append("")

# Residuals
res = j[~j["rule_14_9b"]].copy()
rep.append(f"## Probes Section 14.9b does NOT explain: {len(res)} of {N}\n")
if len(res):
    cols_show = ["OpenTime","Type","Open Price","RSI14","BB_pctB","StochRSI_K",
                 "dist_EMA20_pips","dist_EMA200_pips","dist_to_rollHi_500_pips","dist_to_rollLo_500_pips"]
    nm = res[cols_show].copy()
    for c in cols_show[3:]:
        nm[c] = nm[c].round(2)
    rep.append("```")
    rep.append(nm.to_string(index=False))
    rep.append("```")

# Distribution of new probes' indicator state
rep.append("\n## Indicator distribution - Mar-May probes\n")
def stat(s):
    return f"med={s.median():.2f}  10%={s.quantile(.1):.2f}  90%={s.quantile(.9):.2f}"

rep.append("| Indicator | Buys | Sells |")
rep.append("|---|---|---|")
for ind in ["RSI14","BB_pctB","StochRSI_K","dist_EMA20_pips","dist_EMA200_pips","dist_to_rollHi_500_pips"]:
    rep.append(f"| {ind} | {stat(j.loc[buys, ind])} | {stat(j.loc[sells, ind])} |")

OUT_REPORT.write_text("\n".join(rep), encoding="utf-8")
j.to_csv(OUT_CSV, index=False, float_format="%.5f")
print(f"\nWrote {OUT_REPORT}")
print(f"Wrote {OUT_CSV}")
print()
print(f"Section 14.9b on Mar-May: {pct(hit, N)}  (buys {pct(bhit, NB)}, sells {pct(shit, NS)})")

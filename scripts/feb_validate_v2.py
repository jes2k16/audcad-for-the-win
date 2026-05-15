"""
February probe validation — v2.

v1 found that H3 (Stoch-RSI cross from extreme) only fits 2.3% of probes — but
H3' (Stoch-RSI %K in extreme zone, no cross required) fits 70.5%. This script
refines:
  - Tries multiple Stoch-RSI zone thresholds
  - Tests asymmetric buy/sell thresholds
  - Tests composite OR rules (H1 BB OR H3' zone)
  - Finds the smallest/cleanest rule that explains ≥90% of probes
  - Lists residual unexplained probes for inspection
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(r"d:/CLAUDE/AUDCAD FOR THE WIN")
JOIN_CSV  = ROOT / "data" / "AUDCAD_Feb_Probe_Indicators.csv"
OUT_REPORT = ROOT / "data" / "AUDCAD_Feb_Hypothesis_Test_v2.md"

j = pd.read_csv(JOIN_CSV)
j["dir"] = j["Type"].str.lower()
buys  = j["dir"] == "buy"
sells = j["dir"] == "sell"
N, NB, NS = len(j), buys.sum(), sells.sum()
def pct(n, d): return f"{n}/{d} ({100*n/d:.0f}%)"

# Threshold sweep on Stoch-RSI %K zone, asymmetric buy/sell allowed
rows = []
for sell_thr in (60, 65, 70, 75, 80, 85, 90):
    for buy_thr in (10, 15, 20, 25, 30, 35, 40):
        sell_hit = (sells & (j["StochRSI_K"] >= sell_thr)).sum()
        buy_hit  = (buys  & (j["StochRSI_K"] <= buy_thr )).sum()
        rows.append({
            "sell_thr": sell_thr, "buy_thr": buy_thr,
            "all_hits": sell_hit + buy_hit,
            "buy_hit":  buy_hit, "sell_hit": sell_hit,
            "all_pct":  (sell_hit + buy_hit) / N,
            "buy_pct":  buy_hit / NB,
            "sell_pct": sell_hit / NS,
        })
sweep = pd.DataFrame(rows).sort_values("all_hits", ascending=False).reset_index(drop=True)

# RSI sweep, asymmetric
rsi_rows = []
for sell_thr in (50, 55, 60, 65, 70):
    for buy_thr in (30, 35, 40, 45, 50):
        sh = (sells & (j["RSI14"] >= sell_thr)).sum()
        bh = (buys  & (j["RSI14"] <= buy_thr )).sum()
        rsi_rows.append(dict(sell_thr=sell_thr, buy_thr=buy_thr,
                             all_hits=sh+bh, buy_hit=bh, sell_hit=sh))
rsi_sweep = pd.DataFrame(rsi_rows).sort_values("all_hits", ascending=False).reset_index(drop=True)

# BB sweep, asymmetric (sell when pctB >= sell_thr, buy when pctB <= buy_thr)
bb_rows = []
for sell_thr in (0.7, 0.8, 0.9, 1.0):
    for buy_thr in (0.3, 0.2, 0.1, 0.0):
        sh = (sells & (j["BB_pctB"] >= sell_thr)).sum()
        bh = (buys  & (j["BB_pctB"] <= buy_thr )).sum()
        bb_rows.append(dict(sell_thr=sell_thr, buy_thr=buy_thr,
                            all_hits=sh+bh, buy_hit=bh, sell_hit=sh))
bb_sweep = pd.DataFrame(bb_rows).sort_values("all_hits", ascending=False).reset_index(drop=True)

# Composite rules
def rule_stoch_zone(row, sell_thr, buy_thr):
    if row["dir"] == "sell": return row["StochRSI_K"] >= sell_thr
    return row["StochRSI_K"] <= buy_thr

def rule_bb(row, sell_thr, buy_thr):
    if row["dir"] == "sell": return row["BB_pctB"] >= sell_thr
    return row["BB_pctB"] <= buy_thr

def rule_rsi(row, sell_thr, buy_thr):
    if row["dir"] == "sell": return row["RSI14"] >= sell_thr
    return row["RSI14"] <= buy_thr

# Candidate composite rules to test
candidates = [
    ("Stoch zone 80/20",                lambda r: rule_stoch_zone(r, 80, 20)),
    ("Stoch zone 75/25",                lambda r: rule_stoch_zone(r, 75, 25)),
    ("Stoch zone 70/30",                lambda r: rule_stoch_zone(r, 70, 30)),
    ("Stoch zone 60/40",                lambda r: rule_stoch_zone(r, 60, 40)),
    ("BB 1.0/0.0 (touch)",              lambda r: rule_bb(r, 1.0, 0.0)),
    ("BB 0.9/0.1",                      lambda r: rule_bb(r, 0.9, 0.1)),
    ("BB 0.8/0.2",                      lambda r: rule_bb(r, 0.8, 0.2)),
    ("RSI 60/40",                       lambda r: rule_rsi(r, 60, 40)),
    ("StochZone80/20 OR BBtouch1.0/0",  lambda r: rule_stoch_zone(r, 80, 20) or rule_bb(r, 1.0, 0.0)),
    ("StochZone75/25 OR BBtouch1.0/0",  lambda r: rule_stoch_zone(r, 75, 25) or rule_bb(r, 1.0, 0.0)),
    ("StochZone80/20 OR BB0.9/0.1",     lambda r: rule_stoch_zone(r, 80, 20) or rule_bb(r, 0.9, 0.1)),
    ("StochZone80/20 OR RSI60/40",      lambda r: rule_stoch_zone(r, 80, 20) or rule_rsi(r, 60, 40)),
    ("StochZone80/20 OR BB0.9/0.1 OR RSI60/40",
        lambda r: rule_stoch_zone(r,80,20) or rule_bb(r,0.9,0.1) or rule_rsi(r,60,40)),
]

comp_rows = []
for name, fn in candidates:
    fired = j.apply(fn, axis=1)
    all_h = fired.sum()
    b_h   = (fired & buys).sum()
    s_h   = (fired & sells).sum()
    comp_rows.append(dict(rule=name, all=pct(all_h, N), buys=pct(b_h, NB), sells=pct(s_h, NS),
                          all_pct=all_h/N))
comp_df = pd.DataFrame(comp_rows)

# Best single rule for residual analysis
def composite_winner(row):
    return (rule_stoch_zone(row, 80, 20)
            or rule_bb(row, 0.9, 0.1)
            or rule_rsi(row, 60, 40))
j["winner"] = j.apply(composite_winner, axis=1)
explained   = j[j["winner"]]
unexplained = j[~j["winner"]]

# Build report
lines = []
lines.append("# AUDCAD February Probe Validation — Hypothesis Test v2\n")
lines.append(f"**Probes**: {N} ({NB} buys / {NS} sells), broker time aligned.\n")

lines.append("## Top-10 Stoch-RSI %K zone configurations (asymmetric thresholds)\n")
lines.append("| sell ≥ %K | buy ≤ %K | total | buys | sells |")
lines.append("|---|---|---|---|---|")
for _, r in sweep.head(10).iterrows():
    lines.append(f"| {r.sell_thr:.0f} | {r.buy_thr:.0f} | {pct(r.all_hits, N)} | {pct(r.buy_hit, NB)} | {pct(r.sell_hit, NS)} |")
lines.append("")

lines.append("## Top-10 RSI(14) zone configurations\n")
lines.append("| sell ≥ RSI | buy ≤ RSI | total | buys | sells |")
lines.append("|---|---|---|---|---|")
for _, r in rsi_sweep.head(10).iterrows():
    lines.append(f"| {r.sell_thr:.0f} | {r.buy_thr:.0f} | {pct(r.all_hits, N)} | {pct(r.buy_hit, NB)} | {pct(r.sell_hit, NS)} |")
lines.append("")

lines.append("## Top BB %B configurations\n")
lines.append("| sell ≥ %B | buy ≤ %B | total | buys | sells |")
lines.append("|---|---|---|---|---|")
for _, r in bb_sweep.head(10).iterrows():
    lines.append(f"| {r.sell_thr:.2f} | {r.buy_thr:.2f} | {pct(r.all_hits, N)} | {pct(r.buy_hit, NB)} | {pct(r.sell_hit, NS)} |")
lines.append("")

lines.append("## Composite rule comparison\n")
lines.append("| Rule | All | Buys | Sells |")
lines.append("|---|---|---|---|")
for _, r in comp_df.iterrows():
    lines.append(f"| {r['rule']} | {r['all']} | {r['buys']} | {r['sells']} |")
lines.append("")

lines.append(f"## Probes the winning composite still does NOT explain: {len(unexplained)} of {N}\n")
if len(unexplained):
    cols = ["OpenTime","Type","Open Price","RSI14","BB_pctB","StochRSI_K","StochRSI_D","BarRangePips"]
    nm = unexplained[cols].copy()
    for c in ["RSI14","BB_pctB","StochRSI_K","StochRSI_D","BarRangePips"]:
        nm[c] = nm[c].round(2)
    lines.append("```")
    lines.append(nm.to_string(index=False))
    lines.append("```")

# Per-probe explanation map
lines.append("\n## Per-probe rule attribution (winning composite)\n")
lines.append("| OpenTime | Dir | Price | Stoch %K | BB %B | RSI | Hit by |")
lines.append("|---|---|---|---|---|---|---|")
for _, r in j.iterrows():
    hit = []
    if rule_stoch_zone(r, 80, 20): hit.append("Stoch")
    if rule_bb(r, 0.9, 0.1):       hit.append("BB")
    if rule_rsi(r, 60, 40):        hit.append("RSI")
    if not hit: hit = ["—"]
    lines.append(f"| {r['OpenTime']} | {r['Type']} | {r['Open Price']:.5f} | {r['StochRSI_K']:.1f} | {r['BB_pctB']:.2f} | {r['RSI14']:.1f} | {'+'.join(hit)} |")

OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {OUT_REPORT}")
print(f"Composite (StochZone80/20 OR BB0.9/0.1 OR RSI60/40): {pct(j['winner'].sum(), N)}")
print(f"  Buys: {pct((j['winner'] & buys).sum(), NB)}")
print(f"  Sells: {pct((j['winner'] & sells).sum(), NS)}")

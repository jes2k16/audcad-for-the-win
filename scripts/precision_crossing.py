"""
Section 14.9b precision deep-dive: crossing variants and active-period analysis.

Key question: Section 14.9b fires on 78% of M15 bars (zone condition).
What converts it to a precise trigger?

Tests:
  A. Restrict to active-trading period (Feb 1+) — eliminate Jan FPs
  B. Crossing variants — rule fires ONLY when indicator first crosses threshold
  C. Basket-isolation check — could concurrent baskets explain the probe gaps?
  D. Which threshold subset gives best precision/recall tradeoff
  E. Where in the zone do probes land (entry vs mid-zone vs exit)

Inputs (all on disk, no new data):
  - data/AUDCAD_M15.csv
  - data/AUDCAD_M15MarMay.csv
  - AUDCAD_1st_Position_History.csv

Output:
  - data/AUDCAD_Crossing_Precision.md
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT        = Path(r"d:/CLAUDE/AUDCAD FOR THE WIN")
M15_FEB     = ROOT / "data" / "AUDCAD_M15.csv"
M15_MARMAY  = ROOT / "data" / "AUDCAD_M15MarMay.csv"
PROBES_FILE = ROOT / "AUDCAD_1st_Position_History.csv"
OUT_REPORT  = ROOT / "data" / "AUDCAD_Crossing_Precision.md"

# ---------------------------------------------------------------------------
# Indicators
# ---------------------------------------------------------------------------
def add_indicators(df):
    df = df.copy()
    close = df["Close"]
    def ema(s, n): return s.ewm(span=n, adjust=False).mean()
    def rsi(s, n=14):
        d = s.diff(); up = d.clip(lower=0); dn = (-d).clip(lower=0)
        a = up.ewm(alpha=1/n, adjust=False).mean()
        b = dn.ewm(alpha=1/n, adjust=False).mean()
        return 100 - 100 / (1 + a / b.replace(0, np.nan))
    def bbpct(s, n=20, k=2):
        m = s.rolling(n).mean(); sd = s.rolling(n).std(ddof=0)
        U, L = m + k*sd, m - k*sd
        return (s - L) / (U - L)

    rsi14 = rsi(close)
    df["RSI14"]    = rsi14
    df["BB_pctB"]  = bbpct(close)
    lo = rsi14.rolling(14).min(); hi = rsi14.rolling(14).max()
    K  = ((rsi14 - lo) / (hi - lo) * 100).rolling(3).mean()
    df["StochRSI_K"] = K
    df["rollHi_500"] = df["High"].rolling(500).max()
    df["dist_to_rollHi_pips"] = (df["rollHi_500"] - close) * 10000

    # Previous-bar values for crossing detection
    df["RSI14_prev"]    = rsi14.shift(1)
    df["BB_pctB_prev"]  = df["BB_pctB"].shift(1)
    df["StochK_prev"]   = K.shift(1)

    df["CloseTime"] = df["DateTime"] + pd.Timedelta(minutes=15)
    return df

def load_m15(path):
    df = pd.read_csv(path)
    df["DateTime"] = pd.to_datetime(df["DateTime"], format="%Y.%m.%d %H:%M")
    df = df.sort_values("DateTime").reset_index(drop=True)
    return add_indicators(df)

# ---------------------------------------------------------------------------
# Trigger variants
# ---------------------------------------------------------------------------
def build_triggers(df):
    R, Rp     = df["RSI14"],    df["RSI14_prev"]
    K, Kp     = df["StochRSI_K"], df["StochK_prev"]
    B, Bp     = df["BB_pctB"],  df["BB_pctB_prev"]
    Hi        = df["dist_to_rollHi_pips"]

    # --- Existing Section 14.9b (zone = level) ---
    buy_zone  = (R < 50) & (K.le(20) | B.le(0.10) | R.le(40))
    sell_zone = (R > 50) & (K.ge(60) | B.ge(0.90) | R.ge(60) | Hi.le(50).fillna(False))
    df["buy_zone"]  = buy_zone
    df["sell_zone"] = sell_zone

    # --- Zone entry: first bar where zone becomes true after being false ---
    df["buy_zone_entry"]  = buy_zone  & (~buy_zone.shift(1).fillna(False))
    df["sell_zone_entry"] = sell_zone & (~sell_zone.shift(1).fillna(False))

    # --- Crossing variants: individual threshold crossings (current crosses, prev did not) ---
    # RSI crosses
    df["rsi_cross_down_40"]  = (R <= 40) & (Rp > 40)   # RSI drops below 40
    df["rsi_cross_down_35"]  = (R <= 35) & (Rp > 35)
    df["rsi_cross_up_60"]    = (R >= 60) & (Rp < 60)
    df["rsi_cross_up_65"]    = (R >= 65) & (Rp < 65)

    # Stoch crosses
    df["stoch_cross_down_20"] = (K <= 20) & (Kp > 20)  # StochRSI drops below 20
    df["stoch_cross_down_10"] = (K <= 10) & (Kp > 10)
    df["stoch_cross_up_60"]   = (K >= 60) & (Kp < 60)
    df["stoch_cross_up_80"]   = (K >= 80) & (Kp < 80)
    df["stoch_cross_up_90"]   = (K >= 90) & (Kp < 90)

    # BB crosses
    df["bb_cross_low_10"]  = (B <= 0.10) & (Bp > 0.10)
    df["bb_cross_low_00"]  = (B <= 0.00) & (Bp > 0.00)
    df["bb_cross_high_90"] = (B >= 0.90) & (Bp < 0.90)

    # --- Directional gate applied to crossings ---
    # Buy: need RSI < 50 gate
    df["buy_rsi40x"]    = (R < 50) & df["rsi_cross_down_40"]
    df["buy_rsi35x"]    = (R < 50) & df["rsi_cross_down_35"]
    df["buy_stoch20x"]  = (R < 50) & df["stoch_cross_down_20"]
    df["buy_stoch10x"]  = (R < 50) & df["stoch_cross_down_10"]
    df["buy_bb10x"]     = (R < 50) & df["bb_cross_low_10"]
    df["buy_bb00x"]     = (R < 50) & df["bb_cross_low_00"]
    # Composite crossing: any crossing fires while direction gate holds
    df["buy_any_cross"] = df["buy_rsi40x"] | df["buy_stoch20x"] | df["buy_bb10x"]
    df["buy_strict_cross"] = df["buy_rsi35x"] | df["buy_stoch10x"] | df["buy_bb00x"]

    # Sell: need RSI > 50 gate
    df["sell_rsi60x"]    = (R > 50) & df["rsi_cross_up_60"]
    df["sell_rsi65x"]    = (R > 50) & df["rsi_cross_up_65"]
    df["sell_stoch60x"]  = (R > 50) & df["stoch_cross_up_60"]
    df["sell_stoch80x"]  = (R > 50) & df["stoch_cross_up_80"]
    df["sell_stoch90x"]  = (R > 50) & df["stoch_cross_up_90"]
    df["sell_bb90x"]     = (R > 50) & df["bb_cross_high_90"]
    df["sell_any_cross"] = df["sell_rsi60x"] | df["sell_stoch60x"] | df["sell_bb90x"]
    df["sell_strict_cross"] = df["sell_rsi65x"] | df["sell_stoch80x"] | df["sell_bb90x"]

    # --- Stoch cross back up from OS (reversal signal within OS zone) ---
    # Buy: StochRSI was below 20 and now crosses UPWARD (reversal within buy zone)
    df["buy_stoch_reversal"] = buy_zone & (K > Kp) & (Kp <= 20)
    # Sell: StochRSI was above 80 and now crosses DOWNWARD (reversal within sell zone)
    df["sell_stoch_reversal"] = sell_zone & (K < Kp) & (Kp >= 80)

    return df

print("Loading M15 data...")
feb    = build_triggers(load_m15(M15_FEB))
marmay = build_triggers(load_m15(M15_MARMAY))

# ---------------------------------------------------------------------------
# Load probes
# ---------------------------------------------------------------------------
probes = pd.read_csv(PROBES_FILE)
probes["OpenTime"] = pd.to_datetime(probes["Open Time"], format="%m/%d/%Y %H:%M")
probes["dir"]      = probes["Type"].str.lower()
probes = probes.dropna(subset=["Close Time"])

feb_p    = probes[(probes["OpenTime"] >= "2026-02-01") & (probes["OpenTime"] < "2026-03-01")]
marmay_p = probes[(probes["OpenTime"] >= "2026-03-01") & (probes["OpenTime"] < "2026-05-08")]

# ---------------------------------------------------------------------------
# Precision function
# ---------------------------------------------------------------------------
def precision_recall(m15_df, probes_df, buy_col, sell_col, active_start=None):
    """
    Compute precision and recall for a given buy/sell trigger column pair.
    active_start: if set, only count bars from this date onwards (for FP filtering).
    """
    if active_start:
        m15_df = m15_df[m15_df["DateTime"] >= active_start]

    buy_times  = set(probes_df.loc[probes_df["dir"]=="buy",  "OpenTime"])
    sell_times = set(probes_df.loc[probes_df["dir"]=="sell", "OpenTime"])

    b_sig = m15_df[m15_df[buy_col].fillna(False)]
    s_sig = m15_df[m15_df[sell_col].fillna(False)]

    bTP = b_sig["CloseTime"].isin(buy_times).sum()
    sTP = s_sig["CloseTime"].isin(sell_times).sum()

    Nb, Ns = len(b_sig), len(s_sig)
    Ntot = Nb + Ns
    TP = bTP + sTP

    n_probes = len(probes_df)
    tdays = m15_df["DateTime"].dt.date.nunique()

    prec   = TP / Ntot  if Ntot  else 0
    recall = TP / n_probes if n_probes else 0
    bprec  = bTP / Nb   if Nb    else 0
    sprec  = sTP / Ns   if Ns    else 0
    brecall = bTP / len(buy_times)  if buy_times  else 0
    srecall = sTP / len(sell_times) if sell_times else 0

    return dict(
        Nb=Nb, Ns=Ns, Ntot=Ntot, bTP=bTP, sTP=sTP, TP=TP,
        prec=prec, recall=recall, bprec=bprec, sprec=sprec,
        brecall=brecall, srecall=srecall,
        fires_per_day=Ntot/tdays if tdays else 0,
        actual_per_day=n_probes/tdays if tdays else 0,
        tdays=tdays,
    )

# ---------------------------------------------------------------------------
# Run all variants on Feb (in-sample), two forms:
#   1. Full period (Jan+Feb, as before)
#   2. Active period only (Feb 1+)
# ---------------------------------------------------------------------------
trigger_pairs = [
    # label, buy_col, sell_col
    ("A. Section 14.9b zone (full period)",    "buy_zone",           "sell_zone"),
    ("A. Section 14.9b zone (Feb 1+ only)",    "buy_zone",           "sell_zone"),
    ("B. Zone entry (first bar of cluster)",   "buy_zone_entry",      "sell_zone_entry"),
    ("C. RSI cross (40/60)",                   "buy_rsi40x",         "sell_rsi60x"),
    ("C. RSI cross strict (35/65)",            "buy_rsi35x",         "sell_rsi65x"),
    ("D. Stoch cross (20/60)",                 "buy_stoch20x",       "sell_stoch60x"),
    ("D. Stoch cross strict (10/80)",          "buy_stoch10x",       "sell_stoch80x"),
    ("D. Stoch cross very strict (10/90)",     "buy_stoch10x",       "sell_stoch90x"),
    ("E. BB cross (0.10/0.90)",                "buy_bb10x",          "sell_bb90x"),
    ("E. BB cross strict (0.00/1.00+)",        "buy_bb00x",          "sell_bb90x"),
    ("F. Any crossing (composite)",            "buy_any_cross",      "sell_any_cross"),
    ("F. Strict crossing (composite)",         "buy_strict_cross",   "sell_strict_cross"),
    ("G. Stoch reversal (from extreme)",       "buy_stoch_reversal", "sell_stoch_reversal"),
]

print("\nComputing precision/recall for all trigger variants...")

feb_results_full   = []
feb_results_active = []

for label, bcol, scol in trigger_pairs:
    if "Feb 1+ only" in label:
        r = precision_recall(feb, feb_p, bcol, scol, active_start=pd.Timestamp("2026-02-01"))
    else:
        r = precision_recall(feb, feb_p, bcol, scol)
    r["label"] = label
    if "Feb 1+" in label:
        feb_results_active.append(r)
    else:
        feb_results_full.append(r)
    print(f"  {label[:45]:45s} prec={r['prec']*100:5.1f}%  recall={r['recall']*100:5.1f}%  fires/day={r['fires_per_day']:6.2f}")

# Also run the best-looking ones on Mar-May OOS
print("\nOOS Mar-May:")
mm_results = []
for label, bcol, scol in trigger_pairs:
    if "Feb 1+" in label:
        continue
    r = precision_recall(marmay, marmay_p, bcol, scol)
    r["label"] = label
    mm_results.append(r)
    print(f"  {label[:45]:45s} prec={r['prec']*100:5.1f}%  recall={r['recall']*100:5.1f}%  fires/day={r['fires_per_day']:6.2f}")

# ---------------------------------------------------------------------------
# Where in the zone do probes land? (position within cluster)
# ---------------------------------------------------------------------------
print("\nAnalysing probe position within zone clusters...")
feb["buy_cluster_id"]  = (feb["buy_zone"] != feb["buy_zone"].shift()).cumsum()
feb["sell_cluster_id"] = (feb["sell_zone"] != feb["sell_zone"].shift()).cumsum()

buy_times  = set(feb_p.loc[feb_p["dir"]=="buy",  "OpenTime"])
sell_times = set(feb_p.loc[feb_p["dir"]=="sell", "OpenTime"])

# Position of each bar within its zone cluster (1 = first bar)
def zone_position(df, zone_col, cluster_col):
    in_zone = df[df[zone_col]].copy()
    in_zone["pos"] = in_zone.groupby(cluster_col).cumcount() + 1
    return in_zone

buy_zone_bars  = zone_position(feb, "buy_zone",  "buy_cluster_id")
sell_zone_bars = zone_position(feb, "sell_zone", "sell_cluster_id")

# Tag which bars in zone have probes
buy_zone_bars["is_probe"]  = buy_zone_bars["CloseTime"].isin(buy_times)
sell_zone_bars["is_probe"] = sell_zone_bars["CloseTime"].isin(sell_times)

# Distribution: at what position within the zone do probes land?
bpos = buy_zone_bars[buy_zone_bars["is_probe"]]["pos"]
spos = sell_zone_bars[sell_zone_bars["is_probe"]]["pos"]

# Also: what fraction of the total zone-bar population is at position 1, 2, 3...?
bpos_all = buy_zone_bars["pos"]
spos_all = sell_zone_bars["pos"]

# ---------------------------------------------------------------------------
# Build report
# ---------------------------------------------------------------------------
lines = []
lines.append("# AUDCAD Crossing Trigger Analysis - Precision Deep-Dive\n")
lines.append(f"Section 14.9b fires on 78% of Feb bars (zone condition, not trigger event).")
lines.append(f"This script tests whether CROSSING variants improve precision to the G3 threshold (>=20%).\n")

def fmt_pct(x): return f"{x*100:.1f}%"
def pass_fail(prec, recall):
    g3 = "[PASS]" if prec >= 0.20 else "[WARN]"
    return g3

# Feb full period table
lines.append("## Feb results - all M15 bars (Jan+Feb)\n")
lines.append("| Variant | Fires/day | Buy fires | Sell fires | Precision | Buy prec | Sell prec | Recall | Buy recall | Sell recall | G3 |")
lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
for r in feb_results_full:
    lines.append(f"| {r['label']} | {r['fires_per_day']:.2f} | {r['Nb']} | {r['Ns']} | "
                 f"{fmt_pct(r['prec'])} | {fmt_pct(r['bprec'])} | {fmt_pct(r['sprec'])} | "
                 f"{fmt_pct(r['recall'])} | {fmt_pct(r['brecall'])} | {fmt_pct(r['srecall'])} | "
                 f"{pass_fail(r['prec'], r['recall'])} |")
lines.append("")

# Feb active period
lines.append("## Feb - active period only (Feb 1 onwards, excludes Jan FPs)\n")
lines.append("| Variant | Fires/day | Buy fires | Sell fires | Precision | Recall | G3 |")
lines.append("|---|---|---|---|---|---|---|")
for r in feb_results_active:
    lines.append(f"| {r['label']} | {r['fires_per_day']:.2f} | {r['Nb']} | {r['Ns']} | "
                 f"{fmt_pct(r['prec'])} | {fmt_pct(r['recall'])} | {pass_fail(r['prec'], r['recall'])} |")
lines.append("")

# OOS table
lines.append("## Mar-May OOS results\n")
lines.append("| Variant | Fires/day | Precision | Buy prec | Sell prec | Recall | G3 |")
lines.append("|---|---|---|---|---|---|---|")
for r in mm_results:
    lines.append(f"| {r['label']} | {r['fires_per_day']:.2f} | "
                 f"{fmt_pct(r['prec'])} | {fmt_pct(r['bprec'])} | {fmt_pct(r['sprec'])} | "
                 f"{fmt_pct(r['recall'])} | {pass_fail(r['prec'], r['recall'])} |")
lines.append("")

# Zone position analysis
lines.append("## Where in the zone do probes land? (Feb)\n")
lines.append("Shows probe count at each position within the zone cluster (position 1 = first bar of zone).\n")
lines.append("| Zone position | Buy probe count | Buy total bars at pos | Buy probe% | Sell probe count | Sell total bars | Sell probe% |")
lines.append("|---|---|---|---|---|---|---|")
for pos in range(1, 16):
    bn = (bpos == pos).sum()
    bt = (bpos_all == pos).sum()
    sn = (spos == pos).sum()
    st = (spos_all == pos).sum()
    bp = f"{bn/bt*100:.1f}%" if bt else "-"
    sp = f"{sn/st*100:.1f}%" if st else "-"
    if bn == 0 and sn == 0 and pos > 10: break
    lines.append(f"| {pos} | {bn} | {bt} | {bp} | {sn} | {st} | {sp} |")

lines.append(f"\n**Buy probes**: median zone position = {bpos.median():.0f}, mean = {bpos.mean():.1f}, max = {bpos.max()}")
lines.append(f"**Sell probes**: median zone position = {spos.median():.0f}, mean = {spos.mean():.1f}, max = {spos.max()}\n")

# Summary / interpretation
lines.append("## Interpretation\n")
# Find best variant by precision * recall harmonic
best_feb = max(feb_results_full, key=lambda r: 2*r['prec']*r['recall']/(r['prec']+r['recall']) if r['prec']+r['recall'] else 0)
best_oos = max(mm_results,       key=lambda r: 2*r['prec']*r['recall']/(r['prec']+r['recall']) if r['prec']+r['recall'] else 0)

lines.append(f"- Best F1 (Feb): **{best_feb['label']}** — prec {fmt_pct(best_feb['prec'])}, recall {fmt_pct(best_feb['recall'])}")
lines.append(f"- Best F1 (OOS): **{best_oos['label']}** — prec {fmt_pct(best_oos['prec'])}, recall {fmt_pct(best_oos['recall'])}")
lines.append("")
lines.append("### What this means for the EA")
lines.append("If NO crossing variant reaches 20% precision, Section 14.9b is a ZONE CONDITION (necessary")
lines.append("but not sufficient). The EA will need an additional point trigger within the zone:")
lines.append("- A candlestick event (e.g., hammer, engulfing) on the M15 bar")
lines.append("- A higher-timeframe signal (H1/H4 level test)")
lines.append("- A time-of-day filter reducing the valid entry window")
lines.append("- A sequential constraint (only fire if previous basket of same direction is closed)")
lines.append("")
lines.append("The crossing variants establish the FLOOR on precision — the starting point for adding filters.")

OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")
print(f"\nWrote {OUT_REPORT}")

"""Parse v1.6 backtest log into summary stats."""
import re
import os
import sys
from collections import Counter

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "back test result")


def parse_log(path):
    encodings = ["utf-8", "utf-16", "utf-16-le", "latin-1"]
    lines = None
    for enc in encodings:
        try:
            with open(path, encoding=enc) as f:
                lines = f.readlines()
            break
        except UnicodeDecodeError:
            pass
    if lines is None:
        raise RuntimeError(f"decode fail: {path}")

    cfg = {}
    for ln in lines[:120]:
        if "testing of" in ln and "from" in ln:
            m = re.search(r"from ([0-9.]+ [0-9:]+) to ([0-9.]+ [0-9:]+)", ln)
            if m:
                cfg["period"] = m.group(1) + " -> " + m.group(2)
        for key, pat in [
            ("min_conf", r"Min_Confluence_Count=([0-9]+)"),
            ("max_level", r"Grid_Max_Level_To_SL=([0-9]+)"),
            ("grid_step", r"Grid_Step_Pips=([0-9.]+)"),
            ("auto", r"Auto_Compute_Lot_Size_Based_On_Equity=(true|false)"),
            ("base_lot", r"Default_Base_Lot_Size=([0-9.]+)"),
            ("gate_ema", r"GateEMA_Period=([0-9]+)"),
            ("max_gap", r"Max_EMA200_Gap_Pips=([0-9.]+)"),
            ("atr", r"Enable_ATR_Pause=(true|false)"),
        ]:
            m = re.search(pat, ln)
            if m:
                cfg[key] = m.group(1)
        if "[AUTOSIZE]" in ln:
            m = re.search(r"base=([0-9.]+).*wc_pct=([0-9.]+).*mode=([a-z]+)", ln)
            if m:
                cfg["init_base"] = m.group(1)
                cfg["init_wc_pct"] = m.group(2)
                cfg["sizing_mode"] = m.group(3)

    counts = Counter()
    baskets = []
    cur = None
    start_eq = 2000.0
    final_eq = None

    for ln in lines:
        if "initial deposit" in ln.lower():
            m = re.search(r"initial deposit ([0-9.]+)", ln, re.I)
            if m:
                start_eq = float(m.group(1))

        for tag in [
            "PROBE_OPEN",
            "CLOSE_BASKET",
            "BLOCK_ADD",
            "SKIP_PROBE",
            "GATE_BLOCK",
            "ATR_PAUSE",
            "ATR_RESUME",
            "ADD_PAUSED",
        ]:
            if tag in ln:
                counts[tag] += 1

        m = re.search(
            r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\s+PROBE_OPEN \| (LONG|SHORT).*?base=([0-9.]+).*?wc_pct=([0-9.]+)",
            ln,
        )
        if m:
            cur = {
                "open": m.group(1),
                "dir": m.group(2),
                "legs": 1,
                "base": float(m.group(3)),
                "wc_pct": float(m.group(4)),
            }
            continue

        m = re.search(r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\s+ADD \|", ln)
        if m and cur:
            cur["legs"] += 1
            continue

        m = re.search(
            r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\s+CLOSE_BASKET \| (LONG|SHORT) \| p=[0-9.]+ \| lot=([0-9.]+) \| reason=([a-z_0-9.]+) net_pips=(-?[0-9.]+)",
            ln,
        )
        if m:
            baskets.append(
                {
                    "open": cur["open"] if cur else "?",
                    "close": m.group(1),
                    "dir": m.group(2),
                    "legs": cur["legs"] if cur else 0,
                    "total_lots": float(m.group(3)),
                    "reason": m.group(4),
                    "net_pips": float(m.group(5)),
                    "base": cur["base"] if cur else None,
                }
            )
            cur = None

    for ln in lines:
        if "Tester\tfinal balance" in ln or "Tester final balance" in ln:
            m = re.search(r"final balance\s+([0-9.]+)", ln, re.I)
            if m:
                final_eq = float(m.group(1))
                break

    probes = counts["PROBE_OPEN"]
    closes = counts["CLOSE_BASKET"]
    emerg = [b for b in baskets if "emergency" in b["reason"]]
    wins = sum(1 for b in baskets if b["net_pips"] > 0)
    net_pips = sum(b["net_pips"] for b in baskets)
    max_legs = max((b["legs"] for b in baskets), default=0)
    leg_dist = Counter(b["legs"] for b in baskets)

    gate_long = sum(1 for ln in lines if "GATE_BLOCK | LONG" in ln)
    gate_short = sum(1 for ln in lines if "GATE_BLOCK | SHORT" in ln)
    gap_blocks = sum(1 for ln in lines if "htf_gap" in ln and "GATE_BLOCK" in ln)
    veto_long = sum(1 for ln in lines if "htf_veto_buy" in ln)
    veto_short = sum(1 for ln in lines if "htf_veto_sell" in ln)
    monthly = Counter(b["open"][:7] for b in baskets)
    neg = [b for b in baskets if b["net_pips"] < 0]
    deep = sorted(baskets, key=lambda b: b["legs"], reverse=True)[:5]
    skip = counts["SKIP_PROBE"]

    bases = [b["base"] for b in baskets if b["base"] is not None]

    return {
        "cfg": cfg,
        "start_eq": start_eq,
        "final_eq": final_eq,
        "counts": counts,
        "probes": probes,
        "closes": closes,
        "wins": wins,
        "net_pips": net_pips,
        "max_legs": max_legs,
        "leg_dist": leg_dist,
        "gate_long": gate_long,
        "gate_short": gate_short,
        "gap_blocks": gap_blocks,
        "skip": skip,
        "emerg": emerg,
        "baskets": baskets,
        "base_min": min(bases) if bases else None,
        "base_max": max(bases) if bases else None,
        "veto_long": veto_long,
        "veto_short": veto_short,
        "monthly": monthly,
        "neg": neg,
        "deep": deep,
    }


def main():
    files = sys.argv[1:] or [
        "v1.6_2025_result_v7(2k).log",
        "v1.6_2025_result_v8(2k).log",
        "v1.6_2024_result_v7(2k).log",
        "v1.6_2024_result_v8(2k).log",
    ]
    for fn in files:
        path = os.path.join(BASE, fn)
        r = parse_log(path)
        fe = r["final_eq"]
        net = fe - r["start_eq"] if fe else None
        pct = (fe / r["start_eq"] - 1) * 100 if fe else None
        print("=" * 70)
        print(fn)
        print("cfg:", r["cfg"])
        if fe:
            print(f"final={fe:.2f} net={net:+.2f} pct={pct:+.2f}%")
        else:
            print("final=UNKNOWN")
        if r["closes"]:
            print(
                f"probes={r['probes']} closes={r['closes']} "
                f"win%={r['wins']/r['closes']*100:.1f}% net_pips={r['net_pips']:.1f}"
            )
        print(
            f"emerg={len(r['emerg'])} block_add={r['counts']['BLOCK_ADD']} "
            f"skip={r['skip']} atr_pause={r['counts']['ATR_PAUSE']}"
        )
        print(
            f"gate L/S={r['gate_long']}/{r['gate_short']} "
            f"gap_blocks={r['gap_blocks']} max_legs={r['max_legs']}"
        )
        if r["base_min"] is not None:
            print(f"base range={r['base_min']:.2f}-{r['base_max']:.2f}")
        print("leg_dist:", dict(sorted(r["leg_dist"].items())))
        print(f"veto L/S={r['veto_long']}/{r['veto_short']} neg_closes={len(r['neg'])}")
        print("deep:", [(b['open'], b['dir'], b['legs'], b['net_pips']) for b in r['deep']])
        for e in r["emerg"]:
            print(
                f"  EMERG {e['open']} {e['dir']} L{e['legs']} "
                f"lots={e['total_lots']:.2f} net={e['net_pips']}"
            )


if __name__ == "__main__":
    main()

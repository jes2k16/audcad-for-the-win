"""Parse the 2025 backtest event stream into per-basket records."""
import re

PIP = 0.0001
import os
HERE = os.path.dirname(os.path.abspath(__file__))
events = []
with open(os.path.join(HERE, 'events2025.txt'), encoding='utf-8') as f:
    for ln in f:
        ln = ln.rstrip('\n')
        m = re.match(r'([0-9.]+ [0-9:]+)\s+(PROBE_OPEN|ADD|CLOSE_BASKET)\s+\|\s+(LONG|SHORT)\s+\|\s+p=([0-9.]+)\s+\|\s+lot=([0-9.]+)\s+\|\s*(.*)', ln)
        if not m:
            print("NOMATCH:", ln)
            continue
        dt, ev, d, p, lot, rest = m.groups()
        events.append(dict(dt=dt, ev=ev, dir=d, p=float(p), lot=float(lot), rest=rest))

# Build baskets: PROBE_OPEN starts one, ADDs append, CLOSE_BASKET ends.
baskets = []
cur = None
for e in events:
    if e['ev'] == 'PROBE_OPEN':
        if cur is not None:
            print("WARN: probe while basket open", e['dt'])
        cur = dict(open_dt=e['dt'], dir=e['dir'], legs=[(e['p'], e['lot'])],
                   gate=e['rest'])
    elif e['ev'] == 'ADD':
        if cur is None:
            print("WARN: add with no basket", e['dt']); continue
        cur['legs'].append((e['p'], e['lot']))
    elif e['ev'] == 'CLOSE_BASKET':
        if cur is None:
            print("WARN: close with no basket", e['dt']); continue
        cur['close_dt'] = e['dt']
        cur['close_p'] = e['p']
        cur['total_lots'] = e['lot']
        nm = re.search(r'net_pips=(-?[0-9.]+)', e['rest'])
        rm = re.search(r'reason=([a-z_0-9.]+)', e['rest'])
        cur['net_pips'] = float(nm.group(1)) if nm else None
        cur['reason'] = rm.group(1) if rm else '?'
        cur['level'] = len(cur['legs'])
        # weighted avg entry
        tl = sum(l for _, l in cur['legs'])
        wavg = sum(p * l for p, l in cur['legs']) / tl
        cur['wavg'] = wavg
        cur['lot_sum'] = tl
        # lot-pips P/L using close price
        if cur['dir'] == 'LONG':
            lp = sum((cur['close_p'] - p) / PIP * l for p, l in cur['legs'])
        else:
            lp = sum((p - cur['close_p']) / PIP * l for p, l in cur['legs'])
        cur['lot_pips'] = lp
        baskets.append(cur)
        cur = None

open_at_end = cur  # last probe never closed in event stream

# ---- calibrate USD per lot-pip against actual balance change ----
START_BAL = 50000.00
FINAL_BAL = 56567.29
# the still-open basket was force-closed at end of test at 0.91648
if open_at_end:
    p, l = open_at_end['legs'][0]
    forced_close = 0.91648
    if open_at_end['dir'] == 'LONG':
        oe_lp = (forced_close - p) / PIP * l
    else:
        oe_lp = (p - forced_close) / PIP * l
else:
    oe_lp = 0.0
total_lot_pips = sum(b['lot_pips'] for b in baskets) + oe_lp
usd_per_lotpip = (FINAL_BAL - START_BAL) / total_lot_pips
for b in baskets:
    b['usd'] = b['lot_pips'] * usd_per_lotpip

# ================= SECTION 1 =================
lvl1 = [b for b in baskets if b['level'] == 1]
ladder = [b for b in baskets if b['level'] >= 2]
print("="*60)
print("TOTALS")
print(f"  baskets closed     : {len(baskets)}")
print(f"  + 1 still open at EOT (force-closed by tester)")
print(f"  total probes (lvl1 entries): {len(baskets)+ (1 if open_at_end else 0)}")
print(f"  total legs opened  : {sum(b['level'] for b in baskets) + (len(open_at_end['legs']) if open_at_end else 0)}")
print(f"  usd_per_lot_pip cal: {usd_per_lotpip:.4f}")
print(f"  net result         : {FINAL_BAL-START_BAL:+.2f} USD ({(FINAL_BAL/START_BAL-1)*100:+.2f}%)")
print()
print("SECTION 1 — every 1st entry")
print(f"  reached TP at level 1 (no ladder): {len(lvl1)}  ({len(lvl1)/len(baskets)*100:.1f}%)")
print(f"  created a ladder (level 2+)      : {len(ladder)}  ({len(ladder)/len(baskets)*100:.1f}%)")
win1 = [b for b in lvl1 if b['lot_pips'] > 0]
print(f"  level-1 winners: {len(win1)}/{len(lvl1)}   level-1 USD: {sum(b['usd'] for b in lvl1):+.2f}")

# ================= SECTION 2 =================
print()
print("SECTION 2 — laddered baskets (level >= 2)")
from collections import Counter
lvl_dist = Counter(b['level'] for b in ladder)
for lv in sorted(lvl_dist):
    grp = [b for b in ladder if b['level'] == lv]
    wins = sum(1 for b in grp if b['lot_pips'] > 0)
    usd = sum(b['usd'] for b in grp)
    print(f"  level {lv:2d}: {lvl_dist[lv]:3d} baskets | closed-as-win {wins:3d} | net {usd:+9.2f} USD | avg net_pips {sum(b['net_pips'] for b in grp)/len(grp):+.1f}")
print(f"  max level reached  : {max(lvl_dist)}")
print(f"  ladder total USD   : {sum(b['usd'] for b in ladder):+.2f}")

# net_pips at close: how many closed negative
neg = [b for b in baskets if b['net_pips'] is not None and b['net_pips'] < 0]
print()
print(f"  baskets closed with NEGATIVE net_pips (tp trigger vs bid/ask gap): {len(neg)}")

# write per-basket CSV
with open(os.path.join(HERE, 'baskets2025.csv'), 'w', encoding='utf-8') as o:
    o.write("idx,open_dt,close_dt,dir,level,wavg,close_p,total_lots,net_pips,reason,lot_pips,usd\n")
    for i, b in enumerate(baskets, 1):
        o.write(f"{i},{b['open_dt']},{b['close_dt']},{b['dir']},{b['level']},"
                f"{b['wavg']:.5f},{b['close_p']:.5f},{b['lot_sum']:.2f},"
                f"{b['net_pips']},{b['reason']},{b['lot_pips']:.3f},{b['usd']:.2f}\n")
print()
print("wrote /tmp/baskets2025.csv")
if open_at_end:
    print(f"open-at-EOT basket: {open_at_end['open_dt']} {open_at_end['dir']} "
          f"level={len(open_at_end['legs'])} forced-close lot_pips={oe_lp:.3f}")

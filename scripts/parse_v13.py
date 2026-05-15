"""Parse v1.3 backtest event stream into per-basket records."""
import re, os, csv, statistics, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PIP = 0.0001

events = []
with open(os.path.join(HERE, 'v13_events.txt'), encoding='utf-8') as f:
    for ln in f:
        ln = ln.rstrip('\n')
        m = re.match(r'([0-9.]+ [0-9:]+)\s+(PROBE_OPEN|ADD|CLOSE_BASKET|BLOCK_ADD)\s+\|\s+(LONG|SHORT)\s+\|\s+p=([0-9.]+)\s+\|\s+lot=([0-9.]+)\s+\|\s*(.*)', ln)
        if not m:
            print("NOMATCH:", ln)
            continue
        dt, ev, d, p, lot, rest = m.groups()
        events.append(dict(dt=dt, ev=ev, dir=d, p=float(p), lot=float(lot), rest=rest))

baskets = []
cur = None
block_add_count = 0
for e in events:
    if e['ev'] == 'PROBE_OPEN':
        if cur is not None:
            print("WARN: probe while basket open", e['dt'])
        bm = re.search(r'base=([0-9.]+)', e['rest'])
        wm = re.search(r'wc_pct=([0-9.]+)', e['rest'])
        cur = dict(open_dt=e['dt'], dir=e['dir'], legs=[(e['p'], e['lot'])],
                   base=float(bm.group(1)) if bm else None,
                   wc_pct_open=float(wm.group(1)) if wm else None,
                   blocked=False)
    elif e['ev'] == 'ADD':
        if cur is None: print("WARN: add no basket", e['dt']); continue
        cur['legs'].append((e['p'], e['lot']))
    elif e['ev'] == 'BLOCK_ADD':
        block_add_count += 1
        if cur is not None: cur['blocked'] = True
    elif e['ev'] == 'CLOSE_BASKET':
        if cur is None: print("WARN: close no basket", e['dt']); continue
        cur['close_dt'] = e['dt']
        cur['close_p'] = e['p']
        cur['total_lots'] = e['lot']
        nm = re.search(r'net_pips=(-?[0-9.]+)', e['rest'])
        rm = re.search(r'reason=([a-z_0-9.]+)', e['rest'])
        cur['net_pips'] = float(nm.group(1)) if nm else None
        cur['reason']   = rm.group(1) if rm else '?'
        cur['level']    = len(cur['legs'])
        tl = sum(l for _, l in cur['legs'])
        cur['wavg']    = sum(p*l for p, l in cur['legs']) / tl
        cur['lot_sum'] = tl
        if cur['dir'] == 'LONG':
            lp = sum((cur['close_p'] - p)/PIP * l for p, l in cur['legs'])
        else:
            lp = sum((p - cur['close_p'])/PIP * l for p, l in cur['legs'])
        cur['lot_pips'] = lp
        baskets.append(cur)
        cur = None

open_at_end = cur

# ---- calibrate USD per lot-pip against actual balance change ----
START_BAL = 100000.00
FINAL_BAL = 81651.42
oe_lp = 0.0
if open_at_end:
    p, l = open_at_end['legs'][0]
    # final reported balance includes whatever was open — we approximate using the last
    # known price. For a 0.05-lot LONG probe at 0.99416, force-closed near the end of test.
    # The actual close happens at end-of-test tester behavior; we accept the residual
    # absorbs into the calibration constant.
    pass

total_lot_pips = sum(b['lot_pips'] for b in baskets)
usd_per_lotpip = (FINAL_BAL - START_BAL) / total_lot_pips
for b in baskets:
    b['usd'] = b['lot_pips'] * usd_per_lotpip

# ----- summaries -----
n_tp     = sum(1 for b in baskets if b['reason'].startswith('tp'))
n_emerg  = sum(1 for b in baskets if b['reason'] == 'emergency_dd')
lvl1     = [b for b in baskets if b['level'] == 1]
ladder   = [b for b in baskets if b['level'] >= 2]
emerg    = [b for b in baskets if b['reason'] == 'emergency_dd']

print("="*64)
print(f"baskets closed     : {len(baskets)}  (+1 open at EOT)" if open_at_end else f"baskets closed     : {len(baskets)}")
print(f"  by close reason  : tp={n_tp}  emergency_dd={n_emerg}")
print(f"  level 1 (no ladder): {len(lvl1)}  ({len(lvl1)/len(baskets)*100:.1f}%)")
print(f"  laddered (level 2+): {len(ladder)}  ({len(ladder)/len(baskets)*100:.1f}%)")
print(f"total legs opened  : {sum(b['level'] for b in baskets)}")
print(f"BLOCK_ADD events   : {block_add_count}")
print(f"start / final / delta : {START_BAL:,.2f} / {FINAL_BAL:,.2f} / {FINAL_BAL-START_BAL:+,.2f} ({(FINAL_BAL/START_BAL-1)*100:+.2f}%)")
print(f"usd_per_lot_pip    : {usd_per_lotpip:.4f}")
print()
print("Base sizes used:")
for sz, n in collections.Counter(b['base'] for b in baskets).most_common():
    grp = [b for b in baskets if b['base'] == sz]
    print(f"  base={sz:.2f}: {n} probes, total USD {sum(b['usd'] for b in grp):+,.2f}")
print()
print("Level distribution (laddered):")
for lv, n in sorted(collections.Counter(b['level'] for b in ladder).items()):
    grp = [b for b in ladder if b['level'] == lv]
    wins = sum(1 for b in grp if b['lot_pips'] > 0)
    usd  = sum(b['usd'] for b in grp)
    avg_pips = statistics.mean(b['net_pips'] for b in grp)
    print(f"  L{lv:2d}: {n:3d} baskets | win {wins:3d} | net {usd:+10,.2f} USD | avg net_pips {avg_pips:+.1f}")
print()
print("Emergency exits:")
for b in emerg:
    print(f"  {b['open_dt']} -> {b['close_dt']} | {b['dir']} L{b['level']} | wavg={b['wavg']:.5f} close_p={b['close_p']:.5f}"
          f" total_lots={b['lot_sum']:.2f} net_pips={b['net_pips']:+.1f} usd={b['usd']:+,.2f}")

# write per-basket CSV
with open(os.path.join(HERE, 'v13_baskets.csv'), 'w', encoding='utf-8') as o:
    o.write("idx,open_dt,close_dt,dir,level,base,wavg,close_p,total_lots,net_pips,reason,lot_pips,usd\n")
    for i, b in enumerate(baskets, 1):
        o.write(f"{i},{b['open_dt']},{b['close_dt']},{b['dir']},{b['level']},{b['base']},"
                f"{b['wavg']:.5f},{b['close_p']:.5f},{b['lot_sum']:.2f},{b['net_pips']},{b['reason']},"
                f"{b['lot_pips']:.3f},{b['usd']:.2f}\n")
print(f"\nwrote {os.path.join(HERE,'v13_baskets.csv')}")

# rough direction / monthly stats
dirc = collections.Counter(b['dir'] for b in baskets)
mon = collections.Counter(b['open_dt'][:7] for b in baskets)
print("direction split:", dict(dirc))
print("monthly probes:", dict(sorted(mon.items())))

# duration
def pt(s): return datetime.datetime.strptime(s, '%Y.%m.%d %H:%M:%S')
durs = [(pt(b['close_dt']) - pt(b['open_dt'])).total_seconds()/3600 for b in baskets]
print(f"duration h: min={min(durs):.1f} med={sorted(durs)[len(durs)//2]:.1f} max={max(durs):.1f}")

# best / worst basket
worst = min(baskets, key=lambda r: r['lot_pips'])
best  = max(baskets, key=lambda r: r['lot_pips'])
print("worst:", worst['open_dt'], worst['dir'], 'L'+str(worst['level']), 'reason='+worst['reason'],
      'net_pips=', worst['net_pips'], 'usd=', worst['usd'])
print("best :", best['open_dt'], best['dir'], 'L'+str(best['level']), 'reason='+best['reason'],
      'net_pips=', best['net_pips'], 'usd=', best['usd'])

# negative-net-pips count
neg = [b for b in baskets if b['net_pips'] is not None and b['net_pips'] < 0]
print(f"negative net_pips closes: {len(neg)}")

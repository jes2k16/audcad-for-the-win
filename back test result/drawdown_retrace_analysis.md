# Drawdown & Retrace Analysis — 2023 / 2024 Emergency Baskets

**Purpose**: Map every emergency trigger (date, pips, lot context), measure the total adverse move from L1 to the absolute price extreme, compute the 50% Fibonacci retrace level, and show how lot size determines whether the basket lives long enough to see that retrace.

---

## 1. Emergency Trigger Dates — Where Max Drawdown Fired

### 2023 (v1.4, $1k auto-lot, 22-pip grid, Max_Level=10)

| # | Basket open | Direction | L1 entry price | Emergency date/time | Emergency close price | Adverse pips (L1→close) | Lots at close |
|---|---|---|---|---|---|---|---|
| E1 | Jun 8, 11:00 | SHORT | 0.89133 | **Jun 16, 09:21** | 0.91138 | +200.5 pips | 67.36 |
| E2 | Jun 19, 13:00 | LONG | ~0.91000 | **Jun 23, 05:05** | 0.88548 | −245+ pips | 50.52 |

Both emergencies hit 8 legs (L1–L8) with base lot 0.16 (E1) and 0.12 (E2) — auto-sized to elevated equity (~$1,500+) from 5 months of gains.

**What triggered them**: June 2023 delivered a bearish→bullish 200-pip rally (E1) immediately followed by a bullish→bearish 245-pip reversal (E2) — a double whipsaw within 7 days at peak equity.

---

### 2024 (multiple runs — same calendar events, different lot configs)

The two recurring fatal baskets in 2024 show up across every run. The exact trigger date shifts by lot size because the emergency fires when **DD% = 35%**, and lot size determines how deep the price must go to reach 35%.

#### Basket A — April SHORT (D1 aligned short, AUDCAD rallied against it)

| Run | L1 open | L1 price | Emergency date | Emergency price | Adverse from L1 | Legs |
|---|---|---|---|---|---|---|
| v1.4 v1 (auto 0.11) | Apr 2, 01:15 | 0.88082 | **Apr 9, 17:10** | 0.90075 | +199.3 pips | 8 |
| v1.5 v4 (auto 0.76) | Apr 2 | ~0.88082 | **Apr 9** | ~0.90075 | +199 pips | 6 |
| v1.4 v2 (fixed 0.10) | Apr 2, 01:15 | 0.88082 | **No emergency** ✅ | — | survived | 8→TP Apr 10 |
| v1.5 v3 (fixed 0.10, Lv=6) | Apr 2 | ~0.88082 | **No emergency** ✅ | — | survived | ≤6→TP |

**Absolute price peak for April basket**: 0.90075 (Apr 9, 17:10) — this was also the emergency close price for v1.4 v1. Price reversed within 5 minutes; TP (0.89136) hit 24 hours later (Apr 10, 17:00).

#### Basket B — July LONG (the recurring fatal, appears in every run)

| Run | L1 open | L1 price | Emergency date | Emergency price | Adverse from L1 | Lots |
|---|---|---|---|---|---|---|
| v1.4 v2 (fixed 0.10) | Jul 15, 20:15 | 0.92532 | **Jul 25, 07:08** | 0.90450 | −208.2 pips | 52.90 |
| v1.5 v4 (auto) | Jul 16, 11:45 | 0.92216 | **Jul 25** | ~0.90713 | −150.3 pips | 54.50 |
| v1.5 v5 (fixed 0.30) | Jul 16, 11:45 | 0.92216 | **Jul 31, 04:30** | 0.90049 | −216.7 pips | 72.30 |
| v1.5 v6 (fixed 0.20) | Jul 16, 11:45 | 0.92216 | **Aug 5, 08:52** | 0.89549 | −266.7 pips | 48.20 |
| v1.5 v3 (fixed 0.10, Lv=6) | Jul 16, 11:45 | 0.92216 | **No emergency** ✅ | — | held to Aug 5 low | 24.10→TP Aug 16 |

**Absolute price bottom for July basket**: **0.88937** (Aug 5, 10:00) — 327.9 pips below L1 at 0.92216. This is the same low regardless of lot size; only the trigger date changes.

---

## 2. Total Pip Drawdown vs 50% Retrace from L1

The 50% retrace level is the midpoint between the L1 entry price and the absolute adverse extreme. It represents the point where price has recovered half the total adverse move — a natural Fibonacci support/resistance zone.

### Basket A — April 2024 SHORT (L1: 0.88082, absolute top: 0.90075)

```
L1 entry (SHORT):         0.88082
Absolute adverse peak:    0.90075   ← +199.3 pips from L1
50% retrace level:        0.89079   ← price falls 100 pips from peak back toward L1
TP level (wavg − 10pip):  0.89136   ← computed from 8-leg weighted avg entry

Distance from L1 to 50% retrace: 99.7 pips below the peak (toward L1)
TP vs 50% retrace:        TP at 0.89136 ≈ ABOVE 50% retrace (0.89079)
→ TP requires only ~47% retrace from the adverse peak
→ The market hit TP (0.89136) in just 24 hours after the peak
```

**Conclusion**: The April SHORT basket needed only a **~47% retrace** of the total adverse move for TP. The market gave a full reversal and hit TP the next day. **Emergency was unnecessary — the cap fired at the absolute peak.**

### Basket B — July 2024 LONG (L1: 0.92216, absolute bottom: 0.88937)

```
L1 entry (LONG):          0.92216
Absolute adverse bottom:  0.88937   ← −327.9 pips from L1 (Aug 5 low)
50% retrace level:        0.90577   ← price recovers 164 pips from bottom
                                      (still 163.9 pips BELOW L1)
TP level (wavg + 10pip):  0.91265   ← computed from 6-leg weighted avg entry (v3 config)
                                      (weighted avg ~0.91165)

Distance from L1 to 50% retrace: 163.9 pips below L1
Pips from bottom to TP:   0.91265 − 0.88937 = 232.8 pips of recovery required
% retrace needed for TP:  232.8 / 327.9 = 71% of the total adverse move

Price path after absolute low:
  Aug 5  0.88937   absolute low
  Aug 9  0.90503   ~48% retrace reached (crosses 50% zone)
  Aug 16 0.91291   TP hit — 71% retrace complete ✅
```

**Conclusion**: The July LONG basket required a **~71% retrace** of the full adverse move for TP. Price reached the 50% retrace level around Aug 9 (4 days after the low), and full TP was hit on Aug 16 — 31 days after L1. **The basket that emergency'd in most runs closed at profit in v3 because the 0.10 lot let it survive to see that retrace.**

### 2023 Emergency Baskets (approximate, less detailed data)

| Basket | Dir | L1 price | Adverse peak | Total adverse pips | 50% retrace level | TP reachable? |
|---|---|---|---|---|---|---|
| E1 Jun 8–16 | SHORT | 0.89133 | 0.91138 | +200.5 pips | 0.90136 (100 pips from peak) | Yes — price rallied past 0.91138 then reversed; would have TP'd post-peak |
| E2 Jun 19–23 | LONG | ~0.91000 | 0.88548 | ~245 pips | ~0.89774 (123 pips from low) | Unknown — no post-emergency recovery data available |

The 2023 E2 LONG basket emergency-closed at 0.88548. The subsequent AUDCAD price action after Jun 23 is not captured in the logs, but given the "whipsaw" pattern (the same pair that rallied 200 pips then dropped 245 pips within 7 days), a 50%+ retrace of E2 likely occurred within days — but the account was already frozen.

---

## 3. Does Retrace Improve Based on Lot Size?

**Short answer: lot size does not change the price at which TP fires, but it determines whether the basket survives long enough to see the retrace.**

### How lot size affects emergency timing (July LONG basket)

| Fixed base lot | Emergency fires at... | DD% when cap fires | Pips below L1 at emergency | Price at emergency | Distance to TP | Retrace outcome |
|---|---|---|---|---|---|---|
| **0.10** | **Never fires** | 20.3% at absolute low | **327.9 pips** (held to bottom) | 0.88937 (bottom) | +232.8 pips needed | **TP hit Aug 16 (+12.5 pips)** ✅ |
| 0.20 | Aug 5, 08:52 | 35% | 266.7 pips below L1 | 0.89549 | +171.6 pips needed | Emergency fires — no retrace |
| 0.30 | Jul 31, 04:30 | 35% | 216.7 pips below L1 | 0.90049 | +121.6 pips needed | Emergency fires — no retrace |
| **auto (~0.76)** | Jul 25 | **35%** | **150.3 pips below L1** | 0.90713 | +55 pips needed | **Emergency fires earliest** |

**Key finding**: The smaller the lot, the longer the basket can float adverse, giving the market more time to retrace. At 0.10, the emergency cap is unreachable on this move (only 20.3% DD at the absolute bottom), so the basket simply waits — and price delivers the retrace. At 0.30, the cap fires 110 pips before the bottom, cutting the position before any recovery. At auto-sizing, the cap fires even earlier (150 pips from L1).

### The retrace quality comparison

| Lot config | Saw retrace? | How? | Outcome |
|---|---|---|---|
| Fixed 0.10 (v3) | Yes — 71% retrace waited for | 24.10 lots float at 20% DD maximum; basket stays open 31 days | +$159 for 2024 year |
| Fixed 0.20 (v6) | No — forced exit 267 pips into the move | Cap fires at 35% DD = ~$590 loss | −$258 for 2024 year |
| Fixed 0.30 (v5) | No — forced exit 217 pips into the move | Cap fires at 35% DD = ~$609 loss | −$127 for 2024 year |
| Auto 0.76+ (v4) | No — forced exit 150 pips into the move | Cap fires almost immediately at 35% DD | −$744 for 2024 year |

### Does bigger lot = better retrace?

**No — it's the opposite.** Bigger lots = emergency fires sooner = less time for price to retrace = no TP.

The mechanism:
- **Lot size × pip move = floating loss in dollars**
- Emergency fires when floating loss = 35% of equity
- Bigger lot → same pip move → bigger loss → 35% cap reached sooner
- Less time waiting → less chance price retraces to TP

**Auto-sizing is the worst case**: the auto-sizer deliberately calibrates the base so that the full ladder consumes ~35% of equity by design. This means ANY sustained adverse move past the ladder bottom immediately triggers the emergency, with zero room for a retrace.

### The core trade-off: size vs survival

```
Lot size →     SMALL (0.10)         MEDIUM (0.20–0.30)      LARGE (auto 0.76+)
DD per pip →   low                  moderate                 high
Emergency →    unreachable*         fires at 35% (deep)     fires at 35% (early)
Retrace →      waits for it         cut before retrace       cut earliest
TP rate →      99%+ (all close)     1 emergency/year         3 emergencies/year
Return →       low but consistent   volatile (valley effect) volatile (very high swings)

*at Max_Level=6 + $2k + 0.10 lot, wc_pct=4.6% — the cap literally cannot fire on a 330-pip AUDCAD move
```

---

## 4. The Valley Effect (Key Structural Finding)

Testing lot sizes 0.10, 0.20, and 0.30 on 2024 revealed a non-intuitive **valley**:

| Fixed lot | 2024 result | 2025 result | 2-year total |
|---|---|---|---|
| 0.10 | +7.96% | +6.86% | **+$296** |
| **0.20** | **−12.88%** | **+13.71%** | **+$17** (worst) |
| 0.30 | −6.35% | +20.57% | **+$284** |

**0.20 is the worst option** — it crosses the emergency threshold (like 0.30) but earns less per winning basket (like 0.10). The emergency damage is **identical** at both 0.20 and 0.30 because the cap fires at 35% of equity regardless of lot size — but 0.30's larger lots generate more profit across the 110–120 winning baskets per year to offset it.

The valley boundary is around **0.15–0.17**: this is the largest lot that keeps the July basket floating below 35% DD at the absolute low. Below that threshold = zero emergencies. Above it = one or more capped emergencies.

---

## 5. Summary Table — All Emergency Events

| Year | Run | Emergency # | Date | Direction | L1 entry | Emergency price | Pips from L1 | Lots | $ loss | Post-emergency |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023 | v1.4 auto | E1 | **Jun 16** | SHORT | 0.89133 | 0.91138 | +200.5 | 67.36 | ~$365 | Account active |
| 2023 | v1.4 auto | E2 | **Jun 23** | LONG | ~0.91000 | 0.88548 | ~−245 | 50.52 | ~$271 | Frozen $838 (6mo) |
| 2024 | v1.4 auto | E1 | **Apr 9** | SHORT | 0.88082 | 0.90075 | +199.3 | 46.31 | ~$293 | Frozen $815 (9mo) |
| 2024 | v1.4 fixed | E1 | **Jul 25** | LONG | 0.92532 | 0.90450 | −208.2 | 52.90 | ~$342 | Frozen $935 (5mo) |
| 2024 | v1.5 v1 (3,Lv10) | E1 | **Aug 5** | LONG | ~0.92216 | ~0.89200 | ~−300 | 52.90 | ~$584 | Trading resumes |
| 2024 | v1.5 v1 (3,Lv10) | E2 | **Sep 27** | SHORT | ~Sep 11 | — | ~−224 | 42.10 | ~$429 | Frozen Q4 |
| 2024 | v1.5 v2 (4,Lv10) | E1 | **Aug 5** | LONG | Jul 16 @ 0.92216 | — | −300+ | 52.90 | ~$569 | Recovered |
| 2024 | v1.5 v4 (auto,Lv6) | E1 | **Apr 9** | SHORT | Apr | — | ~−199 | 94.83 | ~$612 | Trading resumes |
| 2024 | v1.5 v4 (auto,Lv6) | E2 | **Apr 19** | LONG | Apr | — | ~−86 | 70.85 | ~$461 | Trading resumes |
| 2024 | v1.5 v4 (auto,Lv6) | E3 | **Jul 25** | LONG | Jul 16 @ 0.92216 | 0.90713 | −150.3 | 54.50 | ~$357 | Trading resumes |
| 2024 | v1.5 v5 (0.30,Lv6) | E1 | **Jul 31** | LONG | Jul 16 @ 0.92216 | 0.90049 | −216.7 | 72.30 | ~$609 | Recovered |
| 2024 | v1.5 v6 (0.20,Lv6) | E1 | **Aug 5** | LONG | Jul 16 @ 0.92216 | 0.89549 | −266.7 | 48.20 | ~$588 | Recovered |
| 2024 | v1.5 v3 (0.10,Lv6) | — | **None** ✅ | — | Jul 16 @ 0.92216 | held | −327.9 (floated) | 24.10 | $0 | TP +$159 |

---

## 6. Key Conclusions

1. **The two "dangerous" dates across all runs**: April 9 (2024 SHORT apex) and July 16–31 (2024 LONG drop). Every run that emergency'd in 2024 hit one or both of these events. June 16 and June 23 are the 2023 equivalents.

2. **50% retrace math is run-specific** — the April SHORT needed only 47% retrace for TP (shallow move, quick reversal). The July LONG needed 71% retrace (deep sustained drop, slow recovery). The bigger the move past L1, the more retrace % is needed before TP fires.

3. **Lot size does NOT improve retrace probability** — it is the opposite. Smaller lots = cap further away = basket survives longer = natural retrace has time to reach TP. The 0.10 fixed lot is the only config that survived the Jul-16 basket and collected the retrace on Aug 16.

4. **Auto-sizing is the worst for retrace survival** — by design it consumes the full 35% budget, so even a modest adverse move triggers the cap immediately. The auto-sizer trades 3× more baskets but emergency-exits at the worst possible moments, long before any retrace.

5. **The zero-emergency safe ceiling is ~0.15 lots** (at $2k, Max_Level=6, 30-pip grid). Below this threshold, the Jul-16 basket floats below 35% DD even at the absolute bottom → basket waits → retrace delivers TP. Above 0.17, the cap fires and cuts the position before recovery.

6. **2023 was structurally worse**: two emergencies in 7 days at peak equity, with E2 opening immediately after E1 before the account could recover. No configuration tested has replayed 2023 at the winning v3 settings yet — this remains the final validation gate.

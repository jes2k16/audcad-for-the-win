# v1.4_2023_result_v1
## settings
- balance: 1,000.00 USD
- account: micro (AUDCADm#, XM cent)
- auto compute lot size: true
- base lot range: 0.10→0.16 (equity-scaled, peaked early Jun)
- max dd: 35%
- max level: 10
- pips/level: 22
- gate: ON (HTF D1 EMA20)

## results
- balance: 838.18 USD (−16.18%)
- total baskets closed: 221 (all Jan–Jun; 0 trades Jul–Dec)
- win rate: 95.5% (211/221)
- emergency closes: 2 (Jun 16 SHORT L8 −77.6 pips; Jun 23 LONG L8 −76.7 pips)
- block add: 0
- max legs hit: 8
- total net pips: +2,555
- post-emergency: permanently frozen (eq $838 < $963 vol_min floor)
- notes: two L8 emergencies in 7 days in June wiped 5 months of gains; account idle rest of year

---

# v1.4_2025_result_v1
## settings
- balance: 1,000.00 USD
- account: micro
- auto compute lot size: true
- base lot size for 1k USD: 0.11
- max dd: 35%
- max level: 10
- pips/level: 22

## results
- balance: 2,074.72 USD (+107.47%)
- total trades: 622
- basket closes: 368
- win rate: 95.4% (351/368)
- emergency closes: 0
- block add: 0
- max legs hit: 6
- gate: ON (HTF D1 EMA20)
- trades up to december

# v1.4_2024_result_v2
## settings
- balance: 1,000.00 USD
- account: micro (AUDCADm#, XM cent)
- auto compute lot size: false (fixed)
- base lot size: 0.10 (fixed throughout)
- max dd: 35%
- max level: 10
- pips/level: 22
- gate: ON (HTF D1 EMA20)

## results
- balance: 934.97 USD (−6.50%)
- total probes: 151
- basket closes: 151 (Jan–Jul 25; 0 trades Jul 25–Dec)
- win rate: 95.4% (144/151)
- emergency closes: 1 (Jul 25 LONG L9 −85.6 pips on 52.90 lots; L1 Jul 15 → L9 Jul 25 → L10 blocked → emergency Jul 25 07:08; ~218 pips adverse)
- block add: 2 (Apr 9 L9 blocked — basket survived; Jul 25 L10 blocked → emergency)
- max legs hit: 9 (Jul emergency)
- total net pips: +1,610.9
- gate: ON
- post-emergency: permanently frozen (eq $935 < $963 vol_min floor)
- post-emergency price: continued falling 153 pips to low 0.88921 (Aug 5); TP would have hit Aug 19 (~75% DD at low — cap was protective, not premature)
- notes: fixed 0.10 lot saved April basket (same basket that caused v1 emergency); July brought deeper 9-leg emergency; +12% better than v1

---

# v1.4_2024_result_v1
## settings
- balance: 1,000.00 USD
- account: micro
- auto compute lot size: true
- base lot size for 1k USD: 0.11
- max dd: 35%
- max level: 10
- pips/level: 22

## results
- balance: 815.27 USD (−18.5%)
- total trades: 138
- basket closes: 84 (Jan–Apr 1 only)
- win rate: ~94% (pre-emergency)
- emergency closes: 1 (Apr 9, 8-leg SHORT, −83.9 pips on 46.31 lots; L1 Apr 2 → L8 Apr 8 → L9 blocked → emergency Apr 9 17:10; ~199 pips adverse)
- block add: 1 (leg 9 blocked by DD fwd-check, Apr 9 16:30)
- max legs hit: 8 (L1–L8 active; L9 blocked before firing)
- reversal: price peaked at 0.90075 (emergency close = absolute top); reversed immediately; TP would have hit Apr 10 17:00 (24 h later) — 0 additional levels needed
- gate: ON
- post-emergency: 0 trades rest of year (equity $815 < $963 vol_min floor — permanently frozen)
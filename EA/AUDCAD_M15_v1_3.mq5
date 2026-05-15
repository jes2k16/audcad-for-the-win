//+------------------------------------------------------------------+
//|                                         AUDCAD_M15_v1_3.mq5     |
//|                     AUDCAD Mean-Reversion EA — v1.3              |
//|                                                                  |
//| Signal:  strategy/AUDCAD_M15_v1.md   §1-5                       |
//| Gate:    strategy/AUDCAD_M15_v1.1.md §1-3 (D1 EMA20)            |
//| Exit:    strategy/AUDCAD_M15_v1.2.md §2  (+10 pip net target)   |
//| Sizing:  strategy/AUDCAD_M15_v1.3.md §2  (equity-scaled base)   |
//| Risk:    plans/1.initial requirements.md §9,10                  |
//|                                                                  |
//| Changes vs v1.2:                                                 |
//|  - Probe lot AUTO-COMPUTED from equity so a full 10-leg ladder   |
//|    consumes exactly MaxDDPct of equity at the worst price.       |
//|    Closed-form: base = floor((eq*MaxDDPct/100) / (WC*pv), step). |
//|    WC = Σ m(n)*adv_pips(n), computed at OnInit from inputs.      |
//|  - ProbeLot input is now an OPTIONAL OVERRIDE (>0 to force).     |
//|  - Default account profile is CENT / micro (e.g. AUDCAD.c).      |
//|  - New struct field BasketState.base_lot caches the computed     |
//|    base at probe-open time; grid adds use the cached value.      |
//|  - MathFloor (not MathRound) used for auto-sized base — rounding |
//|    up one vol_step could breach the 20% DD cap.                  |
//|  - CSV log: two trailing columns added (base_lot, account_type). |
//+------------------------------------------------------------------+
#property copyright "AUDCAD FOR THE WIN Project"
#property version   "1.30"
#property strict

// === SECTION 1: INPUTS ===

input string          TradeSymbol      = "";           // Trade symbol — blank = use chart symbol
input long            MagicLong        = 50000051;    // Magic number: long basket
input long            MagicShort       = 50000052;    // Magic number: short basket
input ENUM_TIMEFRAMES SignalTF         = PERIOD_M15;  // Entry/signal timeframe

// §1 Indicator periods
input int             RSI_Period       = 14;
input int             BB_Period        = 20;
input double          BB_StdDev        = 2.0;
input int             SRSI_K_Period    = 14;          // StochRSI stoch lookback
input int             SRSI_K_Smooth    = 3;           // StochRSI %K smoothing
input int             SwingLookback    = 500;         // Bars for rolling swing high
input double          SwingNearPips    = 50.0;        // SELL: fire if within this many pips of swing high

// §1 BUY thresholds
input double          Buy_RSI_Dir      = 50.0;        // RSI must be below this
input double          Buy_RSI_Deep     = 40.0;        // OR RSI <= this
input double          Buy_Stoch        = 20.0;        // OR StochRSI %K <= this
input double          Buy_PctB         = 0.10;        // OR BB %B <= this

// §1 SELL thresholds
input double          Sell_RSI_Dir     = 50.0;        // RSI must be above this
input double          Sell_RSI_Deep    = 60.0;        // OR RSI >= this
input double          Sell_Stoch       = 60.0;        // OR StochRSI %K >= this
input double          Sell_PctB        = 0.90;        // OR BB %B >= this

// §2 Exit — v1.2
input double          BasketTPPips     = 10.0;        // Close basket when net pips >= this (weighted avg)

// §3 Grid
input double          GridStepPips     = 22.0;        // Adverse pips to trigger next add
input int             MaxLegs          = 10;          // Hard leg cap per basket

// §4 Lot sizing — v1.3
input double          ProbeLot         = 0.0;         // Manual override: >0 forces fixed probe; 0 = auto-compute from equity (default)
input bool            RequireCentAccount = false;     // true = INIT_FAILED if SYMBOL_TRADE_CONTRACT_SIZE looks like a standard symbol (>10000)

// Risk (plans/1 §9)
input double          MaxDDPct         = 20.0;        // Equity DD hard cap %
input double          FitPadPips       = 5.0;         // Pre-trade fit safety pad pips

// v1.1 Gate (strategy/AUDCAD_M15_v1.1.md §1)
input bool            EnableGate       = true;        // false = no HTF gate
input ENUM_TIMEFRAMES GateTF           = PERIOD_D1;
input int             GateEMA          = 20;

// Operational
input bool            ShadowMode       = true;        // Suppress OrderSend; log only
input string          LogFile          = "audcad_v1_3.csv";
input int             Verbosity        = 2;           // 0=err 1=events 2=+detail per bar

// === SECTION 2: STRUCTS & GLOBALS ===

struct BasketState
{
    bool     active;
    bool     is_long;
    int      legs;
    double   wavg;          // weighted-average entry price
    double   total_lots;
    double   last_price;    // price of most recently opened leg
    datetime open_time;     // probe open time
    long     magic;
    bool     exhausted;     // ladder blocked by DD cap
    double   base_lot;      // v1.3: cached base lot for this basket's ladder
};

BasketState g_long, g_short;

int  h_rsi  = INVALID_HANDLE;
int  h_bb   = INVALID_HANDLE;
int  h_gate = INVALID_HANDLE;

datetime g_last_bar  = 0;
datetime g_last_d1   = 0;
bool     g_gate_long  = false;
bool     g_gate_short = false;

double g_pip;           // 1 pip in price units (0.0001 for 5-digit AUDCAD)
double g_tick_val;      // account-currency value of 1 tick per 1.0 lot
double g_tick_size;     // tick size in price
double g_vol_min;
double g_vol_max;
double g_vol_step;

// v1.3 additions:
double g_wc_lotpips     = 0.0;   // worst-case lot-pips per unit base lot (computed at init)
double g_contract_size  = 0.0;   // SYMBOL_TRADE_CONTRACT_SIZE
string g_account_type_tag = "?"; // "cent" | "standard" — heuristic from contract size

int    g_log = INVALID_HANDLE;
string g_sym = "";   // resolved symbol name

// === SECTION 3: UTILITIES ===

double NormLot(double raw)
{
    double n = MathRound(raw / g_vol_step) * g_vol_step;
    n = MathMax(n, g_vol_min);
    n = MathMin(n, g_vol_max);
    return NormalizeDouble(n, 2);
}

// v1.3: equity-scaled base lot. Returns 0 if even vol_min cannot fit under the cap.
// FLOOR (not round) — rounding up one vol_step could breach the 20% DD cap.
double ComputeBaseLot()
{
    double eq = AccountInfoDouble(ACCOUNT_EQUITY);
    double pv = PipValPerLot();
    if(eq <= 0.0 || pv <= 0.0 || g_wc_lotpips <= 0.0) return 0.0;

    double budget = eq * (MaxDDPct / 100.0);
    double raw    = budget / (g_wc_lotpips * pv);

    double snapped = MathFloor(raw / g_vol_step) * g_vol_step;
    if(snapped < g_vol_min) return 0.0;
    if(snapped > g_vol_max) snapped = g_vol_max;
    return NormalizeDouble(snapped, 2);
}

// Lot for leg N (1-based) given a base lot. Leg 1 = probe = base. Leg N>=2: 12*N * base.
// Strategy v1 §4 ladder: 1x / 24x / 36x / 48x / 60x / ... (locked multipliers)
double LegLot(int n, double base)
{
    double raw = (n == 1) ? base : base * 12.0 * n;
    return NormLot(raw);
}

// v1.3: locate the smallest-volume open leg for a given magic — that IS the probe (leg 1)
// and therefore the cached base lot. Used on EA restart to recover state.
double FindMinLegVolume(long magic)
{
    double minv = -1.0;
    for(int i = 0; i < PositionsTotal(); i++)
    {
        ulong t = PositionGetTicket(i);
        if(!PositionSelectByTicket(t)) continue;
        if(PositionGetString(POSITION_SYMBOL) != g_sym) continue;
        if(PositionGetInteger(POSITION_MAGIC) != magic) continue;
        double v = PositionGetDouble(POSITION_VOLUME);
        if(minv < 0.0 || v < minv) minv = v;
    }
    return (minv < 0.0) ? 0.0 : minv;
}

// Smoothed StochRSI %K from RSI buffer (AsSeries=true, [0]=shift 1).
double StochK(double &buf[], int k_period, int k_smooth)
{
    double sum = 0;
    for(int s = 0; s < k_smooth; s++)
    {
        double lo = buf[s], hi = buf[s];
        for(int w = s; w < s + k_period; w++)
        {
            if(buf[w] < lo) lo = buf[w];
            if(buf[w] > hi) hi = buf[w];
        }
        double range = hi - lo;
        sum += (range > 0.0) ? ((buf[s] - lo) / range * 100.0) : 50.0;
    }
    return sum / k_smooth;
}

double PipValPerLot() { return (g_pip / g_tick_size) * g_tick_val; }

ENUM_ORDER_TYPE_FILLING SymbolFilling()
{
    int modes = (int)SymbolInfoInteger(g_sym, SYMBOL_FILLING_MODE);
    if((modes & SYMBOL_FILLING_FOK) != 0) return ORDER_FILLING_FOK;
    if((modes & SYMBOL_FILLING_IOC) != 0) return ORDER_FILLING_IOC;
    return ORDER_FILLING_RETURN;
}

// === SECTION 4: BASKET P/L ===

double RealPL(const BasketState &bsk)
{
    if(!bsk.active) return 0;
    double total = 0;
    for(int i = 0; i < PositionsTotal(); i++)
    {
        ulong t = PositionGetTicket(i);
        if(!PositionSelectByTicket(t)) continue;
        if(PositionGetString(POSITION_SYMBOL) != g_sym) continue;
        if(PositionGetInteger(POSITION_MAGIC) != bsk.magic) continue;
        total += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
    }
    return total;
}

double VirtPL(const BasketState &bsk)
{
    if(!bsk.active) return 0;
    double cur = bsk.is_long
        ? SymbolInfoDouble(g_sym, SYMBOL_BID)
        : SymbolInfoDouble(g_sym, SYMBOL_ASK);
    double pips = bsk.is_long
        ? (cur - bsk.wavg) / g_pip
        : (bsk.wavg - cur) / g_pip;
    return pips * bsk.total_lots * PipValPerLot();
}

double BasketPL(const BasketState &bsk)
{
    return ShadowMode ? VirtPL(bsk) : RealPL(bsk);
}

double BasketSwap(const BasketState &bsk)
{
    if(!bsk.active || ShadowMode) return 0;
    double total = 0;
    for(int i = 0; i < PositionsTotal(); i++)
    {
        ulong t = PositionGetTicket(i);
        if(!PositionSelectByTicket(t)) continue;
        if(PositionGetString(POSITION_SYMBOL) != g_sym) continue;
        if(PositionGetInteger(POSITION_MAGIC) != bsk.magic) continue;
        total += PositionGetDouble(POSITION_SWAP);
    }
    return total;
}

// Net pips from wavg to current price (positive = in profit direction).
double BasketNetPips(const BasketState &bsk)
{
    if(!bsk.active) return 0;
    double cur = bsk.is_long
        ? SymbolInfoDouble(g_sym, SYMBOL_BID)
        : SymbolInfoDouble(g_sym, SYMBOL_ASK);
    return bsk.is_long
        ? (cur - bsk.wavg) / g_pip
        : (bsk.wavg - cur) / g_pip;
}

// === SECTION 5: LOGGER ===

// v1.3 CSV format: same 14 columns as v1.2 + two trailing fields: base_lot, account_type_tag.
// base_lot is sourced from the active basket matching `dir` (0 if none/SKIP/SIGNAL).
void WriteLog(string evt, string dir, double price, double lots,
              double eq, double eq_pct, double wavg, int leg,
              double swap, string note = "")
{
    if(g_log == INVALID_HANDLE) return;

    double bsk_base = 0.0;
    if(dir == "LONG"  && g_long.active)  bsk_base = g_long.base_lot;
    if(dir == "SHORT" && g_short.active) bsk_base = g_short.base_lot;

    string line = StringFormat("%s,%s,%s,%.5f,%.2f,%.2f,%.4f,%.5f,%d,%.2f,%s,%s,%s,%s,%.2f,%s",
        TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES|TIME_SECONDS),
        evt, dir, price, lots, eq, eq_pct, wavg, leg, swap,
        g_gate_long  ? "true":"false",
        g_gate_short ? "true":"false",
        ShadowMode   ? "true":"false",
        note,
        bsk_base,
        g_account_type_tag);
    FileWriteString(g_log, line + "\n");
    if(Verbosity >= 1 || evt == "ERROR")
        Print(evt, " | ", dir, " | p=", DoubleToString(price,5),
              " | lot=", DoubleToString(lots,2), " | ", note);
}

// === SECTION 6: BASKET INIT & RECONSTRUCTION ===

void InitBsk(BasketState &bsk, bool is_long)
{
    bsk.active     = false;
    bsk.is_long    = is_long;
    bsk.legs       = 0;
    bsk.wavg       = 0;
    bsk.total_lots = 0;
    bsk.last_price = 0;
    bsk.open_time  = 0;
    bsk.magic      = is_long ? MagicLong : MagicShort;
    bsk.exhausted  = false;
    bsk.base_lot   = 0.0;
}

void AccumulateLeg(BasketState &bsk, double lot, double open, datetime ot)
{
    bsk.wavg = (bsk.total_lots + lot > 0)
        ? (bsk.wavg * bsk.total_lots + open * lot) / (bsk.total_lots + lot)
        : open;
    bsk.total_lots += lot;
    bsk.legs++;
    bsk.active = true;
    if(bsk.open_time == 0 || ot < bsk.open_time) bsk.open_time  = ot;
    if(ot >= bsk.open_time)                       bsk.last_price = open;
}

void FixLastPrice(BasketState &bsk)
{
    if(!bsk.active) return;
    datetime latest = 0; double lp = 0;
    for(int i = 0; i < PositionsTotal(); i++)
    {
        ulong t = PositionGetTicket(i);
        if(!PositionSelectByTicket(t)) continue;
        if(PositionGetString(POSITION_SYMBOL) != g_sym) continue;
        if(PositionGetInteger(POSITION_MAGIC) != bsk.magic) continue;
        datetime ot = (datetime)PositionGetInteger(POSITION_TIME);
        if(ot > latest) { latest = ot; lp = PositionGetDouble(POSITION_PRICE_OPEN); }
    }
    if(lp > 0) bsk.last_price = lp;
}

void ReconstructBaskets()
{
    InitBsk(g_long,  true);
    InitBsk(g_short, false);

    for(int i = 0; i < PositionsTotal(); i++)
    {
        ulong ticket = PositionGetTicket(i);
        if(!PositionSelectByTicket(ticket)) continue;
        if(PositionGetString(POSITION_SYMBOL) != g_sym) continue;

        long   magic   = PositionGetInteger(POSITION_MAGIC);
        if(magic != MagicLong && magic != MagicShort) continue;

        double lot   = PositionGetDouble(POSITION_VOLUME);
        double open  = PositionGetDouble(POSITION_PRICE_OPEN);
        datetime ot  = (datetime)PositionGetInteger(POSITION_TIME);

        if(magic == MagicLong) AccumulateLeg(g_long,  lot, open, ot);
        else                   AccumulateLeg(g_short, lot, open, ot);
    }

    FixLastPrice(g_long);
    FixLastPrice(g_short);

    // v1.3: re-derive cached base lot from the smallest open leg (= probe).
    if(g_long.active)  g_long.base_lot  = FindMinLegVolume(g_long.magic);
    if(g_short.active) g_short.base_lot = FindMinLegVolume(g_short.magic);

    if(g_long.active)
        Print("Reconstructed LONG: legs=", g_long.legs,
              " wavg=", DoubleToString(g_long.wavg,5),
              " last=", DoubleToString(g_long.last_price,5),
              " base=", DoubleToString(g_long.base_lot,2));
    if(g_short.active)
        Print("Reconstructed SHORT: legs=", g_short.legs,
              " wavg=", DoubleToString(g_short.wavg,5),
              " last=", DoubleToString(g_short.last_price,5),
              " base=", DoubleToString(g_short.base_lot,2));

    // v1.2 guard: both baskets should not be active simultaneously
    if(g_long.active && g_short.active)
        Print("WARNING: both LONG and SHORT baskets reconstructed — v1.2/v1.3 is single-basket only. "
              "Close one manually before signals resume.");
}

// === SECTION 7: GATE EVALUATOR (v1.1 §1) ===

void RefreshGate()
{
    datetime d1_now = iTime(g_sym, GateTF, 0);
    if(d1_now == g_last_d1 && g_last_d1 != 0) return;
    g_last_d1 = d1_now;

    if(!EnableGate) { g_gate_long = g_gate_short = true; return; }

    if(Bars(g_sym, GateTF) < GateEMA + 1)
    {
        Print("Gate: insufficient D1 history. Both sides blocked.");
        g_gate_long = g_gate_short = false;
        return;
    }

    double ema_buf[];
    ArraySetAsSeries(ema_buf, true);
    if(CopyBuffer(h_gate, 0, 1, 1, ema_buf) < 1)
    {
        Print("Gate: CopyBuffer failed. Both sides blocked.");
        g_gate_long = g_gate_short = false;
        return;
    }

    double d1_close = iClose(g_sym, GateTF, 1);
    g_gate_long  = (d1_close > ema_buf[0]);
    g_gate_short = (d1_close < ema_buf[0]);

    if(Verbosity >= 2)
        Print("[GATE] D1_close=", DoubleToString(d1_close,5),
              " EMA", GateEMA, "=", DoubleToString(ema_buf[0],5),
              " gate_long=", g_gate_long, " gate_short=", g_gate_short);
}

// === SECTION 8: SIGNAL EVALUATOR (strategy v1 §1) ===

bool EvalSignal(bool &buy_f, bool &sell_f)
{
    buy_f = sell_f = false;

    int rsi_need = SRSI_K_Period + SRSI_K_Smooth;
    double rsi_buf[];
    ArraySetAsSeries(rsi_buf, true);
    if(CopyBuffer(h_rsi, 0, 1, rsi_need, rsi_buf) < rsi_need) return false;

    double bb_up[], bb_lo[];
    ArraySetAsSeries(bb_up, true);
    ArraySetAsSeries(bb_lo, true);
    if(CopyBuffer(h_bb, 1, 1, 1, bb_up) < 1) return false;
    if(CopyBuffer(h_bb, 2, 1, 1, bb_lo) < 1) return false;

    double close  = iClose(g_sym, SignalTF, 1);
    double rsi14  = rsi_buf[0];
    double pctb   = (bb_up[0] - bb_lo[0] > 1e-10)
                    ? (close - bb_lo[0]) / (bb_up[0] - bb_lo[0])
                    : 0.5;
    double stoch_k = StochK(rsi_buf, SRSI_K_Period, SRSI_K_Smooth);

    double hi_arr[];
    ArraySetAsSeries(hi_arr, true);
    double dist_swing = 9999.0;
    if(CopyHigh(g_sym, SignalTF, 1, SwingLookback, hi_arr) == SwingLookback)
    {
        int idx = ArrayMaximum(hi_arr, 0, WHOLE_ARRAY);
        dist_swing = (hi_arr[idx] - close) / g_pip;
    }

    if(rsi14 < Buy_RSI_Dir)
        buy_f = (stoch_k <= Buy_Stoch || pctb <= Buy_PctB || rsi14 <= Buy_RSI_Deep);

    if(rsi14 > Sell_RSI_Dir)
        sell_f = (stoch_k >= Sell_Stoch || pctb >= Sell_PctB ||
                  rsi14 >= Sell_RSI_Deep || dist_swing <= SwingNearPips);

    return true;
}

// === SECTION 9: PRE-TRADE FIT CHECK (plans/1 §9) ===
// v1.3: takes the chosen base lot as a parameter. Defense-in-depth — by construction
// ComputeBaseLot() already targets the cap, so this should always pass when the auto
// sizing is engaged. If it fails post-auto-sizing it indicates a unit mismatch.

bool FitCheck(bool is_long, double entry_price, double base)
{
    double eq = AccountInfoDouble(ACCOUNT_EQUITY);
    if(eq <= 0) return false;

    double pv = PipValPerLot();

    double worst = is_long
        ? entry_price - (MaxLegs - 1) * GridStepPips * g_pip - FitPadPips * g_pip
        : entry_price + (MaxLegs - 1) * GridStepPips * g_pip + FitPadPips * g_pip;

    double total_loss = 0;
    for(int n = 1; n <= MaxLegs; n++)
    {
        double leg_price = is_long
            ? entry_price - (n-1) * GridStepPips * g_pip
            : entry_price + (n-1) * GridStepPips * g_pip;
        double adv_pips = is_long
            ? (leg_price - worst) / g_pip
            : (worst - leg_price) / g_pip;
        total_loss += LegLot(n, base) * adv_pips * pv;
    }

    if(total_loss / eq > MaxDDPct / 100.0)
    {
        Print("FitCheck FAIL: projected loss=", DoubleToString(total_loss,2),
              " (", DoubleToString(total_loss/eq*100,1), "% of equity ", DoubleToString(eq,2),
              ") base=", DoubleToString(base,2));
        return false;
    }
    return true;
}

// === SECTION 10: BASKET CLOSE ===

void CloseBasket(BasketState &bsk, string reason)
{
    if(!bsk.active) return;
    string dir = bsk.is_long ? "LONG" : "SHORT";
    double eq  = AccountInfoDouble(ACCOUNT_EQUITY);
    double pl  = BasketPL(bsk);
    double sw  = BasketSwap(bsk);

    if(!ShadowMode)
    {
        for(int i = PositionsTotal()-1; i >= 0; i--)
        {
            ulong t = PositionGetTicket(i);
            if(!PositionSelectByTicket(t)) continue;
            if(PositionGetString(POSITION_SYMBOL) != g_sym) continue;
            if(PositionGetInteger(POSITION_MAGIC) != bsk.magic) continue;

            bool pos_buy = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY);
            MqlTradeRequest req = {};
            MqlTradeResult  res = {};
            req.action        = TRADE_ACTION_DEAL;
            req.symbol        = g_sym;
            req.volume        = PositionGetDouble(POSITION_VOLUME);
            req.type          = pos_buy ? ORDER_TYPE_SELL : ORDER_TYPE_BUY;
            req.type_filling  = SymbolFilling();
            req.price         = pos_buy
                ? SymbolInfoDouble(g_sym, SYMBOL_BID)
                : SymbolInfoDouble(g_sym, SYMBOL_ASK);
            req.deviation = 20;
            req.magic     = bsk.magic;
            req.position  = t;
            req.comment   = "audcad_v1.3_close";
            if(!OrderSend(req, res))
                Print("CloseBasket err: ", GetLastError(), " ticket=", t);
        }
    }

    double close_px = bsk.is_long
        ? SymbolInfoDouble(g_sym, SYMBOL_BID)
        : SymbolInfoDouble(g_sym, SYMBOL_ASK);

    double net_pips = BasketNetPips(bsk);
    WriteLog(ShadowMode ? "CLOSE_SHADOW" : "CLOSE_BASKET",
             dir, close_px, bsk.total_lots, eq,
             (eq > 0 ? pl/eq*100.0 : 0), bsk.wavg, bsk.legs, sw,
             "reason=" + reason +
             " net_pips=" + DoubleToString(net_pips, 1));

    InitBsk(bsk, bsk.is_long);
}

// === SECTION 11: PROBE OPEN ===

bool OpenProbe(bool is_long)
{
    double px = is_long
        ? SymbolInfoDouble(g_sym, SYMBOL_ASK)
        : SymbolInfoDouble(g_sym, SYMBOL_BID);

    double eq = AccountInfoDouble(ACCOUNT_EQUITY);

    // v1.3: resolve base lot — manual override or auto-compute from equity.
    double base = (ProbeLot > 0.0) ? ProbeLot : ComputeBaseLot();
    if(base <= 0.0)
    {
        WriteLog("SKIP_PROBE", is_long?"LONG":"SHORT", px, 0, eq, 0, 0, 0, 0,
                 "base_below_vol_min eq=" + DoubleToString(eq,2));
        return false;
    }

    if(!FitCheck(is_long, px, base))
    {
        WriteLog("SKIP_PROBE", is_long?"LONG":"SHORT", px, 0, eq, 0, 0, 0, 0,
                 (ProbeLot > 0.0) ? "fit_check_fail_override" : "fit_check_fail_after_autosize");
        return false;
    }

    double lot = LegLot(1, base);

    if(!ShadowMode)
    {
        MqlTradeRequest req = {};
        MqlTradeResult  res = {};
        req.action       = TRADE_ACTION_DEAL;
        req.symbol       = g_sym;
        req.volume       = lot;
        req.type         = is_long ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
        req.type_filling = SymbolFilling();
        req.price        = px;
        req.deviation    = 20;
        req.magic        = is_long ? MagicLong : MagicShort;
        req.comment      = "audcad_v1.3_probe";
        if(!OrderSend(req, res))
        {
            Print("OpenProbe err: ", GetLastError());
            return false;
        }
    }

    if(is_long)
    {
        g_long.active     = true;
        g_long.legs       = 1;
        g_long.wavg       = px;
        g_long.total_lots = lot;
        g_long.last_price = px;
        g_long.open_time  = TimeCurrent();
        g_long.exhausted  = false;
        g_long.base_lot   = base;
    }
    else
    {
        g_short.active     = true;
        g_short.legs       = 1;
        g_short.wavg       = px;
        g_short.total_lots = lot;
        g_short.last_price = px;
        g_short.open_time  = TimeCurrent();
        g_short.exhausted  = false;
        g_short.base_lot   = base;
    }

    double wc_pct = (eq > 0.0)
        ? base * g_wc_lotpips * PipValPerLot() / eq * 100.0
        : 0.0;

    WriteLog(ShadowMode ? "PROBE_SHADOW" : "PROBE_OPEN",
             is_long?"LONG":"SHORT", px, lot, eq, 0, px, 1, 0,
             "gate_l=" + (g_gate_long?"1":"0") +
             " gate_s=" + (g_gate_short?"1":"0") +
             " base=" + DoubleToString(base,2) +
             " wc_pct=" + DoubleToString(wc_pct,2));
    return true;
}

// === SECTION 12: GRID ADD (strategy v1 §3) ===

void CheckAdd(BasketState &bsk)
{
    if(!bsk.active || bsk.exhausted || bsk.legs >= MaxLegs) return;

    double close = iClose(g_sym, SignalTF, 1);
    bool triggered = bsk.is_long
        ? (close <= bsk.last_price - GridStepPips * g_pip)
        : (close >= bsk.last_price + GridStepPips * g_pip);
    if(!triggered) return;

    int    next_n = bsk.legs + 1;
    double lot    = LegLot(next_n, bsk.base_lot);   // v1.3: use cached base
    double eq     = AccountInfoDouble(ACCOUNT_EQUITY);
    double cur_pl = BasketPL(bsk);
    double pv     = PipValPerLot();

    double proj_extra = (bsk.total_lots + lot) * GridStepPips * pv;
    double proj_loss  = -cur_pl + proj_extra;
    if(proj_loss / eq > MaxDDPct / 100.0)
    {
        bsk.exhausted = true;
        WriteLog("BLOCK_ADD", bsk.is_long?"LONG":"SHORT", close, lot, eq,
                 (eq>0 ? -cur_pl/eq*100.0 : 0), bsk.wavg, next_n, BasketSwap(bsk),
                 "dd_cap_fwd");
        return;
    }

    double add_px = bsk.is_long
        ? SymbolInfoDouble(g_sym, SYMBOL_ASK)
        : SymbolInfoDouble(g_sym, SYMBOL_BID);

    if(!ShadowMode)
    {
        MqlTradeRequest req = {};
        MqlTradeResult  res = {};
        req.action       = TRADE_ACTION_DEAL;
        req.symbol       = g_sym;
        req.volume       = lot;
        req.type         = bsk.is_long ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
        req.type_filling = SymbolFilling();
        req.price        = add_px;
        req.deviation    = 20;
        req.magic        = bsk.magic;
        req.comment      = "audcad_v1.3_add";
        if(!OrderSend(req, res))
        {
            Print("CheckAdd err: ", GetLastError());
            return;
        }
    }

    bsk.wavg       = (bsk.wavg * bsk.total_lots + add_px * lot)
                     / (bsk.total_lots + lot);
    bsk.total_lots += lot;
    bsk.last_price  = add_px;
    bsk.legs        = next_n;

    WriteLog(ShadowMode ? "ADD_SHADOW" : "ADD",
             bsk.is_long?"LONG":"SHORT", add_px, lot, eq,
             (eq>0 ? cur_pl/eq*100.0 : 0), bsk.wavg, next_n, BasketSwap(bsk));
}

// === SECTION 13: PROFIT-TARGET CLOSE CHECK (strategy v1.2 §2) ===

// Returns true if the basket was closed.
bool CheckCloseTarget(BasketState &bsk)
{
    if(!bsk.active) return false;

    double close  = iClose(g_sym, SignalTF, 1);
    double target = BasketTPPips * g_pip;
    bool   hit    = bsk.is_long
        ? (close >= bsk.wavg + target)
        : (close <= bsk.wavg - target);

    if(!hit)
    {
        if(Verbosity >= 2)
        {
            double net = BasketNetPips(bsk);
            Print("[CLOSE_CHECK] ", bsk.is_long?"LONG":"SHORT",
                  " wavg=", DoubleToString(bsk.wavg,5),
                  " close=", DoubleToString(close,5),
                  " net_pips=", DoubleToString(net,1),
                  " target=", DoubleToString(BasketTPPips,1));
        }
        return false;
    }

    CloseBasket(bsk, StringFormat("tp_%.1f_pips", BasketTPPips));
    return true;
}

// === SECTION 14: DECISION TREE (strategy v1.2 §2) ===

void RunTree(bool buy_f, bool sell_f)
{
    // --- Case A: a basket is open — manage it, ignore signals ---
    if(g_long.active)
    {
        if(!CheckCloseTarget(g_long))   // not at target yet
            CheckAdd(g_long);           // check grid add
        return;
    }

    if(g_short.active)
    {
        if(!CheckCloseTarget(g_short))
            CheckAdd(g_short);
        return;
    }

    // --- Case B: no basket open — evaluate signal + gate ---
    if(buy_f)
    {
        if(g_gate_long)
            OpenProbe(true);
        else
        {
            double eq = AccountInfoDouble(ACCOUNT_EQUITY);
            WriteLog("GATE_BLOCK", "LONG",
                     iClose(g_sym,SignalTF,1), 0, eq, 0, 0, 0, 0,
                     "htf_veto_buy");
        }
        return;
    }

    if(sell_f)
    {
        if(g_gate_short)
            OpenProbe(false);
        else
        {
            double eq = AccountInfoDouble(ACCOUNT_EQUITY);
            WriteLog("GATE_BLOCK", "SHORT",
                     iClose(g_sym,SignalTF,1), 0, eq, 0, 0, 0, 0,
                     "htf_veto_sell");
        }
        return;
    }
}

// === SECTION 15: ON BAR CLOSE ===

void OnBarClose()
{
    RefreshGate();

    bool buy_f, sell_f;
    if(!EvalSignal(buy_f, sell_f))
    {
        if(Verbosity >= 1) Print("EvalSignal: not enough indicator data, skipping.");
        return;
    }

    if(Verbosity >= 2)
    {
        double eq  = AccountInfoDouble(ACCOUNT_EQUITY);
        string sig = buy_f ? "BUY" : (sell_f ? "SELL" : "none");
        WriteLog("SIGNAL", sig, iClose(g_sym,SignalTF,1),
                 0, eq, 0, 0, 0, 0,
                 "buy=" + (buy_f?"1":"0") +
                 " sell=" + (sell_f?"1":"0") +
                 " gl=" + (g_gate_long?"1":"0") +
                 " gs=" + (g_gate_short?"1":"0") +
                 " bsk=" + (g_long.active?"LONG":g_short.active?"SHORT":"none"));
    }

    RunTree(buy_f, sell_f);
}

// === SECTION 16: ONINIT ===

int OnInit()
{
    g_sym = (StringLen(TradeSymbol) == 0) ? _Symbol : TradeSymbol;

    if(AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
    {
        if(MQLInfoInteger(MQL_TESTER))
            Print("Warning: tester not in hedging mode — continuing for backtest");
        else
        {
            Alert("AUDCAD EA: requires hedging account. Aborting.");
            return INIT_FAILED;
        }
    }

    if(!SymbolSelect(g_sym, true))
    {
        Alert("AUDCAD EA: symbol not found: ", g_sym);
        return INIT_FAILED;
    }

    g_pip           = 10.0 * SymbolInfoDouble(g_sym, SYMBOL_POINT);
    g_tick_val      = SymbolInfoDouble(g_sym, SYMBOL_TRADE_TICK_VALUE);
    g_tick_size     = SymbolInfoDouble(g_sym, SYMBOL_TRADE_TICK_SIZE);
    g_vol_min       = SymbolInfoDouble(g_sym, SYMBOL_VOLUME_MIN);
    g_vol_max       = SymbolInfoDouble(g_sym, SYMBOL_VOLUME_MAX);
    g_vol_step      = SymbolInfoDouble(g_sym, SYMBOL_VOLUME_STEP);
    g_contract_size = SymbolInfoDouble(g_sym, SYMBOL_TRADE_CONTRACT_SIZE);

    // Cent-vs-standard heuristic — drives the log tag only; does NOT change math.
    g_account_type_tag = (g_contract_size > 0.0 && g_contract_size <= 10000.0)
                         ? "cent" : "standard";

    // v1.3: compute the worst-case lot-pips constant from the LIVE inputs so that
    // changes to MaxLegs / GridStepPips / FitPadPips / multipliers re-derive it.
    // Ladder shape: m(1) = 1; m(n>=2) = 12 * n. (Locked — edit with care.)
    g_wc_lotpips = 0.0;
    for(int n = 1; n <= MaxLegs; n++)
    {
        double m   = (n == 1) ? 1.0 : 12.0 * n;
        double adv = FitPadPips + GridStepPips * (MaxLegs - n);
        g_wc_lotpips += m * adv;
    }

    double pv = PipValPerLot();
    double eq = AccountInfoDouble(ACCOUNT_EQUITY);

    Print("[UNIT_SANITY] equity=", DoubleToString(eq,2),
          " contract_size=", DoubleToString(g_contract_size,2),
          " tick_val=", DoubleToString(g_tick_val,5),
          " tick_size=", DoubleToString(g_tick_size,8),
          " pv_per_lot=", DoubleToString(pv,5),
          " vol_min=", DoubleToString(g_vol_min,2),
          " vol_step=", DoubleToString(g_vol_step,2),
          " account_type_tag=", g_account_type_tag);

    Print("[WC_CONST] ladder_wc_lotpips=", DoubleToString(g_wc_lotpips,2),
          " (MaxLegs=", MaxLegs, " GridStepPips=", DoubleToString(GridStepPips,1),
          " FitPadPips=", DoubleToString(FitPadPips,1), ")");

    if(RequireCentAccount && g_contract_size > 10000.0)
    {
        Alert("AUDCAD v1.3: RequireCentAccount=true but contract_size=", g_contract_size,
              " looks like a standard symbol. Aborting.");
        return INIT_FAILED;
    }

    // v1.3: guard the legacy "ProbeLot < vol_min" check so it only fires
    // when the user actually set a manual override (>0).
    if(ProbeLot > 0.0 && ProbeLot < g_vol_min)
    {
        Alert("ProbeLot override (", ProbeLot, ") < vol_min (", g_vol_min, ")");
        return INIT_FAILED;
    }

    // Projected ladder at current equity — single source of truth for "will it run".
    double base_now = (ProbeLot > 0.0) ? ProbeLot : ComputeBaseLot();
    if(base_now <= 0.0)
    {
        if(ProbeLot <= 0.0)
            Alert("AUDCAD v1.3: equity (", DoubleToString(eq,2),
                  ") too small for a ", MaxLegs, "-leg ladder at ", MaxDDPct,
                  "% cap. EA will skip every probe until equity grows.");
    }
    else
    {
        string ladder = "";
        for(int n = 1; n <= MaxLegs; n++)
        {
            if(n > 1) ladder += ",";
            ladder += DoubleToString(LegLot(n, base_now), 2);
        }
        double wc_pct = base_now * g_wc_lotpips * pv / MathMax(eq, 1.0) * 100.0;
        Print("[AUTOSIZE] base=", DoubleToString(base_now,2),
              " ladder=[", ladder, "]",
              " wc_pct=", DoubleToString(wc_pct,2),
              " mode=", (ProbeLot > 0.0 ? "override" : "auto"));
    }

    h_rsi  = iRSI(g_sym, SignalTF, RSI_Period, PRICE_CLOSE);
    h_bb   = iBands(g_sym, SignalTF, BB_Period, 0, BB_StdDev, PRICE_CLOSE);
    h_gate = iMA(g_sym, GateTF, GateEMA, 0, MODE_EMA, PRICE_CLOSE);

    if(h_rsi == INVALID_HANDLE || h_bb == INVALID_HANDLE || h_gate == INVALID_HANDLE)
    {
        Alert("AUDCAD EA: indicator handle creation failed.");
        return INIT_FAILED;
    }

    ReconstructBaskets();

    g_log = FileOpen(LogFile, FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_SHARE_READ, ',');
    if(g_log == INVALID_HANDLE)
        Print("WARNING: cannot open log file ", LogFile);
    else
    {
        FileWriteString(g_log,
            "# account_type=" + g_account_type_tag +
            ",symbol=" + g_sym +
            ",contract_size=" + DoubleToString(g_contract_size,2) +
            ",ea_version=v1.3\n");
        FileWriteString(g_log,
            "utc_time,event,direction,price,lots_std,equity,equity_pct,"
            "basket_wavg,leg_index,swap_acc,gate_long,gate_short,shadow_mode,note,"
            "base_lot,account_type_tag\n");
    }

    if(ShadowMode)
        Print("*** SHADOW MODE ON — OrderSend suppressed, signals logged only ***");

    Print("v1.3: equity-scaled base lot, cent-account default. ProbeLot=",
          DoubleToString(ProbeLot,2),
          " (", (ProbeLot > 0.0 ? "manual override" : "auto-compute"), ").",
          " Exit: basket +/- ", BasketTPPips, " pips. Single basket at a time.");

    return INIT_SUCCEEDED;
}

// === SECTION 17: ONDEINIT ===

void OnDeinit(const int reason)
{
    if(g_log != INVALID_HANDLE) { FileClose(g_log); g_log = INVALID_HANDLE; }
}

// === SECTION 18: ONTICK ===

void OnTick()
{
    // Emergency DD check on every tick (plans/1 §9)
    double eq = AccountInfoDouble(ACCOUNT_EQUITY);
    if(eq > 0)
    {
        if(g_long.active)
        {
            double pl = BasketPL(g_long);
            if(pl < 0 && (-pl / eq) >= MaxDDPct / 100.0)
            {
                Print("EMERGENCY EXIT: LONG DD=", DoubleToString(-pl/eq*100,1), "%");
                CloseBasket(g_long, "emergency_dd");
            }
        }
        if(g_short.active)
        {
            double pl = BasketPL(g_short);
            if(pl < 0 && (-pl / eq) >= MaxDDPct / 100.0)
            {
                Print("EMERGENCY EXIT: SHORT DD=", DoubleToString(-pl/eq*100,1), "%");
                CloseBasket(g_short, "emergency_dd");
            }
        }
    }

    // Bar-close logic (once per new M15 bar)
    datetime bar_now = iTime(g_sym, SignalTF, 0);
    if(bar_now == g_last_bar) return;
    g_last_bar = bar_now;

    OnBarClose();
}

//+------------------------------------------------------------------+
//|                                         AUDCAD_M15_v1_4.mq5     |
//|                     AUDCAD Mean-Reversion EA — v1.4              |
//|                                                                  |
//| Signal:  strategy/AUDCAD_M15_v1.md   §1-5                       |
//| Gate:    strategy/AUDCAD_M15_v1.1.md §1-3 (D1 EMA20)            |
//| Exit:    strategy/AUDCAD_M15_v1.2.md §2  (+10 pip net target)   |
//| Sizing:  strategy/AUDCAD_M15_v1.3.md §2  (equity-scaled base)   |
//| Renames: strategy/AUDCAD_M15_v1.4.md     (ergonomics release)   |
//| Risk:    plans/1.initial requirements.md §9,10                  |
//|                                                                  |
//| Changes vs v1.3 (ERGONOMICS + SAFER DEFAULTS — no mechanics):    |
//|  - ~30 inputs renamed to descriptive snake_case.                 |
//|  - Inline comments reformatted to `VariableName: description`    |
//|    so MT5 tester panel displays both code name and description.  |
//|  - ProbeLot split into TWO inputs:                               |
//|      Auto_Compute_Lot_Size_Based_On_Equity (bool, default true)  |
//|      Default_Base_Lot_Size               (double, default 0.10)  |
//|  - Abort_If_Standard_Account default FLIPPED to true             |
//|    (was RequireCentAccount=false). Refuses standard symbols      |
//|    unless explicitly overridden — safer for $1k cent target.     |
//|  - Max_Drawdown_Percentage default raised 20 -> 35 (PROVISIONAL).|
//|    Admits vol_min=0.10 cent probes at $1k equity per v4 backtest.|
//|    Subject to revision after more empirical runs.                |
//|  - Log file default audcad_v1_3.csv -> audcad_v1_4.csv.          |
//|  - CSV header carries ea_version=v1.4 (column layout unchanged). |
//|                                                                  |
//| Strategy mechanics (signal, gate, grid, exit, lot formula,       |
//| FitCheck, emergency exit, basket reconstruction) are bit-for-bit |
//| identical to v1.3.                                               |
//+------------------------------------------------------------------+
#property copyright "AUDCAD FOR THE WIN Project"
#property version   "1.40"
#property strict

// === SECTION 1: INPUTS ===

input string          Forex_Pair               = "";           // Forex_Pair: blank = use chart symbol
input long            Long_Basket_Group_Tag    = 50000051;     // Long_Basket_Group_Tag: magic # for long basket positions
input long            Short_Basket_Group_Tag   = 50000052;     // Short_Basket_Group_Tag: magic # for short basket positions
input ENUM_TIMEFRAMES Signal_Timeframe         = PERIOD_M15;   // Signal_Timeframe: bar timeframe for signal evaluation

// §1 Indicator periods
input int             RSI_Period               = 14;           // RSI_Period: RSI lookback bars
input int             Bollinger_Period         = 20;           // Bollinger_Period: Bollinger Bands MA period
input double          Bollinger_StdDev         = 2.0;          // Bollinger_StdDev: Bollinger Bands standard deviations
input int             Stoch_RSI_Lookback       = 14;           // Stoch_RSI_Lookback: StochRSI stochastic lookback bars
input int             Stoch_RSI_Smooth         = 3;            // Stoch_RSI_Smooth: StochRSI %K smoothing
input int             Swing_High_Bars          = 500;          // Swing_High_Bars: bars for rolling swing-high lookup
input double          Swing_High_DistPips      = 50.0;         // Swing_High_DistPips: SELL fires if within this many pips of swing high
input int             Swing_Low_Bars           = 500;          // Swing_Low_Bars: bars for rolling swing-low lookup
input double          Swing_Low_DistPips       = 50.0;         // Swing_Low_DistPips: BUY fires if within this many pips of swing low

// §1 BUY thresholds
input double          Buy_Only_If_RSI_LessThan                = 50.0;  // Buy_Only_If_RSI_LessThan: BUY direction gate (RSI must be below this)
input double          Buy_Fire_If_RSI_LessThan_EqualTo        = 40.0;  // Buy_Fire_If_RSI_LessThan_EqualTo: oversold RSI trigger
input double          Buy_Fire_If_StochRSI_K_LessThan_EqualTo = 20.0;  // Buy_Fire_If_StochRSI_K_LessThan_EqualTo: oversold StochRSI trigger
input double          Buy_Fire_If_Bollinger_LessThan_EqualTo  = 0.10;  // Buy_Fire_If_Bollinger_LessThan_EqualTo: oversold BB %B trigger

// §1 SELL thresholds
input double          Sell_Only_If_RSI_GreaterThan                = 50.0;  // Sell_Only_If_RSI_GreaterThan: SELL direction gate (RSI must be above this)
input double          Sell_Fire_If_RSI_GreaterThan_EqualTo        = 60.0;  // Sell_Fire_If_RSI_GreaterThan_EqualTo: overbought RSI trigger
input double          Sell_Fire_If_StochRSI_K_GreaterThan_EqualTo = 60.0;  // Sell_Fire_If_StochRSI_K_GreaterThan_EqualTo: overbought StochRSI trigger
input double          Sell_Fire_If_Bollinger_GreaterThan_EqualTo  = 0.90;  // Sell_Fire_If_Bollinger_GreaterThan_EqualTo: overbought BB %B trigger

// §2 Exit — v1.2
input double          TP_Basket_If_Total_Pips_GreaterThan_EqualTo = 10.0; // TP_Basket_If_Total_Pips_GreaterThan_EqualTo: close basket when net pips >= this (weighted avg)

// §3 Grid
input double          Grid_Step_Pips           = 22.0;         // Grid_Step_Pips: adverse pips to trigger next grid add
input int             Grid_Max_Level_To_SL     = 10;           // Grid_Max_Level_To_SL: hard leg cap per basket

// §4 Lot sizing — v1.4 (ProbeLot split)
input bool            Auto_Compute_Lot_Size_Based_On_Equity = true;  // Auto_Compute_Lot_Size_Based_On_Equity: true = derive base from equity & Max_Drawdown_Percentage; false = use Default_Base_Lot_Size below
input double          Default_Base_Lot_Size                 = 0.10;  // Default_Base_Lot_Size: probe lot when auto-compute is OFF (used only when Auto_Compute_Lot_Size_Based_On_Equity = false)
input bool            Abort_If_Standard_Account             = true;  // Abort_If_Standard_Account: true = INIT_FAILED if SYMBOL_TRADE_CONTRACT_SIZE looks like a standard symbol (>10000). Default ON: v1.4 is designed for cent.

// Risk (plans/1 §9)
input double          Max_Drawdown_Percentage  = 35.0;         // Max_Drawdown_Percentage: equity DD hard cap (%) — drives auto-sizer, FitCheck, emergency exit. Default 35 admits vol_min=0.10 cent probes at $1k equity. PROVISIONAL — to be revisited based on multi-year / multi-broker testing.
input double          Fit_Check_Pad_Pips       = 5.0;          // Fit_Check_Pad_Pips: safety pad pips on the worst-case ladder fit check

// v1.1 Gate (strategy/AUDCAD_M15_v1.1.md §1)
input bool            Enable_HTF_Gate          = true;         // Enable_HTF_Gate: false = no HTF trend filter; both directions always allowed
input ENUM_TIMEFRAMES GateTimeframe            = PERIOD_D1;    // GateTimeframe: HTF trend filter timeframe
input int             GateEMA_Period           = 20;           // GateEMA_Period: EMA period on GateTimeframe

// Operational
input bool            Shadow_Mode              = true;         // Shadow_Mode: true = suppress OrderSend, log signals only
input string          Log_File                 = "audcad_v1_4.csv"; // Log_File: CSV log filename
input int             Verbosity                = 2;            // Verbosity: 0=err, 1=events, 2=+detail per bar

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

// v1.4 diag: last-bar indicator readings cached for SIGNAL log line
double g_last_rsi           = 0.0;
double g_last_stoch         = 0.0;
double g_last_pctb          = 0.0;
double g_last_dist_swing    = 0.0;   // distance to swing HIGH (for SELL)
double g_last_dist_swing_lo = 0.0;   // distance to swing LOW  (for BUY)

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

    double budget = eq * (Max_Drawdown_Percentage / 100.0);
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
    return Shadow_Mode ? VirtPL(bsk) : RealPL(bsk);
}

double BasketSwap(const BasketState &bsk)
{
    if(!bsk.active || Shadow_Mode) return 0;
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

// v1.4 CSV format: same as v1.3 — 14 base columns + 2 trailing fields (base_lot, account_type_tag).
// Only the header line's ea_version changes (v1.3 -> v1.4).
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
        Shadow_Mode  ? "true":"false",
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
    bsk.magic      = is_long ? Long_Basket_Group_Tag : Short_Basket_Group_Tag;
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
        if(magic != Long_Basket_Group_Tag && magic != Short_Basket_Group_Tag) continue;

        double lot   = PositionGetDouble(POSITION_VOLUME);
        double open  = PositionGetDouble(POSITION_PRICE_OPEN);
        datetime ot  = (datetime)PositionGetInteger(POSITION_TIME);

        if(magic == Long_Basket_Group_Tag) AccumulateLeg(g_long,  lot, open, ot);
        else                                AccumulateLeg(g_short, lot, open, ot);
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
        Print("WARNING: both LONG and SHORT baskets reconstructed — v1.2/v1.3/v1.4 is single-basket only. "
              "Close one manually before signals resume.");
}

// === SECTION 7: GATE EVALUATOR (v1.1 §1) ===

void RefreshGate()
{
    datetime d1_now = iTime(g_sym, GateTimeframe, 0);
    if(d1_now == g_last_d1 && g_last_d1 != 0) return;
    g_last_d1 = d1_now;

    if(!Enable_HTF_Gate) { g_gate_long = g_gate_short = true; return; }

    if(Bars(g_sym, GateTimeframe) < GateEMA_Period + 1)
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

    double d1_close = iClose(g_sym, GateTimeframe, 1);
    g_gate_long  = (d1_close > ema_buf[0]);
    g_gate_short = (d1_close < ema_buf[0]);

    if(Verbosity >= 2)
        Print("[GATE] D1_close=", DoubleToString(d1_close,5),
              " EMA", GateEMA_Period, "=", DoubleToString(ema_buf[0],5),
              " gate_long=", g_gate_long, " gate_short=", g_gate_short);
}

// === SECTION 8: SIGNAL EVALUATOR (strategy v1 §1) ===

bool EvalSignal(bool &buy_f, bool &sell_f)
{
    buy_f = sell_f = false;

    int rsi_need = Stoch_RSI_Lookback + Stoch_RSI_Smooth;
    double rsi_buf[];
    ArraySetAsSeries(rsi_buf, true);
    if(CopyBuffer(h_rsi, 0, 1, rsi_need, rsi_buf) < rsi_need) return false;

    double bb_up[], bb_lo[];
    ArraySetAsSeries(bb_up, true);
    ArraySetAsSeries(bb_lo, true);
    if(CopyBuffer(h_bb, 1, 1, 1, bb_up) < 1) return false;
    if(CopyBuffer(h_bb, 2, 1, 1, bb_lo) < 1) return false;

    double close  = iClose(g_sym, Signal_Timeframe, 1);
    double rsi14  = rsi_buf[0];
    double pctb   = (bb_up[0] - bb_lo[0] > 1e-10)
                    ? (close - bb_lo[0]) / (bb_up[0] - bb_lo[0])
                    : 0.5;
    double stoch_k = StochK(rsi_buf, Stoch_RSI_Lookback, Stoch_RSI_Smooth);

    double hi_arr[];
    ArraySetAsSeries(hi_arr, true);
    double dist_swing = 9999.0;
    if(CopyHigh(g_sym, Signal_Timeframe, 1, Swing_High_Bars, hi_arr) == Swing_High_Bars)
    {
        int idx = ArrayMaximum(hi_arr, 0, WHOLE_ARRAY);
        dist_swing = (hi_arr[idx] - close) / g_pip;
    }

    double lo_arr[];
    ArraySetAsSeries(lo_arr, true);
    double dist_swing_low = 9999.0;
    if(CopyLow(g_sym, Signal_Timeframe, 1, Swing_Low_Bars, lo_arr) == Swing_Low_Bars)
    {
        int idx = ArrayMinimum(lo_arr, 0, WHOLE_ARRAY);
        dist_swing_low = (close - lo_arr[idx]) / g_pip;
    }

    g_last_rsi           = rsi14;
    g_last_stoch         = stoch_k;
    g_last_pctb          = pctb;
    g_last_dist_swing    = dist_swing;
    g_last_dist_swing_lo = dist_swing_low;

    if(rsi14 < Buy_Only_If_RSI_LessThan)
        buy_f = (stoch_k        <= Buy_Fire_If_StochRSI_K_LessThan_EqualTo ||
                 pctb           <= Buy_Fire_If_Bollinger_LessThan_EqualTo  ||
                 rsi14          <= Buy_Fire_If_RSI_LessThan_EqualTo        ||
                 dist_swing_low <= Swing_Low_DistPips);

    if(rsi14 > Sell_Only_If_RSI_GreaterThan)
        sell_f = (stoch_k    >= Sell_Fire_If_StochRSI_K_GreaterThan_EqualTo ||
                  pctb       >= Sell_Fire_If_Bollinger_GreaterThan_EqualTo  ||
                  rsi14      >= Sell_Fire_If_RSI_GreaterThan_EqualTo        ||
                  dist_swing <= Swing_High_DistPips);

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
        ? entry_price - (Grid_Max_Level_To_SL - 1) * Grid_Step_Pips * g_pip - Fit_Check_Pad_Pips * g_pip
        : entry_price + (Grid_Max_Level_To_SL - 1) * Grid_Step_Pips * g_pip + Fit_Check_Pad_Pips * g_pip;

    double total_loss = 0;
    for(int n = 1; n <= Grid_Max_Level_To_SL; n++)
    {
        double leg_price = is_long
            ? entry_price - (n-1) * Grid_Step_Pips * g_pip
            : entry_price + (n-1) * Grid_Step_Pips * g_pip;
        double adv_pips = is_long
            ? (leg_price - worst) / g_pip
            : (worst - leg_price) / g_pip;
        total_loss += LegLot(n, base) * adv_pips * pv;
    }

    if(total_loss / eq > Max_Drawdown_Percentage / 100.0)
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

    if(!Shadow_Mode)
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
            req.comment   = "audcad_v1.4_close";
            if(!OrderSend(req, res))
                Print("CloseBasket err: ", GetLastError(), " ticket=", t);
        }
    }

    double close_px = bsk.is_long
        ? SymbolInfoDouble(g_sym, SYMBOL_BID)
        : SymbolInfoDouble(g_sym, SYMBOL_ASK);

    double net_pips = BasketNetPips(bsk);
    WriteLog(Shadow_Mode ? "CLOSE_SHADOW" : "CLOSE_BASKET",
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

    // v1.4: resolve base lot — auto-compute or manual default.
    double base = Auto_Compute_Lot_Size_Based_On_Equity
                  ? ComputeBaseLot()
                  : Default_Base_Lot_Size;
    if(base <= 0.0)
    {
        WriteLog("SKIP_PROBE", is_long?"LONG":"SHORT", px, 0, eq, 0, 0, 0, 0,
                 "base_below_vol_min eq=" + DoubleToString(eq,2));
        return false;
    }

    if(!FitCheck(is_long, px, base))
    {
        WriteLog("SKIP_PROBE", is_long?"LONG":"SHORT", px, 0, eq, 0, 0, 0, 0,
                 Auto_Compute_Lot_Size_Based_On_Equity
                    ? "fit_check_fail_after_autosize"
                    : "fit_check_fail_override");
        return false;
    }

    double lot = LegLot(1, base);

    if(!Shadow_Mode)
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
        req.magic        = is_long ? Long_Basket_Group_Tag : Short_Basket_Group_Tag;
        req.comment      = "audcad_v1.4_probe";
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

    WriteLog(Shadow_Mode ? "PROBE_SHADOW" : "PROBE_OPEN",
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
    if(!bsk.active || bsk.exhausted || bsk.legs >= Grid_Max_Level_To_SL) return;

    double close = iClose(g_sym, Signal_Timeframe, 1);
    bool triggered = bsk.is_long
        ? (close <= bsk.last_price - Grid_Step_Pips * g_pip)
        : (close >= bsk.last_price + Grid_Step_Pips * g_pip);
    if(!triggered) return;

    int    next_n = bsk.legs + 1;
    double lot    = LegLot(next_n, bsk.base_lot);   // v1.3: use cached base
    double eq     = AccountInfoDouble(ACCOUNT_EQUITY);
    double cur_pl = BasketPL(bsk);
    double pv     = PipValPerLot();

    double proj_extra = (bsk.total_lots + lot) * Grid_Step_Pips * pv;
    double proj_loss  = -cur_pl + proj_extra;
    if(proj_loss / eq > Max_Drawdown_Percentage / 100.0)
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

    if(!Shadow_Mode)
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
        req.comment      = "audcad_v1.4_add";
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

    WriteLog(Shadow_Mode ? "ADD_SHADOW" : "ADD",
             bsk.is_long?"LONG":"SHORT", add_px, lot, eq,
             (eq>0 ? cur_pl/eq*100.0 : 0), bsk.wavg, next_n, BasketSwap(bsk));
}

// === SECTION 13: PROFIT-TARGET CLOSE CHECK (strategy v1.2 §2) ===

// Returns true if the basket was closed.
bool CheckCloseTarget(BasketState &bsk)
{
    if(!bsk.active) return false;

    double close  = iClose(g_sym, Signal_Timeframe, 1);
    double target = TP_Basket_If_Total_Pips_GreaterThan_EqualTo * g_pip;
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
                  " target=", DoubleToString(TP_Basket_If_Total_Pips_GreaterThan_EqualTo,1));
        }
        return false;
    }

    CloseBasket(bsk, StringFormat("tp_%.1f_pips", TP_Basket_If_Total_Pips_GreaterThan_EqualTo));
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
                     iClose(g_sym,Signal_Timeframe,1), 0, eq, 0, 0, 0, 0,
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
                     iClose(g_sym,Signal_Timeframe,1), 0, eq, 0, 0, 0, 0,
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
        string arm = StringFormat("rsi=%.1f stoch=%.1f pctb=%.2f swhi=%.0f swlo=%.0f",
                                  g_last_rsi, g_last_stoch, g_last_pctb,
                                  g_last_dist_swing, g_last_dist_swing_lo);
        WriteLog("SIGNAL", sig, iClose(g_sym,Signal_Timeframe,1),
                 0, eq, 0, 0, 0, 0,
                 "buy=" + (buy_f?"1":"0") +
                 " sell=" + (sell_f?"1":"0") +
                 " gl=" + (g_gate_long?"1":"0") +
                 " gs=" + (g_gate_short?"1":"0") +
                 " bsk=" + (g_long.active?"LONG":g_short.active?"SHORT":"none") +
                 " | " + arm);
    }

    RunTree(buy_f, sell_f);
}

// === SECTION 16: ONINIT ===

int OnInit()
{
    g_sym = (StringLen(Forex_Pair) == 0) ? _Symbol : Forex_Pair;

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
    // changes to Grid_Max_Level_To_SL / Grid_Step_Pips / Fit_Check_Pad_Pips re-derive it.
    // Ladder shape: m(1) = 1; m(n>=2) = 12 * n. (Locked — edit with care.)
    g_wc_lotpips = 0.0;
    for(int n = 1; n <= Grid_Max_Level_To_SL; n++)
    {
        double m   = (n == 1) ? 1.0 : 12.0 * n;
        double adv = Fit_Check_Pad_Pips + Grid_Step_Pips * (Grid_Max_Level_To_SL - n);
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
          " (Grid_Max_Level_To_SL=", Grid_Max_Level_To_SL,
          " Grid_Step_Pips=", DoubleToString(Grid_Step_Pips,1),
          " Fit_Check_Pad_Pips=", DoubleToString(Fit_Check_Pad_Pips,1), ")");

    if(Abort_If_Standard_Account && g_contract_size > 10000.0)
    {
        Alert("AUDCAD v1.4: Abort_If_Standard_Account=true and contract_size=", g_contract_size,
              " looks like a standard symbol. Aborting. Set Abort_If_Standard_Account=false to attach anyway.");
        return INIT_FAILED;
    }

    // v1.4: guard the "Default_Base_Lot_Size < vol_min" check so it only fires
    // when manual override is engaged.
    if(!Auto_Compute_Lot_Size_Based_On_Equity && Default_Base_Lot_Size < g_vol_min)
    {
        Alert("Default_Base_Lot_Size (", Default_Base_Lot_Size, ") < vol_min (", g_vol_min, ")");
        return INIT_FAILED;
    }

    // Projected ladder at current equity — single source of truth for "will it run".
    double base_now = Auto_Compute_Lot_Size_Based_On_Equity
                      ? ComputeBaseLot()
                      : Default_Base_Lot_Size;
    if(base_now <= 0.0)
    {
        if(Auto_Compute_Lot_Size_Based_On_Equity)
            Alert("AUDCAD v1.4: equity (", DoubleToString(eq,2),
                  ") too small for a ", Grid_Max_Level_To_SL, "-leg ladder at ", Max_Drawdown_Percentage,
                  "% cap. EA will skip every probe until equity grows.");
    }
    else
    {
        string ladder = "";
        for(int n = 1; n <= Grid_Max_Level_To_SL; n++)
        {
            if(n > 1) ladder += ",";
            ladder += DoubleToString(LegLot(n, base_now), 2);
        }
        double wc_pct = base_now * g_wc_lotpips * pv / MathMax(eq, 1.0) * 100.0;
        Print("[AUTOSIZE] base=", DoubleToString(base_now,2),
              " ladder=[", ladder, "]",
              " wc_pct=", DoubleToString(wc_pct,2),
              " mode=", (Auto_Compute_Lot_Size_Based_On_Equity ? "auto" : "override"));
    }

    h_rsi  = iRSI(g_sym, Signal_Timeframe, RSI_Period, PRICE_CLOSE);
    h_bb   = iBands(g_sym, Signal_Timeframe, Bollinger_Period, 0, Bollinger_StdDev, PRICE_CLOSE);
    h_gate = iMA(g_sym, GateTimeframe, GateEMA_Period, 0, MODE_EMA, PRICE_CLOSE);

    if(h_rsi == INVALID_HANDLE || h_bb == INVALID_HANDLE || h_gate == INVALID_HANDLE)
    {
        Alert("AUDCAD EA: indicator handle creation failed.");
        return INIT_FAILED;
    }

    ReconstructBaskets();

    g_log = FileOpen(Log_File, FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_SHARE_READ, ',');
    if(g_log == INVALID_HANDLE)
        Print("WARNING: cannot open log file ", Log_File);
    else
    {
        FileWriteString(g_log,
            "# account_type=" + g_account_type_tag +
            ",symbol=" + g_sym +
            ",contract_size=" + DoubleToString(g_contract_size,2) +
            ",ea_version=v1.4\n");
        FileWriteString(g_log,
            "utc_time,event,direction,price,lots_std,equity,equity_pct,"
            "basket_wavg,leg_index,swap_acc,gate_long,gate_short,shadow_mode,note,"
            "base_lot,account_type_tag\n");
    }

    if(Shadow_Mode)
        Print("*** SHADOW MODE ON — OrderSend suppressed, signals logged only ***");

    Print("v1.4: equity-scaled base lot, cent-account default. ",
          (Auto_Compute_Lot_Size_Based_On_Equity
            ? StringFormat("auto-compute (Max_Drawdown_Percentage=%.1f)", Max_Drawdown_Percentage)
            : StringFormat("manual override Default_Base_Lot_Size=%.2f", Default_Base_Lot_Size)),
          ". Exit: basket +/- ", TP_Basket_If_Total_Pips_GreaterThan_EqualTo,
          " pips. Single basket at a time.");

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
            if(pl < 0 && (-pl / eq) >= Max_Drawdown_Percentage / 100.0)
            {
                Print("EMERGENCY EXIT: LONG DD=", DoubleToString(-pl/eq*100,1), "%");
                CloseBasket(g_long, "emergency_dd");
            }
        }
        if(g_short.active)
        {
            double pl = BasketPL(g_short);
            if(pl < 0 && (-pl / eq) >= Max_Drawdown_Percentage / 100.0)
            {
                Print("EMERGENCY EXIT: SHORT DD=", DoubleToString(-pl/eq*100,1), "%");
                CloseBasket(g_short, "emergency_dd");
            }
        }
    }

    // Bar-close logic (once per new M15 bar)
    datetime bar_now = iTime(g_sym, Signal_Timeframe, 0);
    if(bar_now == g_last_bar) return;
    g_last_bar = bar_now;

    OnBarClose();
}

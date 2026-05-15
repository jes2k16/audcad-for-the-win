//+------------------------------------------------------------------+
//|                                         AUDCAD_M15_v1_1.mq5     |
//|                     AUDCAD Mean-Reversion EA â€” v1.1              |
//|                                                                  |
//| Signal:  strategy/AUDCAD_M15_v1.md  Â§1-5                        |
//| Gate:    strategy/AUDCAD_M15_v1.1.md Â§1-3 (D1 EMA20)           |
//| Risk:    plans/1.initial requirements.md Â§9,11,12               |
//+------------------------------------------------------------------+
#property copyright "AUDCAD FOR THE WIN Project"
#property version   "1.10"
#property strict

// === SECTION 1: INPUTS ===

input string          TradeSymbol      = "";           // Trade symbol â€” blank = use chart symbol
input long            MagicLong        = 50000051;    // Magic number: long basket
input long            MagicShort       = 50000052;    // Magic number: short basket
input ENUM_TIMEFRAMES SignalTF         = PERIOD_M15;  // Entry/signal timeframe

// Â§1 Indicator periods
input int             RSI_Period       = 14;
input int             BB_Period        = 20;
input double          BB_StdDev        = 2.0;
input int             SRSI_K_Period    = 14;          // StochRSI stoch lookback
input int             SRSI_K_Smooth    = 3;           // StochRSI %K smoothing
input int             SwingLookback    = 500;         // Bars for rolling swing high
input double          SwingNearPips    = 50.0;        // SELL: fire if within this many pips of swing high

// Â§1 BUY thresholds
input double          Buy_RSI_Dir      = 50.0;        // RSI must be below this
input double          Buy_RSI_Deep     = 40.0;        // OR RSI <= this
input double          Buy_Stoch        = 20.0;        // OR StochRSI %K <= this
input double          Buy_PctB         = 0.10;        // OR BB %B <= this

// Â§1 SELL thresholds
input double          Sell_RSI_Dir     = 50.0;        // RSI must be above this
input double          Sell_RSI_Deep    = 60.0;        // OR RSI >= this
input double          Sell_Stoch       = 60.0;        // OR StochRSI %K >= this
input double          Sell_PctB        = 0.90;        // OR BB %B >= this

// Â§3 Grid
input double          GridStepPips     = 22.0;        // Adverse pips to trigger next add
input int             MaxLegs          = 10;          // Hard leg cap per basket

// Â§4 Lot sizing
input double          ProbeLot         = 0.01;        // Fixed probe lot (standard account)

// Risk (plans/1 Â§9)
input double          MaxDDPct         = 20.0;        // Equity DD hard cap %
input double          FitPadPips       = 5.0;         // Pre-trade fit safety pad pips

// v1.1 Gate (strategy/AUDCAD_M15_v1.1.md Â§1)
input bool            EnableGate       = true;        // false = v1 behavior (no HTF gate)
input ENUM_TIMEFRAMES GateTF           = PERIOD_D1;
input int             GateEMA          = 20;

// Operational
input bool            ShadowMode       = true;        // Suppress OrderSend; log only
input string          LogFile          = "audcad_v1_1.csv";
input int             Verbosity        = 2;           // 0=err 1=events 2=+GATE per bar

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

int    g_log = INVALID_HANDLE;
string g_sym = "";   // resolved symbol name (TradeSymbol input or _Symbol if blank)

// === SECTION 3: UTILITIES ===

double NormLot(double raw)
{
    double n = MathRound(raw / g_vol_step) * g_vol_step;
    n = MathMax(n, g_vol_min);
    n = MathMin(n, g_vol_max);
    return NormalizeDouble(n, 2);
}

// Lot for leg N (1-based). Leg 1 = probe. Leg N>=2: multiplier = 12*N.
// Strategy v1 Â§4: 1x / 24x / 36x / 48x / 60x / ...
double LegLot(int n)
{
    double raw = (n == 1) ? ProbeLot : ProbeLot * 12.0 * n;
    return NormLot(raw);
}

// Smoothed StochRSI %K from RSI buffer (AsSeries=true, [0]=shift 1).
// Replicates: K = rolling_mean(raw_K, k_smooth), raw_K = (rsi-lo)/(hi-lo)*100
// Needs buf[] with at least (k_period + k_smooth - 1) elements.
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

// Returns the first filling mode the symbol actually supports.
ENUM_ORDER_TYPE_FILLING SymbolFilling()
{
    int modes = (int)SymbolInfoInteger(g_sym, SYMBOL_FILLING_MODE);
    if((modes & SYMBOL_FILLING_FOK) != 0) return ORDER_FILLING_FOK;
    if((modes & SYMBOL_FILLING_IOC) != 0) return ORDER_FILLING_IOC;
    return ORDER_FILLING_RETURN;
}

// === SECTION 4: BASKET P/L ===

// Real floating P/L from broker positions (live mode).
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

// Virtual P/L using wavg entry vs current bid/ask (shadow mode).
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

// === SECTION 5: LOGGER ===

void WriteLog(string evt, string dir, double price, double lots,
              double eq, double eq_pct, double wavg, int leg,
              double swap, string note = "")
{
    if(g_log == INVALID_HANDLE) return;
    string line = StringFormat("%s,%s,%s,%.5f,%.2f,%.2f,%.4f,%.5f,%d,%.2f,%s,%s,%s,%s",
        TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES|TIME_SECONDS),
        evt, dir, price, lots, eq, eq_pct, wavg, leg, swap,
        g_gate_long  ? "true":"false",
        g_gate_short ? "true":"false",
        ShadowMode   ? "true":"false",
        note);
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
}

// Accumulate one open position into the basket totals.
// (MQL5 doesn't allow local `&` references, so we pass-by-ref into a helper.)
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

// Find the latest-opened position price for a given magic â€” basket's last_price.
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

// Re-derive basket state from live broker positions on EA restart (plans/1 Â§11).
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

    // Correct last_price to the LATEST opened position per basket
    FixLastPrice(g_long);
    FixLastPrice(g_short);

    if(g_long.active)
        Print("Reconstructed LONG: legs=", g_long.legs,
              " wavg=", DoubleToString(g_long.wavg,5),
              " last=", DoubleToString(g_long.last_price,5));
    if(g_short.active)
        Print("Reconstructed SHORT: legs=", g_short.legs,
              " wavg=", DoubleToString(g_short.wavg,5),
              " last=", DoubleToString(g_short.last_price,5));
}

// === SECTION 7: GATE EVALUATOR (v1.1 Â§1) ===

void RefreshGate()
{
    datetime d1_now = iTime(g_sym, GateTF, 0);
    if(d1_now == g_last_d1 && g_last_d1 != 0) return;  // D1 bar unchanged
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
        Print("Gate refresh: D1_close=", DoubleToString(d1_close,5),
              " EMA", GateEMA, "=", DoubleToString(ema_buf[0],5),
              " long=", g_gate_long, " short=", g_gate_short);
}

// === SECTION 8: SIGNAL EVALUATOR (strategy v1 Â§1) ===

bool EvalSignal(bool &buy_f, bool &sell_f)
{
    buy_f = sell_f = false;

    int rsi_need = SRSI_K_Period + SRSI_K_Smooth;  // 14+3=17; use buf[0..15] max
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

    // Rolling swing high: 500-bar max of M15 High (strategy v1 Â§1)
    double hi_arr[];
    ArraySetAsSeries(hi_arr, true);
    double dist_swing = 9999.0;
    if(CopyHigh(g_sym, SignalTF, 1, SwingLookback, hi_arr) == SwingLookback)
    {
        int idx = ArrayMaximum(hi_arr, 0, WHOLE_ARRAY);
        dist_swing = (hi_arr[idx] - close) / g_pip;
    }

    // BUY: RSI < 50 AND (Stoch<=20 OR %B<=0.10 OR RSI<=40)
    if(rsi14 < Buy_RSI_Dir)
        buy_f = (stoch_k <= Buy_Stoch || pctb <= Buy_PctB || rsi14 <= Buy_RSI_Deep);

    // SELL: RSI > 50 AND (Stoch>=60 OR %B>=0.90 OR RSI>=60 OR near swing high)
    if(rsi14 > Sell_RSI_Dir)
        sell_f = (stoch_k >= Sell_Stoch || pctb >= Sell_PctB ||
                  rsi14 >= Sell_RSI_Deep || dist_swing <= SwingNearPips);

    return true;
}

// === SECTION 9: PRE-TRADE FIT CHECK (plans/1 Â§9) ===

// Simulates worst-case loss if all MaxLegs fire from entry_price.
// Returns false (block probe) if projected loss exceeds MaxDDPct of equity.
bool FitCheck(bool is_long, double entry_price)
{
    double eq = AccountInfoDouble(ACCOUNT_EQUITY);
    if(eq <= 0) return false;

    double pv = PipValPerLot();

    // Worst price: last add fires, then FitPadPips further adverse
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
        total_loss += LegLot(n) * adv_pips * pv;
    }

    if(total_loss / eq > MaxDDPct / 100.0)
    {
        Print("FitCheck FAIL: projected loss=", DoubleToString(total_loss,2),
              " (", DoubleToString(total_loss/eq*100,1), "% of equity ", DoubleToString(eq,2), ")");
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
            req.comment   = "audcad_v1.1_close";
            if(!OrderSend(req, res))
                Print("CloseBasket err: ", GetLastError(), " ticket=", t);
        }
    }

    double close_px = bsk.is_long
        ? SymbolInfoDouble(g_sym, SYMBOL_BID)
        : SymbolInfoDouble(g_sym, SYMBOL_ASK);

    WriteLog(ShadowMode ? "CLOSE_SHADOW" : "CLOSE_BASKET",
             dir, close_px, bsk.total_lots, eq,
             (eq > 0 ? pl/eq*100.0 : 0), bsk.wavg, bsk.legs, sw,
             "reason=" + reason);

    InitBsk(bsk, bsk.is_long);
}

// === SECTION 11: PROBE OPEN ===

bool OpenProbe(bool is_long)
{
    double px = is_long
        ? SymbolInfoDouble(g_sym, SYMBOL_ASK)
        : SymbolInfoDouble(g_sym, SYMBOL_BID);

    if(!FitCheck(is_long, px))
    {
        double eq = AccountInfoDouble(ACCOUNT_EQUITY);
        WriteLog("SKIP_PROBE", is_long?"LONG":"SHORT", px, 0, eq, 0, 0, 0, 0,
                 "fit_check_fail");
        return false;
    }

    double lot = LegLot(1);

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
        req.comment      = "audcad_v1.1_probe";
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
    }

    double eq = AccountInfoDouble(ACCOUNT_EQUITY);
    WriteLog(ShadowMode ? "PROBE_SHADOW" : "PROBE_OPEN",
             is_long?"LONG":"SHORT", px, lot, eq, 0, px, 1, 0,
             "gate_l=" + (g_gate_long?"1":"0") +
             " gate_s=" + (g_gate_short?"1":"0"));
    return true;
}

// === SECTION 12: GRID ADD (strategy v1 Â§3) ===

void CheckAdd(BasketState &bsk)
{
    if(!bsk.active || bsk.exhausted || bsk.legs >= MaxLegs) return;

    double close = iClose(g_sym, SignalTF, 1);
    bool triggered = bsk.is_long
        ? (close <= bsk.last_price - GridStepPips * g_pip)
        : (close >= bsk.last_price + GridStepPips * g_pip);
    if(!triggered) return;

    int    next_n = bsk.legs + 1;
    double lot    = LegLot(next_n);
    double eq     = AccountInfoDouble(ACCOUNT_EQUITY);
    double cur_pl = BasketPL(bsk);
    double pv     = PipValPerLot();

    // Block-add: if adding next leg AND price moves one more grid step,
    // would total loss exceed MaxDDPct? (plans/1 Â§9 forward-looking check)
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
        req.comment      = "audcad_v1.1_add";
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

// === SECTION 13: DECISION TREE (strategy v1.1 Â§2) ===

void RunTree(bool buy_f, bool sell_f)
{
    if(buy_f)
    {
        // Step 1: close opposite SELL basket (gate does NOT block closes)
        if(g_short.active) CloseBasket(g_short, "opp_buy_sig");

        // Step 2: open BUY probe only if gate and no existing buy basket
        if(!g_long.active)
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
        }
        return;
    }

    if(sell_f)
    {
        // Step 1: close opposite BUY basket
        if(g_long.active) CloseBasket(g_long, "opp_sell_sig");

        // Step 2: open SELL probe only if gate and no existing sell basket
        if(!g_short.active)
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
        }
        return;
    }

    // Neither signal: check grid adds
    CheckAdd(g_long);
    CheckAdd(g_short);
}

// === SECTION 14: ON BAR CLOSE ===

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
        double eq = AccountInfoDouble(ACCOUNT_EQUITY);
        string sig = buy_f ? "BUY" : (sell_f ? "SELL" : "none");
        WriteLog("GATE", sig, iClose(g_sym,SignalTF,1),
                 0, eq, 0, 0, 0, 0,
                 "buy=" + (buy_f?"1":"0") +
                 " sell=" + (sell_f?"1":"0") +
                 " gl=" + (g_gate_long?"1":"0") +
                 " gs=" + (g_gate_short?"1":"0"));
    }

    RunTree(buy_f, sell_f);
}

// === SECTION 15: ONINIT ===

int OnInit()
{
    // Resolve symbol: blank input â†’ use the chart/tester symbol
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

    g_pip       = 10.0 * SymbolInfoDouble(g_sym, SYMBOL_POINT);
    g_tick_val  = SymbolInfoDouble(g_sym, SYMBOL_TRADE_TICK_VALUE);
    g_tick_size = SymbolInfoDouble(g_sym, SYMBOL_TRADE_TICK_SIZE);
    g_vol_min   = SymbolInfoDouble(g_sym, SYMBOL_VOLUME_MIN);
    g_vol_max   = SymbolInfoDouble(g_sym, SYMBOL_VOLUME_MAX);
    g_vol_step  = SymbolInfoDouble(g_sym, SYMBOL_VOLUME_STEP);

    Print("Symbol=", g_sym,
          " pip=", DoubleToString(g_pip,6),
          " tick_val=", DoubleToString(g_tick_val,5),
          " vol_min=", g_vol_min, " vol_step=", g_vol_step);

    if(ProbeLot < g_vol_min)
    {
        Alert("ProbeLot (", ProbeLot, ") < vol_min (", g_vol_min, ")");
        return INIT_FAILED;
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
            "# account_type=standard,symbol=" + g_sym + ",ea_version=v1.1\n");
        FileWriteString(g_log,
            "utc_time,event,direction,price,lots_std,equity,equity_pct,"
            "basket_wavg,leg_index,swap_acc,gate_long,gate_short,shadow_mode,note\n");
    }

    if(ShadowMode)
        Print("*** SHADOW MODE ON â€” OrderSend suppressed, signals logged only ***");

    return INIT_SUCCEEDED;
}

// === SECTION 16: ONDEINIT ===

void OnDeinit(const int reason)
{
    if(g_log != INVALID_HANDLE) { FileClose(g_log); g_log = INVALID_HANDLE; }
    // Positions are NOT closed on deinit â€” they persist on the broker (plans/1 Â§11).
}

// === SECTION 17: ONTICK ===

void OnTick()
{
    // Tier 1: emergency DD check on every tick (plans/1 Â§9)
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

    // Tier 2: bar-close logic (once per new M15 bar)
    datetime bar_now = iTime(g_sym, SignalTF, 0);
    if(bar_now == g_last_bar) return;
    g_last_bar = bar_now;

    OnBarClose();
}

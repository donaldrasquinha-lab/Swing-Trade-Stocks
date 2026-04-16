"""
Swing Trading Stock Selector — Upstox Edition
----------------------------------------------
Uses Upstox API v2 for historical OHLC data.

Run with:  streamlit run swing_trader_app.py

Requires an Upstox access token (daily expiry). Paste it in the sidebar.
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# ----------------------------- Page Config ----------------------------- #
st.set_page_config(
    page_title="Swing Trade Selector (Upstox)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

UPSTOX_BASE = "https://api.upstox.com/v2"

# ----------------------------- Stock Universe (Upstox instrument keys) ----------------------------- #
# Format: "NSE_EQ|ISIN"
NSE_UNIVERSE = {
    "Nifty 50": {
        "RELIANCE":    "NSE_EQ|INE002A01018",
        "TCS":         "NSE_EQ|INE467B01029",
        "HDFCBANK":    "NSE_EQ|INE040A01034",
        "INFY":        "NSE_EQ|INE009A01021",
        "ICICIBANK":   "NSE_EQ|INE090A01021",
        "HINDUNILVR":  "NSE_EQ|INE030A01027",
        "ITC":         "NSE_EQ|INE154A01025",
        "SBIN":        "NSE_EQ|INE062A01020",
        "BHARTIARTL":  "NSE_EQ|INE397D01024",
        "KOTAKBANK":   "NSE_EQ|INE237A01028",
        "LT":          "NSE_EQ|INE018A01030",
        "AXISBANK":    "NSE_EQ|INE238A01034",
        "ASIANPAINT":  "NSE_EQ|INE021A01026",
        "MARUTI":      "NSE_EQ|INE585B01010",
        "SUNPHARMA":   "NSE_EQ|INE044A01036",
        "TITAN":       "NSE_EQ|INE280A01028",
        "ULTRACEMCO":  "NSE_EQ|INE481G01011",
        "NESTLEIND":   "NSE_EQ|INE239A01024",
        "BAJFINANCE":  "NSE_EQ|INE296A01024",
        "M&M":         "NSE_EQ|INE101A01026",
        "WIPRO":       "NSE_EQ|INE075A01022",
        "HCLTECH":     "NSE_EQ|INE860A01027",
        "TECHM":       "NSE_EQ|INE669C01036",
        "POWERGRID":   "NSE_EQ|INE752E01010",
        "NTPC":        "NSE_EQ|INE733E01010",
        "TATAMOTORS":  "NSE_EQ|INE155A01022",
        "TATASTEEL":   "NSE_EQ|INE081A01020",
        "JSWSTEEL":    "NSE_EQ|INE019A01038",
        "HINDALCO":    "NSE_EQ|INE038A01020",
        "COALINDIA":   "NSE_EQ|INE522F01014",
        "ONGC":        "NSE_EQ|INE213A01029",
        "BPCL":        "NSE_EQ|INE029A01011",
        "GRASIM":      "NSE_EQ|INE047A01021",
        "DRREDDY":     "NSE_EQ|INE089A01031",
        "CIPLA":       "NSE_EQ|INE059A01026",
        "DIVISLAB":    "NSE_EQ|INE361B01024",
        "ADANIENT":    "NSE_EQ|INE423A01024",
        "ADANIPORTS":  "NSE_EQ|INE742F01042",
        "BAJAJFINSV":  "NSE_EQ|INE918I01026",
        "BAJAJ-AUTO":  "NSE_EQ|INE917I01010",
        "HEROMOTOCO":  "NSE_EQ|INE158A01026",
        "EICHERMOT":   "NSE_EQ|INE066A01021",
        "BRITANNIA":   "NSE_EQ|INE216A01030",
        "TATACONSUM":  "NSE_EQ|INE192A01025",
        "APOLLOHOSP":  "NSE_EQ|INE437A01024",
        "SHRIRAMFIN":  "NSE_EQ|INE721A01013",
        "SBILIFE":     "NSE_EQ|INE123W01016",
        "HDFCLIFE":    "NSE_EQ|INE795G01014",
        "INDUSINDBK":  "NSE_EQ|INE095A01012",
        "LTIM":        "NSE_EQ|INE214T01019",
    },
    "Bank Nifty": {
        "HDFCBANK":    "NSE_EQ|INE040A01034",
        "ICICIBANK":   "NSE_EQ|INE090A01021",
        "SBIN":        "NSE_EQ|INE062A01020",
        "KOTAKBANK":   "NSE_EQ|INE237A01028",
        "AXISBANK":    "NSE_EQ|INE238A01034",
        "INDUSINDBK":  "NSE_EQ|INE095A01012",
        "BANKBARODA":  "NSE_EQ|INE028A01039",
        "PNB":         "NSE_EQ|INE160A01022",
        "AUBANK":      "NSE_EQ|INE949L01017",
        "IDFCFIRSTB":  "NSE_EQ|INE092T01019",
        "FEDERALBNK":  "NSE_EQ|INE171A01029",
        "BANDHANBNK":  "NSE_EQ|INE545U01014",
    },
    "Nifty Midcap": {
        "LUPIN":       "NSE_EQ|INE326A01037",
        "TVSMOTOR":    "NSE_EQ|INE494B01023",
        "GODREJPROP":  "NSE_EQ|INE484J01027",
        "MPHASIS":     "NSE_EQ|INE356A01018",
        "PERSISTENT":  "NSE_EQ|INE262H01021",
        "COFORGE":     "NSE_EQ|INE591G01017",
        "ASHOKLEY":    "NSE_EQ|INE208A01029",
        "CUMMINSIND":  "NSE_EQ|INE298A01020",
        "DIXON":       "NSE_EQ|INE935N01020",
        "POLYCAB":     "NSE_EQ|INE455K01017",
        "VOLTAS":      "NSE_EQ|INE226A01021",
        "TRENT":       "NSE_EQ|INE849A01020",
        "PAGEIND":     "NSE_EQ|INE761H01022",
        "MRF":         "NSE_EQ|INE883A01011",
        "BALKRISIND":  "NSE_EQ|INE787D01026",
        "ESCORTS":     "NSE_EQ|INE042A01014",
        "TATAELXSI":   "NSE_EQ|INE670A01012",
        "LTTS":        "NSE_EQ|INE010V01017",
        "OFSS":        "NSE_EQ|INE881D01027",
    },
}

# ----------------------------- Upstox API Helpers ----------------------------- #
def upstox_headers(token: str) -> dict:
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }


@st.cache_data(ttl=900, show_spinner=False)
def fetch_historical(token: str, instrument_key: str,
                     interval: str = "day", days: int = 250):
    """
    Upstox v2 historical candle endpoint.
    GET /historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}
    Returns DataFrame with columns: Open, High, Low, Close, Volume, OI.
    Returns "AUTH_ERROR" string on 401.
    """
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    safe_key = instrument_key.replace("|", "%7C")
    url = f"{UPSTOX_BASE}/historical-candle/{safe_key}/{interval}/{to_date}/{from_date}"

    try:
        resp = requests.get(url, headers=upstox_headers(token), timeout=15)
        if resp.status_code == 401:
            return "AUTH_ERROR"
        if resp.status_code != 200:
            return None
        data = resp.json()
        candles = data.get("data", {}).get("candles", [])
        if not candles:
            return None

        # Upstox candle format: [timestamp, open, high, low, close, volume, oi]
        df = pd.DataFrame(candles, columns=["Date", "Open", "High", "Low", "Close", "Volume", "OI"])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").set_index("Date")
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["Close"])
        if len(df) < 60:
            return None
        return df
    except Exception:
        return None


def verify_token(token: str):
    """Ping profile endpoint to validate."""
    try:
        resp = requests.get(
            f"{UPSTOX_BASE}/user/profile",
            headers=upstox_headers(token),
            timeout=10,
        )
        if resp.status_code == 200:
            name = resp.json().get("data", {}).get("user_name", "User")
            return True, f"Authenticated as {name}"
        if resp.status_code == 401:
            return False, "Invalid or expired token"
        return False, f"API returned {resp.status_code}"
    except Exception as e:
        return False, f"Connection error: {e}"


# ----------------------------- Technical Indicators ----------------------------- #
def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def atr(df, period=14):
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()


def adx(df, period=14):
    up = df["High"].diff()
    down = -df["Low"].diff()
    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)
    tr = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - df["Close"].shift()).abs(),
        (df["Low"] - df["Close"].shift()).abs(),
    ], axis=1).max(axis=1)
    atr_ = tr.ewm(alpha=1 / period, adjust=False).mean()
    plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(alpha=1 / period, adjust=False).mean() / atr_
    minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(alpha=1 / period, adjust=False).mean() / atr_
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan))
    return dx.ewm(alpha=1 / period, adjust=False).mean()


# ----------------------------- Scoring ----------------------------- #
def analyze_stock(token, symbol, instrument_key):
    df = fetch_historical(token, instrument_key)
    if isinstance(df, str):
        return {"error": df}
    if df is None:
        return None

    close = df["Close"]
    volume = df["Volume"]

    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean() if len(df) >= 200 else pd.Series([np.nan] * len(df), index=df.index)
    rsi14 = rsi(close, 14)
    _, _, macd_hist = macd(close)
    atr14 = atr(df, 14)
    adx14 = adx(df, 14)
    avg_vol_20 = volume.rolling(20).mean()

    last = df.iloc[-1]
    price = float(last["Close"])
    perf_20d = ((price / close.iloc[-21]) - 1) * 100 if len(close) > 21 else 0.0
    high_52w = close.tail(252).max() if len(close) >= 50 else close.max()
    from_high = ((price / high_52w) - 1) * 100

    score = 50.0
    signals = []

    if not np.isnan(sma20.iloc[-1]) and price > sma20.iloc[-1]:
        score += 5; signals.append("Above 20 SMA")
    if not np.isnan(sma50.iloc[-1]) and price > sma50.iloc[-1]:
        score += 8; signals.append("Above 50 SMA")
    if not np.isnan(sma200.iloc[-1]) and price > sma200.iloc[-1]:
        score += 7; signals.append("Above 200 SMA")
    if not np.isnan(sma20.iloc[-1]) and not np.isnan(sma50.iloc[-1]):
        if sma20.iloc[-1] > sma50.iloc[-1]:
            score += 5; signals.append("20>50 SMA")

    current_rsi = float(rsi14.iloc[-1]) if not np.isnan(rsi14.iloc[-1]) else 50.0
    if 50 <= current_rsi <= 65:
        score += 10; signals.append(f"RSI {current_rsi:.0f} (bullish)")
    elif 40 <= current_rsi < 50:
        score += 5; signals.append(f"RSI {current_rsi:.0f} (recovering)")
    elif current_rsi > 70:
        score -= 8; signals.append(f"RSI {current_rsi:.0f} (overbought)")
    elif current_rsi < 30:
        score += 3; signals.append(f"RSI {current_rsi:.0f} (oversold)")

    if not np.isnan(macd_hist.iloc[-1]) and macd_hist.iloc[-1] > 0:
        score += 5; signals.append("MACD bullish")
        recent_hist = macd_hist.tail(4).values
        if len(recent_hist) >= 2 and recent_hist[-2] <= 0 < recent_hist[-1]:
            score += 7; signals.append("MACD fresh crossover")

    current_adx = float(adx14.iloc[-1]) if not np.isnan(adx14.iloc[-1]) else 0.0
    if current_adx > 25:
        score += 8; signals.append(f"Strong trend (ADX {current_adx:.0f})")
    elif current_adx > 20:
        score += 3

    if not np.isnan(avg_vol_20.iloc[-1]) and volume.iloc[-1] > 1.5 * avg_vol_20.iloc[-1]:
        score += 5; signals.append("Volume surge")

    if from_high > -5:
        score += 5; signals.append("Near 52w high")
    elif from_high < -25:
        score -= 3

    score = float(np.clip(score, 0, 100))
    current_atr = float(atr14.iloc[-1]) if not np.isnan(atr14.iloc[-1]) else price * 0.02
    stop_loss = price - (2 * current_atr)
    target_1 = price + (3 * current_atr)
    target_2 = price + (5 * current_atr)

    return {
        "symbol": symbol,
        "instrument_key": instrument_key,
        "price": round(price, 2),
        "score": round(score, 1),
        "rsi": round(current_rsi, 1),
        "adx": round(current_adx, 1),
        "perf_20d": round(perf_20d, 2),
        "from_52w_high": round(from_high, 2),
        "atr": round(current_atr, 2),
        "atr_pct": round((current_atr / price) * 100, 2),
        "stop_loss": round(stop_loss, 2),
        "target_1": round(target_1, 2),
        "target_2": round(target_2, 2),
        "volume": int(last["Volume"]),
        "signals": ", ".join(signals) if signals else "—",
        "df": df,
    }


def position_sizing(capital, price, stop_loss, risk_pct):
    risk_per_share = max(price - stop_loss, 0.01)
    risk_amount = capital * (risk_pct / 100)
    shares = int(risk_amount / risk_per_share)
    max_shares_by_capital = int(capital / price) if price > 0 else 0
    shares = max(min(shares, max_shares_by_capital), 0)
    investment = shares * price
    actual_risk = shares * risk_per_share
    return {
        "shares": shares,
        "investment": round(investment, 2),
        "risk_amount": round(actual_risk, 2),
    }


def plot_stock(result):
    df = result["df"].tail(120).copy()
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06,
        row_heights=[0.75, 0.25],
        subplot_titles=(f"{result['symbol']} — ₹{result['price']}", "Volume"),
    )
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="Price",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA 20",
                             line=dict(color="orange", width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA 50",
                             line=dict(color="blue", width=1.5)), row=1, col=1)
    fig.add_hline(y=result["stop_loss"], line_dash="dash", line_color="red",
                  annotation_text=f"SL ₹{result['stop_loss']}", row=1, col=1)
    fig.add_hline(y=result["target_1"], line_dash="dash", line_color="green",
                  annotation_text=f"T1 ₹{result['target_1']}", row=1, col=1)
    fig.add_hline(y=result["target_2"], line_dash="dot", line_color="darkgreen",
                  annotation_text=f"T2 ₹{result['target_2']}", row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume",
                         marker_color="rgba(100,100,200,0.5)"), row=2, col=1)
    fig.update_layout(
        height=520, showlegend=True, xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


# ----------------------------- UI ----------------------------- #
st.title("📈 Swing Trade Stock Selector")
st.caption("Upstox-powered • NSE equity scan • Capital-aware position sizing")

if "upstox_token" not in st.session_state:
    st.session_state["upstox_token"] = ""
if "token_verified" not in st.session_state:
    st.session_state["token_verified"] = False

with st.sidebar:
    st.header("🔐 Upstox Authentication")

    token_input = st.text_input(
        "Access Token",
        value=st.session_state["upstox_token"],
        type="password",
        help="Paste your Upstox v2 access token. Expires daily ~03:30 AM IST.",
        placeholder="eyJ0eXAiOiJKV1...",
    )

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✅ Verify", use_container_width=True):
            if token_input.strip():
                with st.spinner("Verifying…"):
                    ok, msg = verify_token(token_input.strip())
                st.session_state["upstox_token"] = token_input.strip()
                st.session_state["token_verified"] = ok
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Enter a token first")
    with col_b:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state["upstox_token"] = ""
            st.session_state["token_verified"] = False
            st.cache_data.clear()
            st.rerun()

    if st.session_state["token_verified"]:
        st.markdown("🟢 **Token active**")
    elif st.session_state["upstox_token"]:
        st.markdown("🟡 **Token entered (not verified)**")
    else:
        st.markdown("🔴 **No token**")

    with st.expander("❓ How to get a token"):
        st.markdown("""
        1. Go to [Upstox Developer Console](https://developer.upstox.com/)
        2. Create an app, note the **API Key** & **Secret**
        3. Follow the OAuth flow to get a **code**, then exchange for **access_token**
        4. Paste the token above — valid until ~03:30 AM IST next day

        You already have a token helper from your live options dashboard — reuse it.
        """)

    st.divider()
    st.header("⚙️ Trade Configuration")

    capital = st.number_input(
        "💰 Trading Capital (₹)", min_value=10000, max_value=100000000,
        value=100000, step=10000, format="%d",
    )
    risk_pct = st.slider("Risk per trade (%)", 0.5, 5.0, 2.0, 0.5)
    max_positions = st.slider("Max concurrent positions", 1, 10, 5)

    st.subheader("Universe")
    universe_choice = st.selectbox("Stock universe",
                                   list(NSE_UNIVERSE.keys()) + ["All"])
    if universe_choice == "All":
        universe = {}
        for group in NSE_UNIVERSE.values():
            universe.update(group)
    else:
        universe = NSE_UNIVERSE[universe_choice]

    st.caption(f"Universe size: **{len(universe)}** stocks")

    st.subheader("Filters")
    min_score = st.slider("Minimum score", 0, 100, 60, 5)
    price_min = st.number_input("Min price (₹)", 0, 100000, 50)
    price_max = st.number_input("Max price (₹)", 0, 100000, 10000)

    scan_button = st.button(
        "🔍 Scan Stocks",
        type="primary",
        use_container_width=True,
        disabled=not st.session_state["upstox_token"],
    )

# Landing info
if not scan_button and "results" not in st.session_state:
    if not st.session_state["upstox_token"]:
        st.info("👈 Paste your Upstox access token in the sidebar to begin.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### How it works
        1. **Authenticate** — paste Upstox token (daily expiry)
        2. **Configure** capital, risk %, and universe
        3. **Scan** — each stock gets a 0–100 technical score
        4. **Review** — entry, stop-loss (2×ATR), targets (3× & 5× ATR), share count
        """)
    with col2:
        st.markdown("""
        ### Scoring factors
        - Trend: price vs 20/50/200 SMA
        - Momentum: RSI (14), MACD crossover
        - Trend strength: ADX (14)
        - Volume surge (>1.5× 20-day avg)
        - Proximity to 52-week high
        - Volatility-adjusted stops (ATR)
        """)

# Scanning
if scan_button:
    token = st.session_state["upstox_token"]
    if not token:
        st.error("No token. Paste it in the sidebar first.")
        st.stop()

    progress = st.progress(0, text="Scanning…")
    results = []
    auth_errors = 0
    failed = []

    items = list(universe.items())
    for i, (symbol, ikey) in enumerate(items):
        progress.progress((i + 1) / len(items),
                          text=f"Analyzing {symbol} ({i+1}/{len(items)})")
        r = analyze_stock(token, symbol, ikey)
        if r is None:
            failed.append(symbol)
        elif isinstance(r, dict) and r.get("error") == "AUTH_ERROR":
            auth_errors += 1
            if auth_errors >= 3:
                progress.empty()
                st.error("🔒 Token rejected multiple times. Expired or invalid — generate a fresh one.")
                st.session_state["token_verified"] = False
                st.stop()
        else:
            results.append(r)
        time.sleep(0.08)  # gentle rate-limit

    progress.empty()

    if not results:
        st.error("No data fetched. Check token and try again.")
        st.stop()

    if failed:
        st.warning(f"⚠️ {len(failed)} stocks failed to fetch: {', '.join(failed[:10])}"
                   + ("…" if len(failed) > 10 else ""))

    st.session_state["results"] = results
    st.session_state["scan_time"] = datetime.now()

# Results
if "results" in st.session_state:
    results = st.session_state["results"]
    scan_time = st.session_state.get("scan_time", datetime.now())

    filtered = [
        r for r in results
        if r["score"] >= min_score and price_min <= r["price"] <= price_max
    ]
    filtered.sort(key=lambda x: x["score"], reverse=True)

    st.caption(f"Last scan: {scan_time.strftime('%d %b %Y, %I:%M %p')} "
               f"• {len(filtered)} of {len(results)} passed filters")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Capital", f"₹{capital:,.0f}")
    m2.metric("Risk per trade", f"{risk_pct}%", f"₹{capital * risk_pct / 100:,.0f}")
    m3.metric("Candidates", len(filtered))
    m4.metric("Avg score",
              f"{np.mean([r['score'] for r in filtered]):.1f}" if filtered else "—")

    if not filtered:
        st.warning("No stocks match your filters. Try lowering the minimum score.")
        st.stop()

    st.subheader(f"🎯 Top {min(max_positions, len(filtered))} Swing Picks")
    capital_per_position = capital / max_positions
    top = filtered[:max_positions]

    picks = []
    for r in top:
        sizing = position_sizing(capital_per_position, r["price"], r["stop_loss"], risk_pct)
        picks.append({
            "Symbol": r["symbol"],
            "Score": r["score"],
            "Price": r["price"],
            "Shares": sizing["shares"],
            "Investment": sizing["investment"],
            "Stop Loss": r["stop_loss"],
            "Target 1": r["target_1"],
            "Target 2": r["target_2"],
            "Risk (₹)": sizing["risk_amount"],
            "RSI": r["rsi"],
            "ADX": r["adx"],
            "Signals": r["signals"],
        })

    picks_df = pd.DataFrame(picks)
    st.dataframe(
        picks_df, use_container_width=True, hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score", min_value=0, max_value=100, format="%.1f"),
            "Price": st.column_config.NumberColumn(format="₹%.2f"),
            "Investment": st.column_config.NumberColumn(format="₹%.0f"),
            "Stop Loss": st.column_config.NumberColumn(format="₹%.2f"),
            "Target 1": st.column_config.NumberColumn(format="₹%.2f"),
            "Target 2": st.column_config.NumberColumn(format="₹%.2f"),
            "Risk (₹)": st.column_config.NumberColumn(format="₹%.0f"),
        },
    )

    total_invest = picks_df["Investment"].sum()
    total_risk = picks_df["Risk (₹)"].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total investment", f"₹{total_invest:,.0f}",
              f"{(total_invest/capital)*100:.1f}% deployed")
    c2.metric("Total risk exposure", f"₹{total_risk:,.0f}",
              f"{(total_risk/capital)*100:.2f}% of capital")
    c3.metric("Cash reserve", f"₹{capital - total_invest:,.0f}")

    st.subheader("📊 Stock Chart")
    selected_symbol = st.selectbox(
        "Select stock",
        [r["symbol"] for r in filtered],
        index=0,
    )
    selected = next(r for r in filtered if r["symbol"] == selected_symbol)
    st.plotly_chart(plot_stock(selected), use_container_width=True)

    with st.expander("📋 Full leaderboard"):
        full_df = pd.DataFrame([{
            "Symbol": r["symbol"], "Score": r["score"], "Price": r["price"],
            "RSI": r["rsi"], "ADX": r["adx"], "20d %": r["perf_20d"],
            "From 52wH %": r["from_52w_high"], "ATR %": r["atr_pct"],
            "Signals": r["signals"],
        } for r in filtered])
        st.dataframe(full_df, use_container_width=True, hide_index=True)

    csv = picks_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download picks as CSV",
        csv,
        f"swing_picks_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv",
    )

    st.divider()
    st.caption(
        "⚠️ **Disclaimer**: Educational tool. Not investment advice. "
        "Technical signals are probabilistic. Validate with your own research "
        "and broker's data before trading. Token stays in session memory only — "
        "not logged or persisted."
    )

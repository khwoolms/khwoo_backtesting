import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.title("Multi-Ticker Backtest App")

# ── Sidebar: User inputs ──
tickers = st.sidebar.multiselect(
    "Select Tickers",
    options=["BITU", "SOXL", "TQQQ", "465610.KS"],
    default=["BITU", "SOXL", "TQQQ", "465610.KS"]
    key="ticker_selector"
)
start_date = st.sidebar.date_input("Backtest Start Date", value=pd.to_datetime("2025-06-01"))
run_button = st.sidebar.button("Run Backtest")

def backtest_strategy(ticker, start_date):
    df = yf.Ticker(ticker).history(
        start=start_date, 
        end=datetime.now().strftime("%Y-%m-%d"),
        auto_adjust=False
    )
    if df.empty:
        return pd.DataFrame(), None
    
    df["Prev_Close"] = df["Close"].shift(1)
    position, cost_basis = 0.0, 0.0
    total_realized_pnl, total_buys, total_sells = 0.0, 0, 0
    records = []

    for date, row in df.iterrows():
        open_p, close_p, prev_close = row["Open"], row["Close"], row["Prev_Close"]
        buy_shares = sold_shares = sell_profit = 0.0

        # Sell rule: cum return ≥ 10%
        if position > 0:
            port_val = position * close_p
            cum_return = (port_val - cost_basis) / cost_basis * 100
            if cum_return >= 10:
                sold_shares = position
                avg_price = cost_basis / position
                sell_profit = sold_shares * (close_p - avg_price)
                total_realized_pnl += sell_profit
                position = 0.0
                cost_basis = 0.0
                total_sells += 1

        # Buy rule: gap-down & bearish
        if pd.notna(prev_close) and open_p < prev_close and close_p < open_p:
            buy_shares = 10.0
            position += buy_shares
            cost_basis += buy_shares * close_p
            total_buys += 1

        records.append({
            "date": date,
            "open": open_p,
            "close": close_p,
            "buy_shares": buy_shares,
            "sold_shares": sold_shares,
            "sell_profit": sell_profit,
            "position": position,
            "cost_basis": cost_basis,
            "portfolio_value": position * close_p
        })

    result = pd.DataFrame(records).set_index("date")
    summary = {
        "Total Buys": total_buys,
        "Total Sells": total_sells,
        "Realized P&L": total_realized_pnl,
        "Final Position": position,
        "Final Portfolio": position * result["close"].iloc[-1] if not result.empty else 0,
        "Total Return %": ((position * result["close"].iloc[-1] - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
    }
    return result, summary

if run_button:
    for ticker in tickers:
        st.header(f"Ticker: {ticker}")
        df_res, summary = backtest_strategy(ticker, start_date)
        if df_res.empty:
            st.warning(f"No data for {ticker}")
            continue
        st.subheader("Summary")
        st.write(summary)
        st.subheader("Backtest Details")
        st.dataframe(df_res)

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.title("Multi-Ticker Backtest App")

# ── Sidebar: User inputs ──
tickers = st.sidebar.multiselect(
    "Select Tickers",
    options=["BITU", "SOXL", "TQQQ", "465610.KS"],
    default=["BITU", "SOXL", "TQQQ", "465610.KS"]
)
start_date = st.sidebar.date_input("Backtest Start Date", value=pd.to_datetime("2025-06-01"))
run_button = st.sidebar.button("Run Backtest")

def backtest_strategy(ticker, start_date):
    df = yf.Ticker(ticker).history(
        start=start_date, 
        end=datetime.now().strftime("%Y-%m-%d"),
        auto_adjust=False
    )
    if df.empty:
        return pd.DataFrame(), None
    
    df["Prev_Close"] = df["Close"].shift(1)
    position, cost_basis = 0.0, 0.0
    total_realized_pnl, total_buys, total_sells = 0.0, 0, 0
    records = []

    for date, row in df.iterrows():
        open_p, close_p, prev_close = row["Open"], row["Close"], row["Prev_Close"]
        buy_shares = sold_shares = sell_profit = 0.0

        # Sell rule: cum return ≥ 10%
        if position > 0:
            port_val = position * close_p
            cum_return = (port_val - cost_basis) / cost_basis * 100
            if cum_return >= 10:
                sold_shares = position
                avg_price = cost_basis / position
                sell_profit = sold_shares * (close_p - avg_price)
                total_realized_pnl += sell_profit
                position = 0.0
                cost_basis = 0.0
                total_sells += 1

        # Buy rule: gap-down & bearish
        if pd.notna(prev_close) and open_p < prev_close and close_p < open_p:
            buy_shares = 10.0
            position += buy_shares
            cost_basis += buy_shares * close_p
            total_buys += 1

        records.append({
            "date": date,
            "open": open_p,
            "close": close_p,
            "buy_shares": buy_shares,
            "sold_shares": sold_shares,
            "sell_profit": sell_profit,
            "position": position,
            "cost_basis": cost_basis,
            "portfolio_value": position * close_p
        })

    result = pd.DataFrame(records).set_index("date")
    summary = {
        "Total Buys": total_buys,
        "Total Sells": total_sells,
        "Realized P&L": total_realized_pnl,
        "Final Position": position,
        "Final Portfolio": position * result["close"].iloc[-1] if not result.empty else 0,
        "Total Return %": ((position * result["close"].iloc[-1] - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
    }
    return result, summary

if run_button:
    for ticker in tickers:
        st.header(f"Ticker: {ticker}")
        df_res, summary = backtest_strategy(ticker, start_date)
        if df_res.empty:
            st.warning(f"No data for {ticker}")
            continue
        st.subheader("Summary")
        st.write(summary)
        st.subheader("Backtest Details")
        st.dataframe(df_res)

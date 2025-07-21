import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.title("Multi‑Ticker Backtest App")

# ── Sidebar: 입력 파라미터 ──
tickers = st.sidebar.multiselect(
    "Select Tickers",
    options=["BITU", "SOXL", "TQQQ", "465610.KS"],
    default=["BITU", "SOXL", "TQQQ", "465610.KS"],
    key="ticker_selector"
)

start_date = st.sidebar.date_input(
    "Backtest Start Date",
    value=pd.to_datetime("2025-06-01"),
    key="backtest_start_date"
)

run_button = st.sidebar.button(
    "Run Backtest",
    key="run_backtest_button"
)

# ── 백테스트 함수 정의 ──
def backtest_strategy(ticker: str, start_date: pd.Timestamp):
    df = yf.Ticker(ticker).history(
        start=start_date,
        end=datetime.now().strftime("%Y-%m-%d"),
        auto_adjust=False
    )
    if df.empty:
        return pd.DataFrame(), {}

    df["Prev_Close"] = df["Close"].shift(1)
    position, cost_basis = 0.0, 0.0
    total_realized_pnl, total_buys, total_sells = 0.0, 0, 0
    records = []

    for date, row in df.iterrows():
        open_p, close_p = row["Open"], row["Close"]
        prev_close = row["Prev_Close"]
        buy_shares = sold_shares = sell_profit = 0.0

        # 매도: 누적 수익률 ≥ 10%
        if position > 0:
            portfolio_value = position * close_p
            cum_return = (portfolio_value - cost_basis) / cost_basis * 100
            if cum_return >= 10:
                sold_shares = position
                avg_price = cost_basis / position
                sell_profit = sold_shares * (close_p - avg_price)
                total_realized_pnl += sell_profit
                position = cost_basis = 0.0
                total_sells += 1

        # 매수: 갭하락 & 음봉
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
    final_value = result["portfolio_value"].iloc[-1] if not result.empty else 0
    total_return = (final_value - cost_basis) / cost_basis * 100 if cost_basis > 0 else 0

    summary = {
        "Total Buys": total_buys,
        "Total Sells": total_sells,
        "Realized P&L": total_realized_pnl,
        "Final Position": position,
        "Final Portfolio": final_value,
        "Total Return %": total_return
    }
    return result, summary

# ── 버튼 클릭 시 백테스트 실행 ──
if run_button:
    if not tickers:
        st.sidebar.error("최소 하나 이상의 티커를 선택하세요.")
    else:
        for ticker in tickers:
            st.header(f"▶ {ticker}")
            df_res, summary = backtest_strategy(ticker, start_date)
            if df_res.empty:
                st.warning(f"No data for {ticker}")
                continue
            st.subheader("Summary")
            st.write(summary)
            st.subheader("Details")
            st.dataframe(df_res)

import streamlit as st
import pandas as pd
import portfolio_optimization as po

st.set_page_config(page_title="Portfolio Optimization")

st.header("Portfolio optimization")
st.subheader("Using the Modern Portfolio theory")

# Parameters
st.header("Input parameters")
start_date = st.date_input("Start date", pd.to_datetime("2020-01-01"))
end_date = st.date_input("End date", pd.to_datetime("2024-01-01"))
risk_free_rate = st.number_input("Risk-Free Rate", value=po.RISK_FREE_RATE, format="%.3f")
target = st.number_input("Risk-Free Rate", value=po.TARGET, format="%.3f")
tickers = st.multiselect("Select the tickers", po.TICKERS)

if(st.button("Calculate the results")):
    mean_returns, cov_matrix = po.getData(tickers, start_date, end_date)
    st.table(po.resultsTable(mean_returns, cov_matrix, tickers))
else:
    st.text("Press the button to calculate the optimized Portfolio values")


# table with 2 strategies and SR, returns, volatility and allocation

#camemberts sur allocations

# efficient frontier


import streamlit as st
import pandas as pd
from portfolio_optimization import portfolioPerformance,  maximumSharpeRatio, portfolioVariance, minimumVariance, portfolioReturn, efficientOptimization, calculatedResults, efficientFrontierGraph

st.set_page_config(page_title="Portfolio Optimization")

st.header("Portfolio optimization")
st.subheader("Using the Modern Portfolio theory")

st.header("Input parameters")

start_date = st.date_input("Start date", pd.to_datetime("2020-01-01"))
end_date = st.date_input("End date", pd.to_datetime("2024-01-01"))
tickers = st.text
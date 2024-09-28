import streamlit as st
import pandas as pd
import portfolio_optimization as po
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import companies as co

st.set_page_config(page_title="Portfolio Optimization")

st.title("Portfolio optimization")
st.write("Using the Modern Portfolio theory")
st.text("")
st.text("")

# Parameters
st.subheader("Input parameters")

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Start date", pd.to_datetime(po.START_DATE))
    end_date = st.date_input("End date", pd.to_datetime(po.END_DATE))

with col2:
    risk_free_rate = st.number_input("Risk-Free Rate", value=po.RISK_FREE_RATE, format="%.3f")
    target = st.number_input("Target Rate", value=po.TARGET, format="%.3f")

constraint_set = po.CONSTRAINT_SET

# Tickers
companies_names = []
name_to_ticker = {}
for sector in co.companies.values():
    for company, ticker in sector.items():
        companies_names.append(company)
        name_to_ticker[company] = ticker

selected_companies = st.multiselect("Select the tickers", companies_names)
tickers = [name_to_ticker[company] for company in selected_companies]

st.subheader("VaR parameters")

col1, col2, col3 = st.columns(3)

with col1:
    # Confidence level
    confidence_level = st.radio("Confidence Level", po.CONFIDENCE_LEVEL)
    confidence_level = float(confidence_level.replace(" %", ""))/100

with col2:
    # Time horizon
    time_horizon = st.radio("Time horizon", po.TIME_HORIZONS)
    time_horizon = int(time_horizon.replace(" jours", ""))
with col3:
    n_simulations = st.number_input("Number of simulations (Monte Carlo method)", po.N_SIMULATIONS)

st.text("")

if(st.button("Calculate the results")):
    # Results table
    st.subheader("Results")
    mean_returns, cov_matrix = po.getData(tickers, start_date, end_date)
    results = po.resultsTable(mean_returns, cov_matrix, tickers, risk_free_rate, constraint_set)
    st.table(results)

    # VaR results
    st.subheader("Values at Risk")
    index = ['Maximum Sharpe Ratio', 'Minimum volatility']
    columns = ['Parametric VaR', 'Historical VaR', 'Monte Carlo VaR']
    var = pd.DataFrame(columns=columns, index=index)
    max_SR_weights = po.maximumSharpeRatio(mean_returns, cov_matrix, risk_free_rate, constraint_set)['x']
    min_var_weights = po.minimumVariance(mean_returns, cov_matrix, constraint_set)['x']
    returns = po.getAllReturns(tickers, start_date, end_date)

    # Max Sharpe Ratio
    var.loc['Maximum Sharpe Ratio', 'Parametric VaR'] = parametric_var = po.parametricVar(returns, max_SR_weights, confidence_level)
    var.loc['Maximum Sharpe Ratio', 'Historical VaR'] = historical_var = po.historicalVar(returns, max_SR_weights, confidence_level)
    var.loc['Maximum Sharpe Ratio', 'Monte Carlo VaR'] = montecarlo_var =  po.monteCarloVar(returns, max_SR_weights, confidence_level, n_simulations, time_horizon)

    #Min volatility
    var.loc['Minimum volatility', 'Parametric VaR'] = parametric_var = po.parametricVar(returns, min_var_weights, confidence_level)
    var.loc['Minimum volatility', 'Historical VaR'] = historical_var = po.historicalVar(returns, min_var_weights, confidence_level)
    var.loc['Minimum volatility', 'Monte Carlo VaR'] = montecarlo_var =  po.monteCarloVar(returns, min_var_weights, confidence_level, n_simulations, time_horizon)
    
    st.table(var)

    # Pie charts
    labels = tickers
    max_SR_sizes = results.loc['Maximum Sharpe Ratio', tickers]
    min_vol_sizes = results.loc['Minimum volatility', tickers]

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Maximum Sharpe Ratio stock allocation**")
        fig1, ax1 = plt.subplots()
        ax1.pie(max_SR_sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)
    with col2:
        st.write("**Minimum volatility stock allocation**")
        fig2, ax2 = plt.subplots()
        ax2.pie(min_vol_sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax2.axis('equal')
        st.pyplot(fig2)


    # Efficient frontier
    max_SR_results, max_SR_returns, max_SR_std, max_SR_allocation, min_volatility_results, min_volatility_returns, min_volatility_std, min_volatility_allocation, efficient_list, target_returns = po.calculatedResults(mean_returns, cov_matrix, risk_free_rate, constraint_set)

    #Max SR
    max_SR = go.Scatter(
        name='Maximum Sharpe Ratio',
        mode='markers',
        x=[max_SR_std],
        y=[max_SR_returns],
        marker=dict(color='red', size=14, line=dict(width=3, color='black')))

    # Min volatility
    min_volatility = go.Scatter(
        name='Minimum Volatility',
        mode='markers',
        x=[min_volatility_std],
        y=[min_volatility_returns],
        marker=dict(color='green', size=14, line=dict(width=3, color='black')))

    # Efficient frontier
    efficien_curve = go.Scatter(
        name='Efficient Frontier',
        mode='lines',
        x=[round(ef_std*100,2) for ef_std in efficient_list],
        y=[round(target*100,2) for target in target_returns],
        line=dict(color='black', width=4, dash='dashdot'))

    data = [max_SR, min_volatility, efficien_curve]

    layout = go.Layout(
        title = 'Portfolio optimization with Efficient Frontier',
        yaxis = dict(title='Annualised Return (%)'),
        xaxis= dict(title='Annualised volatility (%)'),
        showlegend = True,
        legend = dict(
            x=0.75, y=0, traceorder='normal', # bottom right corner
            bgcolor='#E2E2E2',
            bordercolor='black',
            borderwidth=2
        ),
        width=800,
        height=600)
    
    efficient_graph = go.Figure(data=data, layout=layout)
    st.plotly_chart(efficient_graph)

else:
    st.write("Press the button to calculate the optimized Portfolio values")
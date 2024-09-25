# Libraries
import numpy as np
import datetime as dt
import yfinance as yf
from scipy.optimize import minimize
import pandas as pd
import plotly.graph_objects as go

# Parameters
TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'JPM', 'V', 'JNJ']
END_DATE = '2023-12-31'
START_DATE = '2020-01-01'
N_TRADING_DAYS = 252
RISK_FREE_RATE = 0.015
CONSTRAINT_SET = (0,1) # no short, we can have 100% of the same asset
TARGET = 0.06

def getData(stocks, start, end):
    """Import the data"""
    data = yf.download(stocks, start, end)['Adj Close']
    returns = data.pct_change()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    return mean_returns, cov_matrix


def portfolioPerformance(weights, mean_returns, cov_matrix):
    """Get the returns and standard deviation of the portfolio"""
    returns = np.sum(mean_returns*weights)*N_TRADING_DAYS
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))*np.sqrt(N_TRADING_DAYS) # variance = w^T * sum(w)
    return returns, std


def negSharpeRatio(weights, mean_returns, cov_matrix, risk_free_rate = RISK_FREE_RATE): # and then take the min of the negative to get the max SR
    """Compute the negative Sharpe ratio"""
    returns, std = portfolioPerformance(weights, mean_returns, cov_matrix)
    sharpe_ratio = (returns - risk_free_rate)/std
    return -sharpe_ratio


def maximumSharpeRatio(mean_returns, cov_matrix, risk_free_rate = RISK_FREE_RATE, constraint_set = CONSTRAINT_SET):
    """Compute the results with the highest Sharpe Ratio"""
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, risk_free_rate)
    constraints = (
        {'type': 'eq',
         'fun': lambda x: np.sum(x)-1
         })
    bound = constraint_set
    bounds = tuple(bound for asset in range(num_assets))
    result = minimize(negSharpeRatio,
                         num_assets*[1./num_assets], # initial guess : let's assume that every weight = 1/num_assets
                         args=args,
                         method='SLSQP',
                         bounds=bounds,
                         constraints=constraints) 
    return result


def portfolioVariance(weights, mean_returns, cov_matrix):
    """Get the portfolio variance"""
    return portfolioPerformance(weights, mean_returns, cov_matrix)[1]


def minimumVariance(mean_returns, cov_matrix, constraint_set = CONSTRAINT_SET):
    """Compute the portfolio with minimum variance"""
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)
    constraints = (
        {'type': 'eq',
         'fun': lambda x: np.sum(x)-1
         })
    bound = constraint_set
    bounds = tuple(bound for asset in range(num_assets))
    result = minimize(portfolioVariance,
                         num_assets*[1./num_assets], # initial guess : let's assume that every weight = 1/num_assets
                         args=args,
                         method='SLSQP',
                         bounds=bounds,
                         constraints=constraints) 
    return result

def portfolioReturn(weights, mean_returns, cov_matrix):
    """Get the portfolio return"""
    return portfolioPerformance(weights, mean_returns, cov_matrix)[0]


def efficientOptimization(mean_returns, cov_matrix, return_target, constraint_set = CONSTRAINT_SET):
    """Optimize the portfolio for a target"""
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)
    constraints = (
        {'type': 'eq', 'fun': lambda x: portfolioReturn(x, mean_returns, cov_matrix) - return_target},
        {'type': 'eq', 'fun': lambda x: np.sum(x)-1})
    bound = constraint_set
    bounds = tuple(bound for asset in range(num_assets))
    eff_opt = minimize(portfolioVariance,
                         num_assets*[1./num_assets], # initial guess : let's assume that every weight = 1/num_assets
                         args=args,
                         method='SLSQP',
                         bounds=bounds,
                         constraints=constraints)
    return eff_opt


def calculatedResults(mean_returns, cov_matrix):
    """Compute all the results and the number of shares for each stock """
    #Max Sharpe ratio portfolio
    max_SR_results = maximumSharpeRatio(mean_returns, cov_matrix)
    max_SR_returns, max_SR_std = portfolioPerformance(max_SR_results['x'], mean_returns, cov_matrix)
    max_SR_allocation = pd.DataFrame(max_SR_results['x'], index=mean_returns.index, columns=['allocation'])
    max_SR_allocation.allocation = [round(i*100,0) for i in max_SR_allocation.allocation]

    #MIn volatility portfolio
    min_volatility_results = minimumVariance(mean_returns, cov_matrix)
    min_volatility_returns, min_volatility_std = portfolioPerformance(min_volatility_results['x'], mean_returns, cov_matrix)
    min_volatility_allocation = pd.DataFrame(min_volatility_results['x'], index=mean_returns.index, columns=['allocation'])
    min_volatility_allocation.allocation = [round(i*100,0) for i in min_volatility_allocation.allocation]

    # Efficient frontier
    efficient_list = []
    target_returns = np.linspace(min_volatility_returns, max_SR_returns, 20)
    
    for target in target_returns:
        efficient_list.append(efficientOptimization(mean_returns, cov_matrix, target)['fun'])
        
    max_SR_returns, max_SR_std = round(max_SR_returns*100,2), round(max_SR_std*100,2)
    min_volatility_returns, min_volatility_std = round(min_volatility_returns*100,2), round(min_volatility_std*100,2)
    return max_SR_returns, max_SR_std, max_SR_allocation, min_volatility_returns, min_volatility_std, min_volatility_allocation, efficient_list, target_returns


def efficientFrontierGraph(mean_returns, cov_matrix):
    """Return a grpah of the efficient frontier"""
    max_SR_returns, max_SR_std, max_SR_allocation, min_volatility_returns, min_volatility_std, min_volatility_allocation, efficient_list, target_returns = calculatedResults(mean_returns, cov_matrix)

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
    
    fig = go.Figure(data=data, layout=layout)
    return fig.show()


mean_returns, cov_matrix = getData(TICKERS, START_DATE, END_DATE)
# max_sharpe_ratio_results = maximumSharpeRatio(mean_returns, cov_matrix, risk_free_rate=RISK_FREE_RATE)
# print(max_sharpe_ratio_results)
# returns, std = portfolioPerformance(max_sharpe_ratio_results['x'], mean_returns, cov_matrix)
# print(calculatedResults(mean_returns, cov_matrix))

# print(efficientOptimization(mean_returns, cov_matrix, TARGET))
efficientFrontierGraph(mean_returns, cov_matrix)
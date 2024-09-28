# Portfolio optimization
This repository contains a Python code that creates a Streamlit app that allows us to create, analyze and optimize a stock portfolio.

## Requirements & installation
Make sure to have installed the Python Packages Installer pip.
Download the files in a specific folder.
Libraries to download on computer : `streamlit`, `pandas`, `matplotlib`, `plotly`, `datetime`, `yfinance`, `scipy`.
Write `pip install {library_name}` on your command terminal.

## Use
In the command terminal, go to the folder containing all these files and write the following command : `streamlit run app.py`.

## Content

`portfolio_optimization.py` : this file contains functions to compute the whole application
`companies.py` : this file contains a python dictionnary containing a lot of companies, associated to their ticker and classified by sectors.
`app.py` : this file contains the streamlit app to run, calling functions from the `portfolio_optimization.py` file.
# %%
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# %%
symbol = 'gme'

# %%
# Fetch the option data
stock= yf.Ticker(symbol)

# create an empty list
calls_bucket = []
puts_bucket = []

# iterate through dataframes for each expiration date
for i in range(0, len(stock.options)):
  option = stock.option_chain(stock.options[i])

# append each dataframe to the list
  calls_bucket.append(option.calls)
  puts_bucket.append(option.puts)

# %%
# concatenate dataframes 
df_calls = pd.concat(calls_bucket)
df_puts = pd.concat(puts_bucket)
df_calls.head()

# %%
# Module to add deltaOI and deltaPrice

# %%
# Module to add StockPrice
def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    return todays_data['Close'][0]

# call the function to get the stock price
current_price = get_current_price(symbol)

# add the stock price to the dataframe
df_calls['StockPrice'] = current_price
df_puts['StockPrice'] = current_price
df_calls.head()

# %%
# Module to filter data

def filter_options_data(df_calls, df_puts, filter=False):
    # Calculate the call upside % threshold for strike
    cPS = 0.03
    cstrike_threshold = df_calls['StockPrice'] + (df_calls['StockPrice'] * cPS)

    # Calculate the call % premium to stock price threshold
    cPP = 0.05
    clastPrice_threshold = df_calls['StockPrice'] * cPP

    # Calculate the put downside % threshold for strike
    pPS = 0.05
    pstrike_threshold = df_puts['StockPrice'] - (df_puts['StockPrice'] * pPS)

    # Calculate the put % premium to stock price threshold
    pPP = 0.03
    plastPrice_threshold = df_puts['StockPrice'] * pPP

    if filter:
        # Filter the Calls data based on the strike and premium criteria
        df_calls = df_calls[(df_calls['strike'] >= cstrike_threshold) & (df_calls['lastPrice'] >= clastPrice_threshold)]

        # Filter the Puts data based on the strike and premium criteria
        df_puts = df_puts[(df_puts['strike'] >= pstrike_threshold) & (df_puts['lastPrice'] >= plastPrice_threshold)]

    # Reset the index of the cleaned dataframe
    df_calls = df_calls.reset_index(drop=True)
    df_puts = df_puts.reset_index(drop=True)

    return df_calls, df_puts

# %%
# set to true/false
filter_options_data(df_calls, df_puts, filter=False)
df_calls.head()

# %%
# Concatenate dataframes 
df_calls_puts = pd.concat([df_calls, df_puts], axis=0)
df_calls_puts.reset_index(drop=True, inplace=True)
df_calls_puts.head()

# %%
# Function to keep only the required columns and add new columns
def process_data(df, drop_col=False, add_col=False):
    if drop_col:
        df = df.loc[:, ['contractSymbol','strike', 'lastPrice', 'openInterest', 'StockPrice']]
    if add_col:
        df.loc[:, 'premiumPrice'] = (df['lastPrice'] / df['StockPrice'])*100
        df.loc[:, 'strike_diff'] = ((df['strike'] - df['StockPrice'])/df['StockPrice'])*100
    return df

# %%
# Set to True/False to activate filtering
df_processed = process_data(df_calls, drop_col=True, add_col=True)
df_processed.head()

# %%
def get_processed_dataframe():
    return df_processed
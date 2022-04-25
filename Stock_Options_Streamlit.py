#Phillip Jones 4/24/2022
#Python script to webscrape and filter stock options.  We want to see the calls and puts 7 strikes back on a variety of tickers.
#we will pass in a list of stocks, functions scrape the data, compile it into a table, and filter out what we want to see.

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from pandas import DataFrame
import datetime
import dateutil.relativedelta as REL
import os
import xlsxwriter
from io import BytesIO

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')


today = datetime.date.today()
start_time = datetime.datetime.now()
rd = REL.relativedelta(days = 1, weekday = REL.FR)
next_friday = today + rd + datetime.timedelta(days=1)
next_friday = next_friday.strftime("%Y-%m-%d %H:%M:%S")
path = os.getcwd()
pd.set_option("display.max_columns", 15)
next_friday1 = today + rd + datetime.timedelta(days=0)
next_friday1 = str(next_friday1)
print(next_friday)
print(next_friday1)

# Modified Lian's function.  Only pulling 1st expiration date (the only thing we care about)
# reduced run time from 14 minutes to about 40 second on 100 tickers.
#used this code from Tony Lian for pulling options table into python
#uses yfinance library: https://pypi.org/project/yfinance/
#https://medium.com/@txlian13/webscrapping-options-data-with-python-and-yfinance-e4deb0124613
def options_chain(symbol):
    tk = yf.Ticker(symbol)
    # Expiration dates
    exps = tk.options
    #grab only first expiration
    for e in exps:
        expiry = exps[0]
    # Get options for each expiration
    options = pd.DataFrame()
    #opt = tk.option_chain(next_friday1)
    opt = tk.option_chain(expiry)
    opt = pd.DataFrame().append(opt.calls).append(opt.puts)
    opt['expirationDate'] = expiry
    options = options.append(opt, ignore_index=True)
    # Bizarre error in yfinance that gives the wrong expiration date
    # Add 1 day to get the correct expiration date
    options['expirationDate'] = pd.to_datetime(options['expirationDate']) + datetime.timedelta(days=1)
    options['dte'] = (options['expirationDate'] - datetime.datetime.today()).dt.days / 365

    # Boolean column if the option is a CALL
    options['CALL'] = options['contractSymbol'].str[4:].apply(
        lambda x: "C" in x)

    options[['bid', 'ask', 'strike']] = options[['bid', 'ask', 'strike']].apply(pd.to_numeric)
    options['mark'] = (options['bid'] + options['ask']) / 2  # Calculate the midpoint of the bid-ask

    # Drop unnecessary and meaningless columns
    options = options.drop(
        columns=['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice'])

    return options

#apparently defunct stocks:
#"WORK",
#"AMTD",
#"ADS",
#"CREE",
#"GRUB",
#"KSU",

stock_list = [
"CLF",
"SIRI",
"CC",
"CODX",
"APT",
"INO",
"EDIT",
"PENN",
"NKLA",
"STNE",
"YETI",
"SAGE",
"DOW",
"LVS",
"EOG",
"CHWY",
"MU",
"ACAD",
"PTON",
"AMAT",
"LYB",
"CSX",
"SBUX",
"FSLY",
"MNST",
"GILD",
"HAS",
"PDD",
"LITE",
"IRBT",
"ROST",
"CVX",
"MRNA",
"EXPE",
"DDOG",
"PZZA",
"CRSP",
"MTCH",
"AXP",
"NKE",
"PXD",
"JPM",
"ABT",
"CRWD",
"TNDM",
"PNC",
"TROW",
"DIS",
"UPS",
"SQ",
"ZS",
"NXPI",
"IBM",
"BYND",
"SWKS",
"CAT",
"EA",
"LOW",
"ROKU",
"HON",
"MMM",
"BA",
"CMI",
"V",
"ULTA",
"GS",
"ANET",
"HD",
"VRTX",
"MA",
"UNH",
"NOC",
"LRCX",
"LMT",
"SPGI",
"AAPL",
"NVDA",
"ADBE",
"TTD",
"NFLX",
"BLK",
"REGN",
"AZO",
"TSLA",
"WOW",
"FOX",
"ADP",
"RCII",
"RHI",
"GPC",
"ECL",
"SHW"]

stonks = ["TSLA","AAPL","NFLX"]

# for loop gets the ticker in the stock list and passes it to the options_chain() function.
# the first expiration date will be the next friday, so the list is then filtered to only weeklys.
# puts and calls are seprated, if the ticker's option has less than 7 strikes back, the last strike is displayed
# otherwise strikes 7 strikes back are displayed.  The table in concated into a new list all_calls_puts
all_calls_puts = []
print("Exp Date: ", next_friday)

for i in stonks:
    all = options_chain(i)
    #expirationDate = all['expirationDate'][0]
    expirationDate = all['expirationDate'][0]
    all = all.loc[all['expirationDate'] == next_friday]
    puts = all.loc[all['CALL'] == False]
    calls = all.loc[all['CALL'] == True]
    if puts.shape[0] < 8:
        put = puts.iloc[(puts.shape[0] - 1):(puts.shape[0])]
        call = calls.iloc[(calls.shape[0] - 1):(calls.shape[0])]
    else:
        put = puts.iloc[6:7]
        call = calls.iloc[6:7]
    options_list1 = pd.concat([put, call], ignore_index=False)
    all_calls_puts.append(options_list1)
    print(i)
    print(expirationDate)
    print("# of puts: ",puts.shape[0])
    print("# of calls: ", calls.shape[0])

options_list = pd.concat(all_calls_puts)
print("")
print("out")
print(options_list)
print(path)
save_name = "options_list_expiring_" + next_friday1 + ".xlsx"
options_list.to_excel(save_name)
fin_time = datetime.datetime.now()

# Notify the reader that the data was successfully loaded.
data_load_state.text("Done!")

output = BytesIO()
workbook = xlsxwriter.Workbook(output, {'in_memory': True})
worksheet = workbook.add_worksheet()


# worksheet.write(A1, options_list)
# workbook.close()

# st.download_button(
#     label="Download Excel workbook",
#     data=output.getvalue(),
#     file_name="workbook.xlsx",
#     mime="application/vnd.ms-excel"
# )



st.subheader('Stock Options Expiring: ', next_friday1)
st.write(options_list)

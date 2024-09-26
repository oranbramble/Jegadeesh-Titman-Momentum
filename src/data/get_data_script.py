import pandas as pd
import yfinance as yf
from datetime import datetime as dt
import json

def get_data(ticker_list):
    code_to_currency = {}
    df = pd.DataFrame()
    for i,code in enumerate(ticker_list):
        ticker = yf.Ticker(code)
        data = ticker.history(start='2010-1-1', end="2024-7-4")['Close']

        currency = ticker.history_metadata.get("currency")
        code_to_currency[code] = currency
        if i < 1:
            df = pd.DataFrame(data)
            df.columns = [code]
        else:
            temp_df = pd.DataFrame(data)
            temp_df.columns = [code]
            df = pd.concat([df, temp_df], axis=1)
    # Resets index and removes 'Ticker' to provide table with only date and close values
    df = df.reset_index()
    df.set_index('Date', inplace=True)
    return df, code_to_currency


def calc_returns(df, columns):
    # Creates table of returns
    returns_df = df.pct_change()
    returns_df = returns_df.reset_index()
    returns_df.columns = ['Date'] + [f"{col}Returns" for col in columns if not col == "Date"]
    return returns_df


def merge_dfs(df1, df2):
    return df1.merge(df2, left_on="Date", right_on="Date")


def clean_df(df):
    # If more than one NaN in column, remove it
    for col in df.columns:
        if df[col].isna().sum() > 10:
            df = df.drop(columns=[col])
    return df


def get_monthly_adj_close_df(df):
    """
    Gets a dataframe containing monthly dates and the first day of the months adjusted close value for each stock
    :param df:
    :return:
    """
    return df.groupby('Date').first().reset_index()


def get_mean_df(df):
    """
    Gets a dataframe containing the mean of each month's stock's returns
    :param df:
    :return:
    """
    return df.groupby(['Date']).mean().reset_index()


def group_df(df, type):
    """
    Groups a dataframe by month, and gets either the monthly average returns, or the monthly first-day adjusted close
    :param df:
    :param type:
    :return:
    """
    # Converts date to MM/YYYY format, then groups and means the adjusted close and return for each month
    df['Date'] = df['Date'].dt.strftime('%m/%Y')
    if type == "returns":
        grouped = get_mean_df(df)
    else:
        grouped = get_monthly_adj_close_df(df)
    grouped['Date'] = pd.to_datetime(grouped['Date'], format="%m/%Y")
    grouped = grouped.sort_values("Date")
    return grouped


if __name__ == "__main__":
    # Gets list of stock tickers from codes.csv
    ticker_list = pd.read_csv("../../data/codes.csv")['Symbol'].astype(str).to_list()

    # Downloads adjusted close data using yfinance
    adj_close_df, code_to_currency = get_data(ticker_list)
    adj_close_df = clean_df(adj_close_df)
    columns = adj_close_df.columns

    # Gets a dataframe contain each stocks daily returns
    returns_df = calc_returns(adj_close_df, columns)
    monthly_returns_df = group_df(returns_df, "returns")

    # Gets a dataframe containing each month's first day adjusted close value
    # Used for buying and selling, need to know price on first day of each month
    adj_close_df = adj_close_df.reset_index()
    monthly_close_df = group_df(adj_close_df, "adj_close")

    monthly_df = merge_dfs(monthly_close_df, monthly_returns_df)

    monthly_df.to_csv("stock_data.csv")
    with open("code_to_currency.json", "w") as f:
        json.dump(code_to_currency, f)
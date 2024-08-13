import pandas as pd

df = pd.read_csv("stock_data.csv")

df['Date'] = pd.to_datetime(df['Date'])

df['Year'] = df['Date'].dt.year

grouped = df.groupby('Year').mean().drop(columns=["Unnamed: 0", 'Date']).T.mean()

print(grouped)


# TODO : Trying to figue out why there is such a dip/rise between 2015 and 2016

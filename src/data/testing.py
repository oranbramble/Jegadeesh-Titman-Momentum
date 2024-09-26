import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("stock_data.csv")

df['Date'] = pd.to_datetime(df['Date'])
df.drop(columns="GMGI", inplace=True)

df['Year'] = df['Date'].dt.year

mean_total = 0
count = 0
for col in df.columns:
    if col != 'Date':
        mean_total += df[col].sum()
        count += len(df[col])

mean_total = mean_total / count

print(mean_total)

for col in df.columns:
    if col != 'Date':
        if not df[col].mean() > mean_total:
            plt.plot(df['Date'], df[col])
        else:
            print(f"STOCK {col} MEAN {df[col].mean()}")
plt.show()

#grouped = df.groupby('Year').mean().drop(columns=["Unnamed: 0", 'Date']).T.mean()



# TODO : Trying to figue out why there is such a dip/rise between 2015 and 2016

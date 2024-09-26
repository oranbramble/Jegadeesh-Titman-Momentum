

import pandas as pd

df = pd.read_csv("../../data/nasdaq_screener_1719598917081.csv")
codes = df['Symbol']
codes.to_csv("data/codes.csv")
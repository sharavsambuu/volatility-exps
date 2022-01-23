
#%%
import matplotlib.pyplot as plt
import pandas as pd
import numpy  as np
import mplfinance as mpf
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['figure.dpi'    ] = 100


#%%


#%%
df = pd.read_csv("./data/BTCUSD_PERP-1m-2021-12.csv", 
        names=[
            "datetime", "open", "high", "low", "close", "volume",
            "close_dt", "quote_asset_volume", "number_of_trades", 
            "taker_buy_base_volume", "taker_buy_quote_volume", "col12"
        ],
        header=None
        ).astype({'datetime':'datetime64[ms]'})

df.set_index('datetime', inplace=True)

df

#%%


#%%

#%%
mpf.plot(df["2021-12-06 06:40":"2021-12-06 13:20"], type='candle', mav=(200, 100), volume=True, style='binance')


#%%


#%%
# daily vol, reindexed to close 

def get_daily_volatility(close, span0=100):
    df0 = close.index.searchsorted(close.index-pd.Timedelta(days=1))
    df0 = df0[df0>0]
    df0 = pd.Series(close.index[df0-1], index = close.index[close.shape[0]-df0.shape[0]:])
    df0 = close.loc[df0.index]/close.loc[df0.values].values-1
    df0 = df0.ewm(span=span0).std() 
    return df0


#%%
volatility_df = get_daily_volatility(df['close'], span0=100)

df['daily_volatility'] = volatility_df


#%%

#%%
ap2 = [
    mpf.make_addplot(df["2021-12-06 06:40":"2021-12-06 13:20"]['daily_volatility'], color='black', panel=1)
    ]
mpf.plot(df["2021-12-06 06:40":"2021-12-06 13:20"], type='candle', title='timebar volatility', volume=False, style='binance', addplot=ap2)


#%%


#%%


#%%
def volume_bars(df, volume_column, m):
    t   = df[volume_column]
    ts  = 0
    idx = []
    for i, x in enumerate(tqdm(t)):
        ts += x
        if ts >= m:
            idx.append(i)
            ts = 0
            continue
    return idx

def volume_bar_df(df, volume_column, m):
    idx = volume_bars(df, volume_column, m)
    return df.iloc[idx].drop_duplicates()

#%%
volumebar_df = volume_bar_df(df, 'volume', 50_000)

volumebar_df

#%%
volumebar_volatility_df = get_daily_volatility(volumebar_df['close'], span0=100)
volumebar_df['daily_volatility'] = volumebar_volatility_df


#%%
ap2 = [
    mpf.make_addplot(volumebar_df["2021-12-06 06:40":"2021-12-06 13:20"]['daily_volatility'], color='black', panel=1)
    ]
mpf.plot(volumebar_df["2021-12-06 06:40":"2021-12-06 13:20"], type='candle', title='volume bar volatility', volume=False, style='binance', addplot=ap2)


#%%


#%%
# time bars
mpf.plot(df["2021-12-06 10:40":"2021-12-06 12:20"], type='candle', title='time bar', volume=True, style='binance')

#%%
# volume bars
mpf.plot(volumebar_df["2021-12-06 10:40":"2021-12-06 12:20"], type='candle', title='volume bar', volume=True, style='binance')


#%%


#%%


#%%
def dollar_bars(df, dv_column, m):
    t = df[dv_column]
    ts = 0
    idx = []
    for i, x in enumerate(tqdm(t)):
        ts += x
        if ts >= m:
            idx.append(i)
            ts = 0
            continue
    return idx

def dollar_bar_df(df, dv_column, m):
    idx = dollar_bars(df, dv_column, m)
    return df.iloc[idx].drop_duplicates()


#%%
df['dollarvolume'] = df['close']*df['volume']


#%%
dollarbar_df = dollar_bar_df(df, 'dollarvolume', 50_000_000)


#%%
mpf.plot(dollarbar_df["2021-12-06 10:40":"2021-12-06 12:20"], type='candle', title='dollar bar', volume=True, style='binance')


#%%
dollarbar_df.head()


#%%


#%%


#%%


#%%


#%%


#%%


#%%


#%%


#%%


#%%


#%%


#%%


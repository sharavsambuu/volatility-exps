
#%%
import matplotlib.pyplot as plt
import pandas as pd
import numpy  as np
import mplfinance as mpf
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
mpf.plot(df, volume=True)

#%%
mpf.plot(df['2021-12-06': '2021-12-06'], type='candle', mav=(200, 100), volume=True)


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
volatility_df = get_daily_volatility(df['close'], span0=150)

df['daily_volatility'] = volatility_df


#%%

#%%
ap2 = [
    mpf.make_addplot(df["2021-12-06":"2021-12-06"]['daily_volatility'], color='black', panel=2)
    ]
mpf.plot(df["2021-12-06":"2021-12-06"], type='candle', volume=True, style='binance', addplot=ap2)


#%%


#%%


#%%


#%%


#%%


#%%


#%%


#%%


#%%


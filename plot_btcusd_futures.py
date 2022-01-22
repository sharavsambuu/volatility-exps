#%%
import matplotlib.pyplot as plt
import pandas as pd
import numpy  as np

#%%
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['figure.dpi'    ] = 100


#%%
!mkdir -p ./data
!wget -O ./data/BTCUSD_PERP-1m-2021-12.zip https://data.binance.vision/data/futures/cm/monthly/klines/BTCUSD_PERP/1m/BTCUSD_PERP-1m-2021-12.zip
!cd ./data && unzip -o ./*.zip


#%%
df = pd.read_csv("./data/BTCUSD_PERP-1m-2021-12.csv", 
        names=[
            "datetime", "open", "high", "low", "close", "volume",
            "close_dt", "quote_asset_volume", "number_of_trades", 
            "taker_buy_base_volume", "taker_buy_quote_volume", "col12"
        ],
        header=None
        )

df

#%%


#%%
df['close'].plot()

#%%
df['volume'].plot()


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


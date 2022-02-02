#
# Binance-аас 1 минутын чартыг бодит хугацаанд татаж харуулах
#
# sudo apt-get install python3-pyqt5  
# virtualenv -p python3 env && source env/bin/activate
# pip install finplot requests websocket scipy

import json
import requests
import websocket
import pandas        as pd
import pyqtgraph     as pg
import finplot       as fplt
from math            import nan
from time            import time as now, sleep
from collections     import defaultdict
from threading       import Thread
from functools       import lru_cache
from pyqtgraph       import QtGui
from PyQt5.QtWidgets import QComboBox, QCheckBox, QWidget, QDoubleSpinBox
from scipy.stats     import t


class BinanceFutureWebsocket:
    def __init__(self):
        self.url      = 'wss://fstream.binance.com/stream'
        self.symbol   = None
        self.interval = None
        self.ws       = None
        self.df       = None
    def reconnect(self, symbol, interval, df):
        '''Connect and subscribe, if not already done so.'''
        self.df = df
        if symbol.lower() == self.symbol and self.interval == interval:
            return
        self.symbol                = symbol.lower()
        self.interval              = interval
        self.thread_connect        = Thread(target=self._thread_connect)
        self.thread_connect.daemon = True
        self.thread_connect.start()
    def close(self, reset_symbol=True):
        if reset_symbol:
            self.symbol = None
        if self.ws:
            self.ws.close()
        self.ws = None
    def _thread_connect(self):
        self.close(reset_symbol=False)
        print('websocket connecting to %s...' % self.url)
        self.ws               = websocket.WebSocketApp(self.url, on_message=self.on_message, on_error=self.on_error)
        self.thread_io        = Thread(target=self.ws.run_forever)
        self.thread_io.daemon = True
        self.thread_io.start()
        for _ in range(100):
            if self.ws.sock and self.ws.sock.connected:
                break
            sleep(0.1)
        else:
            self.close()
            raise websocket.WebSocketTimeoutException('websocket connection failed')
        self.subscribe(self.symbol, self.interval)
        print('websocket connected')
    def subscribe(self, symbol, interval):
        try:
            data = '{"method":"SUBSCRIBE","params":["%s@kline_%s"],"id":1}' % (symbol, interval)
            self.ws.send(data)
        except Exception as e:
            print('websocket subscribe error:', type(e), e)
            raise e
    def on_message(self, *args, **kwargs):
        df = self.df
        if df is None:
            return
        msg = json.loads(args[-1])
        if 'stream' not in msg:
            return
        stream = msg['stream']
        if '@kline_' in stream:
            k  = msg['data']['k']
            t  = k['t']
            t0 = int(df.index[-2].timestamp()) * 1000
            t1 = int(df.index[-1].timestamp()) * 1000
            t2 = t1 + (t1-t0)
            if t < t2:
                # update last candle
                i = df.index[-1]
                df.loc[i, 'Close' ] = float(k['c'])
                df.loc[i, 'High'  ] = max(df.loc[i, 'High'], float(k['h']))
                df.loc[i, 'Low'   ] = min(df.loc[i, 'Low' ], float(k['l']))
                df.loc[i, 'Volume'] = float(k['v'])
            else:
                # create a new candle
                data   = [t] + [float(k[i]) for i in ['o','c','h','l','v']]
                candle = pd.DataFrame([data], columns='Time Open Close High Low Volume'.split()).astype({'Time':'datetime64[ms]'})
                candle.set_index('Time', inplace=True)
                self.df = df.append(candle)
    def on_error(self, error, *args, **kwargs):
        print('websocket error: %s' % error)


def do_load_price_history(symbol, interval):
    limit = 1500
    url   = 'https://www.binance.com/fapi/v1/klines?symbol=%s&interval=%s&limit=%s' % (symbol, interval, limit)
    print('loading binance future %s %s' % (symbol, interval))
    d     = requests.get(url).json()
    df    = pd.DataFrame(d, columns='Time Open High Low Close Volume a b c d e f'.split())
    df    = df.astype({'Time':'datetime64[ms]', 'Open':float, 'High':float, 'Low':float, 'Close':float, 'Volume':float})
    return df.set_index('Time')

@lru_cache(maxsize=5)
def cache_load_price_history(symbol, interval):
    return do_load_price_history(symbol, interval)

def load_price_history(symbol, interval):
    df = cache_load_price_history(symbol, interval)
    t0 = df.index[-2].timestamp()
    t1 = df.index[-1].timestamp()
    t2 = t1 + (t1 - t0)
    if now() >= t2:
        df = do_load_price_history(symbol, interval)
    return df


def vwap(df):
    q  = df['Volume'].values
    p  = df['Close' ].values
    return df.assign(vwap=(p * q).cumsum() / q.cumsum())


def calc_rsi(price, n=14):
    diff   = price.diff().values
    gains  = diff
    losses = -diff
    gains [~(gains >0)] = 0.0
    losses[~(losses>0)] = 1e-10 # we don't want divide by zero/NaN
    m  = (n-1) / n
    ni = 1 / n
    g  = gains[n] = gains[:n].mean()
    l  = losses[n] = losses[:n].mean()
    gains[:n] = losses[:n] = nan
    for i,v in enumerate(gains[n:],n):
        g = gains[i] = ni*v + m*g
    for i,v in enumerate(losses[n:],n):
        l = losses[i] = ni*v + m*l
    rs  = gains / losses
    rsi = 100 - (100/(1+rs))
    return rsi


def calc_plot_data(df):
    price  = df['Open Close High Low'.split()]
    volume = df['Open Close Volume'.split()  ]
    df     = df.groupby(df.index.date, group_keys=False).apply(vwap)
    plot_data = dict(
        price  = price,
        volume = volume,
        vwap   = df['vwap'],
        rsi    = calc_rsi(df['Close'])
        )

    last_close = price.iloc[-1].Close
    last_col   = fplt.candle_bull_color if last_close > price.iloc[-2].Close else fplt.candle_bear_color
    price_data = dict(
        last_close = last_close,
        last_col   = last_col
        )

    return plot_data, price_data


def change_asset(*args, **kwargs):
    fplt._savewindata(fplt.windows[0])
    symbol   = ctrl_panel.symbol.currentText()
    interval = "1m"

    ws.close()
    ws.df    = None
    df       = load_price_history(symbol, interval=interval)
    ws.reconnect(symbol, interval, df)

    ax.reset()
    axo.reset()
    ax_hawkes.reset()
    ax_rsi.reset()

    data, price_data = calc_plot_data(df)

    global plots
    plots = {}
    plots['price' ] = fplt.candlestick_ochl(data['price' ], ax=ax )
    plots['volume'] = fplt.volume_ocv      (data['volume'], ax=axo)
    if data['vwap'] is not None:
        plots['vwap'  ] = fplt.plot(data['vwap'  ], legend='VWAP', ax=ax       , color="#4949FF")
    if data['rsi' ] is not None:
        plots['rsi'] = fplt.plot(data['rsi'], legend='RSI' , ax=ax_rsi, color="#ffffff")
        fplt.add_band(25, 75, color='130f40', ax=ax_rsi)

    ax.price_line = pg.InfiniteLine(angle=0, movable=False, pen=fplt._makepen(fplt.candle_bull_body_color, style='.'))
    ax.price_line.setPos(price_data['last_close'])
    ax.price_line.pen.setColor(pg.mkColor(price_data['last_col']))
    ax.addItem(ax.price_line, ignoreBounds=True)

    ax_hawkes.zero_line = pg.InfiniteLine(angle=0, movable=False, pen=fplt._makepen(fplt.candle_bull_body_color, style='- '))
    ax_hawkes.zero_line.setPos(0.0)
    ax_hawkes.zero_line.pen.setColor(pg.mkColor("#808080"))
    ax_hawkes.addItem(ax_hawkes.zero_line, ignoreBounds=True)

    fplt.refresh()



def create_ctrl_panel(win):
    panel = QWidget(win)
    panel.move(150, 0)
    win.scene().addWidget(panel)
    layout = QtGui.QGridLayout(panel)

    panel.symbol = QComboBox(panel)
    [panel.symbol.addItem(i) for i in
        """
        BTCUSDT  BTCBUSD
        ETHUSDT  ETHBUSD
        SOLUSDT  SOLBUSD
        ADAUSDT  ADABUSD
        XRPUSDT  XRPBUSD
        DOGEUSDT DOGEBUSD
        SANDUSDT
        MANAUSDT
        GALAUSDT
        TRXUSDT
        BNBUSDT  BNBBUSD
        """.strip().split()]
    panel.symbol.setCurrentIndex(0)
    layout.addWidget(panel.symbol, 0, 0)
    panel.symbol.currentTextChanged.connect(change_asset)
    layout.setColumnMinimumWidth(1, 30)

    return panel

def realtime_update_plot():
    if ws.df is None:
        return
    data, price_data = calc_plot_data(ws.df)
    for k in data:
        if data[k] is not None:
            plots[k].update_data(data[k], gfx=False)
    for k in data:
        if data[k] is not None:
            plots[k].update_gfx()
    ax.price_line.setPos(price_data['last_close'])
    ax.price_line.pen.setColor(pg.mkColor(price_data['last_col']))
    fplt.right_margin_candles = 10
    pass

plots                = {}
fplt.y_pad           = 0.07
fplt.max_zoom_points = 7
fplt.autoviewrestore()


ax, ax_hawkes, ax_rsi = fplt.create_plot('Crypto charting by SHS', rows=3, init_zoom_periods=300)
axo = ax.overlay()

ws = BinanceFutureWebsocket()

ax_hawkes.vb.setBackgroundColor(None)
ax.set_visible(xaxis=True)

ctrl_panel = create_ctrl_panel(ax.vb.win)
change_asset()


fplt.timer_callback(realtime_update_plot, 10)
fplt.show()
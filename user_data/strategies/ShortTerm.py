# --- Do not remove these libs ---
from datetime import datetime, timedelta
from typing import Optional, Union

import ta.trend
import ta.utils
import ta.momentum
import ta.volatility
from pandas import DataFrame
from freqtrade.strategy import IStrategy
import freqtrade.vendor.qtpylib.indicators as qtpylib


# Backtesting Report for XRP/USDT
# ================== SUMMARY METRICS ==================
# | Metric                      | Value               |
# |-----------------------------+---------------------|
# | Backtesting from            | 2022-08-31 00:00:00 |
# | Backtesting to              | 2022-09-30 13:44:00 |
# | Max open trades             | 1                   |
# |                             |                     |
# | Total/Daily Avg Trades      | 106 / 3.53          |
# | Starting balance            | 1000 USDT           |
# | Final balance               | 1335.706 USDT       |
# | Absolute profit             | 335.706 USDT        |
# | Total profit %              | 33.57%              |
# | CAGR %                      | 3284.42%            |
# | Profit factor               | 3.46                |
# | Trades per day              | 3.53                |
# | Avg. daily profit %         | 1.12%               |
# | Avg. stake amount           | 989.797 USDT        |
# | Total trade volume          | 104918.507 USDT     |

class ShortTerm(IStrategy):
    INTERFACE_VERSION: int = 3
    # Number of candles needed to calculate signals
    startup_candle_count = 14
    # Minimal ROI designed for the strategy.
    # adjust based on market conditions. We would recommend to keep it low for quick turn arounds
    # This attribute will be overridden if the config file contains "minimal_roi"

    minimal_roi = {
        "0": 0.046,
        "7": 0.0280,
        "16": 0.006,
        "40": 0
    }

    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.112
    trailing_stop_positive_offset = 0.137
    trailing_only_offset_is_reached = True

    # Can this strategy go short?
    can_short = False

    # Optimal stoploss designed for the strategy
    stoploss = -0.333

    # Optimal timeframe for the strategy
    timeframe = '1m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = False
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        MACD = ta.trend.MACD(dataframe['close'])
        EMA7 = ta.trend.EMAIndicator(dataframe['close'], window=7)
        EMA14 = ta.trend.EMAIndicator(dataframe['close'], window=14)
        dataframe['macdhist'] = MACD.macd_diff()
        dataframe['ema7'] = EMA7.ema_indicator()
        dataframe['ema14'] = EMA14.ema_indicator()
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # if macd histogram crossed below zero
                (qtpylib.crossed_below(dataframe['macdhist'], 0)) &
                # if the fast Exponential Moving Average is over the slow Expoential Moving Average
                (dataframe['ema7'] > dataframe['ema14'])
            ), 'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # There is no specific exit signals.
                # exit is fully dependant on stoploss, trailing-stoploss and return on investment values
            ),
            'exit_long'] = 1
        return dataframe

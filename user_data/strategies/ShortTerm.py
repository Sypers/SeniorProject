# --- Do not remove these libs ---
from datetime import datetime, timedelta
from typing import Optional, Union

import ta.trend
import ta.utils
import ta.momentum
import ta.volatility
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
import freqtrade.vendor.qtpylib.indicators as qtpylib


# --------------------------------


class ShortTerm(IStrategy):
    INTERFACE_VERSION: int = 3

    # Minimal ROI designed for the strategy.
    # adjust based on market conditions. We would recommend to keep it low for quick turn arounds
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "120": 0.03,
        "60": 0.05,
        "35": 0.067,
        "0": 0.09
    }

    use_custom_stoploss = True

    # Trailing stoploss
    trailing_stop = False
    trailing_stop_positive = 0.012
    trailing_stop_positive_offset = 0.092
    trailing_only_offset_is_reached = False

    # Can this strategy go short?
    can_short = False

    # Optimal stoploss designed for the strategy
    stoploss = -0.03

    # Optimal timeframe for the strategy
    timeframe = '5m'

    # Strategy Parameters
    # buy_stoch = DecimalParameter(1, 33, default=BUY_STOCH_DEF)
    # sell_stoch = DecimalParameter(67, 100, default=SELL_STOCH_DEF)

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        EMA = ta.trend.EMAIndicator(dataframe['close'], window=9)
        BB = ta.volatility.BollingerBands(dataframe['close'], window=16)
        MACD = ta.trend.MACD(dataframe['close'], window_slow=22, window_fast=8)
        dataframe['ema'] = EMA.ema_indicator()
        dataframe['bb_h'] = BB.bollinger_hband()
        dataframe['bb_m'] = BB.bollinger_mavg()
        dataframe['bb_l'] = BB.bollinger_lband()
        dataframe['bb_w'] = BB.bollinger_wband()
        dataframe['macd'] = MACD.macd()
        dataframe['macdsignal'] = MACD.macd_signal()
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['ema'], dataframe['bb_m']) |
                 dataframe['close'] <= dataframe['bb_l']) &
                ((dataframe['macd'] > 8) | (dataframe['macd'] < -8)) &
                (dataframe['bb_w'] > 0.15)
            ),
            'enter_long'] = 1
        # dataframe.loc[
        #     (
        #
        #     ),
        # ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (qtpylib.crossed_below(dataframe['ema'], dataframe['bb_m']) |
                dataframe['close'] >= dataframe['bb_h'])
            ),
            'exit_long'] = 1
        return dataframe
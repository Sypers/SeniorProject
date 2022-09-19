# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401

# --- Do not remove these libs ---
from functools import reduce

import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame  # noqa
from datetime import datetime  # noqa
from typing import Optional, Union, Dict, List  # noqa
from freqtrade.strategy import (IStrategy, IntParameter, BooleanParameter, CategoricalParameter)
import talib.abstract as ta
# --------------------------------
# Add your lib to import here

import freqtrade.vendor.qtpylib.indicators as qtpylib


class Longterm(IStrategy):
    """
    class HyperOpt:
        def stoploss_space(self):
            return [SKDecimal(-0.15,0.1,decimals=3,name='stoploss')]
        def roi_space(self):
            return[
                Integer(720,1440*3,name='roi_t1'),
                Integer(720, 1440, name='roi_t2'),
                Integer(0, 1440, name='roi_t3'),
                SKDecimal(0.05, 0.10, decimals=3, name='roi_p1'),
                SKDecimal(0.10, 0.20, decimals=3, name='roi_p2'),
                SKDecimal(0.15, 0.45, decimals=3, name='roi_p3'),
            ]
        """

    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Optimal timeframe for the strategy.
    timeframe = '1d'

    # Can this strategy go short?
    can_short: bool = False

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    # ROI HAVE BEEN CHANGED USING HYPEROPT
    minimal_roi = {
        "0": 0.477,
        "10493": 0.429,
        "21245": 0.147,
        "50026": 0
    }
    # Hyperopt\Strategy Parameters
    buy_rsi = IntParameter(10, 40, default=26, space="buy")
    sell_rsi = IntParameter(60, 90, default=90, space="sell")
    enter_indicators = CategoricalParameter(["enter_rsi", "enter_macd", "all"], default="enter_macd", space="buy",
                                            optimize=False)
    exit_indicators = CategoricalParameter(["exit_rsi", "exit_macd", "all"], default="all", space="sell",
                                           optimize=False)
    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    # STOPLOSS HAVE BEEN CHANGED USING HYPEROPT
    stoploss = -0.086
    # Trailing stop-loss
    trailing_stop = True
    trailing_only_offset_is_reached = True
    trailing_stop_positive = 0.289
    trailing_stop_positive_offset = 0.301  # Disabled / not configured

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    # Optional order type mapping.
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'entry': 'gtc',
        'exit': 'gtc'
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return [("BTC/USDT", "1d")]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        :param dataframe: Dataframe with data from the exchange
        :param metadata: Additional information, like the currently traded pair
        :return: a Dataframe with all mandatory indicators for the strategies
        """

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe)
        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        # conditions.append((dataframe['volume'] > 0))
        if self.enter_indicators.value == "all":
            conditions.append(qtpylib.crossed_below(dataframe['rsi'], self.buy_rsi.value))
            conditions.append(qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']))
        elif self.enter_indicators.value == "enter_rsi":
            conditions.append(qtpylib.crossed_below(dataframe['rsi'], self.buy_rsi.value))
        elif self.enter_indicators.value == "enter_macd":
            conditions.append(qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']))
        dataframe.loc[
            reduce(lambda x, y: x | y, conditions), 'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """
        # conditions.append((dataframe['volume'] > 0))  # Make sure Volume is not 0
        if self.exit_indicators.value == "all":
            conditions.append(qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']))
            conditions.append(qtpylib.crossed_above(dataframe['rsi'], self.sell_rsi.value))
        elif self.exit_indicators.value == "exit_rsi":
            conditions.append(qtpylib.crossed_above(dataframe['rsi'], self.sell_rsi.value))
        elif self.exit_indicators.value == "exit_macd":
            conditions.append(qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']))
        dataframe.loc[
            (reduce(lambda x, y: x | y, conditions)), 'exit_long'] = 1
        # Uncomment to use shorts (Only used in futures/margin mode. Check the documentation for more info)
        """
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['rsi'], self.buy_rsi.value)) &  # Signal: RSI crosses above buy_rsi
                (dataframe['tema'] <= dataframe['bb_middleband']) &  # Guard: tema below BB middle
                (dataframe['tema'] > dataframe['tema'].shift(1)) &  # Guard: tema is raising
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'exit_short'] = 1
        """
        return dataframe

    def histogram_reversal_down(self, dataframe: DataFrame):
        df_last_3 = dataframe['macdhist'].tail(3)
        print("From reversal down")
        print(df_last_3)

    def histogram_reversal_up(self, dataframe: DataFrame):
        df_last_3 = dataframe['macdhist'].tail(3)
        print("From reversal down")
        print(df_last_3)


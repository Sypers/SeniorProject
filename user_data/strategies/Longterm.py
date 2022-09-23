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
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Optimal timeframe for the strategy.
    timeframe = '1d'

    # Can this strategy go short?
    can_short: bool = False

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    # Return on investment values has been optimized using hyperopt
    minimal_roi = {
        "0": 0.477,
        "10493": 0.429,
        "21245": 0.147,
        "50026": 0
    }
    # Hyperopt\Strategy Parameters
    # Using the strategy for backtesting or trading will only take the default value.
    buy_rsi = IntParameter(10, 40, default=26, space="buy")  # The value the RSI has to reach for buy signals
    sell_rsi = IntParameter(60, 90, default=90, space="sell")  # The value the RSI has to reach for buy signals
    enter_indicators = CategoricalParameter(["enter_rsi", "enter_macd", "all"], default="enter_macd", space="buy",
                                            optimize=False)  # The mix of buy indicators to use for the strategy
    exit_indicators = CategoricalParameter(["exit_rsi", "exit_macd", "all"], default="all", space="sell",
                                           optimize=False)  # the mix of sell indicators to use for the strategy
    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    # Stoploss and trailing stoploss has been optimized with hyperopt
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

    # This method is for calculating indicator values using the OHCLV candles data in the dataframe
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
        conditions = []  # Using an array to add indicator conditions for buy signals
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        conditions.append(dataframe['volume'] > 0)
        # the if statements values depend on the enter_indicator value
        if self.enter_indicators.value == "all":
            conditions.append(qtpylib.crossed_below(dataframe['rsi'], self.buy_rsi.value))
            conditions.append(qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']))
        elif self.enter_indicators.value == "enter_rsi":
            conditions.append(qtpylib.crossed_below(dataframe['rsi'], self.buy_rsi.value))
        elif self.enter_indicators.value == "enter_macd":
            conditions.append(qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']))
        """
        dataframe.loc will use the conditions array to locate rows in the dataframe that meet the indicators 
        conditions in the conditions array, reduce will use lambda function to apply to check if any of the 
        conditions are met and signal the row in the dataframe that meets any of the conditions to a buy signal """
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
        conditions.append((dataframe['volume'] > 0))  # Make sure Volume is not 0
        # the if statements values depend on the exit_indicator value
        if self.exit_indicators.value == "all":
            conditions.append(qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']))
            conditions.append(qtpylib.crossed_above(dataframe['rsi'], self.sell_rsi.value))
        elif self.exit_indicators.value == "exit_rsi":
            conditions.append(qtpylib.crossed_above(dataframe['rsi'], self.sell_rsi.value))
        elif self.exit_indicators.value == "exit_macd":
            conditions.append(qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']))
        """
        dataframe.loc will use the conditions array to locate rows in the dataframe that meet the indicators 
        conditions in the conditions array, reduce will use lambda function to apply to check if any of the 
        conditions are met and signal the row in the dataframe that meets any of the conditions to a sell signal """
        dataframe.loc[
            (reduce(lambda x, y: x | y, conditions)), 'exit_long'] = 1
        return dataframe
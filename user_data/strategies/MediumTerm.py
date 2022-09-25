# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# EDIT TEST
# --- Do not remove these libs ---
from datetime import datetime  # noqa
from datetime import timedelta, datetime
from functools import reduce
from typing import Optional, Union  # noqa

import numpy as np  # noqa
import pandas as pd  # noqa
import pandas.core.generic
import ta.utils
from pandas import DataFrame, Series  # noqa
from ta.momentum import StochRSIIndicator
from ta.trend import SMAIndicator

# --------------------------------
# Add your lib to import here
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.persistence import Trade
from freqtrade.strategy import (DecimalParameter,
                                IStrategy, IntParameter, BooleanParameter)


class MediumTerm(IStrategy):
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Optimal timeframe for the strategy.
    timeframe = '4h'

    # Can this strategy go short?
    can_short: bool = False

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    # Return on investment values has been optimized using hyperopt
    minimal_roi = {
        "0": 0.253,
      "1691": 0.119,
      "3511": 0.047,
      "8039": 0
    }
    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    # Stoploss and trailing stoploss has been optimized with hyperopt
    stoploss = -0.077

    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.307
    trailing_stop_positive_offset = 0.36
    trailing_only_offset_is_reached = True

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Strategy/Hyperopt parameters
    # Using the strategy for backtesting or trading will only take the default value.
    buy_stoch = DecimalParameter(0.05, 0.3, default=0.255, space="buy")  # the value the stochastic indicator has to reach for a buy signal
    sell_stoch = DecimalParameter(0.7, 1, default=0.731, space="sell")  # the value the stochastic indicator has to reach for a sell signal
    candle_cooldown = IntParameter(0, 5, default=0, space="protection")  # value for the amount of candles to ignore buy signals from after a trade sell.
    enable_buy_rsi = BooleanParameter(default=True, space="buy", optimize=False)  # enable or disable RSI buy signal
    enable_buy_stoch = BooleanParameter(default=True, space="buy")  # enable or disable Stochastic buy signal
    enable_buy_macd = BooleanParameter(default=True, space="buy")  # enable or disable MACD buy signal
    enable_sell_rsi = BooleanParameter(default=True, space="sell", optimize=False)  # enable or disable RSI sell signal
    enable_sell_stoch = BooleanParameter(default=True, space="sell")  # enable or disable Stochastic sell signal
    enable_sell_macd = BooleanParameter(default=True, space="sell")  # enable or disable MACD sell signal
    check_range = 1  # the value for number of candles to check for stoch_check and macd_check methods
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

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": self.candle_cooldown.value
            }
        ]

    @property
    def plot_config(self):
        return {
            # Main plot indicators (Moving averages, ...)
            'main_plot': {

            },
            'subplots': {
                # Subplots - each dict defines one additional plot

            }
        }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        rsi = ta.momentum.RSIIndicator(dataframe['close'])  # load RSI indicator
        stoch = ta.momentum.StochRSIIndicator(dataframe['close'])  # load Stochastic indicator
        macd = ta.trend.MACD(dataframe['close'], window_slow=21, window_fast=8, window_sign=5)  # load MACD indicator
        # attach indicators data to a new column to the pair dataframe
        dataframe['stoch'] = stoch.stochrsi()
        dataframe['d'] = stoch.stochrsi_d()
        dataframe['k'] = stoch.stochrsi_k()
        dataframe['rsi'] = rsi.rsi()
        dataframe['macd'] = macd.macd()
        dataframe['macdsignal'] = macd.macd_signal()
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        :param dataframe: Dataframe with data from the exchange
        :param metadata: Additional information, like the currently traded pair
        :return: a Dataframe with all mandatory indicators for the strategies
        """

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        conditions = []  # Using an array to add indicator conditions for buy signals
        # these indicators are the bare minimum that must be present for hyperopt
        conditions.append(dataframe['volume'] > 0)  # make sure trading volume is not 0
        conditions.append((dataframe['rsi'] >= 50))  # where RSI value is bigger than or equal 50
        if self.enable_buy_stoch.value:
            #  rows where the stochastic value is below the stochastic buy value
            conditions.append(self.stoch_check(dataframe, self.check_range, True))
        if self.enable_buy_macd.value:
            # rows where the MACD value crossed above the MACD Signal value
            conditions.append(qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']))
        """
        dataframe.loc will use the conditions array to locate rows in the dataframe that meet the indicators 
        conditions in the conditions array, reduce will use lambda function to apply to check if all of the 
        conditions are met and signal the row in the dataframe that meets all of the conditions to a buy signal """
        dataframe.loc[(reduce(lambda x, y: x & y, conditions)), 'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """
        conditions = []
        # if self.enable_sell_rsi.value:
        conditions.append(dataframe['rsi'] < 50)
        if self.enable_sell_stoch.value:
            conditions.append(self.stoch_check(dataframe, self.check_range, False))
        if self.enable_sell_macd.value:
            conditions.append(qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']))
        dataframe.loc[(reduce(lambda x, y: x & y, conditions)), 'exit_long'] = 1
        """
        dataframe.loc will use the conditions array to locate rows in the dataframe that meet the indicators 
        conditions in the conditions array, reduce will use lambda function to apply to check if all of the 
        conditions are met and signal the row in the dataframe that meets all of the conditions to a sell signal """
        return dataframe

    #
    def fibonnaci_retractment(self, dataframe: DataFrame, length: int) -> Series:
        values = dataframe['close'].tail(length)
        maximum_price = values.max()
        minimum_price = values.min()
        difference = maximum_price - minimum_price
        first_level = maximum_price - difference * 0.618
        second_level = maximum_price - difference * 0.5
        third_level = maximum_price - difference * 0.382
        fourth_level = maximum_price - difference * 0.236
        fibonacci = pandas.Series(name='fibonacci_r',
                                  data={1: first_level, 2: second_level, 3: third_level, 4: fourth_level}
                                  , index=[1, 2, 3, 4])
        return fibonacci

    def macd_check(self, dataframe: DataFrame, check_range: int, buy_signal: bool) -> Series:
        """
        Check the dataframe for MACD and MACD Signal crossover within a certain range, the reason for this method is
        buy and sell signals might not be always on the same candle so we check for previous nearby candles for the
        signals needed for the strategy
        :param dataframe: Dataframe that contains the pair data including the indicators data.
        :param check_range: the amount of previous candles to check NOTE: setting it as 0 will not check any candle including the current one.
        :param buy_signal: True to check for buy signals, False to check for sell signals of the indicator.
        :return: A pandas Series that includes the rows where MACD and MACD Signal crossed depending on value
        """
        series = pandas.Series(dtype="float64")
        if buy_signal:
            for x in range(check_range):
                pandas.concat([series, qtpylib.crossed_above(dataframe['macd'].shift(x), dataframe['macdsignal'].shift(x))])
        else:
            for x in range(check_range):
                pandas.concat([series, qtpylib.crossed_below(dataframe['macd'].shift(x), dataframe['macdsignal'].shift(x))])
        return series

    def stoch_check(self, dataframe: DataFrame, check_range: int, buy_signal: bool) -> Series:
        """
        Check the dataframe for Stochastic crossover with stochastic buy and sell values within a certain range, the reason for this method is
        buy and sell signals might not be always on the same candle so we check for previous nearby candles for the
        signals needed for the strategy
        :param dataframe: Dataframe that contains the pair data including the indicators data.
        :param check_range: the amount of previous candles to check NOTE: setting it as 0 will not check any candle including the current one.
        :param buy_signal: True to check for buy signals, False to check for sell signals of the indicator.
        :return: A pandas Series that includes the rows where Stochastic crossed with Stochastic buy or sell values
        """
        series = pandas.Series(dtype="float64")
        if buy_signal:
            for x in range(check_range):
                pandas.concat([series, qtpylib.crossed_below(dataframe['stoch'].shift(x), self.buy_stoch.value)])
        else:
            for x in range(check_range):
                pandas.concat([series, qtpylib.crossed_above(dataframe['stoch'].shift(x), self.sell_stoch.value)])
        return series

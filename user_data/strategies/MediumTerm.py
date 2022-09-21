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
    """
    This is a strategy template to get you started.
    More information in https://www.freqtrade.io/en/latest/strategy-customization/

    You can:
        :return: a Dataframe with all mandatory indicators for the strategies
    - Rename the class name (Do not forget to update class_name)
    - Add any methods you want to build your strategy
    - Add any lib you need to build your strategy

    You must keep:
    - the lib in the section "Do not remove these libs"
    - the methods: populate_indicators, populate_entry_trend, populate_exit_trend
    You should keep:
    - timeframe, minimal_roi, stoploss, trailing_*
    """
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Optimal timeframe for the strategy.
    timeframe = '4h'

    # Can this strategy go short?
    can_short: bool = False

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "0": 0.025,
        "787": 0.05,
        "2524": 0.1,
        "6897": 0.2
    }
    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.05

    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.011
    trailing_stop_positive_offset = 0.109
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
    buy_stoch = DecimalParameter(0.05, 0.3, default=0.15, space="buy")
    sell_stoch = DecimalParameter(0.7, 1, default=0.92, space="sell")
    candle_cooldown = IntParameter(0, 5, default=2, space="protection")
    enable_buy_rsi = BooleanParameter(default=True, space="buy")
    enable_buy_stoch = BooleanParameter(default=True, space="buy")
    enable_buy_macd = BooleanParameter(default=True, space="buy")
    enable_sell_rsi = BooleanParameter(default=True, space="sell")
    enable_sell_stoch = BooleanParameter(default=True, space="sell")
    enable_sell_macd = BooleanParameter(default=True, space="sell")
    check_range = 1
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
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # PSAR = ta.trend.PSARIndicator(dataframe['high'], dataframe['low'], dataframe['close'],
        #                               step=self.psar_steps.value, max_step=self.psar_max.value,
        #                               fillna=True)
        # dataframe['PSARUp'] = PSAR.psar_up_indicator()
        # dataframe['PSARDown'] = PSAR.psar_down_indicator()
        rsi = ta.momentum.RSIIndicator(dataframe['close'])
        stoch = ta.momentum.StochRSIIndicator(dataframe['close'])
        #  sma = ta.trend.SMAIndicator(dataframe['close'], 100).sma_indicator()
        macd = ta.trend.MACD(dataframe['close'], window_slow=21, window_fast=8, window_sign=5)
        dataframe['stoch'] = stoch.stochrsi()
        dataframe['d'] = stoch.stochrsi_d()
        dataframe['k'] = stoch.stochrsi_k()
        #  dataframe['sma'] = sma
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
        conditions = []
        # if self.enable_buy_rsi.value:
        conditions.append((dataframe['rsi'] >= 50))
        if self.enable_buy_stoch.value:
            conditions.append(self.stoch_check(dataframe, self.check_range, True))
        if self.enable_buy_macd.value:
            conditions.append(qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']))
        dataframe.loc[(reduce(lambda x, y: x & y, conditions)), 'enter_long'] = 1
        # qtpylib.crossed_above(dataframe['PSARDown'], 0)
        # (qtpylib.crossed_below(dataframe['d'], self.buy_stoch.value)) &
        # (qtpylib.crossed_below(dataframe['k'], self.buy_stoch.value)) &
        # (dataframe['stoch'] <= self.buy_stoch.value) &
        # (dataframe['rsi'] >= 50) &
        # (dataframe['d'] > self.sell_stoch.value) & (dataframe['k'] > self.sell_stoch.value) &
        # self.stoch_check(dataframe, self.check_range, True) &
        # self.macd_check(dataframe, self.check_range, True)
        # (qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']))

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
        # qtpylib.crossed_above(dataframe['PSARUp'], 0)
        # (qtpylib.crossed_above(dataframe['d'], self.sell_stoch.value)) &
        # (qtpylib.crossed_above(dataframe['k'], self.sell_stoch.value)) &
        # (dataframe['stoch'] >= self.sell_stoch.value) &
        # (dataframe['rsi'] < 50) &
        # self.stoch_check(dataframe, self.check_range, False) &
        #  (dataframe['d'] > self.sell_stoch.value) & (dataframe['k'] > self.sell_stoch.value) &
        # self.macd_check(dataframe, self.check_range, False)
        # (qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']))

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

    def entry_cooldown(self, dataframe: DataFrame, check_range: int) -> bool:
        for x in range(check_range):
            if (dataframe['enter_long'].shift(x)).any():
                return False
        return True

    def macd_check(self, dataframe: DataFrame, check_range: int, buy_signal: bool) -> Series:
        series = pandas.Series(dtype="float64")
        if buy_signal:
            for x in range(check_range):
                pandas.concat([series, qtpylib.crossed_above(dataframe['macd'].shift(x), dataframe['macdsignal'].shift(x))])
        else:
            for x in range(check_range):
                pandas.concat([series, qtpylib.crossed_below(dataframe['macd'].shift(x), dataframe['macdsignal'].shift(x))])
        return series

    def stoch_check(self, dataframe: DataFrame, check_range: int, buy_signal: bool) -> Series:
        series = pandas.Series(dtype="float64")
        if buy_signal:
            for x in range(check_range):
                pandas.concat([series, qtpylib.crossed_below(dataframe['stoch'].shift(x), self.buy_stoch.value)])
        else:
            for x in range(check_range):
                pandas.concat([series, qtpylib.crossed_above(dataframe['stoch'].shift(x), self.sell_stoch.value)])
        return series

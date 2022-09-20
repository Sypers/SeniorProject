# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# EDIT TEST
# --- Do not remove these libs ---
from datetime import datetime  # noqa
from typing import Optional, Union  # noqa

import numpy as np  # noqa
import pandas as pd  # noqa
import pandas.core.generic
from ta.momentum import StochRSIIndicator
from ta.trend import SMAIndicator
import ta.utils
from pandas import DataFrame  # noqa

# --------------------------------
# Add your lib to import here
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.strategy import (DecimalParameter,
                                IStrategy)


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
    sell_stoch = DecimalParameter(0.7, 1, default=0.98, space="sell")
    check_range = 2
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
        macd = ta.trend.MACD(dataframe['close'])
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
        # dataframe.loc[
        #     (
        #         (dataframe['ema200'] < dataframe['close']) &
        #         (dataframe['engulfing'] == 100) &  # Bullish engulfing detected
        #         (qtpylib.crossed_above(dataframe['close'], dataframe['ema23'])) |
        #         (qtpylib.crossed_above(dataframe['close'], dataframe['ema38']))
        #     ),
        #     'enter_long'] = 1

        #  print("UP INDICATOR: ", dataframe['PSARUp'].sum())
        dataframe.loc[
            (
                # qtpylib.crossed_above(dataframe['PSARDown'], 0)
                     #(qtpylib.crossed_below(dataframe['d'], self.buy_stoch.value)) &
                     #(qtpylib.crossed_below(dataframe['k'], self.buy_stoch.value)) &
                (dataframe['rsi'] > 50) &
                self.stoch_check(dataframe, self.check_range, True) &
                self.macd_check(dataframe, self.check_range, True)
                # (qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']))
            )
            , 'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """
        #  print("DOWN INDICATOR: ", dataframe['PSARDown'].sum())
        dataframe.loc[
            (
                # qtpylib.crossed_above(dataframe['PSARUp'], 0)
                #(qtpylib.crossed_above(dataframe['d'], self.buy_stoch.value)) &
                #(qtpylib.crossed_above(dataframe['k'], self.buy_stoch.value)) &
                (dataframe['rsi'] < 50) &
                self.stoch_check(dataframe, self.check_range, True) &
                self.macd_check(dataframe, self.check_range, True)
                # (qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']))
            ),
            'exit_long'] = 1
        return dataframe

    #
    def fibonnaci_retractment(self, dataframe: DataFrame, length: int) -> DataFrame:
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

    def macd_check(self, dataframe: DataFrame, check_range: int, buy_signal: bool) -> bool:
        if buy_signal:
            for x in range(check_range):
                if (qtpylib.crossed_above(dataframe['macd'].shift(x), dataframe['macdsignal'].shift(x))).any():
                    return True
        else:
            for x in range(check_range):
                if qtpylib.crossed_below(dataframe['macd'].shift(x), dataframe['macdsignal'].shift(x)).any():
                    return True
        return False

    def stoch_check(self, dataframe: DataFrame, check_range: int, buy_signal: bool) -> bool:
        if buy_signal:
            for x in range(check_range):
                if ((qtpylib.crossed_above(dataframe['d'].shift(x), self.buy_stoch.value)) & (qtpylib.crossed_above(dataframe['k'].shift(x), self.buy_stoch.value))).any():
                    return True
        else:
            for x in range(check_range):
                if ((qtpylib.crossed_below(dataframe['d'].shift(x), self.sell_stoch.value)) & (qtpylib.crossed_below(dataframe['k'].shift(x), self.buy_stoch.value))).any():
                    return True
        return False

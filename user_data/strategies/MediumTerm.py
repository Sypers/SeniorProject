# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# --- Do not remove these libs ---
from datetime import datetime  # noqa
from typing import Optional, Union  # noqa
import numpy as np  # noqa
import pandas as pd  # noqa
import ta.utils
from pandas import DataFrame, Series  # noqa
from ta.momentum import StochRSIIndicator
from ta.trend import SMAIndicator

# --------------------------------
# Add your lib to import here
import freqtrade.vendor.qtpylib.indicators as qtpylib
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
    startup_candle_count: int = 21

    # Strategy/Hyperopt parameters
    # Using the strategy for backtesting or trading will only take the default value.
    # the value the stochastic indicator has to reach for a buy signal.
    buy_stoch = DecimalParameter(0.05, 0.3, default=0.255, space="buy")
    # the value the stochastic indicator has to reach for a sell signal.
    sell_stoch = DecimalParameter(0.7, 1, default=0.731, space="sell")
    # value for the amount of candles to ignore buy signals from after a trade sell.
    candle_cooldown = IntParameter(0, 5, default=0, space="protection")
    # enable or disable RSI buy signal.
    enable_buy_rsi = BooleanParameter(default=True, space="buy", optimize=False)
    # enable or disable Stochastic buy signal.
    enable_buy_stoch = BooleanParameter(default=True, space="buy", optimize=False)
    # enable or disable MACD buy signal.
    enable_buy_macd = BooleanParameter(default=True, space="buy")
    # enable or disable RSI sell signal.
    enable_sell_rsi = BooleanParameter(default=True, space="sell", optimize=False)
    # enable or disable Stochastic sell signal.
    enable_sell_stoch = BooleanParameter(default=True, space="sell", optimize=False)
    # enable or disable MACD sell signal.
    enable_sell_macd = BooleanParameter(default=True, space="sell")
    check_range = 2  # the value for number of candles to check for stoch_check and macd_check methods.

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
        dataframe['rsi'] = rsi.rsi()
        dataframe['macd'] = macd.macd()
        dataframe['macdsignal'] = macd.macd_signal()
        dataframe['stoch_buy'] = self.stoch_check(dataframe, True)
        dataframe['stoch_sell'] = self.stoch_check(dataframe, False)
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
        # locate the row which meets these conditions:
        dataframe.loc[
            (
                # RSI value is more than 50 means a bullish (up) trend
                (dataframe['rsi'] >= 50) &
                # check if there is stochasticRSI buy signal in the previous 3 rows/candles
                ((dataframe['stoch_buy']) | dataframe['stoch_buy'].shift() | dataframe['stoch_buy'].shift(2)
                 | dataframe['stoch_buy'].shift(3)) &
                # check if the MACD value crossed above the MACD Signal value within 2 rows
                (qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']))
            ), 'enter_long'] = 1  # issue a buy signal if a row is located with all conditions met
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """
        # locate the row which meets these conditions:
        dataframe.loc[(
                        # RSI value is less than 50 means a bearish (down) trend
                        (dataframe['rsi'] < 50) &
                        # check if there is stochasticRSI sell signal in the previous 3 rows/candles
                        ((dataframe['stoch_sell']) | (dataframe['stoch_sell'].shift()) | (dataframe['stoch_sell']).shift(2)) &
                        # check if the MACD value crossed below the MACD Signal value within 2 rows
                        (qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']))
                      ), 'exit_long'] = 1  # issue a sell signal if a row is located with all conditions met
        return dataframe

    def stoch_check(self, dataframe: DataFrame, buy_signal: bool) -> Series:
        """
        Check the dataframe for Stochastic crossover with stochastic buy and sell values.
        :param dataframe: Dataframe that contains the pair data including the indicators data.
        :param buy_signal: True to check for buy signals, False to check for sell signals of the indicator.
        :return: A pandas Series that includes the rows where Stochastic crossed with Stochastic buy or sell values
        """
        if buy_signal:
            series = qtpylib.crossed_below(dataframe['stoch'], self.buy_stoch.value)
        else:
            series = qtpylib.crossed_above(dataframe['stoch'], self.sell_stoch.value)
        return series

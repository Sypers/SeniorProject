
# --- Do not remove these libs ---
import ta.trend
import ta.utils
from pandas import DataFrame
from freqtrade.strategy import IStrategy
import freqtrade.vendor.qtpylib.indicators as qtpylib

# --------------------------------


class ShortTerm(IStrategy):

    INTERFACE_VERSION: int = 3
    # Minimal ROI designed for the strategy.
    # adjust based on market conditions. We would recommend to keep it low for quick turn arounds
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "20": 0.001,
        "10": 0.002,
        "5": 0.004,
        "0": 0.005
    }

    # Optimal stoploss designed for the strategy
    stoploss = -0.003

    # Optimal timeframe for the strategy
    timeframe = '1m'

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        MACD = ta.trend.MACD(close=dataframe['close'], window_slow=8, window_fast=5)
        PSAR = ta.trend.PSARIndicator(close=dataframe['close'], high=dataframe['high'], low=dataframe['low'])
        MA = ta.trend.SMAIndicator(dataframe['close'], 100)
        # dataframe['macd'] = MACD.macd()
        dataframe['macdhist'] = MACD.macd_diff()
        dataframe['psar_up'] = PSAR.psar_up_indicator()
        dataframe['psar_down'] = PSAR.psar_down_indicator()
        dataframe['sma'] = MA.sma_indicator()
        dataframe['smasmooth'] = ta.trend.SMAIndicator(dataframe['sma'], 10).sma_indicator()
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['psar_up'] == 1) &
                (dataframe['macdhist'] > 0) &
                (qtpylib.crossed_above(dataframe['close'], dataframe['sma'])) &
                (dataframe['sma'] > dataframe['smasmooth'])
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['psar_down'] == 1) &
                    (dataframe['macdhist'] < 0) *
                    (qtpylib.crossed_below(dataframe['close'], dataframe['sma'])) &
                    (dataframe['sma'] < dataframe['smasmooth'])
            ),
            'exit_long'] = 1
        return dataframe

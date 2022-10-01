# --- Do not remove these libs ---
import ta.trend
import ta.utils
import ta.momentum
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

    # Trailing stoploss
    trailing_stop = False
    trailing_stop_positive = 0.012
    trailing_stop_positive_offset = 0.092
    trailing_only_offset_is_reached = False

    # Can this strategy go short?
    can_short = False

    # Optimal stoploss designed for the strategy
    stoploss = -0.003

    # Optimal timeframe for the strategy
    timeframe = '1m'

    # Strategy Parameters
    buy_stoch = 23.0
    sell_stoch = 77.0

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        MACD = ta.trend.MACD(close=dataframe['close'], window_slow=8, window_fast=5)
        PSAR = ta.trend.PSARIndicator(close=dataframe['close'], high=dataframe['high'], low=dataframe['low'])
        MA = ta.trend.SMAIndicator(dataframe['close'], 100)
        Stoch = ta.momentum.StochasticOscillator(high=dataframe['high'], low=dataframe['low'], close=dataframe['close'])
        # dataframe['macd'] = MACD.macd()
        dataframe['sma'] = MA.sma_indicator()
        dataframe['macdhist'] = MACD.macd_diff()
        dataframe['psar_up'] = PSAR.psar_up_indicator()
        dataframe['psar_down'] = PSAR.psar_down_indicator()
        dataframe['stoch'] = Stoch.stoch()
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['psar_up'] == 1) &
                    (dataframe['macdhist'] > 0) &
                    #  (qtpylib.crossed_above(dataframe['close'], dataframe['sma'])) &
                    (dataframe['stoch'] < self.buy_stoch)
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['psar_down'] == 1) &
                    (dataframe['macdhist'] < 0) &
                    #  (qtpylib.crossed_below(dataframe['close'], dataframe['sma'])) &
                    (dataframe['stoch'] > self.sell_stoch)),
            'exit_long'] = 1
        return dataframe

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

    # Strategy Default values
    BUY_RSI_DEF = 20
    SELL_RSI_DEF = 80
    # Minimal ROI designed for the strategy.
    # adjust based on market conditions. We would recommend to keep it low for quick turn arounds
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "60": 0.002,
        "30": 0.004,
        "15": 0.006,
        "0": 0.009
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
    stoploss = -0.003

    # Optimal timeframe for the strategy
    timeframe = '5m'

    # Strategy Parameters
    # buy_stoch = DecimalParameter(1, 33, default=BUY_STOCH_DEF)
    # sell_stoch = DecimalParameter(67, 100, default=SELL_STOCH_DEF)
    buy_rsi = IntParameter(1, 34, default=BUY_RSI_DEF)
    sell_rsi = IntParameter(66, 100, default=SELL_RSI_DEF)

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # MACD = ta.trend.MACD(close=dataframe['close'], window_slow=8, window_fast=5)
        # Stoch = ta.momentum.StochasticOscillator(high=dataframe['high'], low=dataframe['low'], close=dataframe['close'])
        ATR = ta.volatility.AverageTrueRange(dataframe['high'], dataframe['low'], dataframe['close'])
        # MA = ta.trend.SMAIndicator(dataframe['close'], window=50)
        RSI = ta.momentum.RSIIndicator(dataframe['close'], window=2)
        EMA200 = ta.trend.EMAIndicator(dataframe['close'], window=200)
        EMA50 = ta.trend.EMAIndicator(dataframe['close'], window=50)
        # Appending indicator results to new dataframe columns
        dataframe['atr'] = ATR.average_true_range()
        # dataframe['macdhist'] = MACD.macd_diff()
        # dataframe['stoch'] = Stoch.stoch()
        # dataframe['ma'] = MA.sma_indicator()
        dataframe['rsi'] = RSI.rsi()
        dataframe['ema200'] = EMA200.ema_indicator()
        dataframe['ema50'] = EMA50.ema_indicator()
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['ema50'] > dataframe['ema200']) &
                    (dataframe['close'] > dataframe['ema200']) &
                    (qtpylib.crossed_below(dataframe['rsi'], self.BUY_RSI_DEF))
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['ema50'] < dataframe['ema200']) &
                    (dataframe['close'] < dataframe['ema200']) &
                    (qtpylib.crossed_above(dataframe['rsi'], self.SELL_RSI_DEF))
            ),
            'exit_long'] = 1
        return dataframe

    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime, current_rate: float,
                        current_profit: float, **kwargs) -> float:
        if current_time - timedelta(minutes=60) > trade.open_date_utc:
            return -0.0025
        elif current_time - timedelta(minutes=30) > trade.open_date_utc:
            return -0.005
        elif current_time - timedelta(minutes=15) > trade.open_date_utc:
            return -0.007
        return 1

    def custom_exit(self, pair: str, trade: Trade, current_time: datetime, current_rate: float,
                    current_profit: float, **kwargs) -> Optional[Union[str, bool]]:
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()

        if current_profit > 0.005:
            if (last_candle['rsi'] < self.SELL_RSI_DEF) | (last_candle['atr'] >= 55):
                return 'volatility_escape'
        if 0.0001 < current_profit < 0.0005:
            if last_candle['ema50'] <= last_candle['ema200']:
                return 'ema_cross_sell'

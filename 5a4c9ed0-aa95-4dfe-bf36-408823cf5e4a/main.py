from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["GFAI", "PLUG", "OPTT", "GFS", "DDD", "NAT", "LXFR", "PSHG", "SKYT", "HAL"]
        self.entry_prices = {ticker: None for ticker in self.tickers}
        self.sell_flags = {ticker: {5: False, 10: False} for ticker in self.tickers}
        self.holdings_core = 0.3
        self.sell_levels = {5: 0.1, 10: 0.2}  # Smaller scale-outs for micro caps

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1day"

    def run(self, data):
        allocation_dict = {}
        rsi_period = 14

        for ticker in self.tickers:
            try:
                current_price = data["ohlcv"][-1][ticker]["close"]
                rsi_value = RSI(ticker, data["ohlcv"], rsi_period)[-1]
                price_low_3d = min([bar["low"] for bar in data["ohlcv"][-3:]])
            except:
                log(f"Missing data for {ticker}, skipping.")
                continue

            # Entry condition: RSI < 35 and price bounce from recent low
            if rsi_value < 35 and current_price > price_low_3d:
                if not self.entry_prices[ticker]:
                    allocation_dict[ticker] = self.holdings_core
                    self.entry_prices[ticker] = current_price
                    self.sell_flags[ticker] = {5: False, 10: False}
                    log(f"Buying {ticker} at {current_price}")
                else:
                    allocation_dict[ticker] = self.holdings_core

            # Scale-out logic
            if self.entry_prices[ticker] is not None:
                profit_pct = (current_price - self.entry_prices[ticker]) / self.entry_prices[ticker] * 100
                allocation = allocation_dict.get(ticker, self.holdings_core)
                for level, sell_pct in self.sell_levels.items():
                    if profit_pct >= level and not self.sell_flags[ticker][level]:
                        allocation -= sell_pct
                        self.sell_flags[ticker][level] = True
                        log(f"Scaling out {sell_pct*100}% of {ticker} at +{level}%")
                allocation_dict[ticker] = max(0, allocation)

            # Stop-loss condition
            if self.entry_prices[ticker] and current_price < self.entry_prices[ticker] * 0.93:
                allocation_dict[ticker] = 0
                log(f"Stop-loss triggered for {ticker} at {current_price}")
                self.entry_prices[ticker] = None
                self.sell_flags[ticker] = {5: False, 10: False}

            # Default allocation if no action
            if ticker not in allocation_dict:
                allocation_dict[ticker] = self.holdings_core if self.entry_prices[ticker] else 0

        return TargetAllocation(allocation_dict)
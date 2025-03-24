from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, MFI
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["BBAI", "SOUN", "SKYT", "INTC", "PLTR", "NVDA", "AMCR", "GFAI", "DDD", "OPIT", "QBTS"]
        self.entry_prices = {ticker: None for ticker in self.tickers}
        self.sell_flags = {ticker: {10: False, 20: False, 30: False} for ticker in self.tickers}
        self.holdings_core = 0.5
        self.sell_levels = {10: 0.15, 20: 0.15, 30: 0.15}

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1day"

    def run(self, data):
        allocation_dict = {}
        rsi_period = 14
        mfi_period = 14

        for ticker in self.tickers:
            current_price = data["ohlcv"][-1][ticker]["close"]
            rsi_value = RSI(ticker, data["ohlcv"], rsi_period)[-1]
            mfi_current = MFI(ticker, data["ohlcv"], mfi_period)[-1]
            mfi_previous = MFI(ticker, data["ohlcv"], mfi_period)[-2]

            # Entry or Rebuy Condition
            if rsi_value < 30 and mfi_current > mfi_previous:
                if not self.entry_prices[ticker]:
                    allocation_dict[ticker] = self.holdings_core
                    self.entry_prices[ticker] = current_price
                    self.sell_flags[ticker] = {10: False, 20: False, 30: False}
                    log(f"Buying {ticker} at {current_price}")
                else:
                    allocation_dict[ticker] = self.holdings_core

            # Scale-out Logic
            if self.entry_prices[ticker] is not None:
                profit_pct = (current_price - self.entry_prices[ticker]) / self.entry_prices[ticker] * 100
                allocation = allocation_dict.get(ticker, self.holdings_core)
                for level, sell_pct in self.sell_levels.items():
                    if profit_pct >= level and not self.sell_flags[ticker][level]:
                        allocation -= sell_pct
                        self.sell_flags[ticker][level] = True
                        log(f"Scaling out {sell_pct*100}% of {ticker} at +{level}%")
                allocation_dict[ticker] = max(0, allocation)

            # Stop-Loss Logic
            if self.entry_prices[ticker] and current_price < self.entry_prices[ticker] * 0.9:
                allocation_dict[ticker] = 0
                log(f"Stop-loss triggered for {ticker} at {current_price}")
                self.entry_prices[ticker] = None
                self.sell_flags[ticker] = {10: False, 20: False, 30: False}

            # Ensure allocation is defined
            if ticker not in allocation_dict:
                allocation_dict[ticker] = self.holdings_core if self.entry_prices[ticker] else 0

        return TargetAllocation(allocation_dict)
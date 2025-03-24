from surmount.base_class import Strategy, TargetAllocation
from surmount.data import OHLCV

class TradingStrategy(Strategy):
    def __init__(self):
        self.ticker = "BBAI"
        self.cost_basis = 2.59  # Average purchase price or cost basis of the stock

    @property
    def assets(self):
        return [self.ticker]

    @property
    def interval(self):
        return "1day"

    def run(self, data):
        current_price = data["ohlcv"][-1][self.ticker]["close"]  # Latest close price
        allocation = 1.0

        # Scale out as price increases
        if current_price >= self.cost_basis + 5.00:
            allocation = 0.5  # Cap at 50%
        elif current_price >= self.cost_basis + 3.50:
            allocation = 0.55
        elif current_price >= self.cost_basis + 2.00:
            allocation = 0.70
        elif current_price > self.cost_basis:  # Avoids selling before reaching the cost basis
            allocation = 0.85

        # Scale out as price decreases
        if current_price <= 1.80:
            allocation = 0.55
        elif current_price <= 2.00:
            allocation = 0.70
        elif current_price <= 2.20:
            allocation = 0.85
        if current_price < 1.50:
            allocation = 0.5  # Cap at 50% for lower bound as well

        # Ensuring the allocation is within logical bounds
        allocation = max(0.5, min(1, allocation))  # Ensures allocation stays within 50%-100%

        return TargetAllocation({self.ticker: allocation})
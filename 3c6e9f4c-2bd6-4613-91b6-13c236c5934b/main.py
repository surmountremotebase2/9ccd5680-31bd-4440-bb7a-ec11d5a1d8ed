from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the asset and initial thresholds for stop loss and take profit
        self.asset = "XYZ"
        self.stop_loss_price = 95.0  # Trigger sell if price drops to this level or below
        self.take_profit_price = 110.0 # Trigger buy if price rises to this level or above

    @property
    def assets(self):
        # The assets that the strategy will trade
        return [self.asset]

    @property
    def interval(self):
        # The time interval for price checking
        return "1day"

    def run(self, data):
        # Fetch the latest close price of the asset
        latest_close_price = data["ohlcv"][-1][self.asset]["close"]
        log(f"Latest close price of {self.asset}: {latest_close_price}")

        # Default to holding (no change)
        allocation_dict = {self.asset: 0}

        # If the latest close price is below the stop loss price, trigger a sell by setting allocation to 0
        if latest_close_price <= self.stop_loss_price:
            log(f"Triggering sell for {self.asset} due to stop loss")
            allocation_dict[self.asset] = 0  # Sell all holdings
            
        # If the latest close price is above the take profit price, trigger a buy by setting allocation higher
        elif latest_close_price >= self.take_profit_price:
            log(f"Triggering buy for {self.asset} due to take profit opportunity")
            allocation_dict[self.asset] = 1  # Buy or maintain a full position
        
        # Return the allocation decision
        return TargetAllocation(allocation_dict)
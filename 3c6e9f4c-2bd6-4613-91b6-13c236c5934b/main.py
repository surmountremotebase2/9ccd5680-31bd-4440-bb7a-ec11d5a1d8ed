from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the assets and initial thresholds for stop loss and take profit
        self.asset_list = ["BBAI", "SOUN", "DNN", "NVDA", "ACMR", "INTC"]
        self.stop_loss_price = 95.0    # Trigger sell if price drops to this level or below
        self.take_profit_price = 110.0 # Trigger buy if price rises to this level or above

    @property
    def assets(self):
        # The assets that the strategy will trade
        return self.asset_list

    @property
    def interval(self):
        # The time interval for price checking
        return "1day"

    def run(self, data):
        allocation_dict = {}

        for asset in self.asset_list:
            try:
                latest_close_price = data["ohlcv"][-1][asset]["close"]
                log(f"Latest close price of {asset}: {latest_close_price}")

                if latest_close_price <= self.stop_loss_price:
                    log(f"Triggering sell for {asset} due to stop loss")
                    allocation_dict[asset] = 0

                elif latest_close_price >= self.take_profit_price:
                    log(f"Triggering buy for {asset} due to take profit opportunity")
                    allocation_dict[asset] = 1

                else:
                    allocation_dict[asset] = 0  # Hold / No position change

            except KeyError:
                log(f"Data not available for {asset}, skipping.")
                allocation_dict[asset] = 0  # Safe default

        return TargetAllocation(allocation_dict)
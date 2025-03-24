from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.asset_thresholds = {
            "BBAI": {"stop": 2.5, "target": 4.5},
            "SOUN": {"stop": 8.0, "target": 12.0},
            "DNN":  {"stop": 1.0, "target": 2.0},
            "NVDA": {"stop": 95.0, "target": 115.0},
            "ACMR": {"stop": 20.0, "target": 35.0},
            "INTC": {"stop": 22.0, "target": 30.0}
        }
        self.asset_list = list(self.asset_thresholds.keys())

    @property
    def assets(self):
        return self.asset_list

    @property
    def interval(self):
        return "1day"

    def run(self, data):
        allocation_dict = {}

        for asset in self.asset_list:
            try:
                close = data["ohlcv"][-1][asset]["close"]
                t = self.asset_thresholds[asset]
                stop, target = t["stop"], t["target"]

                log(f"[{asset}] Price: {close} | Stop: {stop} | Target: {target}")

                # ↓↓↓ Moderate sell (profit-taking) tiers
                if close >= target * 1.10:
                    allocation = 0.25
                    log(f"[{asset}] Price well above target — trimming to 25%.")
                elif close >= target:
                    allocation = 0.5
                    log(f"[{asset}] Target reached — trimming to 50%.")
                elif close >= target * 0.90:
                    allocation = 0.75
                    log(f"[{asset}] Approaching target — light trim to 75%.")

                # ↑↑ Rebuy or hold tiers
                elif close <= stop * 0.90:
                    allocation = 0.25
                    log(f"[{asset}] Sharp drop below stop — rebuying 25%.")
                elif close <= stop:
                    allocation = 0.5
                    log(f"[{asset}] Hit stop — partial sell to 50%.")
                elif close <= stop * 1.05:
                    allocation = 0.75
                    log(f"[{asset}] Mild drop near stop — rebalancing to 75%.")
                else:
                    allocation = 1.0
                    log(f"[{asset}] Stable — holding full position.")

                allocation_dict[asset] = allocation

            except KeyError:
                log(f"[{asset}] Missing data — skipping.")
                allocation_dict[asset] = 0

        return TargetAllocation(allocation_dict)
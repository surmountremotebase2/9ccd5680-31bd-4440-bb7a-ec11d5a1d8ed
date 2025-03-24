from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Thresholds for all assets
        self.asset_thresholds = {
            "BBAI": {
                "avg_cost": 2.59,
                "scale_up_levels": [4.59, 6.09, 7.59],  # $2, $3.5, $5 above cost
                "scale_down_levels": [2.20, 2.00, 1.80],  # $0.40, $0.60, $0.80 drop
            },
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
                log(f"[{asset}] Close: {close}")

                # Slow scale logic for BBAI only
                if asset == "BBAI":
                    thresholds = self.asset_thresholds[asset]
                    allocation = 1.0  # Start fully allocated

                    # Scale out on price increase
                    if close >= thresholds["scale_up_levels"][2]:
                        allocation = 0.55
                        log(f"[{asset}] +$5 above cost — scaling to 55%.")
                    elif close >= thresholds["scale_up_levels"][1]:
                        allocation = 0.70
                        log(f"[{asset}] +$3.5 above cost — scaling to 70%.")
                    elif close >= thresholds["scale_up_levels"][0]:
                        allocation = 0.85
                        log(f"[{asset}] +$2 above cost — scaling to 85%.")

                    # Scale down on price drops
                    elif close <= thresholds["scale_down_levels"][2]:
                        allocation = 0.55
                        log(f"[{asset}] Sharp drop — trimming to 55%.")
                    elif close <= thresholds["scale_down_levels"][1]:
                        allocation = 0.70
                        log(f"[{asset}] Moderate drop — trimming to 70%.")
                    elif close <= thresholds["scale_down_levels"][0]:
                        allocation = 0.85
                        log(f"[{asset}] Minor drop — trimming to 85%.")

                    else:
                        allocation = 1.0  # Hold fully

                    allocation_dict[asset] = allocation

                # Use default logic for other assets
                else:
                    t = self.asset_thresholds[asset]
                    stop, target = t["stop"], t["target"]

                    if close >= target * 1.10:
                        allocation = 0.25
                    elif close >= target:
                        allocation = 0.5
                    elif close >= target * 0.90:
                        allocation = 0.75
                    elif close <= stop * 0.90:
                        allocation = 0.25
                    elif close <= stop:
                        allocation = 0.5
                    elif close <= stop * 1.05:
                        allocation = 0.75
                    else:
                        allocation = 1.0

                    allocation_dict[asset] = allocation

            except KeyError:
                log(f"[{asset}] Missing data — skipping.")
                allocation_dict[asset] = 0

        return TargetAllocation(allocation_dict)
#!/usr/bin/env python
"""
Converted from: ch5_fx.ipynb

This script demonstrates rateslib functionality.
Run from the python/ directory to ensure imports work correctly.
"""

import sys
import os

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')


from rateslib.fx import FXRates, FXForwards
from rateslib.dual import Dual
from rateslib.curves import Curve
from datetime import datetime as dt



#======================================================================
# Chapter 5 - FX Rates
#======================================================================
#

#======================================================================
# Unsuitable initialisation
#======================================================================


FXRates({"usdeur": 1.0, "noksek":1.0})


FXRates({"usdeur": 1.0, "gbpusd":1.0, "gbpeur": 1.0})


FXRates({"usdeur": 1.0, "eurusd":1.0, "noksek": 1.0})



#======================================================================
# FX Rates Array
#======================================================================
#
#


fxr = FXRates({"usdeur": 2.0, "usdgbp": 2.5})
fxr.rates_table()


fxr.rate("eurgbp")



#======================================================================
# Representation via Dual
#======================================================================


fxr = FXRates({"usdnok": 8.0})
fxr.convert(1000000, "nok", "usd")



#======================================================================
# Equivalence of Cash Positions and Base Value
#======================================================================


fxr.currencies


base_value = fxr.convert_positions([0, 1000000], "usd")
base_value


positions = fxr.positions(base_value, "usd")
positions


# Introduce a third currency


fxr = FXRates({"usdeur": 0.9, "eurnok": 8.888889})
fxr.currencies


base_value = fxr.convert_positions([0, 0, 1000000], "usd")
base_value


fxr.positions(base_value, "usd")


base_value = Dual(125000, "fx_usdnok", [-15625])
positions = fxr.positions(base_value, "usd")
positions


fxr.convert_positions(positions, "usd")



#======================================================================
# Re-expression in Majors
#======================================================================


fxr_crosses = FXRates({"eurusd": 1.0, "gbpjpy": 100, "eurjpy": 100})
fxr_crosses.convert(1, "usd", "jpy")


fxr_majors = fxr_crosses.restate(["eurusd", "usdjpy", "gbpusd"])
fxr_majors.convert(1, "usd", "jpy")



#======================================================================
# FX Forwards
#======================================================================


fx_rates = FXRates({"usdeur": 0.9, "eurnok": 8.888889}, dt(2022, 1, 3))
fx_curves = {
    "usdusd": Curve({dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.96}),
    "eureur": Curve({dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.99}),
    "eurusd": Curve({dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.991}),
    "noknok": Curve({dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.98}),
    "nokeur": Curve({dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.978}),
}
fxf = FXForwards(fx_rates, fx_curves)
fxf.rate("usdnok", dt(2022, 8, 15))



#======================================================================
# Equivalence of Delta Risk
#======================================================================


fx_rates = FXRates({"usdeur": 0.9, "eurnok": 8.888889}, dt(2022, 1, 3))
start, end = dt(2022, 1, 1), dt(2023, 1,1)
fx_curves = {
    "usdusd": Curve({start: 1.0, end: 0.96}, id="uu", ad=1),
    "eureur": Curve({start: 1.0, end: 0.99}, id="ee", ad=1),
    "eurusd": Curve({start: 1.0, end: 0.991}, id="eu", ad=1),
    "noknok": Curve({start: 1.0, end: 0.98}, id="nn", ad=1),
    "nokeur": Curve({start: 1.0, end: 0.978}, id="ne", ad=1),
}
fxf = FXForwards(fx_rates, fx_curves)


discounted_nok = fx_curves["nokeur"][dt(2022, 8, 15)] * 1000
base_value = discounted_nok * fxf.rate("nokusd", dt(2022, 1, 1))
base_value


forward_eur = fxf.rate("nokeur", dt(2022, 8, 15)) * 1000
discounted_eur = forward_eur * fx_curves["eureur"][dt(2022, 8, 15)]
base_value = discounted_eur * fxf.rate("eurusd", dt(2022, 1, 1))
base_value


base_value.gradient(["uu1", "ee1", "eu1", "nn1", "ne1", "fx_usdeur", "fx_eurnok"])




#======================================================================
# Combining Settlement Dates
#======================================================================
#

#======================================================================
# Separable system
#======================================================================


fxr1 = FXRates({"eurusd": 1.05}, settlement=dt(2022, 1, 3))
fxr2 = FXRates({"usdcad": 1.1}, settlement=dt(2022, 1, 2))
fxf = FXForwards(
    fx_rates=[fxr1, fxr2],
    fx_curves={
        "usdusd": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "eureur": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "cadcad": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "usdeur": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "cadusd": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
    }
)


fxf.rate("eurcad", dt(2022, 2, 1))



#======================================================================
# Acyclic Dependent Systems
#======================================================================


fxf = FXForwards(
    fx_rates=[fxr1, fxr2],
    fx_curves={
        "usdusd": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "eureur": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "cadcad": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "usdeur": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "cadeur": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
    }
)


fxf.rate("eurcad", dt(2022, 2, 1))



#======================================================================
# Cyclic Dependent Systems Fail
#======================================================================


fxr1 = FXRates({"eurusd": 1.05, "gbpusd": 1.25}, settlement=dt(2022, 1, 3))
fxf = FXForwards(
    fx_rates=[fxr1, fxr2],
    fx_curves={
        "usdusd": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "eureur": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "cadcad": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "usdeur": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "cadeur": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "gbpcad": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "gbpgbp": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
    }
)


# But cyclic systems can be restructured


fxr1 = FXRates({"eurusd": 1.05}, settlement=dt(2022, 1, 3))
fxr3 = FXRates({"gbpusd": 1.25}, settlement=dt(2022, 1, 3))
fxf = FXForwards(
    fx_rates=[fxr1, fxr2, fxr3],
    fx_curves={
        "usdusd": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "eureur": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "cadcad": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "usdeur": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "cadeur": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "gbpcad": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "gbpgbp": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
    }
)


fxf.rate("eurcad", dt(2022, 2, 1))



#======================================================================
# Unsolvable System
#======================================================================


fxr1 = FXRates({"eurusd": 1.05, "gbpusd": 1.25}, settlement=dt(2022, 1, 3))
fxr3 = FXRates({"gbpjpy": 100}, settlement=dt(2022, 1, 4))
FXForwards(
    fx_rates=[fxr1, fxr2, fxr3],
    fx_curves={
        "usdusd": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "eureur": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "cadcad": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "gbpgbp": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "usdjpy": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "eurcad": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "eurjpy": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "gbpcad": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
    }
)



#======================================================================
# Dual Representation
#======================================================================


fxr1 = FXRates({"eurusd": 1.05}, settlement=dt(2022, 1, 3))
fxr2 = FXRates({"usdcad": 1.1}, settlement=dt(2022, 1, 2))
fxf = FXForwards(
    fx_rates=[fxr1, fxr2],
    fx_curves={
        "usdusd": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "eureur": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "cadcad": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "usdeur": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
        "cadusd": Curve({dt(2022, 1, 1):1.0, dt(2022, 2, 1): 0.999}),
    }
)
pv = Dual(100000, ["fx_eurusd", "fx_usdcad"], [-100000, -150000])
fxf.positions(pv, base="usd")


fxf.positions(pv, base="usd", aggregate=True)


fxf.convert_positions(fxf.positions(pv, base="usd"))


if __name__ == "__main__":
    print("Script completed successfully!")
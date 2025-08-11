#!/usr/bin/env python
"""
Converted from: FXRates.ipynb

This script demonstrates rateslib functionality.
Run from the python/ directory to ensure imports work correctly.
"""

import sys
import os

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')


from rateslib import FXRates, FXForwards, Dual, dt, Curve, gradient
import numpy as np



#======================================================================
# Defined FXRates Systems - Errors
#======================================================================


try:
    FXRates(fx_rates={"usdeur": 0.9, "noksek": 1.10})
except ValueError as e:
    print(e)


try:
    FXRates(fx_rates={"usdeur": 0.9, "gbpusd": 1.10, "eurgbp": 1.124})
except ValueError as e:
    print(e)


try:
    FXRates ( fx_rates ={" usdeur ": 0.90 , " eurusd ": 1.11 , " noksek ": 1.10})
except ValueError as e:
    print(e)



#======================================================================
# FXRates Array
#======================================================================


fxr = FXRates({"usdeur": 2.0, "usdgbp": 2.5})
from rateslib.dual.utils import _dual_float
np.reshape([_dual_float(_) for _ in fxr.fx_array.ravel()], (3,3))


fxr.rate("eurgbp")



#======================================================================
# Representation via Dual
#======================================================================


1e6  * (1/8.0)


fxr = FXRates({"usdnok": 8.0})
fxr.convert(1e6, "nok", "usd")


fxr._set_ad_order(2)
fxr.convert(1e6, "nok", "usd")



#======================================================================
# Cash positions and base value
#======================================================================


fxr = FXRates({"usdnok": 8.0})
fxr.currencies


# convert cash positions into an aggregated NOK value
base_nok_value = fxr . convert_positions ([0 , 1000000] , "nok")
base_nok_value


# Convert cash positions into an aggregated USD value
base_usd_value = fxr.convert_positions ([0 , 1000000] , "usd")
base_usd_value


# Convert an aggregated USD value back to cash positions
positions = fxr.positions(base_usd_value , "usd")
positions



#======================================================================
# Introducing additional currency exposures
#======================================================================


fxr = FXRates ({"usdeur": 0.9 , "eurnok ": 8.888889})
fxr.currencies


base_value = fxr.convert_positions ([0 , 0, 1000000] , "usd")
base_value


positions = fxr.positions(base_value, "usd")
positions


base_usd_value = Dual(125000 , ["fx_usdnok"], [-15625])
positions = fxr.positions(base_usd_value, "usd")
positions


fxr.convert_positions(positions, "usd")



#======================================================================
# Re-expression in Majors or Crosses
#======================================================================


fxr_crosses = FXRates({"eurusd": 1.0 , "gbpjpy": 100 , "eurjpy": 100})
fxr_crosses.convert(1, "usd", "jpy")


fxr_majors = fxr_crosses.restate (["eurusd", "usdjpy", "gbpusd"])
fxr_majors.convert(1, "usd", "jpy")



#======================================================================
# FXForwards
#======================================================================


fx_rates = FXRates ({"usdeur": 0.9 , "eurnok": 8.888889} , dt(2022, 1, 3))
fx_curves = {
    # local currency curves first
    "usdusd": Curve({dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.96}),
    "eureur": Curve({dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.99}),
    "noknok": Curve({dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.98}),
    # cross - currency collateral curves next
    "eurusd": Curve({dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.991}) ,
    "nokeur": Curve({dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.978}) ,
}
fxf = FXForwards(fx_rates, fx_curves)
fxf.rate("usdnok", dt(2022, 8, 15))


fxf.currencies


# Paths are expressed by indexed currencies: 1 = "EUR"
fxf._paths



#======================================================================
# Equivalence of Delta Risk
#======================================================================


fx_rates = FXRates({"usdeur": 0.9, "eurnok": 8.888889}, dt(2022 , 1, 3))
start, end = dt(2022, 1, 1), dt(2023, 1, 1)
fx_curves = {
    "usdusd": Curve({start: 1.0 , end: 0.96}, id="uu", ad=1) ,
    "eureur": Curve({start: 1.0 , end: 0.99}, id="ee", ad=1) ,
    "eurusd": Curve({start: 1.0 , end: 0.991}, id="eu", ad=1) ,
    "noknok": Curve({start: 1.0 , end: 0.98}, id="nn", ad=1) ,
    "nokeur": Curve({start: 1.0 , end: 0.978}, id="ne", ad=1) ,
}
fxf = FXForwards(fx_rates, fx_curves)


discounted_nok = fx_curves["nokeur"][dt(2022, 8, 15)] * 1000
base_value_1 = discounted_nok * fxf.rate("nokusd", dt(2022 , 1, 1))
base_value_1


gradient(base_value_1, ["uu1", "ee1", "eu1", "nn1", "ne1", "fx_usdeur", "fx_eurnok"])


forward_eur = fxf.rate("nokeur", dt(2022, 8, 15)) * 1000
discounted_eur = forward_eur * fx_curves["eureur"][dt(2022, 8, 15)]
base_value_2 = discounted_eur * fxf.rate("eurusd", dt(2022, 1, 1))
base_value_2


gradient(base_value_2, ["uu1", "ee1", "eu1", "nn1", "ne1", "fx_usdeur", "fx_eurnok"])



#======================================================================
# Combining Settlement dates
#======================================================================


curve = Curve ({ dt (2000 , 1, 1): 1.0 , dt (2001 , 1, 1): 0.99})
fxr1 = FXRates ({"eurusd": 1.10 , "gbpusd": 1.30} , settlement =dt (2000 , 1, 1))
fxr2 = FXRates ({"usdcad": 1.05} , settlement =dt (2000 , 1, 2))
fxr3 = FXRates ({"gbpjpy": 100.0} , settlement =dt (2000 , 1, 3))
try:
    fxf = FXForwards (
        fx_curves ={
            "usdusd": curve, "eureur": curve, "gbpgbp": curve,
            "jpyjpy": curve, "cadcad": curve, "usdjpy": curve,
            "eurjpy": curve, "eurcad": curve, "gbpcad": curve,
        },
        fx_rates =[fxr1, fxr2, fxr3]
    )
except ValueError as e:
    print(e)



#======================================================================
# Dual represenation
#======================================================================


pv = Dual(100000 , ["fx_eurusd", "fx_usdcad"], [-100000 , 150000]) # base is USD


fxr1 = FXRates ({"eurusd": 1.05} , settlement=dt(2022, 1, 3))
fxr2 = FXRates ({"usdcad": 1.1} , settlement=dt(2022, 1, 2))
fxf = FXForwards (
    fx_rates =[fxr1, fxr2],
    fx_curves ={
        "usdusd": Curve ({dt(2022, 1, 1): 1.0 , dt(2022, 2, 1): 0.999}) ,
        "eureur": Curve ({dt(2022, 1, 1): 1.0 , dt(2022, 2, 1): 0.999}) ,
        "cadcad": Curve ({dt(2022, 1, 1): 1.0 , dt(2022, 2, 1): 0.999}) ,
        "usdeur": Curve ({dt(2022, 1, 1): 1.0 , dt(2022, 2, 1): 0.999}) ,
        "cadusd": Curve ({dt(2022, 1, 1): 1.0 , dt(2022, 2, 1): 0.999}) ,
    }
)
fxf.positions(pv, base="usd")


if __name__ == "__main__":
    print("Script completed successfully!")
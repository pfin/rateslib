#!/usr/bin/env python
"""
Converted from: FXVolatility.ipynb

This script demonstrates rateslib functionality.
Run from the python/ directory to ensure imports work correctly.
"""

import sys
import os

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')


from rateslib import *
from pandas import Series



#======================================================================
# Time Weighting for Volatility Surface
#======================================================================


fxv = FXDeltaVolSurface( 
    eval_date=dt(2024, 7, 25),
    expiries=[dt(2024, 7, 30), dt(2024, 8, 5)], 
    delta_indexes=[0.5],
    node_values =[[10.0] , [10.0]] , 
    weights=Series(0.1, index=[
        dt(2024, 7, 27), dt(2024, 7, 28), dt(2024, 8, 3), dt(2024, 8, 4)]
    ),
    delta_type="forward", 
)
print(fxv.meta.weights[dt(2024, 7, 25):dt(2024, 8, 5)])



#======================================================================
# Sticky strike, sticky delta and Solver delta
#======================================================================


# Define Curves
usd = Curve({dt(2024, 5, 7): 1.0, dt(2024, 5, 30): 1.0}, calendar="nyc", id="usd") 
eur = Curve({dt(2024, 5, 7): 1.0, dt(2024, 5, 30): 1.0}, calendar="tgt", id="eur") 
eurusd = Curve({dt(2024, 5, 7): 1.0, dt(2024, 5, 30): 1.0}, id="eurusd")

# Create an FX Forward market with spot FX rate data
spot = dt(2024, 5, 9)
fxr = FXRates({"eurusd": 1.0760}, settlement=spot) 
fxf = FXForwards(
    fx_rates=fxr, 
    fx_curves={"eureur": eur, "usdusd": usd, "eurusd": eurusd},
)

# Solve the Curves to market
pre_solver = Solver(
    curves=[eur, eurusd, usd], 
    instruments=[
        IRS(spot, "3W", spec="eur_irs", curves="eur"),
        IRS(spot, "3W", spec="usd_irs", curves="usd"),
        FXSwap(spot, "3W", pair="eurusd", curves=[None, "eurusd", None, "usd"]),
    ],
    s=[3.90, 5.32, 8.85], 
    fx=fxf,
    id="fxf",
)


# Define the Vol Smile
smile = FXSabrSmile(
    nodes={"alpha": 0.05, "beta": 1.0, "rho": 0.01, "nu": 0.03}, 
    eval_date=dt(2024, 5, 7),
    expiry=dt(2024, 5, 28),
    id="smile",
    pair="eurusd",
)


# Collect FXOption arguments
option_args = dict(
    pair="eurusd",
    expiry=dt(2024, 5, 28), 
    calendar="tgt|fed", 
    delta_type="spot",
    curves=[None, "eurusd", None, "usd"], 
    vol="smile",
)
# Calibrate the Smile to market option data
solver = Solver( 
    pre_solvers=[pre_solver], 
    curves=[smile],
    instruments=[
        FXStraddle(strike="atm_delta", **option_args),
        FXRiskReversal(strike=("-25d", "25d"), **option_args),
        FXRiskReversal(strike=("-10d", "10d"), **option_args),
        FXBrokerFly(strike=(("-25d", "25d"), "atm_delta"), **option_args),
        FXBrokerFly(strike=(("-10d", "10d"), "atm_delta"), **option_args),
    ],
    s=[5.493, -0.157, -0.289, 0.071, 0.238],
    fx=fxf,
    id="smile",
)


fxc = FXCall(**option_args, notional=100e6, strike =1.07, premium=982144.59) # <-- mid-market premium giving zero NPV


fxc.delta(solver=solver).loc[("fx", "fx", "eurusd")]


fxc.gamma(solver=solver).loc[("usd", "usd", "fx", "fx", "eurusd"), ("fx", "fx", "eurusd")]


fxr.update({"eurusd": 1.0761})
pre_solver.iterate()
solver.iterate()
fxc.npv(solver=solver)



#======================================================================
# Sticky delta
#======================================================================


fxc.analytic_greeks(solver=solver)["delta_sticky"]


fxc.analytic_greeks(solver=solver)["delta"]


option_args = dict(
    pair="eurusd",
    expiry=dt(2024, 5, 28), 
    calendar="tgt|fed", 
    delta_type="forward",
    curves=[None, "eurusd", None, "usd"], 
    vol="smile",
)
fxc = FXCall(**option_args, notional=100e6, strike =1.07, premium=982144.59) # <-- mid-market premium giving zero NPV
fxc.analytic_greeks(solver=solver)["delta_sticky"]


fxc.analytic_greeks(solver=solver)["delta"]


if __name__ == "__main__":
    print("Script completed successfully!")
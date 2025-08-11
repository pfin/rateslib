#!/usr/bin/env python
"""
Converted from: InterpolationAndSplines.ipynb

This script demonstrates rateslib functionality.
Run from the python/ directory to ensure imports work correctly.
"""

import sys
import os

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')


from rateslib import *
from rateslib.splines import evaluate



#======================================================================
# Splines and AD
#======================================================================


pps = PPSplineDual(
    k=3,
    t=[0,0,0,4,4,4]
)
pps.csolve(
    tau=[1, 2, 3],
    y=[
        Dual(2.0, ["y1"], []),
        Dual(1.0, ["y2"], []),
        Dual(2.6, ["y3"], []),
    ],
    left_n=0,
    right_n=0,
    allow_lsq=False
)


pps.ppev_single(3.5)



#======================================================================
# Application to curves
#======================================================================


spline = PPSplineF64(
    k=4,
    t=[_.timestamp() for _ in [
        dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1),
        dt(2023, 1, 1),
        dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1)
    ]]
)


spline.bsplmatrix(
    tau=[_.timestamp() for _ in [
        dt(2022, 1, 1), dt(2022, 1, 1), dt(2023, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1)
    ]],
    left_n=2,
    right_n=2
)


spline.csolve(
    tau=[_.timestamp() for _ in [
        dt(2022, 1, 1), dt(2022, 1, 1), dt(2023, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1)
    ]],
    y=[0.0, 1.5, 1.85, 1.80, 0.0],
    left_n=2,
    right_n=2,
    allow_lsq=False,
)


spline.c



#======================================================================
# Log-spline to DFs
#======================================================================


from math import log, exp
from datetime import timedelta

log_spline = PPSplineF64(
    k=4,
    t=[_.timestamp() for _ in [
        dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1),
        dt(2023, 1, 1),
        dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1)
    ]]
)
log_spline.csolve(
    tau=[_.timestamp() for _ in [
        dt(2022,1,1), dt(2022,1,1), dt(2023,1,1), dt(2024,1,1), dt(2024,1,1)
    ]], 
    y=[0, log(1.0), log(0.983), log(0.964), 0],
    left_n=2,
    right_n=2,
    allow_lsq=False,
)
log_spline.c


import matplotlib.pyplot as plt
x = [_.timestamp() for _ in [
    dt(2022, 1, 1) + timedelta(days=i) for i in range(720)]]
fix, ax = plt.subplots(1,1)
ax.plot(x, [exp(log_spline.ppev_single(_)) for _ in x])
    


if __name__ == "__main__":
    print("Script completed successfully!")
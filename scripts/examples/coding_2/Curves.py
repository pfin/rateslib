#!/usr/bin/env python
"""
Converted from: Curves.ipynb

This script demonstrates rateslib functionality.
Run from the python/ directory to ensure imports work correctly.
"""

import sys
import os

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')



#======================================================================
# Curves
#======================================================================
#

#======================================================================
# CompositeCurve example
#======================================================================
#
# The first section here regards efficient operations and compositing two curves.


from rateslib import dt, defaults
from rateslib.curves import Curve, LineCurve, CompositeCurve, MultiCsaCurve


line_curve1 = LineCurve({dt(2022, 1, 1): 2.0, dt(2022, 1, 3): 4.0}, id="C1_")
line_curve2 = LineCurve({dt(2022, 1, 1): 0.5, dt(2022, 1, 3): 1.0}, id="C2_")
composite_curve = CompositeCurve(curves=(line_curve1, line_curve2))
composite_curve.rate(dt(2022, 1, 2))


line_curve1._set_ad_order(1)
line_curve2._set_ad_order(1)
composite_curve.rate(dt(2022, 1, 2))


# The code above demonstrates the summing of individual rates and of interoperability with Dual datatypes.
#
# Below measures rate lookup.


defaults.curve_caching = False

composite_curve = CompositeCurve(
    (
        Curve({dt(2022, 1, 1): 1.0, dt(2024, 1, 1): 0.95}, id="C1_"),
        Curve({dt(2022, 1, 1): 1.0, dt(2024, 1, 1): 0.99}, id="C2_"),
    )
)
# Timing: composite_curve.rate(dt(2022, 6, 1), "1y")
import timeit
print('Timing:', timeit.timeit(lambda: composite_curve.rate(dt(2022, 6, 1), "1y"), number=1000))



#======================================================================
# MultiCsaCurve
#======================================================================


c1 = Curve({dt(2022, 1, 1): 1.0, dt(2052, 1, 1): 0.5})
c2 = Curve({dt(2022, 1, 1): 1.0, dt(2032, 1, 1): 0.4, dt(2052, 1, 1):0.39}) 
mcc = MultiCsaCurve([c1, c2])

# Timing: c2[dt(2052, 1, 1)]
import timeit
print('Timing:', timeit.timeit(lambda: c2[dt(2052, 1, 1)], number=1000))


# Timing: mcc[dt(2052, 1, 1)]
import timeit
print('Timing:', timeit.timeit(lambda: mcc[dt(2052, 1, 1)], number=1000))



#======================================================================
# Error in approximated rates and execution time
#======================================================================


import numpy as np
MIN, MAX, SAMPLES, DAYS, d = 0, 4, 100000, 3, 1.0/365
c1 = np.random.rand(DAYS, SAMPLES) * (MAX - MIN) + MIN
c2 = np.random.rand(DAYS, SAMPLES) * (MAX - MIN) + MIN
r_true=((1 + d * (c1 + c2) / 100).prod(axis=0) - 1) * 100 / (d * DAYS)
c1_bar = ((1 + d * c1 / 100).prod(axis=0)**(1/DAYS) - 1) * 100 / d
c2_bar = ((1 + d * c2 / 100).prod(axis=0)**(1/DAYS) - 1) * 100 / d
r_bar = ((1 + d * (c1_bar + c2_bar) / 100) ** DAYS - 1) * 100 / (d * DAYS)
np.histogram(np.abs(r_true-r_bar), bins=[0, 5e-7, 1e-6, 5e-6, 1e-5, 5e-5, 1]) 



#======================================================================
# Curve operations: shift
#======================================================================


curve = Curve({dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.98}, convention="Act365F", id="v", ad=1)
curve.rate(dt(2022, 6, 1), "1b")


shifted_curve = curve.shift(50)
shifted_curve.rate(dt(2022, 6, 1), "1b")


type(shifted_curve)


# Timing: curve.rate(dt(2022, 6, 1), "1b")
import timeit
print('Timing:', timeit.timeit(lambda: curve.rate(dt(2022, 6, 1), "1b"), number=1000))


# Timing: shifted_curve.rate(dt(2022, 6, 1), "1b")
import timeit
print('Timing:', timeit.timeit(lambda: shifted_curve.rate(dt(2022, 6, 1), "1b"), number=1000))



#======================================================================
# Curve operations: roll
#======================================================================


curve = Curve(
    nodes={dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.98, dt(2024, 1, 1): 0.97},
    t=[dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1),
       dt(2023, 1, 1),
       dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1)]
)
print(curve.rate(dt(2022, 6, 1), "1d"))
print(curve.roll("30d").rate(dt(2022, 7, 1), "1d"))


line_curve = LineCurve(
    nodes={dt(2022, 1, 1): 2.0, dt(2023, 1, 1): 2.6, dt(2024, 1, 1): 2.5},
    t=[dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1),
       dt(2023, 1, 1),
       dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1)]
)
print(line_curve.rate(dt(2022, 6, 1)))
print(line_curve.roll("-31d").rate(dt(2022, 5, 1), "1d"))



#======================================================================
# Curve operations: translate
#======================================================================


for interpolation in [
    "linear", "log_linear", "linear_index", "flat_forward", "flat_backward", "linear_zero_rate"
]:
    curve = Curve(
        nodes={dt(2022, 1, 1): 1.0, dt(2022, 2, 1):0.998, dt(2022, 3, 1): 0.995}, 
        interpolation=interpolation
    )
    curve_translated = curve.translate(dt(2022, 1, 15)) 
    print(
        curve.rate(dt(2022, 2, 15), "1d"),
        curve_translated.rate(dt(2022, 2, 15), "1d") 
    )



#======================================================================
# Operations on CompositeCurves
#======================================================================


composite_curve.rate(dt(2022, 6, 1), "1d")


composite_curve.shift(50).rate(dt(2022, 6, 1), "1d")


composite_curve.roll("30d").rate(dt(2022, 7, 1), "1d")


composite_curve.translate(dt(2022, 5, 1)).rate(dt(2022, 6, 1), "1d")


if __name__ == "__main__":
    print("Script completed successfully!")
#!/usr/bin/env python
"""
Converted from: Periods.ipynb

This script demonstrates rateslib functionality.
Run from the python/ directory to ensure imports work correctly.
"""

import sys
import os

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')


from rateslib import Curve, FloatPeriod, dt, defaults



#======================================================================
# Expression of fixings risk in fixings table
#======================================================================


curve = Curve ({dt(2022, 1, 1): 1.0 , dt(2025, 1, 1): 0.94},
               id="euribor3m", calendar="tgt", convention="act360"
)


imm_fp = FloatPeriod (
    start=dt(2023, 3, 15),
    end=dt(2023, 6, 21), # <--- IMM start and end dates
    payment=dt(2023, 6, 21),
    frequency="q",
    convention="act360",
    calendar="tgt",
    fixing_method="ibor",
    method_param=2,
    notional=-1e6 # <-- Notional for period is -1mm
 )
imm_fp.fixings_table(curve)


curve2 = Curve ({dt(2022, 1, 1): 1.0 , dt(2025, 1, 1): 0.94} ,
                id="euribor1m", calendar="tgt", convention="act360"
)

stub_fp = FloatPeriod (
    start=dt(2022, 3, 14),
    end=dt(2022, 5, 14), # <--- 2M stub tenor
    payment =dt(2022, 5, 14),
    frequency="q",
    convention="act360",
    calendar="tgt",
    fixing_method="ibor",
    method_param=2,
    notional=-1e6 ,
    stub=True,
)
stub_fp.fixings_table({"1m": curve2 , "3m": curve}, disc_curve=curve2)


defaults.curve_caching = False


curve = Curve ({ dt(2022, 1, 4): 1.0, dt(2023, 1, 4): 0.98}, calendar="ldn")
float_period = FloatPeriod(start=dt(2022, 1, 4), end=dt(2023, 1, 4),
                           payment=dt(2023, 1, 4) ,frequency ="A",
                           fixing_method="rfr_lookback", method_param=0)

# Timing: float_period.fixings_table(curve)
import timeit
print('Timing:', timeit.timeit(lambda: float_period.fixings_table(curve), number=1000))


# Timing: float_period.fixings_table(curve, approximate=True)
import timeit
print('Timing:', timeit.timeit(lambda: float_period.fixings_table(curve, approximate=True), number=1000))


if __name__ == "__main__":
    print("Script completed successfully!")
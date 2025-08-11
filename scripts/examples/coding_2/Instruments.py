#!/usr/bin/env python
"""
Converted from: Instruments.ipynb

This script demonstrates rateslib functionality.
Run from the python/ directory to ensure imports work correctly.
"""

import sys
import os

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')


from rateslib import FixedRateBond, dt, Bill, IndexFixedRateBond



#======================================================================
# Bond analogue methods
#======================================================================


bond = FixedRateBond (
    effective=dt(2022, 1, 1) ,
    termination=dt(2023, 1, 1) ,
    fixed_rate=5.0,
    spec ="uk_gb",
)
bond.accrued(dt(2022, 4, 15))


bond = FixedRateBond (
    effective=dt(2022, 1, 1) ,
    termination=dt(2023, 1, 1) ,
    fixed_rate=5.0,
    spec ="ca_gb",
)
bond.accrued(dt(2022, 4, 15))



#======================================================================
# YTM iteration
#======================================================================


bond = FixedRateBond (
    effective=dt(2000 , 1, 1) , termination =dt(2010 , 1, 1) ,
    fixed_rate=2.5 , spec="us_gb"
)
bond.ytm(95.0, settlement=dt(2000, 7, 1))
# ( -3.0000 , 2.0000 , 12.0000) - Initial interval requires 4 function evaluations
# (2.0000 , 3.2858 , 12.0000) - Second interval requires 1 function evaluation
# (2.0000 , 3.1063 , 3.2858) - Third interval requires 1 function evaluation
# (3.1063 , 3.1120 , 3.2858) - Fourth interval requires 1 function evaluation



#======================================================================
# Bills
#======================================================================


bill = Bill(
    effective=dt(2023, 5, 17),
    termination=dt(2023, 9, 26),
    spec="us_gbb"
)
bill.ytm(99.75, settlement=dt(2023 , 9, 7))


bond = FixedRateBond (
    effective=dt(2023, 3, 26),
    termination=dt(2023, 9, 26),
    fixed_rate=0.0,
    spec="us_gb",
)
bond.ytm(99.75, settlement=dt(2023, 9, 7))



#======================================================================
# Inflation Linked
#======================================================================


ukt = FixedRateBond (
    spec ="uk_gb",
    effective =dt (2022 , 2, 1) ,
    termination ="2y",
    fixed_rate =2.5 ,
)
ukt.price(ytm=3.0, settlement=dt(2023 , 10, 1))


ukti = IndexFixedRateBond (
    spec="uk_gbi",
    effective=dt(2022, 2, 1) ,
    termination="2y",
    fixed_rate=2.5,
    index_base=100.0,
)
ukti.price(ytm=3.0, settlement=dt(2023 , 10, 1))


if __name__ == "__main__":
    print("Script completed successfully!")
#!/usr/bin/env python
"""
Converted from: Scheduling.ipynb

This script demonstrates rateslib functionality.
Run from the python/ directory to ensure imports work correctly.
"""

import sys
import os

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')


from rateslib import *



#======================================================================
# Regular Unadjusted Schedules
#======================================================================


from rateslib.scheduling import _generate_regular_schedule_unadjusted

dates = list (_generate_regular_schedule_unadjusted (
    ueffective=dt(2023 , 3, 15),
    utermination=dt(2023 , 9, 20),
    frequency="M", 
    roll="imm",
))

dates



#======================================================================
# Stub and Roll Inference
#======================================================================



#======================================================================
# Get a Roll
#======================================================================


from rateslib . scheduling import _get_unadjusted_roll

_get_unadjusted_roll (
    ueffective =dt (2022 ,3 ,15) , utermination =dt (2023 ,3 ,15) , eom = True
)


_get_unadjusted_roll (
    ueffective =dt (2022 ,2 ,28) , utermination =dt (2023 ,2 ,28) , eom = False
)


_get_unadjusted_roll (
    ueffective =dt (2022 ,2 ,28) , utermination =dt (2023 ,2 ,28) , eom = True
)



#======================================================================
# Validate for a regular unadjusted swap
#======================================================================


from rateslib . scheduling import _check_unadjusted_regular_swap

_check_unadjusted_regular_swap(
    ueffective=dt(2022, 2, 28),
    utermination=dt(2023, 2, 28),
    frequency="M",
    eom=False,
    roll=NoInput(0),
)


_check_unadjusted_regular_swap (
    ueffective=dt (2022 , 2, 28) ,
    utermination=dt (2023 , 2, 28) ,
    frequency="M",
    eom=True,
    roll=NoInput(0),
)


_check_unadjusted_regular_swap (
    ueffective=dt(2022 , 3, 16) ,
    utermination=dt(2022 , 9, 21) ,
    frequency="M",
    eom=False ,
    roll=NoInput(0),
)


_check_unadjusted_regular_swap (
    ueffective=dt(2022 , 3, 16) ,
    utermination=dt(2022 , 9, 21) ,
    frequency="M",
    eom=False ,
    roll="imm",
)



#======================================================================
# Get a stub
#======================================================================


from rateslib.scheduling import _get_unadjusted_short_stub_date

kws = dict (
    ueffective =dt (2022 , 6, 15),
    utermination =dt (2023 , 2, 28),  # <-- End of Fenruary
    frequency ="M",
)

_get_unadjusted_short_stub_date (**kws , eom=False , roll=NoInput(0) ,stub_side="FRONT")


_get_unadjusted_short_stub_date(**kws, eom=True, roll=NoInput(0), stub_side="FRONT")


_get_unadjusted_short_stub_date(**kws, eom=True, roll=29, stub_side="FRONT")


from rateslib . scheduling import _get_unadjusted_stub_date

_get_unadjusted_stub_date(**kws, eom=False, roll=NoInput(0), stub="LONGFRONT")


_get_unadjusted_stub_date(**kws, eom=True, roll=NoInput(0), stub="LONGFRONT")


_get_unadjusted_stub_date(**kws, eom=False, roll=29, stub="LONGFRONT")



#======================================================================
# Validate for a regular swap account for business days
#======================================================================


from rateslib.scheduling import _check_regular_swap

_check_regular_swap( 
    effective=dt(2022, 6, 6), 
    termination=dt(2022, 12, 5),
    frequency="Q",
    eom=False,
    roll=NoInput(0),
    modifier ="MF",
    calendar=get_calendar("bus"),
)



#======================================================================
# Schedule Building
#======================================================================


sch = Schedule (
    effective ="1Y",
    termination ="1Y",
    frequency ="S",
    calendar ="tgt",
    payment_lag =1,
    eval_date=dt (2023 , 8, 17) ,
    eval_mode="swaps_align", 
)
print(sch)


sch = Schedule (
    effective ="1Y",
    termination ="1Y",
    frequency ="S",
    calendar ="tgt",
    payment_lag =1,
    eval_date =dt (2023 , 8, 17) ,
    eval_mode="swaptions_align", 
)
print(sch)


if __name__ == "__main__":
    print("Script completed successfully!")
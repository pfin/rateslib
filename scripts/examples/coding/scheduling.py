#!/usr/bin/env python
"""
Converted from: scheduling.ipynb

This script demonstrates rateslib functionality.
Run from the python/ directory to ensure imports work correctly.
"""

import sys
import os

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')


from rateslib import dt
from rateslib.scheduling import _get_unadjusted_roll


_get_unadjusted_roll(ueffective=dt(2022, 3, 15), utermination=dt(2023, 3, 15), eom=False)


_get_unadjusted_roll(ueffective=dt(2022, 2, 28), utermination=dt(2023, 2, 28), eom=False)


_get_unadjusted_roll(ueffective=dt(2022, 2, 28), utermination=dt(2023, 2, 28), eom=True)


from rateslib.scheduling import _generate_regular_schedule_unadjusted


dates = [
    d for d in 
    _generate_regular_schedule_unadjusted(
        ueffective=dt(2023, 3, 15),
        utermination=dt(2023, 9, 20),
        frequency="M",
        roll="imm"
    )
]
dates


from rateslib.scheduling import _check_unadjusted_regular_swap


_check_unadjusted_regular_swap(
        ueffective=dt(2022, 3, 16), utermination=dt(2022, 9, 21),
        frequency="M", roll=None, eom=False
    )


_check_unadjusted_regular_swap(
        ueffective=dt(2022, 2, 28), utermination=dt(2023, 2, 28),
        frequency="M", eom=True, roll=None
    )


from rateslib.scheduling import _get_unadjusted_short_stub_date


_get_unadjusted_short_stub_date(
        ueffective=dt(2022, 6, 15), utermination=dt(2023, 2, 28),
        frequency="M", eom=True, roll=None, stub_side="FRONT"
    )


_get_unadjusted_short_stub_date(
        ueffective=dt(2022, 6, 15), utermination=dt(2023, 2, 28),
        frequency="M", eom=False, roll=None, stub_side="FRONT"
    )


_get_unadjusted_short_stub_date(
        ueffective=dt(2022, 6, 15), utermination=dt(2023, 2, 28),
        frequency="M", eom=True, roll=29, stub_side="FRONT"
    )


from rateslib.scheduling import _get_unadjusted_stub_date


_get_unadjusted_stub_date(
        ueffective=dt(2022, 6, 15), utermination=dt(2023, 2, 28),
        frequency="M", eom=True, roll=None, stub="LONGFRONT"
    )


_get_unadjusted_stub_date(
        ueffective=dt(2022, 6, 15), utermination=dt(2023, 2, 28),
        frequency="M", eom=False, roll=None, stub="LONGFRONT"
    )


_get_unadjusted_stub_date(
        ueffective=dt(2022, 6, 15), utermination=dt(2023, 2, 28),
        frequency="M", eom=True, roll=29, stub="LONGFRONT"
    )


from rateslib.calendars import get_calendar
from rateslib.scheduling import _check_regular_swap


_check_regular_swap(
    effective=dt(2022, 6, 6),
    termination=dt(2022, 12,  5),
    frequency="Q",
    modifier="MF",
    eom=False,
    roll=None,
    calendar=get_calendar("bus"),
)
    


if __name__ == "__main__":
    print("Script completed successfully!")
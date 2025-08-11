#!/usr/bin/env python
"""
Converted from: Calendars.ipynb

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
# Timings
#======================================================================
#
# Get a calendar straight from a hash table.


# Timing: get_calendar("ldn")
import timeit
print('Timing:', timeit.timeit(lambda: get_calendar("ldn"), number=1000))


# Construct a ``Cal`` directly from a list of holidays and week mask.


cal = get_calendar("ldn")
holidays = cal.holidays
# Timing: Cal(holidays=holidays, week_mask=[5,6])
import timeit
print('Timing:', timeit.timeit(lambda: Cal(holidays=holidays, week_mask=[5,6]), number=1000))


# Get a ``NamedCal`` parsed and constructed in Python.


# Timing: get_calendar("ldn,tgt")
import timeit
print('Timing:', timeit.timeit(lambda: get_calendar("ldn,tgt"), number=1000))


# Construct a ``UnionCal`` directly from multiple ``Cal``.


c1 = Cal(holidays=get_calendar("ldn", named=False).holidays, week_mask=[5,6])
c2 = Cal(holidays=get_calendar("tgt", named=False).holidays, week_mask=[5,6])

# Timing: UnionCal([c1, c2])
import timeit
print('Timing:', timeit.timeit(lambda: UnionCal([c1, c2]), number=1000))


# Add a new calendar to ``defaults.calendars`` and fetch that directly.


defaults.calendars["ldn,tgt"] = get_calendar("ldn,tgt")


# Timing: get_calendar("ldn,tgt")
import timeit
print('Timing:', timeit.timeit(lambda: get_calendar("ldn,tgt"), number=1000))



#======================================================================
# Tenor Manipulations
#======================================================================


add_tenor(dt(2001, 9, 28), "-6m", modifier="MF", calendar="LDN")


add_tenor(dt(2001, 9, 28), "-6m", modifier="MF", calendar="LDN", roll=31)


add_tenor(dt(2001, 9, 28), "-6m", modifier="MF", calendar="LDN", roll=29)



#======================================================================
# Associated Settlement Calendars
#======================================================================


tgt_and_nyc = get_calendar("tgt,nyc")
tgt_and_nyc.add_bus_days(dt(2009, 11, 10), 2, True)


tgt_plus_nyc_settle = get_calendar("tgt|nyc")
tgt_plus_nyc_settle.add_bus_days(dt(2009, 11, 10), 2, True)


tgt_plus_nyc_settle.add_bus_days(dt(2009, 11, 10), 1, settlement=True)


tgt_plus_nyc_settle.add_bus_days(dt(2009, 11, 10), 1, settlement=False)


if __name__ == "__main__":
    print("Script completed successfully!")
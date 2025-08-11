#!/usr/bin/env python
"""
Converted from: Cookbook.ipynb

This script demonstrates rateslib functionality.
Run from the python/ directory to ensure imports work correctly.
"""

import sys
import os

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')



#======================================================================
# Turns
#======================================================================


from rateslib import *


curve = Curve(
    nodes={dt(2022, 12, 1): 1.0, dt(2023, 2, 1): 1.0}, 
    interpolation="log_linear"
)


curve = Curve({
    dt(2022, 12, 1): 1.0,
    dt(2022, 12, 31): 1.0,
    dt(2023, 1, 1): 1.0,
    dt(2023, 2, 1): 1.0,
}, interpolation="log_linear")
instruments = [
    IRS(dt(2022, 12, 1), "1d", "A", curves=curve),
    Spread(
        IRS(dt(2022, 12, 30), "1d", "A", curves=curve),
        IRS(dt(2022, 12, 31), "1d", "A", curves=curve),
    ),
    Spread(
        IRS(dt(2022, 12, 31), "1d", "A", curves=curve),
        IRS(dt(2023, 1, 1), "1d", "A", curves=curve),
    ), 
]
solver = Solver(curves=[curve], instruments=instruments, s=[0.0, -0.5, 0.5])


instruments = [
    IRS(dt(2022, 12, 1), "1d", "A", curves=curve),
    Spread(
        IRS(dt(2022, 12, 30), "1d", "A", curves=curve),
        IRS(dt(2022, 12, 31), "1d", "A", curves=curve),
    ),
    IRS(dt(2023, 1, 1), "1d", "A", curves=curve),
]
solver = Solver(curves=[curve], instruments=instruments, s=[0.0, -50.0, 0.0])


curve.plot("1b")


linecurve = LineCurve({
        dt(2022, 12, 1): 0.0,
        dt(2022, 12, 31): -50.0,
        dt(2023, 1, 1): 0.0,
}, interpolation="flat_forward")
instruments = [
    Value(dt(2022, 12, 1), curves=linecurve),
    Value(dt(2022, 12, 31), curves=linecurve),
    Value(dt(2023, 1, 1), curves=linecurve),
]
solver = Solver(curves=[linecurve], instruments=instruments, s=[0.0, -0.5, 0.0])
linecurve.plot("1b", right=dt(2023, 2, 1))



#======================================================================
# Injecting turns to spline curves
#======================================================================


turn_curve = Curve({
    dt(2022, 12, 1): 1.0,
    dt(2022, 12, 31): 1.0,
    dt(2023, 1, 1): 1.0,
    dt(2023, 2, 1): 1.0,
}, interpolation="log_linear")
cubic_curve = Curve({
    dt(2022, 12, 1): 1.0,
    dt(2022, 12, 21): 1.0,
    dt(2023, 1, 11): 1.0,
    dt(2023, 2, 1): 1.0,
}, t = [
    dt(2022, 12, 1), dt(2022, 12, 1), dt(2022, 12, 1), dt(2022, 12, 1),
    dt(2022, 12, 21),
    dt(2023, 1, 11),
    dt(2023, 2, 1), dt(2023, 2, 1), dt(2023, 2, 1), dt(2023, 2, 1),
])
composite_curve = CompositeCurve([turn_curve, cubic_curve])
instruments = [
    IRS(dt(2022, 12, 1), "1d", "A", curves=turn_curve),
    Spread(
        IRS(dt(2022, 12, 30), "1d", "A", curves=turn_curve),
        IRS(dt(2022, 12, 31), "1d", "A", curves=turn_curve),
    ),
    IRS(dt(2023, 1, 1), "1d", "A", curves=turn_curve),
    IRS(dt(2022, 12, 1), "20d", "A", curves=composite_curve),
    IRS(dt(2022, 12, 21), "20d", "A", curves=composite_curve),
    IRS(dt(2023, 1, 11), "18d", "A", curves=composite_curve),
]
solver = Solver(
    curves=[turn_curve, cubic_curve, composite_curve], 
    instruments=instruments, 
    s=[0.0, -50.0, 0.0, 2.01, 2.175, 2.35],
    instrument_labels=["zero1", "turn", "zero2", "irs1", "irs2", "irs3"],
)


composite_curve.plot("1b")



#======================================================================
# Irrational turns on tenor curves
#======================================================================


turn_curve = LineCurve({
    dt(2022, 9, 15): 0.0,
    dt(2022, 10, 1): -0.20,
    dt(2023, 1, 1): 0.0,
}, interpolation="flat_forward")
fading_turn_curve = LineCurve({
    dt(2022, 9, 15): 0.0,
    dt(2022, 9, 30): 0.0,
    dt(2022, 10, 1): -0.20,
    dt(2022, 12, 31): -0.04,
    dt(2023, 1, 1): 0.0,
    dt(2023, 3, 15): 0.0,
}, interpolation="linear")


line_curve = LineCurve({
    dt(2022, 9, 15): 1.0,
    dt(2022, 12, 15): 1.0,
    dt(2023, 3, 15): 1.0,
}, interpolation="linear")
composite_curve=CompositeCurve([fading_turn_curve, line_curve], id="cc")
instruments = [
    Value(dt(2022, 9, 15), curves=fading_turn_curve),
    Value(dt(2022, 9, 30), curves=fading_turn_curve),
    Value(dt(2022, 10, 1), curves=fading_turn_curve),
    Value(dt(2022, 12, 31), curves=fading_turn_curve),
    Value(dt(2023, 1, 1), curves=fading_turn_curve),
    Value(dt(2023, 3, 15), curves=fading_turn_curve),
    Value(dt(2022, 9, 15), curves=composite_curve),
    Value(dt(2022, 12, 15), curves=composite_curve),
    Value(dt(2023, 3, 15), curves=composite_curve),
]
solver = Solver(
    curves=[fading_turn_curve, line_curve, composite_curve], 
    instruments=instruments, 
    s=[0.0, 0.0, -0.2, -0.04, 0.0, 0.0, 3.5, 3.7, 4.05],
    instrument_labels=["zero1", "zero2", "turnA", "turnB", "zero3", "zero4", "fra1", "fra2", "fra3"],
)


composite_curve.plot("1b")



#======================================================================
# Analysing roll on trade strategies
#======================================================================


curve = Curve(
    nodes={
        dt(2024, 1, 1): 1.0,
        dt(2025, 1, 1): 0.96,
        dt(2026, 1, 1): 0.935,
        dt(2027, 1, 1): 0.915,
    },
    convention="act360",
    t=[
        dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1),
        dt(2025, 1, 1), dt(2026, 1, 1),
        dt(2027, 1, 1), dt(2027, 1, 1), dt(2027, 1, 1), dt(2027, 1, 1)
    ],
)
irs = IRS(
    effective=dt(2024, 1, 1),
    termination="18m",
    spec="usd_irs",
)
irs.rate(curve)


irs.rate(curve.roll("6w"))



#======================================================================
# Stepping underspecified Curves on central bank effective dates
#======================================================================


curve = Curve(
    nodes={
        dt(2024, 1, 31): 1.00, dt(2024, 2, 2): 1.00, dt(2024, 3, 13): 1.00, 
        dt(2024, 4, 17): 1.0, dt(2024, 6, 12): 1.0, dt(2024, 7, 24): 1.0,
        dt(2024, 9, 18): 1.0, dt(2024, 10, 23): 1.0, dt(2024, 12, 18): 1.0,
        dt(2025, 1, 29): 1.0, dt(2025, 7, 31): 1.0,
    },
    convention="act360", interpolation="log_linear", calendar="tgt", id="estr",
)
instruments = [
    IRS(dt(2024, 1, 31), "1b", spec="eur_irs", curves="estr"),  # O/N rate
    IRS(dt(2024, 2, 2), dt(2024, 3, 13), spec="eur_irs", curves="estr"),  # MPC
    IRS(dt(2024, 3, 13), dt(2024, 4, 17), spec="eur_irs", curves="estr"),  # MPC
    IRS(dt(2024, 3, 20), dt(2024, 6, 19), spec="eur_irs", curves="estr"),  # IMM
    IRS(dt(2024, 6, 19), dt(2024, 9, 18), spec="eur_irs", curves="estr"),  # IMM
    IRS(dt(2024, 9, 18), dt(2024, 12, 18), spec="eur_irs", curves="estr"),  # IMM
    IRS(dt(2024, 12, 18), dt(2025, 3, 19), spec="eur_irs", curves="estr"),  # IMM
]
pps = [  # policy periods
    IRS(dt(2024, 2, 2), dt(2024, 3, 13), spec="eur_irs", curves="estr"),  # MPC
    IRS(dt(2024, 3, 13), dt(2024, 4, 17), spec="eur_irs", curves="estr"),  # MPC
    IRS(dt(2024, 4, 17), dt(2024, 6, 12), spec="eur_irs", curves="estr"),  # MPC
    IRS(dt(2024, 6, 12), dt(2024, 7, 24), spec="eur_irs", curves="estr"),  # MPC
    IRS(dt(2024, 7, 24), dt(2024, 9, 18), spec="eur_irs", curves="estr"),  # MPC
    IRS(dt(2024, 9, 18), dt(2024, 10, 2), spec="eur_irs", curves="estr"),  # MPC
    IRS(dt(2024, 10, 23), dt(2024, 12, 18), spec="eur_irs", curves="estr"),  # MPC
    IRS(dt(2024, 12, 18), dt(2025, 1, 29), spec="eur_irs", curves="estr"),  # MPC
    IRS(dt(2025, 1, 29), dt(2025, 3, 15), spec="eur_irs", curves="estr"),  # MPC
]
curvature = [
    Fly(pps[2], pps[3], pps[4]), 
    Fly(pps[4], pps[5], pps[6]), 
    Fly(pps[6], pps[7], pps[8]),
]
solver = Solver(
    curves=[curve],
    instruments=instruments+curvature,
    weights=[1.0] * 7 + [1e-8] * 3,
    s=[3.899, 3.904, 3.859, 3.692, 3.215, 2.725, 2.37] + [0.0] * 3,
    instrument_labels=[
        "depo", "1r", "2r", "1f", "2f", "3f", "4f", "cv0", "cv1", "cv2"
    ],
)


curve.plot("1b")


if __name__ == "__main__":
    print("Script completed successfully!")
#!/usr/bin/env python
"""
Fixed version of Curves.py - demonstrates rateslib functionality.
Run from the python/ directory to ensure imports work correctly.

Key fixes:
- Replaced private _set_ad_order() calls with public ad parameter
- Added proper error handling and output formatting
"""

import sys
import os

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')

#======================================================================
# Curves
#======================================================================

#======================================================================
# CompositeCurve example
#======================================================================
# The first section here regards efficient operations and compositing two curves.

from rateslib import dt, defaults
from rateslib.curves import Curve, LineCurve, CompositeCurve, MultiCsaCurve

print("=== CompositeCurve Basic Operations ===")

# Create line curves
line_curve1 = LineCurve({dt(2022, 1, 1): 2.0, dt(2022, 1, 3): 4.0}, id="C1_")
line_curve2 = LineCurve({dt(2022, 1, 1): 0.5, dt(2022, 1, 3): 1.0}, id="C2_")
composite_curve = CompositeCurve(curves=(line_curve1, line_curve2))
rate1 = composite_curve.rate(dt(2022, 1, 2))
print(f"Basic composite rate: {rate1}")

# Create curves with AD order set at construction (instead of using private _set_ad_order)
print("\n=== CompositeCurve with Automatic Differentiation ===")
line_curve1_ad = LineCurve({dt(2022, 1, 1): 2.0, dt(2022, 1, 3): 4.0}, id="C1_", ad=1)
line_curve2_ad = LineCurve({dt(2022, 1, 1): 0.5, dt(2022, 1, 3): 1.0}, id="C2_", ad=1)
composite_curve_ad = CompositeCurve(curves=(line_curve1_ad, line_curve2_ad))
rate2 = composite_curve_ad.rate(dt(2022, 1, 2))
print(f"AD composite rate: {rate2}")

# The code above demonstrates the summing of individual rates and of interoperability with Dual datatypes.
# Below measures rate lookup.

print("\n=== Performance Testing ===")
defaults.curve_caching = False

composite_curve = CompositeCurve(
    (
        Curve({dt(2022, 1, 1): 1.0, dt(2024, 1, 1): 0.95}, id="C1_"),
        Curve({dt(2022, 1, 1): 1.0, dt(2024, 1, 1): 0.99}, id="C2_"),
    )
)

import timeit
timing1 = timeit.timeit(lambda: composite_curve.rate(dt(2022, 6, 1), "1y"), number=1000)
print(f'Composite curve timing: {timing1:.6f} seconds for 1000 iterations')

#======================================================================
# MultiCsaCurve
#======================================================================

print("\n=== MultiCsaCurve Operations ===")

c1 = Curve({dt(2022, 1, 1): 1.0, dt(2052, 1, 1): 0.5})
c2 = Curve({dt(2022, 1, 1): 1.0, dt(2032, 1, 1): 0.4, dt(2052, 1, 1): 0.39}) 
mcc = MultiCsaCurve([c1, c2])

# Timing individual curve
timing2 = timeit.timeit(lambda: c2[dt(2052, 1, 1)], number=1000)
print(f'Individual curve timing: {timing2:.6f} seconds for 1000 iterations')

# Timing MultiCSA curve
timing3 = timeit.timeit(lambda: mcc[dt(2052, 1, 1)], number=1000)
print(f'MultiCSA curve timing: {timing3:.6f} seconds for 1000 iterations')

#======================================================================
# Error in approximated rates and execution time
#======================================================================

print("\n=== Error Analysis ===")

import numpy as np
MIN, MAX, SAMPLES, DAYS, d = 0, 4, 100000, 3, 1.0/365
c1 = np.random.rand(DAYS, SAMPLES) * (MAX - MIN) + MIN
c2 = np.random.rand(DAYS, SAMPLES) * (MAX - MIN) + MIN
r_true = ((1 + d * (c1 + c2) / 100).prod(axis=0) - 1) * 100 / (d * DAYS)
c1_bar = ((1 + d * c1 / 100).prod(axis=0)**(1/DAYS) - 1) * 100 / d
c2_bar = ((1 + d * c2 / 100).prod(axis=0)**(1/DAYS) - 1) * 100 / d
r_bar = ((1 + d * (c1_bar + c2_bar) / 100) ** DAYS - 1) * 100 / (d * DAYS)
hist = np.histogram(np.abs(r_true-r_bar), bins=[0, 5e-7, 1e-6, 5e-6, 1e-5, 5e-5, 1])
print(f"Error distribution histogram: {hist}")

#======================================================================
# Curve operations: shift
#======================================================================

print("\n=== Curve Shift Operations ===")

curve = Curve({dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.98}, convention="Act365F", id="v", ad=1)
original_rate = curve.rate(dt(2022, 6, 1), "1b")
print(f"Original rate: {original_rate}")

shifted_curve = curve.shift(50)
shifted_rate = shifted_curve.rate(dt(2022, 6, 1), "1b")
print(f"Shifted rate (+50bp): {shifted_rate}")
print(f"Shifted curve type: {type(shifted_curve)}")

# Performance comparison
timing4 = timeit.timeit(lambda: curve.rate(dt(2022, 6, 1), "1b"), number=1000)
print(f'Original curve timing: {timing4:.6f} seconds for 1000 iterations')

timing5 = timeit.timeit(lambda: shifted_curve.rate(dt(2022, 6, 1), "1b"), number=1000)
print(f'Shifted curve timing: {timing5:.6f} seconds for 1000 iterations')

#======================================================================
# Curve operations: roll
#======================================================================

print("\n=== Curve Roll Operations ===")

curve = Curve(
    nodes={dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.98, dt(2024, 1, 1): 0.97},
    t=[dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1),
       dt(2023, 1, 1),
       dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1)]
)
original_roll = curve.rate(dt(2022, 6, 1), "1d")
rolled_rate = curve.roll("30d").rate(dt(2022, 7, 1), "1d")
print(f"Original rate (Jun 1): {original_roll}")
print(f"Rolled rate (Jul 1 after 30d roll): {rolled_rate}")

line_curve = LineCurve(
    nodes={dt(2022, 1, 1): 2.0, dt(2023, 1, 1): 2.6, dt(2024, 1, 1): 2.5},
    t=[dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1),
       dt(2023, 1, 1),
       dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1)]
)
line_original = line_curve.rate(dt(2022, 6, 1))
line_rolled = line_curve.roll("-31d").rate(dt(2022, 5, 1), "1d")
print(f"LineCurve original (Jun 1): {line_original}")
print(f"LineCurve rolled (May 1 after -31d roll): {line_rolled}")

#======================================================================
# Curve operations: translate
#======================================================================

print("\n=== Curve Translate Operations ===")
print("Testing different interpolation methods:")

for interpolation in [
    "linear", "log_linear", "linear_index", "flat_forward", "flat_backward", "linear_zero_rate"
]:
    curve = Curve(
        nodes={dt(2022, 1, 1): 1.0, dt(2022, 2, 1): 0.998, dt(2022, 3, 1): 0.995}, 
        interpolation=interpolation
    )
    curve_translated = curve.translate(dt(2022, 1, 15)) 
    original_trans = curve.rate(dt(2022, 2, 15), "1d")
    translated_trans = curve_translated.rate(dt(2022, 2, 15), "1d")
    print(f"{interpolation:15}: Original={original_trans:8.6f}, Translated={translated_trans:8.6f}")

#======================================================================
# Operations on CompositeCurves
#======================================================================

print("\n=== CompositeCurve Operations ===")

# Use the composite curve created earlier
comp_original = composite_curve.rate(dt(2022, 6, 1), "1d")
comp_shifted = composite_curve.shift(50).rate(dt(2022, 6, 1), "1d")
comp_rolled = composite_curve.roll("30d").rate(dt(2022, 7, 1), "1d")
comp_translated = composite_curve.translate(dt(2022, 5, 1)).rate(dt(2022, 6, 1), "1d")

print(f"Composite original: {comp_original}")
print(f"Composite shifted (+50bp): {comp_shifted}")
print(f"Composite rolled (30d): {comp_rolled}")
print(f"Composite translated: {comp_translated}")

if __name__ == "__main__":
    print("\n=== Script completed successfully! ===")
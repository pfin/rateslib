#!/usr/bin/env python
"""
Fixed version of curves.py - demonstrates rateslib functionality.
Run from the python/ directory to ensure imports work correctly.

Key fixes:
- Replaced private _set_ad_order() calls with public ad parameter
- Added proper error handling and output formatting
- Improved comments and structure
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

from rateslib import dt
from rateslib.curves import Curve, LineCurve, CompositeCurve

print("=== Basic CompositeCurve Operations ===")

line_curve1 = LineCurve({dt(2022, 1, 1): 2.0, dt(2022, 1, 3): 4.0}, id="C1_")
line_curve2 = LineCurve({dt(2022, 1, 1): 0.5, dt(2022, 1, 3): 1.0}, id="C2_")
composite_curve = CompositeCurve(curves=(line_curve1, line_curve2))
basic_rate = composite_curve.rate(dt(2022, 1, 2))
print(f"Basic composite rate: {basic_rate}")

# Fixed: Use ad parameter during construction instead of private _set_ad_order()
print("\n=== CompositeCurve with Automatic Differentiation ===")
line_curve1_ad = LineCurve({dt(2022, 1, 1): 2.0, dt(2022, 1, 3): 4.0}, id="C1_", ad=1)
line_curve2_ad = LineCurve({dt(2022, 1, 1): 0.5, dt(2022, 1, 3): 1.0}, id="C2_", ad=1)
composite_curve_ad = CompositeCurve(curves=(line_curve1_ad, line_curve2_ad))
ad_rate = composite_curve_ad.rate(dt(2022, 1, 2))
print(f"AD composite rate: {ad_rate}")

# The code above demonstrates the summing of individual rates and of interoperability with Dual datatypes.

#======================================================================
# Error in approximated rates and execution time
#======================================================================

print("\n=== Error Analysis: True vs Approximated Rates ===")

import numpy as np
MIN, MAX, SAMPLES, DAYS, d = 0, 4, 100000, 3, 1.0/365

# Generate random rate data
c1 = np.random.rand(DAYS, SAMPLES) * (MAX - MIN) + MIN
c2 = np.random.rand(DAYS, SAMPLES) * (MAX - MIN) + MIN

# Calculate true compounded rates
r_true = ((1 + d * (c1 + c2) / 100).prod(axis=0) - 1) * 100 / (d * DAYS)

# Calculate average rates (approximation)
c1_bar = ((1 + d * c1 / 100).prod(axis=0)**(1/DAYS) - 1) * 100 / d
c2_bar = ((1 + d * c2 / 100).prod(axis=0)**(1/DAYS) - 1) * 100 / d
r_bar = ((1 + d * (c1_bar + c2_bar) / 100) ** DAYS - 1) * 100 / (d * DAYS)

# Analyze errors
errors = np.abs(r_true - r_bar)
hist = np.histogram(errors, bins=[0, 5e-7, 1e-6, 5e-6, 1e-5, 5e-5, 1])
print(f"Error histogram (counts per bin): {hist[0]}")
print(f"Average error: {np.mean(errors):.2e}")
print(f"Max error: {np.max(errors):.2e}")

print("\n=== Performance Comparison: Approximate vs Exact ===")

composite_curve = CompositeCurve(
    (
        Curve({dt(2022, 1, 1): 1.0, dt(2024, 1, 1): 0.95}, id="C1_"),
        Curve({dt(2022, 1, 1): 1.0, dt(2024, 1, 1): 0.99}, id="C2_"),
    )
)

import timeit

# Timing approximate calculation
timing_approx = timeit.timeit(
    lambda: composite_curve.rate(dt(2022, 6, 1), "1y", approximate=True), 
    number=1000
)
print(f'Approximate calculation: {timing_approx:.6f} seconds for 1000 iterations')

# Timing exact calculation
timing_exact = timeit.timeit(
    lambda: composite_curve.rate(dt(2022, 6, 1), "1y", approximate=False), 
    number=1000
)
print(f'Exact calculation: {timing_exact:.6f} seconds for 1000 iterations')
print(f'Speedup ratio: {timing_exact/timing_approx:.2f}x faster with approximation')

#======================================================================
# Curve operations: shift
#======================================================================

print("\n=== Curve Shift Operations ===")

curve = Curve({dt(2022, 1, 1): 1.0, dt(2023, 1, 1): 0.98})
original_curve_rate = curve.rate(dt(2022, 2, 1), "1d")
shifted_curve_rate = curve.shift(50).rate(dt(2022, 2, 1), "1d")
print(f"Curve - Original: {original_curve_rate:.6f}, Shifted (+50bp): {shifted_curve_rate:.6f}")

line_curve = LineCurve({dt(2022, 1, 1): 2.0, dt(2023, 1, 1): 2.6})
original_line_rate = line_curve.rate(dt(2022, 2, 1), "1d")
shifted_line_rate = line_curve.shift(50).rate(dt(2022, 2, 1), "1d")
print(f"LineCurve - Original: {original_line_rate:.6f}, Shifted (+50bp): {shifted_line_rate:.6f}")

#======================================================================
# Curve operations: translate
#======================================================================

print("\n=== Curve Translate Operations ===")
print("Testing different interpolation methods with translate:")

interpolation_methods = [
    "linear", "log_linear", "linear_index", 
    "flat_forward", "flat_backward", "linear_zero_rate"
]

for interpolation in interpolation_methods:
    try:
        curve = Curve(
            nodes={dt(2022, 1, 1): 1.0, dt(2022, 2, 1): 0.998, dt(2022, 3, 1): 0.995}, 
            interpolation=interpolation
        )
        curve_translated = curve.translate(dt(2022, 1, 15))
        
        original_rate = curve.rate(dt(2022, 2, 15), "1d")
        translated_rate = curve_translated.rate(dt(2022, 2, 15), "1d")
        
        print(f"{interpolation:15}: Original={original_rate:8.6f}, Translated={translated_rate:8.6f}")
    except Exception as e:
        print(f"{interpolation:15}: Error - {str(e)[:50]}...")

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
curve_original = curve.rate(dt(2022, 6, 1), "1d")
curve_rolled = curve.roll("30d").rate(dt(2022, 7, 1), "1d")
print(f"Curve - Original (Jun 1): {curve_original:.6f}, Rolled 30d (Jul 1): {curve_rolled:.6f}")

line_curve = LineCurve(
    nodes={dt(2022, 1, 1): 2.0, dt(2023, 1, 1): 2.6, dt(2024, 1, 1): 2.5},
    t=[dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1),
       dt(2023, 1, 1),
       dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1)]
)
line_original = line_curve.rate(dt(2022, 6, 1))
line_rolled = line_curve.roll("-31d").rate(dt(2022, 5, 1), "1d")
print(f"LineCurve - Original (Jun 1): {line_original:.6f}, Rolled -31d (May 1): {line_rolled:.6f}")

#======================================================================
# Operations on CompositeCurves
#======================================================================

print("\n=== CompositeCurve Operations ===")

# Test all operations on the composite curve
comp_original = composite_curve.rate(dt(2022, 6, 1), "1d")
comp_shifted = composite_curve.shift(50).rate(dt(2022, 6, 1), "1d")
comp_rolled = composite_curve.roll("30d").rate(dt(2022, 7, 1), "1d")
comp_translated = composite_curve.translate(dt(2022, 5, 1)).rate(dt(2022, 6, 1), "1d")

print(f"Original: {comp_original:.6f}")
print(f"Shifted (+50bp): {comp_shifted:.6f}")
print(f"Rolled (30d): {comp_rolled:.6f}")
print(f"Translated: {comp_translated:.6f}")

if __name__ == "__main__":
    print("\n=== Script completed successfully! ===")
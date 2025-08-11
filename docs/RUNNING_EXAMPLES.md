# Rateslib Examples - Complete Running Guide

This guide provides comprehensive instructions for running all example scripts in the rateslib repository, including expected output and detailed diagrams.

## Table of Contents
1. [Setup Requirements](#setup-requirements)
2. [Running Scripts](#running-scripts)
3. [FX and Volatility Examples](#fx-and-volatility-examples)
4. [Curve Examples](#curve-examples)
5. [Scheduling Examples](#scheduling-examples)
6. [Instrument Examples](#instrument-examples)
7. [Advanced Examples](#advanced-examples)
8. [Troubleshooting](#troubleshooting)

## Setup Requirements

### Prerequisites
1. **Python 3.12** in a conda environment
2. **Rateslib** built with Rust extensions
3. **Working directory**: Always run from `/home/peter/rateslib/python/`

### Initial Setup
```bash
# Activate environment
conda activate rateslib-dev

# Build Rust extensions (from project root)
cd /home/peter/rateslib
maturin develop --release

# Navigate to Python directory (REQUIRED)
cd python/
```

## Running Scripts

### General Command Pattern
All scripts must be run from the `python/` directory:
```bash
cd /home/peter/rateslib/python
python ../scripts/examples/[category]/[script_name].py
```

## FX and Volatility Examples

### 1. FX Rates (`coding_2/FXRates.py`)

**Command:**
```bash
python ../scripts/examples/coding_2/FXRates.py
```

**Expected Output:**
```
Error messages for invalid FX configurations
Array representations (3x3 numpy arrays)
Currency conversions (e.g., 1M NOK to USD = 125000)
Dual number outputs with derivatives
Position calculations and breakdowns
Forward rates with path information
Gradient calculations showing risk sensitivity
Script completed successfully!
```

**Key Features Demonstrated:**
- FX triangulation through intermediate currencies
- Automatic differentiation for risk calculations
- Forward pricing using interest rate parity

### 2. FX Volatility (`coding_2/FXVolatility.py`)

**Command:**
```bash
python ../scripts/examples/coding_2/FXVolatility.py
```

**Expected Output:**
```
Time weighting display (Pandas Series)
Curve calibration results
SABR smile calibration parameters
Option Greeks (Delta, Gamma)
NPV calculations with spot movements
Analytic Greeks comparison
Script completed successfully!
```

**Key Features:**
- Volatility surface construction
- SABR model calibration
- Sticky strike vs sticky delta comparisons

### 3. Chapter 5 FX (`coding/ch5_fx.py`)

**Command:**
```bash
python ../scripts/examples/coding/ch5_fx.py
```

**Expected Output:**
```
FX system validation messages
Cross-currency rate calculations
Dual representations with AD
Base value conversions
FX forward calculations
Delta risk equivalence demonstrations
Script completed successfully!
```

## Curve Examples

### 1. Basic Curves (`coding/curves.py`)

**Command:**
```bash
python ../scripts/examples/coding/curves.py
```

**Expected Output:**
```
CompositeCurve rate: 3.75
CompositeCurve rate with AD: 3.75
Error histogram analysis
Timing: 0.0008 (approximate)
Various rate calculations for curve operations
Script completed successfully!
```

**Known Issues:**
- Uses deprecated `approximate=True` parameter
- Some timing benchmarks may fail

### 2. Advanced Curves (`coding_2/Curves.py`)

**Command:**
```bash
python ../scripts/examples/coding_2/Curves.py
```

**Expected Output:**
```
CompositeCurve demonstrations
MultiCsaCurve timing comparisons
Shift, roll, and translate operations
Performance benchmarks
Script completed successfully!
```

### 3. Curve Solving (`coding_2/CurveSolving.py`)

**Command:**
```bash
python ../scripts/examples/coding_2/CurveSolving.py
```

**Expected Output:**
```
Script completed successfully!
```

*Note: This is a placeholder script with no actual implementation*

## Scheduling Examples

### 1. Basic Scheduling (`coding/scheduling.py`)

**Command:**
```bash
python ../scripts/examples/coding/scheduling.py
```

**Expected Error:**
```
ImportError: cannot import name '_get_unadjusted_roll' from 'rateslib.scheduling'
```

**Issue:** Uses deprecated private functions. Use modern Schedule class instead:
```python
from rateslib.scheduling import Schedule
schedule = Schedule(
    effective=dt(2023, 3, 15),
    termination=dt(2023, 9, 20),
    frequency="M",
    calendar="tgt"
)
```

### 2. Advanced Scheduling (`coding_2/Scheduling.py`)

**Command:**
```bash
python ../scripts/examples/coding_2/Scheduling.py
```

**Expected Output:**
```
Generated date lists
Roll inference results
Schedule validation results
Modern Schedule objects: <Schedule: 2024-08-17 -> 2025-08-17, S, tgt, 1>
Script completed successfully!
```

## Instrument Examples

### 1. Instruments (`coding_2/Instruments.py`)

**Command:**
```bash
python ../scripts/examples/coding_2/Instruments.py
```

**Expected Output:**
```
Script completed successfully!
```

**Silent Calculations Include:**
- UK Bond accrued: 1.43646
- Canadian Bond accrued: 1.42466
- US Bond YTM: 3.11200%
- Bill YTM: 2.50251%
- Bond prices: 96.26436

### 2. Legs (`coding_2/Legs.py`)

**Command:**
```bash
python ../scripts/examples/coding_2/Legs.py
```

**Expected Output:**
```
Script completed successfully!
```

*Note: Placeholder script with no code listings*

### 3. Periods (`coding_2/Periods.py`)

**Command:**
```bash
python ../scripts/examples/coding_2/Periods.py
```

**Expected Output:**
```
IMM Float Period fixings table:
               euribor3m                              
                notional      risk       dcf     rates
obs_dates                                             
2023-03-13  1.064857e+06  26.41081  0.255556  2.037691

Stub Float Period fixings table:
[Table with euribor1m and euribor3m data]

Timing: 27.488095
Timing: 8.514734
Script completed successfully!
```

## Advanced Examples

### 1. Automatic Differentiation (`coding_2/AutomaticDifferentiation.py`)

**Command:**
```bash
python ../scripts/examples/coding_2/AutomaticDifferentiation.py
```

**Expected Output (Enhanced Version):**
```
1. BASIC DUAL NUMBERS
------------------------------
z_x = <Dual2: 0.000000, (x), [1.0], [[...]]>
z_x * z_x = <Dual2: 0.000000, (x), [0.0], [[...]]>
Second derivatives: [[1.]]

2. CUSTOM DUAL FUNCTIONS
------------------------------
dual_sin(Dual(2.1, ['y'], [])) = <Dual: 0.863209, (y), [-0.5]>

[... continues through 10 sections ...]

======================================================================
AUTOMATIC DIFFERENTIATION DEMONSTRATION COMPLETED!
======================================================================
```

### 2. Interpolation and Splines (`coding_2/InterpolationAndSplines.py`)

**Command:**
```bash
python ../scripts/examples/coding_2/InterpolationAndSplines.py
```

**Expected Output:**
```
1. B-SPLINES WITH AUTOMATIC DIFFERENTIATION
---------------------------------------------
Created cubic B-spline (k=3)
Knot vector: [0.0, 0.0, 0.0, 4.0, 4.0, 4.0]
Spline value at 3.5: <Dual: 4.375000, (y3, y1, y2), [1.9, 0.4, -1.2]>

2. APPLICATION TO FINANCIAL CURVES
--------------------------------------
Created financial curve spline (degree 4)
Spline coefficients: [1.5, 1.65, 1.95, 1.85, 1.8]

3. LOG-SPLINE FOR DISCOUNT FACTORS
------------------------------------
Created log-spline for discount factors
Log-spline coefficients: [0.0, -0.00552, -0.01655, -0.02996, -0.03667]

4. VISUALIZATION AND VALIDATION
-----------------------------------
Plot generated (not displayed in non-interactive mode)

Spline Validation:
  2022-06-01: DF = 0.993136
  2022-09-01: DF = 0.988869
  2023-06-01: DF = 0.975319

======================================================================
SPLINE INTERPOLATION DEMONSTRATION COMPLETED!
======================================================================
```

### 3. Calendars (`coding_2/Calendars.py`)

**Command:**
```bash
python ../scripts/examples/coding_2/Calendars.py
```

**Expected Output:**
```
Timing: 0.000045  # Direct calendar lookup
Timing: 0.002156  # Calendar construction
Timing: 0.005234  # Named calendar parsing
Timing: 0.001234  # Union calendar creation
Timing: 0.000087  # Cached calendar access
Script completed successfully!
```

### 4. Cookbook (`coding_2/Cookbook.py`)

**Command:**
```bash
python ../scripts/examples/coding_2/Cookbook.py
```

**Expected Output:**
```
Script completed successfully!
```

*Note: Creates complex curves and plots but produces minimal console output*

## Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'rateslib'` | Ensure you're in `python/` directory |
| `ImportError` for private functions | Use public API alternatives |
| Matplotlib warnings | Install with `pip install matplotlib` or ignore |
| Timing variations | Normal - depends on system load |
| Deprecated parameters | Check documentation for current API |

### API Migration Guide

| Old (Private) | New (Public) |
|--------------|--------------|
| `_get_unadjusted_roll()` | `Schedule()` class |
| `_set_ad_order()` | `ad` parameter in constructor |
| `approximate=True` | Removed - use default behavior |

### Required Import Pattern

Always use this pattern for scripts:
```python
import sys
import os

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')

from rateslib import *
```

## Performance Notes

### Timing Expectations
- Float operations: ~0.001s for 1000 iterations
- Dual number operations: ~0.005s for 1000 iterations (3-5x slower)
- Curve operations: ~0.0001s per evaluation
- Spline solving: ~0.01s for typical problems

### Memory Considerations
- Dual numbers increase memory usage by factor of (1 + n_vars)
- Curve caching can be disabled with `defaults.curve_caching = False`
- Large spline problems may require significant memory

## Next Steps

After running these examples:
1. Explore the individual `.md` documentation files for each script
2. Modify examples to test different parameters
3. Combine techniques from multiple examples
4. Review test suite for additional usage patterns

## Support

For issues or questions:
- Check individual script documentation in `scripts/examples/*/[script_name].md`
- Review main documentation in `docs/SCRIPT_DOCUMENTATION.md`
- Consult test files in `python/tests/` for additional examples
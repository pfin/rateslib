# Curves.py Documentation

## Overview
Demonstrates curve operations including composition, shifting, rolling, and translation with automatic differentiation support.

## Key Concepts
- **CompositeCurve**: Sum multiple curves together
- **Curve Operations**: Shift (parallel move), Roll (time shift), Translate (reference change)
- **Automatic Differentiation**: Track sensitivities through operations
- **Approximation vs Exact**: Performance trade-offs

## Sections

### 1. CompositeCurve Example
Shows efficient operations when compositing two curves:
- Creates LineCurve objects with IDs
- Builds CompositeCurve from multiple curves
- Demonstrates rate calculation with AD

### 2. Error in Approximated Rates
Analyzes accuracy of approximation methods:
- Compares true compounded rates vs averaged approximations
- Shows error distribution histogram
- Performance comparison (approximate ~2x faster)

### 3. Curve Shift Operations
Parallel shift of entire curve:
- `curve.shift(50)`: Adds 50 basis points
- Works on both Curve and LineCurve objects
- Preserves curve shape

### 4. Curve Translate Operations
Changes reference date while preserving future values:
- Tests multiple interpolation methods
- Some methods may not support translation
- Used for scenario analysis

### 5. Curve Roll Operations
Time shifts the entire curve:
- `curve.roll("30d")`: Roll forward 30 days
- `curve.roll("-31d")`: Roll backward 31 days
- Maintains curve characteristics

### 6. Operations on CompositeCurves
All operations work on composite curves:
- Shift, roll, translate apply to all component curves
- Maintains curve relationships

## Classes
- `Curve`: Base curve with nodes and interpolation
- `LineCurve`: Linear interpolation between rate points
- `CompositeCurve`: Sum of multiple curves

## Interpolation Methods Tested
- `linear`: Linear interpolation of discount factors
- `log_linear`: Linear interpolation of log(DF)
- `linear_index`: Linear on index values
- `flat_forward`: Constant forward rates
- `flat_backward`: Constant backward rates
- `linear_zero_rate`: Linear zero rates

## Usage
```bash
cd python/
python ../scripts/examples/coding_2/Curves.py
```

## Performance Notes
- Approximation: ~2x faster than exact calculation
- Error typically < 1e-5 for daily compounding
- AD adds ~3-5x overhead vs pure floats
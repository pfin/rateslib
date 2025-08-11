# curves.py Documentation

## Overview
Demonstrates curve operations with focus on automatic differentiation and performance comparisons.

## Known Issues
This script uses private API methods that should be replaced:
- `_set_ad_order()` → Use `ad` parameter in constructor
- Should use public API throughout

## Key Concepts
- **CompositeCurve**: Combining multiple curves
- **Automatic Differentiation**: Tracking sensitivities
- **Performance Trade-offs**: Exact vs approximate calculations

## Sections

### 1. CompositeCurve with AD
Shows how to enable automatic differentiation:
```python
# Incorrect (private API):
line_curve1._set_ad_order(1)

# Correct (public API):
line_curve1 = LineCurve(..., ad=1)
```

### 2. Error Analysis
Compares approximation errors in composite rates:
- True compounded rates
- Averaged approximations
- Error distribution analysis

### 3. Performance Timing
Benchmarks approximate vs exact calculations:
- Approximate: ~2x faster
- Trade-off: Speed vs accuracy
- Errors typically < 1e-5

### 4. Curve Operations
Tests shift, roll, and translate on various curve types.

## Corrections Needed
Replace all private API usage with public equivalents.

## Usage
```bash
cd python/
python ../scripts/examples/coding/curves.py
```
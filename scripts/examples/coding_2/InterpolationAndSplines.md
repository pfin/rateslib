# InterpolationAndSplines.py Documentation

## Overview
Demonstrates spline interpolation techniques for financial curves using B-splines with automatic differentiation support.

## Key Concepts
- **B-Splines**: Piecewise polynomial interpolation with local support
- **PPSpline**: Piecewise polynomial spline implementation
- **Log-Spline**: Interpolating log of discount factors for positivity
- **Automatic Differentiation**: Splines that propagate derivatives

## Sections

### 1. Splines with Automatic Differentiation
Creates cubic B-spline with dual number support:
- Degree k=3 (cubic)
- Knot vector defines segments
- Solves with dual inputs for AD

### 2. Application to Financial Curves
Builds quartic spline (k=4) for yield curve:
- Multiple knots at boundaries for control
- B-spline matrix construction
- Boundary conditions (2nd derivative = 0)

### 3. Log-Spline for Discount Factors
Ensures positive discount factors:
- Interpolate log(DF) instead of DF directly
- Convert back: DF = exp(log_spline(t))
- Maintains monotonicity constraints

### 4. Visualization (if matplotlib available)
Plots:
- Discount factor curve from log-spline
- Implied forward rates

## Classes Used
- `PPSplineF64`: Float-based spline
- `PPSplineDual`: Dual number spline with AD

## Key Methods
- `csolve()`: Solve for spline coefficients
- `ppev_single()`: Evaluate at single point
- `bsplmatrix()`: Build B-spline basis matrix

## Boundary Conditions
- `left_n=0, right_n=0`: Natural (2nd derivative = 0)
- `left_n=1, right_n=1`: Clamped (1st derivative given)
- `left_n=2, right_n=2`: 2nd derivative specified

## Usage
```bash
cd python/
python ../scripts/examples/coding_2/InterpolationAndSplines.py
```

## Example Data Points
- Yield curve: 0% → 1.5% → 1.85% → 1.8% → 0%
- Discount factors: 1.0 → 0.983 → 0.964

## Performance
- Evaluation complexity: O(k) per point
- Memory: O(n) where n = number of coefficients
# CurveSolving.py Documentation

## Overview
Demonstrates curve solving, bootstrapping, and optimization techniques for fixed income curve construction.

## Key Concepts
- **Bootstrapping**: Sequential solving from liquid market instruments
- **Newton-Raphson**: Root finding with analytical derivatives
- **Inverse Function Theorem**: Finding inputs from target outputs
- **Nelson-Siegel Model**: Parametric yield curve fitting

## Sections

### 1. Basic Curve Construction
Creates a simple curve with known discount factor nodes and tests interpolation.

### 2. Newton-Raphson Root Finding
Implements bond YTM calculation using Newton-Raphson with exact derivatives.
- Function: `bond_price_error(ytm, bond_price, cashflows, dates, settle_date)`
- Returns pricing error and its derivative

### 3. Curve Bootstrapping
Demonstrates building a curve from market instruments:
- Short-term deposits
- Swap rates
- Sequential discount factor calculation

### 4. Inverse Function Application
Uses IFT to find rates that produce target prices:
- Example: 2-year zero coupon bond
- Find rate given price of 95.0

### 5. Multi-dimensional Curve Fitting
Nelson-Siegel yield curve model:
```
yield(t) = β₀ + β₁ * (1-exp(-t/τ))/(t/τ) + β₂ * [(1-exp(-t/τ))/(t/τ) - exp(-t/τ)]
```
Parameters: β₀ (level), β₁ (slope), β₂ (curvature), τ (decay)

## Usage
```bash
cd python/
python ../scripts/examples/coding_2/CurveSolving.py
```

## Key Functions
- `newton_1dim`: 1D Newton-Raphson solver
- `ift_1dim`: Inverse function theorem solver
- `nelson_siegel_yield`: Parametric yield curve function

## Example Market Data
- Deposits: 3M @ 2.5%, 6M @ 2.8%
- Swaps: 1Y @ 3.2%, 2Y @ 3.6%, 3Y @ 3.9%
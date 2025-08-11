# Instruments.py Documentation

## Overview
Demonstrates bond pricing, yield calculations, and various fixed income instrument metrics.

## Key Concepts
- **FixedRateBond**: Bond with regular coupon payments
- **NPV**: Net Present Value using discount curves
- **YTM**: Yield to Maturity from price
- **Duration**: Price sensitivity to yield changes
- **Convexity**: Second-order price sensitivity

## Sections

### 1. Basic Bond Creation
Creates fixed rate bond with specifications:
- Effective date (start)
- Termination date (maturity)
- Coupon rate and frequency
- Day count convention

### 2. Pricing with Curves
Calculates NPV using discount curve:
```python
npv = bond.npv(curve)
```
Process:
1. Generate cashflow schedule
2. Apply discount factors
3. Sum present values

### 3. Yield to Maturity
Solves for constant discount rate that matches market price:
```python
ytm = bond.ytm(price=102.5)
```
Uses Newton-Raphson internally.

### 4. Risk Metrics
- **DV01**: Dollar value of 1bp move
- **Duration**: Weighted average time to cashflows
- **Modified Duration**: Price sensitivity percentage
- **Convexity**: Curvature of price-yield relationship

### 5. Cashflow Analysis
Access underlying cashflows:
```python
cashflows = bond.cashflows(curve)
```
Returns DataFrame with:
- Payment dates
- Cashflow amounts
- Discount factors
- Present values

## Classes
- `FixedRateBond`: Standard coupon bond
- `FloatRateBond`: Floating rate note
- `Bill`: Zero-coupon instrument
- `BondFuture`: Bond future contract

## Common Parameters
- `effective`: Start date
- `termination`: Maturity date
- `frequency`: Payment frequency (A, S, Q, M)
- `coupon`: Annual coupon rate (%)
- `convention`: Day count (ACT360, ACT365F, 30360)
- `calendar`: Holiday calendar for adjustments
- `modifier`: Business day adjustment (MF, F, P)

## Metrics Formulas
- **Macaulay Duration**: Σ(t × PV(CF_t)) / Price
- **Modified Duration**: MacDuration / (1 + y/n)
- **DV01**: -ModDuration × Price × 0.0001
- **Convexity**: Σ(t² × PV(CF_t)) / Price

## Usage
```bash
cd python/
python ../scripts/examples/coding_2/Instruments.py
```

## Example Bond
5% semi-annual coupon, 5-year maturity:
- Cashflows: 2.5% every 6 months + 100 at maturity
- Price at 4% yield: ~104.45
- Duration: ~4.5 years
- DV01: ~0.045 per $100 face
# Legs.py Documentation

## Overview
Demonstrates the leg structure used in swaps and other multi-leg instruments, showing how cashflow streams are constructed and valued.

## Key Concepts
- **Leg**: Collection of cashflow periods
- **FixedLeg**: Regular fixed payments
- **FloatLeg**: Variable rate payments
- **IndexLeg**: Inflation or index-linked payments

## Sections

### 1. Fixed Leg Construction
Creates leg with fixed rate payments:
```python
fixed_leg = FixedLeg(
    effective=dt(2022, 1, 1),
    termination=dt(2027, 1, 1),
    frequency="Q",
    coupon=5.0
)
```

### 2. Float Leg Construction
Creates leg with floating rate payments:
- References an interest rate index
- Spread can be added to floating rate
- Reset frequency may differ from payment

### 3. Leg Periods
Each leg contains periods with:
- Start and end dates
- Accrual calculations
- Payment dates
- Day count fractions

### 4. Cashflow Generation
Process:
1. Generate schedule of periods
2. Apply rates (fixed or floating)
3. Calculate accrual amounts
4. Apply payment conventions

### 5. NPV Calculation
Present value calculation:
```python
npv = leg.npv(curve)
```
- Discounts each cashflow
- Sums to get total PV
- Can include spread adjustments

## Classes
- `FixedLeg`: Fixed rate payments
- `FloatLeg`: Floating rate payments
- `IndexLeg`: Index-linked payments
- `ZeroFloatLeg`: Zero coupon floating
- `FixedLegMtm`: Mark-to-market fixed leg

## Key Parameters
- `effective`: Start date
- `termination`: End date
- `frequency`: Payment frequency
- `coupon/spread`: Rate or spread
- `convention`: Day count convention
- `notional`: Principal amount
- `amortization`: Principal paydown schedule

## Swap Construction
Typical swap has two legs:
```python
swap = IRS(
    fixed_leg=FixedLeg(...),
    float_leg=FloatLeg(...)
)
```

## Amortization Types
- **Bullet**: Full principal at maturity
- **Linear**: Equal principal payments
- **Custom**: User-defined schedule

## Usage
```bash
cd python/
python ../scripts/examples/coding_2/Legs.py
```

## Example Output
Fixed leg quarterly payments:
- Notional: $1,000,000
- Rate: 5% annual
- Quarterly payment: ~$12,500
- Number of periods: 20 (5 years × 4)
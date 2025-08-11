# Periods.py Documentation

## Overview
Demonstrates period generation and cashflow calculations, the building blocks of legs and instruments.

## Key Concepts
- **Period**: Single accrual/payment interval
- **Cashflow**: Actual payment amount and timing
- **DCF**: Day Count Fraction calculation
- **Compounding**: How interest accumulates

## Sections

### 1. Period Creation
Individual period with dates:
```python
period = Period(
    start=dt(2022, 1, 1),
    end=dt(2022, 4, 1),
    payment=dt(2022, 4, 1)
)
```

### 2. Day Count Fractions
Different conventions for time calculation:
- **ACT/360**: Actual days / 360
- **ACT/365F**: Actual days / 365
- **30/360**: Standardized months
- **ACT/ACT**: Actual/Actual ISDA

### 3. Cashflow Calculation
From period to cashflow:
1. Calculate DCF
2. Apply rate
3. Multiply by notional
4. Account for amortization

### 4. Stub Periods
Handling irregular first/last periods:
- **Short stub**: Less than full period
- **Long stub**: More than full period
- **Front/Back**: Position of stub

### 5. Compounding Methods
For periods longer than rate frequency:
- **Simple**: No compounding
- **Compounded**: Geometric compounding
- **Continuous**: Exponential

## Classes
- `Period`: Base period class
- `FixedPeriod`: Fixed rate period
- `FloatPeriod`: Floating rate period
- `IndexPeriod`: Index-linked period

## Period Attributes
- `start`: Accrual start date
- `end`: Accrual end date
- `payment`: Payment date
- `dcf`: Day count fraction
- `notional`: Principal amount
- `rate`: Applicable rate
- `cashflow`: Calculated payment

## Schedule Generation
From schedule to periods:
```python
schedule = Schedule(
    effective=start_date,
    termination=end_date,
    frequency="Q"
)
periods = [Period(s, e, e) for s, e in schedule.periods()]
```

## Business Day Adjustments
- **Following**: Next business day
- **Modified Following**: Next unless different month
- **Preceding**: Previous business day
- **Modified Preceding**: Previous unless different month

## Usage
```bash
cd python/
python ../scripts/examples/coding_2/Periods.py
```

## Example Period
Q1 2022 with quarterly frequency:
- Start: 2022-01-01
- End: 2022-04-01
- DCF (ACT/360): 90/360 = 0.25
- Rate: 5% annual
- Cashflow: 1,000,000 × 0.05 × 0.25 = $12,500
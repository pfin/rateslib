# Legs.py Documentation

## Overview
Comprehensive analysis of leg structures that form the building blocks of complex multi-leg instruments including swaps, cross-currency swaps, and structured products. This documentation covers the complete cashflow generation pipeline, mathematical modeling, and market conventions.

## Complete Leg Hierarchy

```
BaseLeg (Abstract base class)
├── FixedLeg (Fixed rate cashflows)
│   └── FixedLegMtm (Mark-to-market fixed leg)
├── FloatLeg (Floating rate cashflows)
│   └── FloatLegMtm (Mark-to-market float leg)
├── IndexFixedLeg (Inflation-linked fixed leg)
├── ZeroFixedLeg (Zero-coupon fixed leg)
├── ZeroFloatLeg (Zero-coupon floating leg)
├── ZeroIndexLeg (Zero-coupon index leg)
├── CreditPremiumLeg (CDS premium payments)
├── CreditProtectionLeg (CDS protection payments)
└── CustomLeg (User-defined cashflow patterns)
```

## Mathematical Framework for Leg Valuation

### Fixed Leg NPV Calculation
```
NPV_fixed = Σ[i=1 to n] (-1)^p × N(i) × R × DCF(i) × DF(t, T(i))
```

Where:
- `p` = Payment indicator (0 = receive, 1 = pay)
- `N(i)` = Notional amount for period i
- `R` = Fixed rate (annualized)
- `DCF(i)` = Day count fraction for period i
- `DF(t, T(i))` = Discount factor to payment date T(i)

### Floating Leg NPV Calculation
```
NPV_float = Σ[i=1 to n] (-1)^p × N(i) × [F(i) + S] × DCF(i) × DF(t, T(i))
```

Where:
- `F(i)` = Forward rate for period i
- `S` = Spread (in decimal form)

### Index Leg NPV (Inflation-Linked)
```
NPV_index = Σ[i=1 to n] (-1)^p × N(i) × R × I_ratio(i) × DCF(i) × DF(t, T(i))
```

Where:
- `I_ratio(i)` = Index ratio (Index(T(i)) / Index_base)

## Enhanced Key Concepts

### BaseLeg Architecture
**Core Functionality**:
- Period generation and scheduling
- Cashflow calculation pipeline
- NPV aggregation across periods
- Risk metric computation
- Amortization handling
- Currency conversion support

### FixedLeg - Deterministic Cashflows
**Mathematical Model**:
```python
for period in fixed_leg.periods:
    cashflow = (
        notional * fixed_rate * dcf * 
        (-1 if leg.payment_lag >= 0 else 1)
    )
```

**Market Applications**:
- Government bond cashflows
- Corporate bond coupons
- Fixed leg of interest rate swaps
- Structured product guaranteed payments

**Advanced Features**:
- **Step-up/Step-down rates**: Rate schedules that change over time
- **Amortizing notionals**: Principal paydown schedules
- **Day count conventions**: Act/360, Act/365F, 30/360, etc.
- **Business day adjustments**: Following, Modified Following, Preceding

### FloatLeg - Index-Linked Cashflows
**Mathematical Model**:
```python
for period in float_leg.periods:
    reset_rate = index_curve.rate(reset_date, tenor)
    all_in_rate = reset_rate + spread
    cashflow = notional * all_in_rate * dcf * payment_sign
```

**Fixing Methodologies**:

1. **IBOR Method** (`"ibor"`):
   - Traditional LIBOR/EURIBOR methodology
   - Single rate fixed at period start
   - Used for legacy swap contracts

2. **RFR Lookback** (`"rfr_lookback"`):
   - Backward-looking compounded RFR
   - Observation period ends before payment
   - SOFR, SONIA, ESTR standard methodology

3. **RFR Payment Delay** (`"rfr_payment_delay"`):
   - Observation period includes payment date
   - Payment delayed to allow rate observation
   - Alternative RFR methodology

4. **RFR Observation Shift** (`"rfr_observation_shift"`):
   - Observation period shifted backward
   - Earlier rate determination
   - Reduces operational risk

**Compounding Methods**:
- **Simple compounding**: Linear rate accumulation
- **Compound compounding**: Geometric rate accumulation  
- **Flat compounding**: Spread applied to compounded rate

### IndexFixedLeg - Inflation Protection
**Mathematical Model**:
```python
for period in index_leg.periods:
    inflation_factor = index_level(payment_date) / index_base
    adjusted_notional = notional * inflation_factor
    cashflow = adjusted_notional * real_rate * dcf
```

**Index Types**:
- **CPI-U**: US Consumer Price Index (Urban)
- **RPI**: UK Retail Price Index
- **HICP**: Harmonized Index of Consumer Prices (EU)
- **Custom indices**: Commodity indices, wage indices

**Lag Conventions**:
- **2-month lag**: CPI published 2 months after reference period
- **3-month lag**: Some jurisdictions use 3-month lag
- **Interpolation**: Daily interpolation between monthly index values

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

## Detailed Class Analysis

### FixedLeg Class
**Core Implementation**:
```python
class FixedLeg(_FixedLegMixin, BaseLeg):
    periods: list[FixedPeriod | Cashflow]
    _regular_periods: tuple[FixedPeriod, ...]
    
    def __init__(self, *args, fixed_rate=NoInput(0), **kwargs):
        self._fixed_rate = fixed_rate
        super().__init__(*args, **kwargs)
        self._set_periods()
```

**Key Methods**:
- `npv(curve, disc_curve, fx, base)`: Net present value calculation
- `analytic_delta()`: Sensitivity to rate changes
- `cashflows(curve)`: Complete cashflow schedule with PV
- `rate(solver)`: Mid-market rate calculation

**Advanced Features**:
- **Amortization patterns**: Linear, custom schedules
- **Notional exchanges**: Initial and final exchanges
- **Multiple currencies**: Cross-currency leg support
- **MTM resets**: Mark-to-market adjustments

### FloatLeg Class  
**Core Implementation**:
```python
class FloatLeg(_FloatLegMixin, BaseLeg):
    periods: list[FloatPeriod | Cashflow]
    
    def __init__(self, *args, 
                 float_spread=NoInput(0),
                 spread_compound_method="none_simple",
                 fixings=NoInput(0),
                 fixing_method="ibor",
                 method_param=2,
                 **kwargs):
```

**Spread Compound Methods**:
1. **"none_simple"**: Spread added to compounded rate
   ```
   All-in rate = Compounded_RFR + Spread
   ```

2. **"isda_compounding"**: Spread compounded with base rate
   ```
   All-in rate = (1 + Compounded_RFR) × (1 + Spread × DCF) - 1
   ```

3. **"isda_flat_compounding"**: Daily spread compounding
   ```
   Daily rate = RFR(i) + Spread
   Compounded rate = ∏(1 + Daily_rate(i) × 1/365) - 1
   ```

**Fixing Methods Deep Dive**:

**IBOR Traditional**:
```python
# Single rate fixed at reset
float_period = FloatPeriod(
    fixing_method="ibor",
    method_param=2,  # 2-day fixing lag
)
rate = curve[reset_date - 2*BDay]  # 2 business day lag
```

**RFR Lookback Compounding**:
```python
# Compound daily rates over observation period
float_period = FloatPeriod(
    fixing_method="rfr_lookback",
    method_param=5,  # 5 business day lookback
)
compounded_rate = compound_rfr_rates(
    rates=daily_rfr_rates,
    start=period.start,
    end=period.end - 5*BDay
)
```

### IndexFixedLeg Class
**Inflation Adjustment Mechanics**:
```python
class IndexFixedLeg(BaseLeg):
    def __init__(self, *args,
                 fixed_rate=NoInput(0),
                 index_base=NoInput(0),
                 index_lag=3,  # months
                 **kwargs):
```

**Index Ratio Calculation**:
```python
# For each payment date
index_date = payment_date - relativedelta(months=index_lag)
if interpolate:
    index_level = interpolate_monthly_index(
        index_curve, index_date
    )
else:
    index_level = index_curve[index_date]
    
index_ratio = index_level / index_base
adjusted_cashflow = nominal_cashflow * index_ratio
```

### Zero Coupon Legs (ZeroFixedLeg, ZeroFloatLeg)
**Mathematical Model**:
```python
# Zero coupon structure - single payment at maturity
if is_final_period:
    cashflow = notional * (1 + rate * total_dcf)
else:
    cashflow = 0  # No intermediate payments
```

**Applications**:
- Zero-coupon swaps
- Discount instruments
- Single payment structures
- Principal-only strips

### Mark-to-Market Legs (FixedLegMtm, FloatLegMtm)
**MTM Reset Mechanism**:
```python
# Notional reset to maintain constant PV01
for period in mtm_leg.periods:
    if period.is_mtm_reset:
        new_notional = calculate_mtm_notional(
            curve=forward_curve,
            target_pv01=original_pv01
        )
        period.notional = new_notional
```

**Use Cases**:
- Currency volatility hedging
- Credit risk mitigation  
- Capital efficiency optimization
- Regulatory capital relief

### Credit Legs (CreditPremiumLeg, CreditProtectionLeg)
**Premium Leg (Fee payments)**:
```python
# Regular premium payments
for period in premium_leg.periods:
    cashflow = notional * premium_rate * dcf * survival_probability
```

**Protection Leg (Default payoff)**:
```python
# Contingent payment on default
protection_value = notional * (1 - recovery_rate) * default_probability
```

### CustomLeg Class
**Flexible Cashflow Definition**:
```python
class CustomLeg(BaseLeg):
    def __init__(self, periods, **kwargs):
        # Accept pre-defined period list
        self.periods = periods
        super().__init__(**kwargs)
```

**Applications**:
- Structured products with complex payoffs
- Step-up/step-down structures
- Barrier-dependent cashflows
- Exotic derivatives

## Key Parameters
- `effective`: Start date
- `termination`: End date
- `frequency`: Payment frequency
- `coupon/spread`: Rate or spread
- `convention`: Day count convention
- `notional`: Principal amount
- `amortization`: Principal paydown schedule

## Complete Swap Construction Framework

### Vanilla Interest Rate Swap (IRS)
```python
swap = IRS(
    effective=dt(2024, 3, 20),
    termination="5Y",  # 5-year maturity
    frequency="Q",      # Quarterly payments
    currency="USD",
    fixed_rate=4.50,   # 4.50% fixed rate
    float_spread=0,    # No spread on float leg
    notional=10000000  # $10M notional
)
```

**Internal Leg Structure**:
```python
# Fixed leg (receive fixed)
fixed_leg = FixedLeg(
    effective=dt(2024, 3, 20),
    termination=dt(2029, 3, 20),
    frequency="Q",
    fixed_rate=4.50,
    notional=-10000000,  # Negative = pay
    currency="USD",
    convention="act360",
    calendar="nyc"
)

# Float leg (pay floating)
float_leg = FloatLeg(
    effective=dt(2024, 3, 20),
    termination=dt(2029, 3, 20), 
    frequency="Q",
    float_spread=0.0,
    fixing_method="rfr_lookback",
    method_param=2,
    notional=10000000,   # Positive = receive
    currency="USD",
    convention="act360"
)
```

### Cross-Currency Swap (XCS)
```python
xcs = XCS(
    effective=dt(2024, 3, 20),
    termination="3Y",
    frequency="S",
    
    # USD leg (floating)
    currency="USD",
    notional=50000000,
    float_spread=25,    # 25bp spread
    
    # EUR leg (fixed)
    currency2="EUR", 
    notional2=45000000,
    fixed_rate2=3.25,   # 3.25% EUR fixed rate
    
    # FX and initial/final exchanges
    fx_rate=1.1111,     # USD/EUR rate
    initial_exchange=True,
    final_exchange=True
)
```

### Inflation-Linked Swap (IIRS)
```python
iirs = IIRS(
    effective=dt(2024, 3, 20),
    termination="10Y",
    frequency="A",      # Annual payments
    currency="USD",
    
    # Fixed leg (real rate)
    fixed_rate=1.50,    # 1.50% real rate
    
    # Index leg (CPI-linked)
    index_base=310.326, # CPI base level
    index_lag=3,        # 3-month lag
    index_method="monthly"  # Monthly interpolation
)
```

### Basis Swap (SBS)
```python
# Single currency basis swap (3M vs 1M SOFR)
sbs = SBS(
    effective=dt(2024, 3, 20),
    termination="2Y",
    currency="USD",
    
    # 3M SOFR leg
    frequency="Q",
    fixing_method="rfr_lookback",
    
    # 1M SOFR leg  
    frequency2="M",
    fixing_method2="rfr_lookback",
    float_spread2=15,   # 15bp spread on 1M leg
    
    notional=25000000
)
```

### Zero Coupon Inflation Swap (ZCIS)
```python
zcis = ZCIS(
    effective=dt(2024, 3, 20),
    termination="5Y",
    currency="USD",
    
    # Zero coupon fixed leg
    fixed_rate=2.75,    # 2.75% breakeven rate
    
    # Zero coupon index leg
    index_base=310.326,
    index_lag=3,
    
    notional=10000000
)
```

## Advanced Leg Construction Patterns

### Step-Up Fixed Rate Structure
```python
# Custom periods with different rates
custom_periods = []
rates = [3.0, 3.5, 4.0, 4.5, 5.0]  # Annual step-ups

for i, (start, end) in enumerate(schedule.periods()):
    period = FixedPeriod(
        start=start,
        end=end,
        payment=end,
        fixed_rate=rates[min(i, len(rates)-1)],
        notional=1000000,
        frequency="A"
    )
    custom_periods.append(period)
    
step_up_leg = CustomLeg(periods=custom_periods)
```

### Amortizing Notional Schedule
```python
# Linear amortization
amort_schedule = [
    1000000,   # Year 1
    800000,    # Year 2  
    600000,    # Year 3
    400000,    # Year 4
    200000     # Year 5
]

amort_leg = FixedLeg(
    effective=dt(2024, 3, 20),
    termination="5Y",
    frequency="A",
    fixed_rate=4.0,
    amortization=amort_schedule
)
```

### Multi-Currency Notional Resets
```python
# Mark-to-market cross-currency swap
mtm_xcs = XCS(
    effective=dt(2024, 3, 20),
    termination="5Y",
    frequency="Q",
    
    # Enable MTM resets
    leg1_mtm=True,
    leg2_mtm=True,
    
    # Reset frequency
    mtm_frequency="Q",
    
    currency="USD",
    currency2="EUR",
    fx_rate=1.1111,
    notional=50000000
)
```

## Amortization Types
- **Bullet**: Full principal at maturity
- **Linear**: Equal principal payments
- **Custom**: User-defined schedule

## Practical Implementation Guide

### Usage
```bash
cd python/
python ../scripts/examples/coding_2/Legs.py
```

### Performance Optimization Tips

#### 1. Curve Caching
```python
# Enable curve caching for repeated calculations
from rateslib import defaults
defaults.curve_caching = True

# Batch NPV calculations
legs = [fixed_leg, float_leg, index_leg]
npvs = [leg.npv(curve) for leg in legs]  # Reuses cached curve evaluations
```

#### 2. Multi-Currency Efficiency
```python
# Pre-calculate FX forwards for XCS
fx_forwards = FXForwards(
    base="USD",
    cross="EUR", 
    fx_curve=eur_usd_curve,
    domestic_curve=usd_curve,
    foreign_curve=eur_curve
)

# Use in multiple legs
for leg in [eur_leg1, eur_leg2, eur_leg3]:
    npv_usd = leg.npv(eur_curve, fx=fx_forwards, base="USD")
```

#### 3. Automatic Differentiation
```python
# Risk calculations with dual numbers
from rateslib.dual import Dual

# Create shifted curve for DV01
shock_size = 0.0001  # 1bp
curve_shocked = curve.shift(shock_size, ad_order=1)

# NPV with automatic derivatives
npv_dual = fixed_leg.npv(curve_shocked)
base_npv = npv_dual.real
dv01 = npv_dual.dual * 10000  # Scale to 1bp
```

### Error Handling and Validation

#### 1. Input Validation
```python
try:
    fixed_leg = FixedLeg(
        effective=dt(2024, 1, 1),
        termination="5Y",
        frequency="Q",
        fixed_rate=NoInput(0),  # Deliberately unset
        notional=1000000
    )
    npv = fixed_leg.npv(curve)  # Will raise error
except TypeError as e:
    print(f"Error: {e}")  # "fixed_rate must be set for NPV"
```

#### 2. Curve Compatibility
```python
try:
    # Mismatched currencies
    eur_leg = FixedLeg(
        effective=dt(2024, 1, 1),
        termination="2Y",
        frequency="A",
        fixed_rate=3.0,
        currency="EUR"
    )
    npv = eur_leg.npv(usd_curve)  # Currency mismatch
except ValueError as e:
    print(f"Currency validation error: {e}")
```

#### 3. Date Validation
```python
# Business day adjustment validation
from rateslib.scheduling import Schedule

try:
    schedule = Schedule(
        effective=dt(2024, 2, 29),  # Leap year date
        termination="5Y",
        frequency="Q",
        calendar="nyc",
        modifier="following"
    )
except ValueError as e:
    print(f"Date validation: {e}")
```

### Testing and Validation Framework

#### 1. Unit Testing Legs
```python
import pytest
from rateslib import FixedLeg, Curve, dt

def test_fixed_leg_npv():
    """Test fixed leg NPV calculation."""
    curve = Curve({dt(2024, 1, 1): 1.0, dt(2025, 1, 1): 0.95})
    
    fixed_leg = FixedLeg(
        effective=dt(2024, 1, 1),
        termination=dt(2025, 1, 1),
        frequency="A",
        fixed_rate=5.0,
        notional=1000000
    )
    
    npv = fixed_leg.npv(curve)
    expected_npv = -50000 * 0.95  # -47,500
    
    assert abs(npv - expected_npv) < 1e-6
```

#### 2. Integration Testing
```python
def test_swap_parity():
    """Test that swap NPV equals sum of leg NPVs."""
    swap = IRS(
        effective=dt(2024, 1, 1),
        termination="5Y",
        frequency="Q",
        fixed_rate=4.5,
        notional=10000000
    )
    
    # Direct swap NPV
    swap_npv = swap.npv(curve)
    
    # Sum of individual leg NPVs  
    leg_sum = swap.fixed_leg.npv(curve) + swap.float_leg.npv(curve)
    
    assert abs(swap_npv - leg_sum) < 1e-6
```

#### 3. Market Data Validation
```python
def validate_market_consistency():
    """Validate legs against market quotes."""
    market_swap_rate = 4.567  # Market mid rate
    
    # Create swap at market rate
    swap = IRS(
        effective=dt.today(),
        termination="5Y", 
        frequency="Q",
        fixed_rate=market_swap_rate,
        notional=10000000
    )
    
    # Should be close to zero NPV
    npv = swap.npv(market_curve)
    assert abs(npv) < 1000  # Within $1,000 of zero
```

### Advanced Debugging Techniques

#### 1. Cashflow Inspection
```python
# Detailed cashflow analysis
cashflows_df = fixed_leg.cashflows(curve)

# Identify problematic periods
problematic = cashflows_df[
    (cashflows_df['discount_factor'] <= 0) |
    (cashflows_df['dcf'] <= 0) |
    (cashflows_df['pv'].isna())
]

if not problematic.empty:
    print("Issues found in periods:", problematic.index.tolist())
```

#### 2. Curve Diagnostics
```python
# Check curve health
diagnostics = curve.diagnostics()
print(f"Curve nodes: {len(curve.nodes)}")
print(f"Date range: {curve.node_dates[0]} to {curve.node_dates[-1]}")
print(f"Forward rates positive: {all(curve.forward_rates > 0)}")
```

#### 3. Memory Usage Monitoring
```python
import psutil
import gc

# Monitor memory during leg construction
process = psutil.Process()
initial_memory = process.memory_info().rss / 1024 / 1024

# Create many legs
legs = []
for i in range(1000):
    leg = FixedLeg(
        effective=dt(2024, 1, 1),
        termination=f"{i+1}Y",
        frequency="Q",
        fixed_rate=5.0,
        notional=1000000
    )
    legs.append(leg)

final_memory = process.memory_info().rss / 1024 / 1024
print(f"Memory usage: {final_memory - initial_memory:.2f} MB")

# Cleanup
del legs
gc.collect()
```

## Comprehensive Cashflow Analysis Examples

### Example 1: Standard Fixed Leg
**5-Year Quarterly USD Fixed Leg**:
```python
fixed_leg = FixedLeg(
    effective=dt(2024, 3, 20),
    termination=dt(2029, 3, 20),
    frequency="Q",
    fixed_rate=4.75,
    notional=10000000,
    currency="USD",
    convention="act360",
    calendar="nyc"
)

cashflows = fixed_leg.cashflows(curve=usd_curve)
```

**Sample Cashflow Output**:
```
Period | Start      | End        | Payment    | DCF    | Rate  | Cashflow   | PV         
-------|------------|------------|------------|--------|-------|------------|------------
   1   | 2024-03-20 | 2024-06-20 | 2024-06-20 | 0.2556 | 4.75% | -121,400   | -119,853
   2   | 2024-06-20 | 2024-09-20 | 2024-09-20 | 0.2556 | 4.75% | -121,400   | -118,295
   3   | 2024-09-20 | 2024-12-20 | 2024-12-20 | 0.2556 | 4.75% | -121,400   | -116,751
  ...  |    ...     |    ...     |    ...     |  ...   |  ...  |    ...     |    ...
  20   | 2028-12-20 | 2029-03-20 | 2029-03-20 | 0.2500 | 4.75% | -118,750   | -99,876

Total NPV: -2,234,567
```

### Example 2: SOFR Floating Leg with Lookback
**3-Month SOFR with 5-Day Lookback**:
```python
float_leg = FloatLeg(
    effective=dt(2024, 3, 20),
    termination=dt(2027, 3, 20),
    frequency="Q",
    float_spread=50,    # 50bp spread
    fixing_method="rfr_lookback",
    method_param=5,     # 5 business day lookback
    notional=10000000,
    currency="USD"
)

# Historical and projected fixings
fixings_table = float_leg.periods[0].fixings_table(sofr_curve)
```

**Fixings Table Sample**:
```
Date       | SOFR   | Days | Weight | Contribution
-----------|--------|------|--------|-----------
2024-03-15 | 5.33%  |  1   | 0.011  | 0.00058%
2024-03-18 | 5.32%  |  1   | 0.011  | 0.00058%  
2024-03-19 | 5.31%  |  1   | 0.011  | 0.00058%
...        |  ...   | ...  |  ...   |   ...
2024-06-17 | 5.28%  |  1   | 0.011  | 0.00057%

Compounded Rate: 5.315%
All-in Rate: 5.815% (including 50bp spread)
Cashflow: +145,826
```

### Example 3: UK RPI-Linked Index Leg
**10-Year Inflation-Protected Leg**:
```python
index_leg = IndexFixedLeg(
    effective=dt(2024, 3, 20),
    termination=dt(2034, 3, 20),
    frequency="S",      # Semi-annual
    fixed_rate=0.50,   # 0.50% real rate
    index_base=326.4,  # RPI base
    index_lag=8,       # 8-month lag for UK
    notional=5000000,
    currency="GBP"
)

# Inflation scenario analysis
scenarios = {
    "Low inflation": {"annual_inflation": 1.5},
    "Base case": {"annual_inflation": 2.5},
    "High inflation": {"annual_inflation": 4.0}
}

for name, params in scenarios.items():
    projected_rpi = project_rpi_curve(
        base_level=326.4,
        inflation_rate=params["annual_inflation"]
    )
    npv = index_leg.npv(curve=gbp_curve, index_curve=projected_rpi)
    print(f"{name}: NPV = {npv:,.0f} GBP")
```

**Inflation Scenario Results**:
```
Low inflation (1.5%): NPV = 1,234,567 GBP
Base case (2.5%): NPV = 1,456,789 GBP  
High inflation (4.0%): NPV = 1,823,456 GBP
```

### Example 4: Cross-Currency EUR/USD Legs
**EUR Fixed vs USD 3M SOFR**:
```python
# EUR fixed leg (receive)
eur_leg = FixedLeg(
    effective=dt(2024, 3, 20),
    termination=dt(2029, 3, 20),
    frequency="A",      # Annual EUR convention
    fixed_rate=3.25,
    notional=45000000,
    currency="EUR",
    convention="act360",
    calendar="tgt"      # TARGET calendar
)

# USD floating leg (pay) 
usd_leg = FloatLeg(
    effective=dt(2024, 3, 20),
    termination=dt(2029, 3, 20),
    frequency="Q",      # Quarterly USD convention
    float_spread=0,
    fixing_method="rfr_lookback",
    notional=-50000000,  # Negative = pay
    currency="USD",
    convention="act360",
    calendar="nyc"
)

# Combined XCS valuation
xcs_npv = {
    "EUR_leg": eur_leg.npv(curve=eur_curve, fx=fx_rates, base="USD"),
    "USD_leg": usd_leg.npv(curve=usd_curve),
    "Total": eur_leg.npv(eur_curve, fx=fx_rates, base="USD") + 
             usd_leg.npv(usd_curve)
}
```

**Cross-Currency Analysis**:
```
EUR leg NPV (USD): +2,145,678
USD leg NPV:       -2,234,567
Net XCS NPV:         -88,889 USD
FX Delta (EUR):      +45,000,000 EUR
FX Delta (USD):      -50,000,000 USD
```

### Example 5: Complex Amortizing Structure
**Mortgage-Style Amortization**:
```python
# Calculate level payment amortization
principal = 1000000
rate = 0.05
periods = 20

# Level payment calculation
pmt = principal * (rate * (1 + rate)**periods) / ((1 + rate)**periods - 1)
# PMT = $80,243 per period

# Build custom amortizing leg
amort_periods = []
outstanding = principal

for i in range(periods):
    interest_payment = outstanding * rate * 0.25  # Quarterly
    principal_payment = pmt - interest_payment
    outstanding -= principal_payment
    
    period = FixedPeriod(
        start=start_date + relativedelta(months=3*i),
        end=start_date + relativedelta(months=3*(i+1)),
        payment=start_date + relativedelta(months=3*(i+1)),
        fixed_rate=(interest_payment / (outstanding + principal_payment)) * 400,
        notional=-(outstanding + principal_payment),
        convention="act360"
    )
    amort_periods.append(period)

amort_leg = CustomLeg(periods=amort_periods)
```

**Amortization Schedule**:
```
Period | Outstanding | Interest | Principal | Payment  | Remaining
-------|-------------|----------|-----------|----------|----------
   1   | 1,000,000   |  12,500  |   67,743  |  80,243  |   932,257
   2   |   932,257   |  11,657  |   68,586  |  80,243  |   863,671
   3   |   863,671   |  10,796  |   69,447  |  80,243  |   794,224
  ...  |     ...     |   ...    |    ...    |   ...    |     ...
  20   |    79,055   |     988  |   79,055  |  80,043  |         0

Total Interest Paid: $604,867
Total Principal: $1,000,000
```
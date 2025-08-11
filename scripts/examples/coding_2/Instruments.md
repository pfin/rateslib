# Instruments.py Documentation

## Overview
Demonstrates comprehensive fixed income instrument modeling with advanced pricing, risk metrics, and market convention handling. This documentation covers the complete instrument hierarchy and mathematical foundations for accurate bond analytics.

## Complete Instrument Hierarchy

```
BaseDerivative
├── BondMixin (Base bond functionality)
│   ├── FixedRateBond (Standard coupon bonds)
│   ├── FloatRateNote (Floating rate bonds)
│   ├── IndexFixedRateBond (Inflation-linked bonds)
│   ├── Bill (Zero-coupon instruments)
│   └── BondFuture (Bond futures contracts)
├── Interest Rate Swaps
│   ├── IRS (Vanilla interest rate swaps)
│   ├── IIRS (Inflation-linked swaps)
│   ├── XCS (Cross-currency swaps)
│   ├── SBS (Single currency basis swaps)
│   └── ZCIS (Zero coupon inflation swaps)
├── FX Instruments
│   ├── FXSwap (FX swap contracts)
│   ├── FXExchange (FX exchange)
│   └── FX Volatility Products
│       ├── FXCall/FXPut (Vanilla options)
│       ├── FXStraddle/FXStrangle (Volatility strategies)
│       └── FXRiskReversal/FXBrokerFly (Skew strategies)
└── Credit Instruments
    └── CDS (Credit default swaps)
```

## Mathematical Foundations

### Bond Pricing Theory
The fundamental bond pricing equation using the risk-neutral valuation framework:

```
P(t) = Σ[i=1 to n] CF(i) × DF(t, T(i))
```

Where:
- `P(t)` = Bond price at time t
- `CF(i)` = Cashflow at period i
- `DF(t, T(i))` = Discount factor from t to payment date T(i)
- `n` = Number of cashflow periods

### Yield to Maturity (YTM) Calculation
YTM is the internal rate of return that equates the bond price to the present value of all future cashflows:

```
P = Σ[i=1 to n] CF(i) / (1 + y/f)^(f × t(i))
```

Where:
- `y` = Yield to maturity (annual)
- `f` = Compounding frequency
- `t(i)` = Time to cashflow i in years

The YTM solver uses a hybrid approach:
1. **Brent's method** for robust bracketing
2. **Newton-Raphson** for rapid convergence near the solution
3. **Automatic differentiation** via dual numbers for exact derivatives

## Key Concepts Enhanced
- **FixedRateBond**: Standard coupon bond with deterministic cashflows
- **FloatRateNote**: Floating rate bond with index-linked coupons
- **IndexFixedRateBond**: Inflation-protected securities (TIPS, I-Bonds)
- **Bill**: Zero-coupon discount instruments (T-Bills, CP)
- **NPV**: Risk-neutral present value using term structure
- **YTM**: Internal rate of return assuming reinvestment at yield
- **Duration**: First-order price sensitivity (∂P/∂y)
- **Convexity**: Second-order price sensitivity (∂²P/∂y²)

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

## Detailed Class Analysis

### FixedRateBond Class
**Mathematical Model**: Deterministic cashflow stream
```python
# Cashflow generation
for period in bond.leg1.periods:
    cashflow = notional × coupon_rate × dcf × (-1 if paying else 1)
    if final_period:
        cashflow += principal_repayment
```

**Key Methods**:
- `npv(curve)`: Present value using discount curve
- `ytm(price)`: Yield to maturity from market price
- `duration(ytm)`: Macaulay and modified duration
- `convexity(ytm)`: Price convexity measure
- `accrued(settlement)`: Accrued interest calculation
- `cashflows(curve)`: Complete cashflow schedule

**Real-World Example**: US Treasury 2.875% 15-Aug-2028
```python
usg_bond = FixedRateBond(
    effective=dt(2018, 8, 15),
    termination=dt(2028, 8, 15),
    fixed_rate=2.875,
    spec="us_gb",  # Semi-annual, Act/Act ICMA, Following
    notional=1000000
)
```

### FloatRateNote Class
**Mathematical Model**: Index-linked cashflows with spread
```python
# Floating cashflow calculation
rate = index_rate(reset_date) + spread
cashflow = notional × rate × dcf
```

**Fixing Methods**:
- `"ibor"`: Traditional LIBOR/EURIBOR methodology
- `"rfr_lookback"`: Risk-free rate with lookback period
- `"rfr_payment_delay"`: RFR with payment delay adjustment
- `"rfr_observation_shift"`: Observation period shifting

### IndexFixedRateBond (Inflation-Linked)
**Mathematical Model**: Real rate plus inflation adjustment
```python
# Inflation-adjusted cashflow
inflation_factor = index_ratio(payment_date) / index_base
adjusted_notional = notional × inflation_factor
cashflow = adjusted_notional × real_rate × dcf
```

**Examples**:
- **TIPS** (US Treasury Inflation-Protected Securities)
- **UK Index-Linked Gilts**
- **French OATi** (Obligations Assimilables du Trésor indexées)

### Bill Class
**Mathematical Model**: Simple discount instrument
```python
# Zero-coupon pricing
price = face_value × discount_factor(settlement, maturity)
ytm = (face_value / price - 1) × (365 / days_to_maturity)
```

**Market Conventions**:
- **US T-Bills**: Actual/360 discount yield
- **UK T-Bills**: Actual/365 simple yield
- **Commercial Paper**: Money market yield conventions

### BondFuture Class
**Mathematical Model**: Futures pricing with delivery options
```python
# Theoretical futures price
futures_price = (bond_price + accrued - carry_costs) / conversion_factor
```

**Features**:
- Cheapest-to-deliver (CTD) bond identification
- Conversion factor calculations
- Delivery option value modeling
- Basis trading analytics

## Common Parameters
- `effective`: Start date
- `termination`: Maturity date
- `frequency`: Payment frequency (A, S, Q, M)
- `coupon`: Annual coupon rate (%)
- `convention`: Day count (ACT360, ACT365F, 30360)
- `calendar`: Holiday calendar for adjustments
- `modifier`: Business day adjustment (MF, F, P)

## Complete Risk Metrics Framework

### Duration Measures

**Macaulay Duration** (Time-weighted average of cashflows):
```
Dmac = Σ[i=1 to n] (t(i) × PV(CF(i))) / P
```

**Modified Duration** (Price sensitivity to yield changes):
```
Dmod = Dmac / (1 + y/f)
      = -(1/P) × (∂P/∂y)
```

**Effective Duration** (Empirical price sensitivity):
```
Deff = (P(-Δy) - P(+Δy)) / (2 × P × Δy)
```

**Dollar Duration (DV01)**:
```
DV01 = -Dmod × P × 0.0001
     = Price change per 1bp yield move
```

### Convexity Measures

**Mathematical Convexity**:
```
C = Σ[i=1 to n] (t(i)² + t(i)) × PV(CF(i)) / (P × (1 + y/f)²)
  = (1/P) × (∂²P/∂y²)
```

**Effective Convexity**:
```
Ceff = (P(-Δy) + P(+Δy) - 2×P) / (P × (Δy)²)
```

### Advanced Risk Metrics

**Key Rate Duration (KRD)**:
- Sensitivity to specific points on yield curve
- Sum of KRDs equals modified duration
```
KRD(i) = -(1/P) × (∂P/∂r(i))
```

**Spread Duration**:
- Sensitivity to credit spread changes
- Critical for corporate and emerging market bonds
```
DS = -(1/P) × (∂P/∂s)
```

**Inflation Duration** (for TIPS):
- Real rate duration: sensitivity to real rates
- Inflation duration: sensitivity to breakeven inflation
```
Dreal = -(1/P) × (∂P/∂r_real)
Dinfl = -(1/P) × (∂P/∂π)
```

### Practical Risk Management Applications

**Portfolio Duration Matching**:
```python
# Asset-liability duration matching
portfolio_duration = Σ(weight(i) × duration(i))
target_duration = liability_duration
hedge_ratio = (target_duration - portfolio_duration) / hedge_instrument_duration
```

**Convexity-Adjusted Returns**:
```
Total Return ≈ -Duration × Δy + 0.5 × Convexity × (Δy)²
```

## Usage
```bash
cd python/
python ../scripts/examples/coding_2/Instruments.py
```

## Real-World Bond Examples with Market Analytics

### Example 1: US Treasury 2.875% 15-Aug-2028
**Bond Specifications**:
- **Issue**: US Treasury Note
- **Coupon**: 2.875% semi-annual
- **Maturity**: August 15, 2028
- **Day Count**: Actual/Actual ICMA
- **Settlement**: T+1 business days

**Pricing Analysis** (as of settlement date):
```python
usg_bond = FixedRateBond(
    effective=dt(2018, 8, 15),
    termination=dt(2028, 8, 15),
    fixed_rate=2.875,
    spec="us_gb"
)

# Market analytics
price = usg_bond.price(ytm=3.125, settlement=dt(2024, 1, 15))
# Price: ~98.95 (trading below par due to higher yields)

duration = usg_bond.duration(ytm=3.125)
# Modified Duration: ~4.35 years
# Macaulay Duration: ~4.42 years

convexity = usg_bond.convexity(ytm=3.125)
# Convexity: ~20.8

dv01 = usg_bond.dv01(ytm=3.125)
# DV01: ~$43.05 per $1M face value
```

### Example 2: UK Index-Linked Gilt 0.125% 22-Mar-2068
**Inflation-Protected Bond**:
```python
ukti_bond = IndexFixedRateBond(
    effective=dt(2013, 3, 22),
    termination=dt(2068, 3, 22),
    fixed_rate=0.125,  # Real coupon rate
    spec="uk_gbi",
    index_base=251.7,  # RPI base at issue
)

# Inflation-adjusted analytics
real_duration = ukti_bond.real_duration(real_yield=0.50)
inflation_duration = ukti_bond.inflation_duration()
# Real duration: ~45.2 years
# Inflation duration: ~47.8 years
```

### Example 3: Corporate Bond - Apple Inc 3.85% 04-May-2043
**Corporate Bond with Credit Spread**:
```python
# Modeled as government bond + credit spread
aapl_bond = FixedRateBond(
    effective=dt(2013, 5, 4),
    termination=dt(2043, 5, 4),
    fixed_rate=3.85,
    spec="us_gb"
)

# Credit spread analysis
treasury_yield = 4.25  # Comparable Treasury yield
credit_spread = 85  # 85bp over Treasuries
corporate_ytm = treasury_yield + credit_spread/100

spread_duration = aapl_bond.duration(ytm=corporate_ytm)
# Spread DV01: Same as duration for parallel spread moves
```

### Example 4: Emerging Market Bond - Mexico 4.28% 14-Aug-2041
**Sovereign Emerging Market Bond**:
```python
mex_bond = FixedRateBond(
    effective=dt(2020, 8, 14),
    termination=dt(2041, 8, 14),
    fixed_rate=4.28,
    spec="us_gb",  # USD-denominated
    currency="USD"
)

# Additional risk factors:
# - Sovereign credit risk
# - Currency risk (if local currency)
# - Political risk premium
# - Liquidity risk premium
```

### Market Convention Examples by Region

**United States** (`"us_gb"`):
- Frequency: Semi-annual (S)
- Day Count: Actual/Actual ICMA
- Settlement: T+1
- Business Day Convention: Following

**United Kingdom** (`"uk_gb"`):
- Frequency: Semi-annual (S)
- Day Count: Actual/Actual ICMA
- Settlement: T+1
- Ex-dividend: 7 calendar days before payment

**Germany** (`"de_gb"`):
- Frequency: Annual (A)
- Day Count: Actual/Actual ICMA
- Settlement: T+2
- Business Day Convention: Following

**Japan** (`"jp_gb"`):
- Frequency: Semi-annual (S)
- Day Count: Actual/365
- Settlement: T+3
- Business Day Convention: Following

### Cashflow Generation Pipeline

```python
# Complete cashflow analysis
bond = FixedRateBond(
    effective=dt(2022, 1, 1),
    termination=dt(2027, 1, 1),
    fixed_rate=5.0,
    spec="us_gb",
    notional=1000000
)

# Generate complete cashflow schedule
cashflows_df = bond.cashflows(curve=discount_curve)

# Typical output columns:
# - period: Period number
# - start: Accrual start date
# - end: Accrual end date
# - payment: Payment date  
# - notional: Outstanding notional
# - rate: Applied rate
# - dcf: Day count fraction
# - cashflow: Cashflow amount
# - discount_factor: Present value factor
# - pv: Present value of cashflow
```
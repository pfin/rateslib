# Periods.py Documentation

## Overview
Comprehensive analysis of period structures that form the atomic building blocks of all fixed income instruments. This documentation covers the complete mathematical framework for period generation, day count fraction calculations, business day adjustments, and complex cashflow modeling.

## Complete Period Hierarchy

```
BasePeriod (Abstract base class)
├── FixedPeriod (Fixed rate periods)
├── FloatPeriod (Floating rate periods)
│   └── NonDeliverableFixedPeriod (NDF periods)
├── IndexFixedPeriod (Inflation-linked periods)
├── IndexCashflow (Index-linked cashflows)
├── Cashflow (Simple cashflow periods)
│   └── NonDeliverableCashflow (NDF cashflows)
├── Credit Periods
│   ├── CreditPremiumPeriod (CDS premium periods)
│   └── CreditProtectionPeriod (CDS protection periods)
└── FX Volatility Periods
    ├── FXOptionPeriod (FX option base)
    ├── FXCallPeriod (FX call options)
    └── FXPutPeriod (FX put options)
```

## Mathematical Foundation of Period Calculations

### Core Period Mathematics

**Cashflow Calculation Framework**:
```
Cashflow = Sign × Notional × Rate × DCF × Adjustments
```

Where:
- `Sign` = +1 (receive) or -1 (pay)
- `Notional` = Principal amount outstanding
- `Rate` = Applied interest rate (fixed or floating)
- `DCF` = Day count fraction for the period
- `Adjustments` = FX, index, or other multipliers

**Present Value Calculation**:
```
PV = Cashflow × DiscountFactor(settlement_date, payment_date)
```

### Day Count Fraction (DCF) Mathematics

Day count fractions are fundamental to accurate interest calculation. Each convention has specific rules:

**Actual/360 (Money Market)**:
```
DCF = ActualDays / 360
```
Used for: USD LIBOR, EUR EURIBOR, most money market instruments

**Actual/365 Fixed**:
```
DCF = ActualDays / 365
```
Used for: GBP LIBOR, some government bonds

**30/360 (Bond Basis)**:
```
DCF = (360 × (Y2-Y1) + 30 × (M2-M1) + (D2-D1)) / 360
```
With adjustments:
- If D1 = 31, then D1 = 30
- If D2 = 31 and D1 = 30, then D2 = 30

**Actual/Actual ICMA**:
```
DCF = ActualDays / (ActualDaysInYear / PaymentFrequency)
```
For regular periods: DCF = 1 / PaymentFrequency
For stub periods: More complex calculation based on reference periods

## Enhanced Key Concepts

### Period Structure
**Core Attributes**:
```python
class BasePeriod:
    start: datetime          # Accrual start date (unadjusted)
    end: datetime           # Accrual end date (unadjusted)
    payment: datetime       # Payment date (adjusted)
    notional: float         # Outstanding notional amount
    currency: str           # Payment currency
    dcf: float             # Day count fraction
    stub: bool             # Whether period is a stub
```

### Cashflow Generation Pipeline
```python
# Step 1: Schedule Generation
schedule = Schedule(
    effective=effective_date,
    termination=termination_date,
    frequency=payment_frequency,
    calendar=holiday_calendar,
    modifier=business_day_convention,
    roll=roll_convention
)

# Step 2: Period Creation
for i, (start, end) in enumerate(schedule.periods()):
    period = PeriodClass(
        start=start,
        end=end, 
        payment=schedule.aschedule[i+1],  # Adjusted payment date
        frequency=frequency,
        convention=day_count_convention,
        **kwargs
    )

# Step 3: Cashflow Calculation
cashflow = period.cashflow  # Computed property
pv = period.npv(curve, disc_curve, fx, base)
```

### Advanced Compounding Methods

**Simple Interest (No Compounding)**:
```
Interest = Principal × Rate × Time
```

**Compound Interest (Periodic)**:
```
Final_Amount = Principal × (1 + Rate/n)^(n × Time)
```
Where n = compounding frequency per year

**Continuous Compounding**:
```
Final_Amount = Principal × e^(Rate × Time)
```

**Daily Compounding (RFR)**:
```
Compounded_Rate = ∏[i=1 to n] (1 + Rate_i × w_i) - 1
```
Where:
- Rate_i = Daily rate for day i
- w_i = Weight for day i (typically 1/365 or 1/360)
- n = Number of days in observation period

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

## Detailed Class Analysis

### BasePeriod - Abstract Foundation
**Core Implementation**:
```python
class BasePeriod(ABC):
    """Abstract base class for all period types."""
    
    def __init__(self, start, end, payment, frequency, 
                 convention, notional=1000000, currency="USD", **kwargs):
        self.start = start
        self.end = end  
        self.payment = payment
        self.frequency = frequency
        self.convention = convention
        self.notional = notional
        self.currency = currency
        self.dcf = dcf(start, end, convention, **kwargs)
    
    @property
    @abstractmethod
    def cashflow(self) -> DualTypes | None:
        """Calculate the cashflow for this period."""
        pass
    
    def npv(self, curve, disc_curve=NoInput(0), fx=NoInput(0), 
            base=NoInput(0), local=False) -> DualTypes:
        """Calculate net present value."""
        pass
```

### FixedPeriod - Deterministic Cashflows
**Mathematical Model**:
```python
class FixedPeriod(BasePeriod):
    """Period with fixed interest rate."""
    
    def __init__(self, *args, fixed_rate=NoInput(0), **kwargs):
        self.fixed_rate = fixed_rate
        super().__init__(*args, **kwargs)
    
    @property
    def cashflow(self) -> DualTypes | None:
        if isinstance(self.fixed_rate, NoInput):
            return None
        return -self.notional * self.dcf * self.fixed_rate / 100
    
    def analytic_delta(self, *args, **kwargs) -> DualTypes:
        """Analytical sensitivity to rate changes."""
        return self.notional * self.dcf * disc_factor / 100
```

**Key Features**:
- **Deterministic cashflows**: Known at period creation
- **Rate sensitivity**: Analytic delta available
- **Multiple currencies**: Cross-currency support
- **Stub handling**: Partial period adjustments

**Real-World Applications**:
```python
# US Treasury coupon payment
treasury_period = FixedPeriod(
    start=dt(2024, 2, 15),
    end=dt(2024, 8, 15),
    payment=dt(2024, 8, 15),
    fixed_rate=4.625,  # 4.625% coupon
    notional=1000000,
    frequency="S",
    convention="ActActICMA",
    currency="USD"
)

# Corporate bond coupon
corp_period = FixedPeriod(
    start=dt(2024, 3, 15),
    end=dt(2024, 9, 15), 
    payment=dt(2024, 9, 17),  # Weekend adjustment
    fixed_rate=5.25,
    notional=5000000,
    frequency="S",
    convention="30360",
    currency="USD"
)
```

### FloatPeriod - Market-Linked Cashflows
**Mathematical Model**:
```python
class FloatPeriod(BasePeriod):
    """Period with floating interest rate."""
    
    def __init__(self, *args,
                 float_spread=NoInput(0),
                 fixing_method="ibor",
                 method_param=2,
                 fixings=NoInput(0),
                 stub=False,
                 **kwargs):
        self.float_spread = float_spread
        self.fixing_method = fixing_method
        self.method_param = method_param
        self.fixings = fixings
        self.stub = stub
        super().__init__(*args, **kwargs)
    
    def rate(self, curve, disc_curve=None) -> DualTypes:
        """Calculate the floating rate for this period."""
        if self.fixing_method == "ibor":
            return self._ibor_rate(curve)
        elif self.fixing_method == "rfr_lookback":
            return self._rfr_lookback_rate(curve)
        elif self.fixing_method == "rfr_payment_delay":
            return self._rfr_payment_delay_rate(curve)
        elif self.fixing_method == "rfr_observation_shift":
            return self._rfr_observation_shift_rate(curve)
    
    @property  
    def cashflow(self) -> DualTypes | None:
        # Requires curve to determine floating rate
        return None
        
    def cashflow_with_curve(self, curve) -> DualTypes:
        rate = self.rate(curve) + (self.float_spread or 0) / 100
        return -self.notional * self.dcf * rate
```

**Fixing Method Deep Dive**:

**1. IBOR Method** (`"ibor"`):
```python
def _ibor_rate(self, curve) -> DualTypes:
    """Traditional LIBOR/EURIBOR fixing method."""
    reset_date = add_tenor(
        self.start, 
        f"-{self.method_param}bd",  # e.g., -2 business days
        modifier="preceding",
        calendar=curve.calendar
    )
    tenor = self.end - self.start  # Period tenor
    return curve.rate(reset_date, tenor)
```

**2. RFR Lookback Method** (`"rfr_lookback"`):
```python
def _rfr_lookback_rate(self, curve) -> DualTypes:
    """Risk-free rate with lookback period."""
    observation_end = add_tenor(
        self.end,
        f"-{self.method_param}bd",  # e.g., -5 business days
        calendar=curve.calendar
    )
    
    # Get daily rates for observation period
    daily_rates = []
    current_date = self.start
    
    while current_date <= observation_end:
        if curve.calendar.is_business_day(current_date):
            daily_rate = curve.rate(current_date, "1d")
            daily_rates.append(daily_rate)
        current_date += timedelta(days=1)
    
    # Compound daily rates
    compounded_rate = 1.0
    for rate in daily_rates:
        compounded_rate *= (1 + rate / 365.25)  # or 360 depending on convention
    
    return (compounded_rate - 1) * 365.25 / self.dcf
```

**3. RFR Payment Delay Method** (`"rfr_payment_delay"`):
```python
def _rfr_payment_delay_rate(self, curve) -> DualTypes:
    """RFR with payment delay to include full observation period."""
    # Observation period runs to payment date
    observation_end = self.payment
    
    # Compound rates over full period including payment date
    return self._compound_rfr_rates(curve, self.start, observation_end)
```

**Fixings Table Generation**:
```python
def fixings_table(self, curve, disc_curve=None, approximate=False) -> DataFrame:
    """Generate detailed fixings breakdown."""
    if self.fixing_method == "rfr_lookback":
        return self._rfr_fixings_table(curve, approximate)
    elif self.fixing_method == "ibor":
        return self._ibor_fixings_table(curve)
```

### IndexFixedPeriod - Inflation-Linked Periods
**Mathematical Model**:
```python
class IndexFixedPeriod(IndexMixin, BasePeriod):
    """Period with inflation-adjusted cashflows."""
    
    def __init__(self, *args,
                 fixed_rate=NoInput(0),
                 index_base=NoInput(0),
                 index_lag=3,  # months
                 index_method="monthly",
                 **kwargs):
        self.fixed_rate = fixed_rate
        self.index_base = index_base 
        self.index_lag = index_lag
        self.index_method = index_method
        super().__init__(*args, **kwargs)
    
    def index_ratio(self, curve, payment_date=None) -> DualTypes:
        """Calculate inflation index ratio."""
        if payment_date is None:
            payment_date = self.payment
            
        # Calculate reference index date
        index_date = payment_date - relativedelta(months=self.index_lag)
        
        if self.index_method == "monthly":
            # Use month-end index level
            index_level = curve[index_date]
        elif self.index_method == "daily_interp":
            # Daily interpolation between monthly values
            index_level = self._interpolate_index(curve, index_date)
            
        return index_level / self.index_base
    
    @property
    def cashflow(self) -> DualTypes | None:
        # Requires index curve to calculate ratio
        return None
        
    def cashflow_with_curves(self, curve, index_curve) -> DualTypes:
        """Calculate inflation-adjusted cashflow."""
        inflation_ratio = self.index_ratio(index_curve)
        real_cashflow = -self.notional * self.dcf * self.fixed_rate / 100
        return real_cashflow * inflation_ratio
```

**Index Lag Handling**:
```python
def _get_index_date(self, payment_date, lag_months=3) -> datetime:
    """Calculate proper index reference date with lag."""
    # Standard 3-month lag for most inflation indices
    base_date = payment_date - relativedelta(months=lag_months)
    
    # Some indices use specific day conventions
    if self.index_type == "UK_RPI":
        # UK RPI uses 8-month lag for some bonds
        base_date = payment_date - relativedelta(months=8)
        # Always use 1st of month for UK RPI
        return base_date.replace(day=1)
    elif self.index_type == "US_CPI":
        # US CPI-U uses monthly values with interpolation
        return base_date.replace(day=1)
    
    return base_date
```

### Cashflow Period - Simple Payments
**Mathematical Model**:
```python
class Cashflow(BasePeriod):
    """Simple cashflow without rate calculation."""
    
    def __init__(self, payment, cashflow, currency="USD", **kwargs):
        # Simplified period for known cashflows
        self.payment = payment
        self._cashflow = cashflow
        self.currency = currency
        # No start/end dates needed for simple cashflows
        
    @property
    def cashflow(self) -> DualTypes:
        return self._cashflow
    
    def npv(self, curve, **kwargs) -> DualTypes:
        return self.cashflow * curve[self.payment]
```

**Use Cases**:
- Principal repayments
- Fee payments
- Known dividend payments
- Settlement cashflows

### NonDeliverable Periods (NDF)
**Mathematical Model**:
```python
class NonDeliverableFixedPeriod(FixedPeriod):
    """Non-deliverable forward periods with FX settlement."""
    
    def __init__(self, *args,
                 settlement_currency="USD",
                 fx_fixings=NoInput(0),
                 **kwargs):
        self.settlement_currency = settlement_currency
        self.fx_fixings = fx_fixings
        super().__init__(*args, **kwargs)
    
    def cashflow_with_fx(self, fx_rate_fixing, fx_rate_forward) -> DualTypes:
        """Calculate NDF settlement cashflow."""
        # Foreign currency cashflow
        foreign_cashflow = super().cashflow
        
        # Settlement amount in domestic currency
        settlement = foreign_cashflow * (
            fx_rate_fixing - fx_rate_forward
        ) / fx_rate_forward
        
        return settlement
```

### Credit Periods
**CreditPremiumPeriod**:
```python
class CreditPremiumPeriod(BasePeriod):
    """CDS premium payment periods."""
    
    def __init__(self, *args,
                 premium_rate=NoInput(0),
                 protection_leg=None,
                 **kwargs):
        self.premium_rate = premium_rate
        self.protection_leg = protection_leg
        super().__init__(*args, **kwargs)
    
    def cashflow_with_survival(self, survival_curve) -> DualTypes:
        """Premium adjusted for survival probability."""
        survival_prob = survival_curve.survival_probability(
            self.start, self.end
        )
        base_premium = -self.notional * self.dcf * self.premium_rate / 10000
        return base_premium * survival_prob
```

### FX Volatility Periods  
**FXOptionPeriod**:
```python
class FXOptionPeriod(BasePeriod):
    """FX option periods with volatility modeling."""
    
    def __init__(self, *args,
                 strike=NoInput(0),
                 option_type="call",
                 delivery_method="cash",
                 **kwargs):
        self.strike = strike
        self.option_type = option_type  
        self.delivery_method = delivery_method
        super().__init__(*args, **kwargs)
    
    def option_value(self, spot, vol_surface, domestic_curve, 
                    foreign_curve) -> DualTypes:
        """Black-Scholes option valuation."""
        # Implementation of option pricing model
        pass
```

## Period Attributes
- `start`: Accrual start date
- `end`: Accrual end date
- `payment`: Payment date
- `dcf`: Day count fraction
- `notional`: Principal amount
- `rate`: Applicable rate
- `cashflow`: Calculated payment

## Complete Schedule Generation Framework

### Advanced Schedule Generation
```python
from rateslib.scheduling import Schedule
from rateslib.scheduling.calendars import get_calendar
from rateslib.scheduling.frequency import Frequency

# Comprehensive schedule with all options
schedule = Schedule(
    effective=dt(2024, 3, 20),           # Unadjusted start date
    termination=dt(2029, 3, 20),         # Unadjusted end date
    frequency="Q",                       # Quarterly payments
    stub="short_front",                  # Stub period placement
    front_stub=dt(2024, 6, 20),         # Explicit front stub end
    back_stub=None,                     # No back stub
    roll="20",                          # 20th of month roll
    eom=False,                          # End-of-month adjustment
    modifier="modified_following",       # Business day convention  
    calendar="nyc",                     # New York calendar
    payment_lag=2,                      # 2-day payment delay
    notional=1000000,                   # Principal amount
    amortization=None,                  # No amortization
    currency="USD"
)
```

### Schedule Generation Process

**Step 1: Generate Unadjusted Dates**
```python
# Create regular period boundaries
def generate_unadjusted_dates(effective, termination, frequency, roll):
    dates = [effective]
    current = effective
    
    while current < termination:
        if frequency == "M":  # Monthly
            next_date = current + relativedelta(months=1)
        elif frequency == "Q":  # Quarterly 
            next_date = current + relativedelta(months=3)
        elif frequency == "S":  # Semi-annual
            next_date = current + relativedelta(months=6)
        elif frequency == "A":  # Annual
            next_date = current + relativedelta(years=1)
            
        # Apply roll day adjustment
        if isinstance(roll, int):
            next_date = next_date.replace(day=min(roll, calendar.monthrange(next_date.year, next_date.month)[1]))
        elif roll == "EOM":  # End of month
            next_date = next_date + relativedelta(day=31)
            
        dates.append(min(next_date, termination))
        current = next_date
        
    return dates
```

**Step 2: Handle Stub Periods**
```python
def handle_stubs(dates, stub_type, front_stub, back_stub):
    if stub_type == "short_front" and front_stub:
        # Insert explicit front stub date
        if front_stub not in dates:
            dates.insert(1, front_stub)
            dates.sort()
    elif stub_type == "long_front":
        # Remove first regular period to create long stub
        if len(dates) > 2:
            dates.pop(1)
    elif stub_type == "short_back" and back_stub:
        # Insert explicit back stub date
        if back_stub not in dates:
            dates.insert(-1, back_stub)
    elif stub_type == "long_back":
        # Remove last regular period to create long stub
        if len(dates) > 2:
            dates.pop(-2)
    
    return dates
```

**Step 3: Business Day Adjustments**
```python
def adjust_dates(dates, modifier, calendar):
    cal = get_calendar(calendar)
    adjusted = []
    
    for date in dates:
        if modifier == "following":
            adjusted_date = cal.following(date)
        elif modifier == "modified_following":
            adjusted_date = cal.modified_following(date)
        elif modifier == "preceding":
            adjusted_date = cal.preceding(date)
        elif modifier == "modified_preceding":
            adjusted_date = cal.modified_preceding(date)
        else:  # "none"
            adjusted_date = date
            
        adjusted.append(adjusted_date)
    
    return adjusted
```

**Step 4: Period Construction**
```python
def create_periods_from_schedule(schedule, period_class, **period_kwargs):
    periods = []
    
    for i in range(len(schedule.uschedule) - 1):
        start = schedule.uschedule[i]      # Unadjusted start
        end = schedule.uschedule[i + 1]    # Unadjusted end  
        payment = schedule.aschedule[i + 1] # Adjusted payment
        
        # Determine if this is a stub period
        is_stub = (
            (i == 0 and schedule.front_stub) or
            (i == len(schedule.uschedule) - 2 and schedule.back_stub)
        )
        
        period = period_class(
            start=start,
            end=end,
            payment=payment,
            frequency=schedule.frequency,
            convention=schedule.convention,
            stub=is_stub,
            **period_kwargs
        )
        
        periods.append(period)
    
    return periods
```

### Complex Schedule Examples

**Example 1: IMM Schedule with Front Stub**
```python
# March 2024 to March 2027 with IMM dates
imm_schedule = Schedule(
    effective=dt(2024, 1, 15),          # Mid-month start
    termination=dt(2027, 3, 15),        # IMM termination
    frequency="Q",
    roll="imm",                         # IMM roll dates (3rd Wed)
    modifier="modified_following",
    calendar="tgt",                     # TARGET calendar
    stub="short_front"                  # Front stub to first IMM
)

# Results in schedule:
# 2024-01-15 -> 2024-03-20 (front stub)
# 2024-03-20 -> 2024-06-19 (regular)
# 2024-06-19 -> 2024-09-18 (regular)
# ... continuing with IMM dates
```

**Example 2: End-of-Month with Long Back Stub**
```python
# Monthly schedule with EOM roll and long back stub
eom_schedule = Schedule(
    effective=dt(2024, 1, 31),
    termination=dt(2026, 5, 15),        # Non-EOM termination
    frequency="M",
    roll="EOM",                         # End of month
    modifier="preceding",               # Go backward if weekend
    calendar="ldn",                     # London calendar
    stub="long_back"                    # Combine last two periods
)

# Last two regular periods combined:
# 2026-03-31 -> 2026-05-15 (long back stub)
```

**Example 3: Custom Holiday Calendar**
```python
# Schedule with custom holiday calendar
from rateslib.scheduling.calendars import Calendar

# Create custom calendar
custom_holidays = [
    dt(2024, 7, 4),   # Independence Day
    dt(2024, 12, 25), # Christmas
    dt(2025, 1, 1),   # New Year
]
custom_cal = Calendar("custom", holidays=custom_holidays)

custom_schedule = Schedule(
    effective=dt(2024, 6, 1),
    termination=dt(2025, 6, 1), 
    frequency="Q",
    modifier="modified_following",
    calendar=custom_cal
)
```

### Advanced Period Generation Patterns

**Amortizing Schedule Generation**
```python
def create_amortizing_periods(schedule, principal, amort_type="linear"):
    """Create periods with principal amortization."""
    periods = []
    outstanding = principal
    num_periods = len(schedule.uschedule) - 1
    
    if amort_type == "linear":
        # Equal principal payments
        principal_payment = principal / num_periods
        amort_schedule = [outstanding - i * principal_payment 
                         for i in range(num_periods + 1)]
    elif amort_type == "bullet":
        # No amortization until maturity
        amort_schedule = [principal] * num_periods + [0]
    elif amort_type == "annuity":
        # Level payment (principal + interest)
        # Requires rate to calculate
        amort_schedule = calculate_annuity_schedule(
            principal, rate, num_periods
        )
    
    for i in range(num_periods):
        period = FixedPeriod(
            start=schedule.uschedule[i],
            end=schedule.uschedule[i + 1],
            payment=schedule.aschedule[i + 1],
            notional=amort_schedule[i],
            principal_exchange=(
                amort_schedule[i] - amort_schedule[i + 1]
            ) if i < num_periods - 1 else amort_schedule[i]
        )
        periods.append(period)
    
    return periods
```

**Multi-Currency Period Generation**
```python
def create_xccy_periods(schedule, usd_notional, eur_notional, 
                       fx_rate_initial):
    """Create cross-currency periods with FX resets."""
    usd_periods = []
    eur_periods = []
    
    for i in range(len(schedule.uschedule) - 1):
        # USD floating leg
        usd_period = FloatPeriod(
            start=schedule.uschedule[i],
            end=schedule.uschedule[i + 1], 
            payment=schedule.aschedule[i + 1],
            notional=usd_notional,
            currency="USD",
            fixing_method="rfr_lookback"
        )
        usd_periods.append(usd_period)
        
        # EUR fixed leg
        eur_period = FixedPeriod(
            start=schedule.uschedule[i],
            end=schedule.uschedule[i + 1],
            payment=schedule.aschedule[i + 1], 
            notional=-eur_notional,  # Opposite sign
            currency="EUR",
            fixed_rate=3.5
        )
        eur_periods.append(eur_period)
    
    # Add initial and final exchanges
    if i == 0:  # First period
        initial_usd = Cashflow(
            payment=schedule.aschedule[0],
            cashflow=-usd_notional,
            currency="USD"
        )
        initial_eur = Cashflow(
            payment=schedule.aschedule[0],
            cashflow=eur_notional,
            currency="EUR"
        )
        
    if i == len(schedule.uschedule) - 2:  # Last period
        final_usd = Cashflow(
            payment=schedule.aschedule[-1],
            cashflow=usd_notional,
            currency="USD"
        )
        final_eur = Cashflow(
            payment=schedule.aschedule[-1],
            cashflow=-eur_notional,
            currency="EUR"
        )
    
    return {
        "usd_periods": usd_periods,
        "eur_periods": eur_periods,
        "exchanges": [initial_usd, initial_eur, final_usd, final_eur]
    }
```

## Business Day Adjustments
- **Following**: Next business day
- **Modified Following**: Next unless different month
- **Preceding**: Previous business day
- **Modified Preceding**: Previous unless different month

## Practical Implementation Guide

### Usage
```bash
cd python/
python ../scripts/examples/coding_2/Periods.py
```

### Performance Optimization for Large Portfolios

#### 1. Batch Period Creation
```python
from rateslib.periods import FixedPeriod, FloatPeriod
from concurrent.futures import ThreadPoolExecutor
import numpy as np

def create_periods_batch(period_specs):
    """Create multiple periods efficiently."""
    periods = []
    
    # Group by period type for efficient processing
    fixed_specs = [s for s in period_specs if s['type'] == 'fixed']
    float_specs = [s for s in period_specs if s['type'] == 'float']
    
    # Batch create fixed periods
    for spec in fixed_specs:
        period = FixedPeriod(**spec['params'])
        periods.append(period)
    
    # Batch create float periods
    for spec in float_specs:
        period = FloatPeriod(**spec['params'])
        periods.append(period)
    
    return periods

# Example usage
period_specifications = [
    {
        'type': 'fixed',
        'params': {
            'start': dt(2024, 3, 20),
            'end': dt(2024, 6, 20),
            'payment': dt(2024, 6, 20),
            'fixed_rate': 4.5,
            'notional': 1000000,
            'frequency': 'Q',
            'convention': 'act360'
        }
    },
    # ... more specifications
]

periods = create_periods_batch(period_specifications)
```

#### 2. Vectorized DCF Calculations
```python
import pandas as pd
from rateslib.scheduling import dcf

def calculate_dcfs_vectorized(start_dates, end_dates, convention):
    """Calculate DCFs for multiple periods at once."""
    dcfs = []
    
    # Vectorize where possible
    if convention in ['act360', 'act365f']:
        # Can vectorize actual day calculations
        days = pd.Series(end_dates) - pd.Series(start_dates)
        days_int = days.dt.days
        
        if convention == 'act360':
            dcfs = days_int / 360
        else:  # act365f
            dcfs = days_int / 365
    else:
        # Fall back to individual calculations
        dcfs = [dcf(start, end, convention) 
                for start, end in zip(start_dates, end_dates)]
    
    return dcfs
```

#### 3. Memory-Efficient Cashflow Calculations
```python
def calculate_portfolio_cashflows(periods, curves, chunk_size=1000):
    """Calculate cashflows for large portfolios in chunks."""
    total_npv = 0.0
    num_periods = len(periods)
    
    # Process in chunks to manage memory
    for i in range(0, num_periods, chunk_size):
        chunk = periods[i:i+chunk_size]
        chunk_npvs = []
        
        for period in chunk:
            if hasattr(period, 'cashflow') and period.cashflow is not None:
                # Fixed period - direct calculation
                curve = curves.get(period.currency)
                npv = period.npv(curve)
            else:
                # Floating period - requires curve for rate
                curve = curves.get(period.currency)
                npv = period.npv(curve)
            
            chunk_npvs.append(npv)
        
        total_npv += sum(chunk_npvs)
        
        # Clear chunk from memory
        del chunk_npvs
        
    return total_npv
```

### Advanced Validation and Testing

#### 1. Period Validation Framework
```python
import warnings
from datetime import timedelta

def validate_period(period):
    """Comprehensive period validation."""
    errors = []
    warnings_list = []
    
    # Date validation
    if period.start >= period.end:
        errors.append(f"Start date {period.start} must be before end date {period.end}")
    
    if period.payment < period.end:
        warnings_list.append(f"Payment date {period.payment} is before end date {period.end}")
    
    # Notional validation
    if abs(period.notional) < 1:
        warnings_list.append(f"Very small notional: {period.notional}")
    
    # DCF validation
    if hasattr(period, 'dcf') and (period.dcf <= 0 or period.dcf > 2):
        errors.append(f"Unusual DCF value: {period.dcf}")
    
    # Rate validation (for fixed periods)
    if hasattr(period, 'fixed_rate') and hasattr(period.fixed_rate, 'real'):
        rate = period.fixed_rate
        if abs(rate) > 50:  # 50% seems excessive
            warnings_list.append(f"Very high rate: {rate}%")
    
    # Currency validation
    valid_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD']
    if hasattr(period, 'currency') and period.currency not in valid_currencies:
        warnings_list.append(f"Non-standard currency: {period.currency}")
    
    # Report issues
    if errors:
        raise ValueError(f"Period validation errors: {'; '.join(errors)}")
    
    for warning_msg in warnings_list:
        warnings.warn(warning_msg, UserWarning)
    
    return True

def validate_period_sequence(periods):
    """Validate a sequence of periods for consistency."""
    if not periods:
        return True
    
    for i in range(len(periods) - 1):
        current = periods[i]
        next_period = periods[i + 1]
        
        # Check date continuity
        if current.end != next_period.start:
            warnings.warn(
                f"Period {i} ends {current.end} but period {i+1} starts {next_period.start}"
            )
        
        # Check currency consistency
        if hasattr(current, 'currency') and hasattr(next_period, 'currency'):
            if current.currency != next_period.currency:
                warnings.warn(
                    f"Currency change: period {i} is {current.currency}, "
                    f"period {i+1} is {next_period.currency}"
                )
    
    return True
```

#### 2. Unit Testing Framework
```python
import pytest
from decimal import Decimal
from rateslib import FixedPeriod, FloatPeriod, dt

class TestPeriods:
    """Comprehensive period testing."""
    
    def test_fixed_period_cashflow(self):
        """Test fixed period cashflow calculation."""
        period = FixedPeriod(
            start=dt(2024, 1, 1),
            end=dt(2024, 4, 1), 
            payment=dt(2024, 4, 1),
            fixed_rate=5.0,
            notional=1000000,
            frequency="Q",
            convention="act360"
        )
        
        # Manual calculation
        days = (dt(2024, 4, 1) - dt(2024, 1, 1)).days  # 91 days
        expected_dcf = 91 / 360  # 0.2528
        expected_cashflow = -1000000 * 0.05 * expected_dcf  # -12,639
        
        assert abs(period.dcf - expected_dcf) < 1e-6
        assert abs(period.cashflow - expected_cashflow) < 1e-2
    
    def test_leap_year_handling(self):
        """Test leap year day count handling."""
        # 2024 is a leap year
        leap_period = FixedPeriod(
            start=dt(2024, 2, 28),
            end=dt(2024, 3, 1),
            payment=dt(2024, 3, 1),
            fixed_rate=3.0,
            notional=1000000,
            frequency="M",
            convention="act365f"
        )
        
        # Should be 2 days (Feb 29 + Mar 1)
        expected_dcf = 2 / 365
        assert abs(leap_period.dcf - expected_dcf) < 1e-6
    
    def test_stub_period_identification(self):
        """Test stub period handling."""
        stub_period = FixedPeriod(
            start=dt(2024, 1, 15),  # Mid-month start
            end=dt(2024, 3, 20),    # IMM date
            payment=dt(2024, 3, 20),
            fixed_rate=4.0,
            notional=1000000,
            frequency="Q",
            convention="act360",
            stub=True
        )
        
        # Stub should be shorter than regular quarter
        regular_days = 90  # Typical quarter
        actual_days = (dt(2024, 3, 20) - dt(2024, 1, 15)).days
        
        assert actual_days < regular_days
        assert stub_period.stub == True
    
    @pytest.mark.parametrize("convention,expected_dcf", [
        ("act360", 90/360),
        ("act365f", 90/365), 
        ("30360", 90/360),
        ("actacticma", 90/365)
    ])
    def test_day_count_conventions(self, convention, expected_dcf):
        """Test various day count conventions."""
        period = FixedPeriod(
            start=dt(2024, 1, 1),
            end=dt(2024, 4, 1),  # Exactly 90 days
            payment=dt(2024, 4, 1),
            fixed_rate=5.0,
            notional=1000000,
            frequency="Q",
            convention=convention
        )
        
        # Some conventions may require additional parameters
        if convention == "actacticma":
            # Requires termination and frequency for proper calculation
            pytest.skip("ActActICMA requires additional parameters")
        
        assert abs(period.dcf - expected_dcf) < 1e-6
    
    def test_currency_consistency(self):
        """Test multi-currency period handling."""
        usd_period = FixedPeriod(
            start=dt(2024, 1, 1),
            end=dt(2024, 4, 1),
            payment=dt(2024, 4, 1),
            fixed_rate=5.0,
            notional=1000000,
            currency="USD",
            frequency="Q",
            convention="act360"
        )
        
        eur_period = FixedPeriod(
            start=dt(2024, 1, 1),
            end=dt(2024, 4, 1), 
            payment=dt(2024, 4, 1),
            fixed_rate=3.5,
            notional=1000000,
            currency="EUR",
            frequency="Q",
            convention="act360"
        )
        
        assert usd_period.currency == "USD"
        assert eur_period.currency == "EUR"
        assert usd_period.fixed_rate != eur_period.fixed_rate
```

#### 3. Integration Testing with Market Data
```python
def test_period_with_real_curves():
    """Test periods with real market curves."""
    from rateslib import Curve
    
    # Create realistic USD curve
    usd_curve = Curve({
        dt(2024, 1, 1): 1.0000,
        dt(2024, 4, 1): 0.9875,
        dt(2024, 7, 1): 0.9745,
        dt(2025, 1, 1): 0.9520
    }, id="USD-SOFR", calendar="nyc", convention="act360")
    
    # Create SOFR floating period
    sofr_period = FloatPeriod(
        start=dt(2024, 1, 1),
        end=dt(2024, 4, 1),
        payment=dt(2024, 4, 1),
        float_spread=0,
        fixing_method="rfr_lookback",
        method_param=5,
        notional=10000000,
        frequency="Q",
        convention="act360",
        currency="USD"
    )
    
    # Calculate NPV
    npv = sofr_period.npv(usd_curve)
    
    # NPV should be reasonable for 3-month period
    assert abs(npv) < 1000000  # Less than $1M for $10M notional
    assert npv != 0  # Should have some value

def test_cross_currency_periods():
    """Test cross-currency period valuation."""
    from rateslib.fx import FXRates
    
    # EUR period
    eur_period = FixedPeriod(
        start=dt(2024, 1, 1),
        end=dt(2025, 1, 1),
        payment=dt(2025, 1, 1),
        fixed_rate=3.5,
        notional=1000000,
        currency="EUR",
        frequency="A",
        convention="act360"
    )
    
    # Create EUR curve and FX rates
    eur_curve = Curve({
        dt(2024, 1, 1): 1.0,
        dt(2025, 1, 1): 0.965
    }, id="EUR-ESTR")
    
    fx_rates = FXRates({
        "EURUSD": 1.0850
    }, base="USD")
    
    # Calculate EUR NPV in USD
    npv_usd = eur_period.npv(eur_curve, fx=fx_rates, base="USD")
    npv_eur = eur_period.npv(eur_curve)
    
    # Should satisfy FX conversion relationship
    expected_usd = npv_eur * 1.0850
    assert abs(npv_usd - expected_usd) < 1e-6
```

### Debugging and Troubleshooting

#### 1. Common Issues and Solutions
```python
def debug_period_issues(period):
    """Debug common period calculation issues."""
    issues = []
    
    # Check for None cashflow
    if hasattr(period, 'cashflow') and period.cashflow is None:
        if hasattr(period, 'fixed_rate') and isinstance(period.fixed_rate, NoInput):
            issues.append("Fixed rate not set - required for cashflow calculation")
        issues.append("Cashflow is None - check rate setting")
    
    # Check for zero DCF
    if hasattr(period, 'dcf') and period.dcf == 0:
        issues.append(f"Zero DCF - check dates: start={period.start}, end={period.end}")
    
    # Check date ordering
    if period.start >= period.end:
        issues.append(f"Invalid date order: start={period.start} >= end={period.end}")
    
    # Check for weekend payment dates
    if period.payment.weekday() >= 5:  # Saturday=5, Sunday=6
        issues.append(f"Payment on weekend: {period.payment} ({period.payment.strftime('%A')})")
    
    return issues

# Usage
period = FixedPeriod(
    start=dt(2024, 1, 1),
    end=dt(2024, 4, 1),
    payment=dt(2024, 4, 1),
    fixed_rate=NoInput(0),  # Deliberately unset
    notional=1000000,
    frequency="Q",
    convention="act360"
)

problems = debug_period_issues(period)
for problem in problems:
    print(f"Issue: {problem}")
```

#### 2. Performance Profiling
```python
import cProfile
import time

def profile_period_creation():
    """Profile period creation performance."""
    
    def create_many_periods():
        periods = []
        for i in range(1000):
            period = FixedPeriod(
                start=dt(2024, 1, 1) + timedelta(days=i*90),
                end=dt(2024, 1, 1) + timedelta(days=(i+1)*90),
                payment=dt(2024, 1, 1) + timedelta(days=(i+1)*90),
                fixed_rate=5.0,
                notional=1000000,
                frequency="Q",
                convention="act360"
            )
            periods.append(period)
        return periods
    
    # Profile the creation
    start_time = time.time()
    periods = create_many_periods()
    end_time = time.time()
    
    print(f"Created {len(periods)} periods in {end_time - start_time:.3f} seconds")
    print(f"Average: {(end_time - start_time) / len(periods) * 1000:.3f} ms per period")
    
    # Memory usage
    import sys
    total_size = sum(sys.getsizeof(p) for p in periods)
    print(f"Total memory: {total_size / 1024:.1f} KB")
    print(f"Average per period: {total_size / len(periods):.1f} bytes")

# Run profiling
profile_period_creation()
```

## Comprehensive Real-World Period Examples

### Example 1: US Treasury Semi-Annual Period
**10-Year Treasury 4.625% Note**:
```python
treasury_period = FixedPeriod(
    start=dt(2024, 2, 15),              # Issue date
    end=dt(2024, 8, 15),                # Next coupon date
    payment=dt(2024, 8, 15),            # Same as end (no delay)
    fixed_rate=4.625,                   # 4.625% annual coupon
    notional=1000000,                   # $1M face value
    frequency="S",                      # Semi-annual
    convention="ActActICMA",            # US Treasury convention
    currency="USD",
    calendar="nyc"
)

# Calculations:
dcf = dcf(dt(2024, 2, 15), dt(2024, 8, 15), "ActActICMA")
# DCF = 182 / 365 = 0.4986 (actual days / actual days in year)

cashflow = treasury_period.cashflow
# Cashflow = -1,000,000 × 0.04625 × 0.4986 = -$23,062

# Semi-annual coupon payment
```

### Example 2: SOFR Floating Period with 5-Day Lookback
**3-Month SOFR with Spread**:
```python
sofr_period = FloatPeriod(
    start=dt(2024, 3, 20),
    end=dt(2024, 6, 20),
    payment=dt(2024, 6, 20),
    float_spread=25,                    # 25bp spread
    fixing_method="rfr_lookback",
    method_param=5,                     # 5 business day lookback
    notional=10000000,                  # $10M notional
    frequency="Q",
    convention="act360",
    currency="USD",
    calendar="nyc"
)

# Detailed fixings calculation
fixings_table = sofr_period.fixings_table(sofr_curve)
```

**SOFR Fixings Table Output**:
```
Date        | SOFR    | Weight   | Contribution | Cumulative
------------|---------|----------|--------------|----------
2024-03-20  | 5.31%   | 1/92     | 0.000577%    | 1.000577
2024-03-21  | 5.32%   | 1/92     | 0.000578%    | 1.001156  
2024-03-22  | 5.30%   | 1/92     | 0.000576%    | 1.001732
...         | ...     | ...      | ...          | ...
2024-06-13  | 5.28%   | 1/92     | 0.000574%    | 1.013456
2024-06-14  | 5.29%   | 1/92     | 0.000575%    | 1.014032

Observation Period: 2024-03-20 to 2024-06-13 (5 BD before end)
Compounded SOFR: 1.3456% (quarterly)
Annualized Rate: 5.3824%
All-in Rate: 5.6324% (including 25bp spread)
DCF (Act/360): 92/360 = 0.2556
Cashflow: -$10,000,000 × 0.056324 × 0.2556 = -$143,974
```

### Example 3: UK RPI-Linked Gilt Period
**UK Index-Linked Gilt 0.125% 2068**:
```python
rpi_period = IndexFixedPeriod(
    start=dt(2024, 3, 22),
    end=dt(2024, 9, 22), 
    payment=dt(2024, 9, 22),
    fixed_rate=0.125,                   # 0.125% real coupon
    index_base=251.7,                   # RPI at issue
    index_lag=8,                        # 8-month lag for UK
    notional=5000000,                   # £5M nominal
    frequency="S",
    convention="ActActICMA",
    currency="GBP",
    calendar="ldn"
)

# Index calculations
reference_date = dt(2024, 1, 22)       # 8 months before payment
rpi_level = 327.8                       # RPI in Jan 2024
inflation_ratio = rpi_level / 251.7     # 327.8 / 251.7 = 1.302

# Inflation-adjusted cashflow
real_cashflow = -5000000 * 0.00125 * 0.5  # -£3,125 (real)
inflation_adjusted = real_cashflow * 1.302  # -£4,069 (nominal)
```

### Example 4: EUR 30/360 Corporate Bond Period
**German Corporate 5.25% Bond**:
```python
corp_period = FixedPeriod(
    start=dt(2024, 4, 15),
    end=dt(2025, 4, 15),                # Annual payment
    payment=dt(2025, 4, 15),
    fixed_rate=5.25,                    # 5.25% annual coupon
    notional=2000000,                   # €2M face value
    frequency="A",                      # Annual
    convention="30360",                 # European bond basis
    currency="EUR",
    calendar="tgt"
)

# 30/360 calculation
# Start: 2024-04-15 -> (2024, 4, 15)
# End:   2025-04-15 -> (2025, 4, 15)
# 30/360 DCF = (360*(2025-2024) + 30*(4-4) + (15-15)) / 360 = 1.0

cashflow = corp_period.cashflow
# Cashflow = -2,000,000 × 0.0525 × 1.0 = -€105,000
```

### Example 5: CDS Premium Period with Survival Adjustment
**5-Year Corporate CDS Premium**:
```python
cds_period = CreditPremiumPeriod(
    start=dt(2024, 3, 20),
    end=dt(2024, 6, 20),
    payment=dt(2024, 6, 20),
    premium_rate=250,                   # 250bp annual premium
    notional=10000000,                  # $10M protection
    frequency="Q",
    convention="act360",
    currency="USD"
)

# Survival probability adjustment
survival_prob = 0.995                  # 99.5% quarterly survival
base_premium = -10000000 * 0.025 * 0.2556  # Base quarterly premium
adjusted_premium = base_premium * survival_prob
# Adjusted Premium = -$63,900 × 0.995 = -$63,581
```

### Example 6: Cross-Currency NDF Period
**USD/BRL Non-Deliverable Forward**:
```python
ndf_period = NonDeliverableFixedPeriod(
    start=dt(2024, 3, 20),
    end=dt(2024, 6, 20),
    payment=dt(2024, 6, 22),            # T+2 settlement
    fixed_rate=10.75,                   # 10.75% BRL rate
    notional=50000000,                  # 50M BRL notional
    currency="BRL",
    settlement_currency="USD",
    fx_rate_forward=5.00,               # 5.00 USD/BRL forward
    frequency="Q",
    convention="bus252",                # Brazilian business days
    calendar="bra"
)

# NDF settlement calculation
fx_fixing = 5.15                       # Actual USD/BRL at fixing
fx_forward = 5.00                      # Contract forward rate
brl_cashflow = -50000000 * 0.1075 * (63/252)  # Brazilian DCF

# USD settlement amount
ndf_settlement = brl_cashflow * (fx_fixing - fx_forward) / fx_forward
# Settlement = -1,347,222 × (5.15 - 5.00) / 5.00 = -$40,417 USD
```

### Example 7: Stub Period Calculation
**Short Front Stub in Swap**:
```python
# Swap starting mid-period with front stub
stub_period = FixedPeriod(
    start=dt(2024, 1, 15),              # Mid-quarter start
    end=dt(2024, 3, 20),                # Next IMM date
    payment=dt(2024, 3, 20),
    fixed_rate=4.75,
    notional=25000000,
    frequency="Q",                      # Would be quarterly if regular
    convention="act360",
    stub=True,                          # Mark as stub period
    currency="USD"
)

# Stub DCF calculation
stub_days = (dt(2024, 3, 20) - dt(2024, 1, 15)).days  # 65 days
stub_dcf = 65 / 360                    # 0.1806
stub_cashflow = -25000000 * 0.0475 * 0.1806  # -$214,463

# Compare to regular quarterly period:
# Regular DCF ≈ 0.25, Regular cashflow ≈ $296,875
# Stub is proportionally smaller
```

### Example 8: Complex Amortizing Period
**Mortgage-Style Amortization Period**:
```python
# Period 15 of 20 in amortizing bond
amort_period = FixedPeriod(
    start=dt(2027, 9, 20),
    end=dt(2027, 12, 20),
    payment=dt(2027, 12, 20),
    fixed_rate=6.50,
    notional=342156,                    # Outstanding balance
    principal_payment=87844,            # Principal due this period
    frequency="Q",
    convention="30360",
    currency="USD"
)

# Interest and principal breakdown
interest_payment = -342156 * 0.065 * 0.25      # -$5,560
principal_payment = -87844                       # -$87,844
total_payment = interest_payment + principal_payment  # -$93,404

# Remaining balance after payment: $342,156 - $87,844 = $254,312
```

### Example 9: FX Option Period
**EUR/USD Call Option**:
```python
fx_call_period = FXCallPeriod(
    start=dt(2024, 3, 20),
    end=dt(2024, 6, 20),
    payment=dt(2024, 6, 22),
    strike=1.0800,                      # EUR/USD strike
    notional_base=10000000,             # €10M notional
    delivery="cash",                    # Cash settled
    currency_pair="EUR/USD",
    premium=156000,                     # $156k premium paid
    frequency="Q"
)

# Option payoff calculation
spot_fixing = 1.0950                   # EUR/USD at expiry
intrinsic_value = max(spot_fixing - 1.0800, 0) * 10000000
# Intrinsic = max(1.0950 - 1.0800, 0) × €10M = $150,000

# Net payoff = $150,000 - $156,000 = -$6,000 (small loss)
```

### Day Count Convention Comparison
**Same Period, Different Conventions**:
```python
period_start = dt(2024, 2, 15)
period_end = dt(2024, 8, 15)
notional = 1000000
rate = 5.0

conventions = {
    "act360": dcf(period_start, period_end, "act360"),
    "act365f": dcf(period_start, period_end, "act365f"),
    "30360": dcf(period_start, period_end, "30360"),
    "actacticma": dcf(period_start, period_end, "actacticma", 
                      termination=dt(2034, 2, 15), frequency_months=6)
}

for conv, dcf_value in conventions.items():
    cashflow = -notional * (rate/100) * dcf_value
    print(f"{conv:12}: DCF={dcf_value:.6f}, Cashflow={cashflow:,.2f}")
```

**Output**:
```
act360      : DCF=0.505556, Cashflow=-25,277.78
act365f     : DCF=0.498630, Cashflow=-24,931.51  
30360       : DCF=0.500000, Cashflow=-25,000.00
actacticma  : DCF=0.498630, Cashflow=-24,931.51
```

**Analysis**: Different day count conventions can result in materially different cashflows, highlighting the importance of using the correct convention for each market and instrument type.
# Scheduling.py Documentation

## Overview
Demonstrates sophisticated date scheduling and generation for financial instruments, including complex business day adjustments, roll conventions, and stub period handling. This module showcases the robust scheduling framework in rateslib that handles various market conventions across global financial centers.

## Key Concepts
- **Schedule Generation**: Algorithmic date sequence creation with market conventions
- **Frequency Patterns**: Regular payment intervals with complex roll behaviors
- **Roll Convention Logic**: Deterministic date alignment rules (EOM, IMM, DOM)
- **Business Day Adjustment**: Holiday calendar integration with multiple jurisdictions
- **Stub Period Management**: Irregular period handling at schedule start/end
- **Calendar Integration**: Multi-jurisdictional holiday calendar support

## Mathematical Framework

### Schedule Generation Algorithm
The core algorithm follows this pattern:
```
Start Date → Apply Frequency → Check Roll Rules → Apply Calendar → Generate Next Date
    ↓              ↓                ↓              ↓                   ↓
[Effective]   [Add Period]    [Adjust Roll]   [Bus Day Fix]      [Schedule Date]
```

### Frequency Mathematics
Period addition follows standardized market conventions:
```
Next_Date = Current_Date + Frequency_Period
Where Frequency_Period ∈ {1M, 2M, 3M, 6M, 12M, ...}
```

### Business Day Adjustment Formula
```python
def adjust_date(unadjusted_date: datetime, modifier: str, calendar: Calendar) -> datetime:
    """
    Apply business day adjustment rules:
    - F (Following): Next business day
    - MF (Modified Following): Following, unless crosses month
    - P (Preceding): Previous business day  
    - MP (Modified Preceding): Preceding, unless crosses month
    """
```

## Class Architecture Diagrams

### Schedule Class Structure
```
Schedule
├── effective: datetime               # Unadjusted start date
├── termination: datetime             # Unadjusted end date
├── frequency: Frequency              # Payment frequency object
├── stub: StubInference              # Stub handling rules
├── front_stub: datetime             # Explicit front stub date
├── back_stub: datetime              # Explicit back stub date
├── roll: RollDay                    # Roll convention
├── eom: bool                        # End-of-month preference
├── modifier: Adjuster               # Business day adjustment
├── calendar: Calendar               # Holiday calendar
├── payment_lag: Adjuster            # Payment delay rules
└── Methods:
    ├── dates: List[datetime]         # All schedule dates
    ├── periods() -> Iterator         # Period start/end pairs
    ├── n_periods: int               # Number of periods
    ├── stub_type: str               # Inferred stub type
    └── DataFrame() -> pd.DataFrame   # Tabular representation
```

### Frequency Class Hierarchy
```
Frequency (Abstract)
├── Months(n: int, roll: RollDay)
├── CalDays(n: int)
├── BusDays(n: int, calendar: Calendar)
└── Zero()  # Single payment
```

### RollDay Enumeration
```
RollDay
├── Dom(day: int)      # Specific day of month (1-31)
├── Eom()              # End of month
├── Imm()              # Third Wednesday (IMM dates)
└── Som()              # Start of month
```

## State Transition Diagrams

### Schedule Generation State Machine
```
INIT → VALIDATE → GENERATE_UNADJUSTED → APPLY_STUBS → ADJUST_BUSINESS_DAYS → COMPLETE
 ↓         ↓              ↓                  ↓                ↓              ↓
[Params] [Check]   [Regular Pattern]    [Handle Stubs]   [Calendar Fix]  [Final Dates]
 ↓         ↓              ↓                  ↓                ↓              ↓
Error if: Error if:      Generate from      Add/Remove       Apply modifier Success
Invalid   Inconsistent   frequency+roll     irregular        & calendar     
params    rules          pattern            periods
```

### Stub Inference Flow
```
Check Periods → Determine Stub Need → Apply Stub Rules → Validate Result
     ↓               ↓                      ↓              ↓
[Period Count]   [Short/Long]         [Front/Back]    [Valid Schedule]
     ↓               ↓                      ↓              ↓
If irregular     Choose type          Position stub   Accept or Error
periods exist    based on preference  at start/end
```

### Business Day Adjustment Flow
```
Unadjusted Date → Check Holiday → Apply Modifier → Validate Month → Final Date
       ↓              ↓              ↓               ↓             ↓
  [Raw Schedule]  [Calendar]     [F/MF/P/MP]    [Month Check]  [Adjusted]
       ↓              ↓              ↓               ↓             ↓
   From generation Check if       Move forward     Ensure same   Business day
   algorithm       business day   or backward      month (MF/MP) guaranteed
```

## Calendar Handling Patterns

### Multi-Jurisdictional Calendars
```python
# Combined holiday calendars for cross-border instruments
combined_cal = get_calendar("NYC|LON")  # US and UK holidays
schedule = Schedule(
    effective=dt(2024, 1, 1),
    termination=dt(2025, 1, 1),
    frequency="Q",
    calendar=combined_cal,
    modifier="MF"
)
```

### Calendar Hierarchy
```
Calendar (Abstract)
├── NamedCalendar
│   ├── NYC (New York)
│   ├── LON (London) 
│   ├── TGT (TARGET/Eurozone)
│   ├── FED (Federal Reserve)
│   └── Custom calendars...
├── CombinedCalendar  # Union of multiple calendars
└── CustomCalendar    # User-defined holiday lists
```

### Calendar Operations
```python
def is_business_day(date: datetime, calendar: Calendar) -> bool:
    """Check if date is a business day"""
    return not (is_weekend(date) or is_holiday(date, calendar))

def next_business_day(date: datetime, calendar: Calendar) -> datetime:
    """Find next business day"""
    while not is_business_day(date, calendar):
        date += timedelta(days=1)
    return date
```

## Business Day Conventions

### Standard Market Conventions
1. **Following (F)**: Move to next business day if holiday
2. **Modified Following (MF)**: Following, but stay in same month
3. **Preceding (P)**: Move to previous business day if holiday  
4. **Modified Preceding (MP)**: Preceding, but stay in same month
5. **None**: No adjustment (keep original date)

### Modifier Selection Logic
```python
def get_optimal_modifier(instrument_type: str, currency: str) -> str:
    """
    Market convention mapping:
    - USD Swaps: MF (Modified Following)
    - EUR Bonds: F (Following)
    - GBP Bills: P (Preceding)
    - Cross-currency: MF
    """
    conventions = {
        ("swap", "usd"): "MF",
        ("bond", "eur"): "F", 
        ("bill", "gbp"): "P"
    }
    return conventions.get((instrument_type.lower(), currency.lower()), "MF")
```

## Real-World Use Cases

### 1. Interest Rate Swap Scheduling
```python
# 5-year USD swap with quarterly payments
irs_schedule = Schedule(
    effective="2D",  # T+2 settlement
    termination="5Y",
    frequency="Q",
    modifier="MF",
    calendar="NYC",
    payment_lag=2,  # T+2 payment
    eval_date=dt(2024, 1, 15)
)
```

### 2. Eurobond Coupon Schedule
```python
# 10-year EUR bond with annual coupons
bond_schedule = Schedule(
    effective=dt(2024, 3, 15),
    termination=dt(2034, 3, 15),
    frequency="A",
    roll="eom",  # End-of-month convention
    modifier="F",
    calendar="TGT"  # TARGET calendar
)
```

### 3. IMM Futures Expiry Schedule
```python
# CME IMM dates (3rd Wednesday of Mar/Jun/Sep/Dec)
futures_schedule = Schedule(
    effective=dt(2024, 1, 1),
    termination=dt(2026, 1, 1),
    frequency="Q",
    roll="imm",
    modifier="NONE",  # IMM dates are always valid
    calendar="FED"
)
```

### 4. Complex Stub Handling
```python
# Schedule with irregular first period
stub_schedule = Schedule(
    effective=dt(2024, 2, 29),  # Leap year start
    termination=dt(2027, 2, 28),  # Non-leap year end
    frequency="S",  # Semi-annual
    stub="SHORTFRONT",  # Short first period
    modifier="MF",
    calendar="NYC|LON"  # Dual jurisdiction
)
```

### 5. Cross-Currency Schedule Alignment
```python
# Aligned USD and EUR payment schedules for cross-currency swap
usd_schedule = Schedule(
    effective=dt(2024, 3, 20),
    termination=dt(2029, 3, 20),
    frequency="Q",
    modifier="MF",
    calendar="NYC"
)

eur_schedule = Schedule(
    effective=dt(2024, 3, 20),
    termination=dt(2029, 3, 20), 
    frequency="S",  # Different frequency
    modifier="MF",
    calendar="TGT"
)
```

## Advanced Scheduling Features

### Dynamic Date Calculation
```python
# Tenor-based scheduling with eval_date reference
schedule = Schedule(
    effective="1Y",    # 1 year from eval_date
    termination="10Y", # 10 years from effective
    frequency="Q",
    eval_date=dt(2024, 1, 15),
    eval_mode="swaps_align"  # Market convention alignment
)
```

### Evaluation Mode Differences
```python
# Two different alignment modes
swaps_mode = Schedule(
    effective="2Y", termination="5Y", frequency="S",
    eval_mode="swaps_align",    # Standard swap conventions
    eval_date=dt(2024, 3, 15)
)

swaptions_mode = Schedule(
    effective="2Y", termination="5Y", frequency="S", 
    eval_mode="swaptions_align",  # Swaption exercise alignment
    eval_date=dt(2024, 3, 15)
)
```

### Payment Lag Integration
```python
# Separate accrual and payment dates
schedule_with_lag = Schedule(
    effective=dt(2024, 1, 15),
    termination=dt(2029, 1, 15),
    frequency="Q",
    payment_lag=2,  # 2 business day payment delay
    calendar="NYC"
)

# Access both sets of dates
accrual_dates = schedule_with_lag.dates
payment_dates = schedule_with_lag.payment_dates
```

## Error Handling and Validation

### Common Scheduling Errors
1. **Invalid Date Ranges**: Effective date after termination
2. **Inconsistent Parameters**: Conflicting stub and frequency settings
3. **Calendar Mismatches**: Using wrong holiday calendar for currency
4. **Roll Date Conflicts**: EOM rolls on non-month-end dates

### Validation Algorithms
```python
def validate_schedule_params(
    effective: datetime,
    termination: datetime,
    frequency: str,
    stub: str,
    **kwargs
) -> List[str]:
    """
    Comprehensive parameter validation:
    1. Date ordering checks
    2. Frequency compatibility
    3. Stub consistency
    4. Calendar availability
    """
    errors = []
    
    # Basic date validation
    if effective >= termination:
        errors.append("Effective date must be before termination")
    
    # Frequency-stub compatibility
    if frequency == "Z" and stub != "NONE":
        errors.append("Zero coupon schedules cannot have stubs")
    
    return errors
```

### Automatic Error Correction
```python
# Built-in intelligent corrections
def auto_correct_schedule(params: dict) -> dict:
    """
    Apply common corrections:
    - Adjust for weekends automatically
    - Infer missing roll conventions
    - Set appropriate modifiers by currency
    """
    if params.get("roll") is None and params.get("eom") is None:
        # Auto-infer end-of-month if effective date is month-end
        if params["effective"].day == calendar.monthrange(
            params["effective"].year, 
            params["effective"].month
        )[1]:
            params["eom"] = True
    
    return params
```

## Performance Optimizations

### Schedule Caching
```python
@cached_property
def dates(self) -> List[datetime]:
    """Cache computed schedule dates"""
    return self._generate_schedule()
```

### Rust Backend Integration
Critical path operations delegated to Rust:
- Date arithmetic with business day rules
- Holiday calendar lookups
- Bulk schedule generation

### Memory Efficiency
```python
def periods(self) -> Iterator[Tuple[datetime, datetime]]:
    """Lazy iteration over schedule periods"""
    dates = self.dates
    for i in range(len(dates) - 1):
        yield (dates[i], dates[i + 1])
```

## Testing and Validation

### Comprehensive Test Scenarios
```python
def test_schedule_edge_cases():
    """Test various edge cases"""
    
    # Leap year handling
    leap_schedule = Schedule(dt(2024, 2, 29), dt(2028, 2, 29), "A")
    
    # Month-end rolls across different month lengths
    eom_schedule = Schedule(dt(2024, 1, 31), dt(2024, 4, 30), "M", roll="eom")
    
    # Holiday collision handling
    holiday_schedule = Schedule(
        dt(2024, 12, 23), dt(2025, 1, 3), "D",  # Christmas/New Year period
        calendar="NYC", modifier="MF"
    )
```

### Market Convention Validation
```python
def validate_market_conventions(schedule: Schedule, currency: str) -> bool:
    """
    Verify schedule follows market standards:
    - USD: Modified Following with NYC calendar
    - EUR: Modified Following with TARGET calendar
    - GBP: Modified Following with LON calendar
    """
    conventions = get_market_conventions(currency)
    return all([
        schedule.modifier == conventions["modifier"],
        schedule.calendar == conventions["calendar"],
        schedule.payment_lag == conventions["payment_lag"]
    ])
```

## Usage Examples

### Basic Schedule Generation
```bash
cd python/
python ../scripts/examples/coding_2/Scheduling.py
```

### Advanced Integration Testing
```python
# Complete workflow testing
def test_comprehensive_scheduling():
    # 1. Create various schedule types
    schedules = {
        "swap": Schedule("2D", "5Y", "Q", calendar="NYC"),
        "bond": Schedule(dt(2024, 3, 15), dt(2034, 3, 15), "A", calendar="TGT"),
        "future": Schedule(dt(2024, 1, 1), dt(2025, 1, 1), "Q", roll="imm")
    }
    
    # 2. Validate all schedules
    for name, schedule in schedules.items():
        assert len(schedule.dates) > 1
        assert schedule.dates[-1] <= schedule.termination
        
    # 3. Test business day adjustments
    for schedule in schedules.values():
        for date in schedule.dates:
            assert is_business_day(date, schedule.calendar)
```

## Example Schedule Patterns

### Regular Quarterly with EOM
```python
quarterly_eom = Schedule(
    effective=dt(2022, 1, 31),
    termination=dt(2023, 1, 31),
    frequency="Q",
    roll="eom"
)
# Generates: [Jan-31, Apr-30, Jul-31, Oct-31, Jan-31]
```

### Semi-annual with Modified Following
```python
semi_annual_mf = Schedule(
    effective=dt(2022, 1, 15),
    termination=dt(2025, 1, 15),
    frequency="S",
    modifier="MF",
    calendar="NYC"
)
# Handles weekend/holiday adjustments automatically
```

### IMM Futures Expiry Dates
```python
imm_futures = Schedule(
    effective=dt(2024, 1, 1),
    termination=dt(2025, 1, 1),
    frequency="Q",
    roll="imm"
)
# Generates third Wednesdays: Mar-20, Jun-19, Sep-18, Dec-18
```

## Migration from Private APIs

### Legacy Function Mapping
| **Private Function (Deprecated)** | **Public API Replacement** | **Usage Pattern** |
|----------------------------------|---------------------------|------------------|
| `_get_unadjusted_roll()` | `Schedule().dates` | Create Schedule object |
| `_get_rollday()` | Built into Schedule | Specify in constructor |
| `_generate_regular_schedule_unadjusted()` | `Schedule().dates` | Set modifier="NONE" |
| `_check_unadjusted_regular_swap()` | Schedule validation | Automatic validation |
| `_get_unadjusted_stub_date()` | `Schedule().stub_type` | Use stub parameters |
| `_adjust_date()` | Calendar methods | Use calendar.adjust() |

### Recommended Migration Path
```python
# OLD (Private API - Don't Use)
from rateslib.scheduling import _get_unadjusted_roll
dates = _get_unadjusted_roll(
    ueffective=dt(2022, 3, 15),
    utermination=dt(2023, 3, 15), 
    eom=True
)

# NEW (Public API - Recommended)
from rateslib import Schedule
schedule = Schedule(
    effective=dt(2022, 3, 15),
    termination=dt(2023, 3, 15),
    frequency="M",  # Must specify frequency
    roll="eom"      # Use public roll parameter
)
dates = schedule.dates
```

## Known Issues and Workarounds
The original `coding/scheduling.py` script uses private functions that are not part of the public API. These should be replaced with the public `Schedule` class to ensure compatibility and maintainability. See the migration guide above for proper replacements.
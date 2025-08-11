# scheduling.py Documentation

## Overview
Demonstrates schedule generation with various conventions and adjustments. **This is a legacy script that uses deprecated private APIs and should be migrated to the public API.**

## Critical Warning
⚠️ **This script uses private functions that are not part of the public API:**
- `_get_unadjusted_roll()`
- `_get_rollday()`
- `_generate_regular_schedule_unadjusted()`
- `_check_unadjusted_regular_swap()`
- `_get_unadjusted_short_stub_date()`
- `_get_unadjusted_stub_date()`
- `_check_regular_swap()`

These are internal implementation details that can break without notice and should **never be used in production code**.

## What This Legacy Script Demonstrates

### 1. Roll Day Calculation (Private API)
```python
# DEPRECATED - DO NOT USE
from rateslib.scheduling import _get_unadjusted_roll

_get_unadjusted_roll(
    ueffective=dt(2022, 3, 15),
    utermination=dt(2023, 3, 15), 
    eom=False
)
```

**Modern Replacement:**
```python
# PUBLIC API - USE THIS INSTEAD
from rateslib import Schedule

schedule = Schedule(
    effective=dt(2022, 3, 15),
    termination=dt(2023, 3, 15),
    frequency="M",
    roll=15  # Day of month
)
roll_date = schedule.dates[0]  # First roll date
```

### 2. Regular Schedule Generation (Private API)
```python
# DEPRECATED - DO NOT USE  
from rateslib.scheduling import _generate_regular_schedule_unadjusted

dates = list(_generate_regular_schedule_unadjusted(
    ueffective=dt(2023, 3, 15),
    utermination=dt(2023, 9, 20),
    frequency="M",
    roll="imm"
))
```

**Modern Replacement:**
```python
# PUBLIC API - USE THIS INSTEAD
from rateslib import Schedule

schedule = Schedule(
    effective=dt(2023, 3, 15),
    termination=dt(2023, 9, 20),
    frequency="M",
    roll="imm"
)
dates = schedule.dates
```

### 3. Swap Validation (Private API)
```python
# DEPRECATED - DO NOT USE
from rateslib.scheduling import _check_unadjusted_regular_swap

_check_unadjusted_regular_swap(
    ueffective=dt(2022, 2, 28),
    utermination=dt(2023, 2, 28),
    frequency="M",
    eom=False,
    roll=NoInput(0)
)
```

**Modern Replacement:**
```python
# PUBLIC API - USE THIS INSTEAD  
from rateslib import Schedule

try:
    schedule = Schedule(
        effective=dt(2022, 2, 28),
        termination=dt(2023, 2, 28),
        frequency="M",
        eom=False
    )
    print(f"Valid schedule with {len(schedule.dates)} periods")
except ValueError as e:
    print(f"Invalid schedule: {e}")
```

### 4. Stub Date Calculation (Private API)
```python
# DEPRECATED - DO NOT USE
from rateslib.scheduling import _get_unadjusted_short_stub_date

stub_date = _get_unadjusted_short_stub_date(
    ueffective=dt(2022, 6, 15),
    utermination=dt(2023, 2, 28),
    frequency="M",
    eom=True,
    roll=NoInput(0),
    stub_side="FRONT"
)
```

**Modern Replacement:**
```python
# PUBLIC API - USE THIS INSTEAD
from rateslib import Schedule

schedule = Schedule(
    effective=dt(2022, 6, 15),
    termination=dt(2023, 2, 28),
    frequency="M",
    eom=True,
    stub="SHORTFRONT"
)

# Get stub information
if schedule.n_periods > 0:
    first_period_length = (schedule.dates[1] - schedule.dates[0]).days
    if first_period_length < 25:  # Typical short stub threshold
        print(f"Short front stub detected: {schedule.dates[1]}")
```

## Complete Migration Guide

### Legacy to Modern API Mapping

| **Legacy Private Function** | **Modern Public API** | **Notes** |
|------------------------------|----------------------|-----------|
| `_get_unadjusted_roll()` | `Schedule().dates[0]` | First generated date |
| `_generate_regular_schedule_unadjusted()` | `Schedule().dates` | Full date list |
| `_check_unadjusted_regular_swap()` | `Schedule()` constructor | Built-in validation |
| `_get_unadjusted_short_stub_date()` | `Schedule(stub="SHORTFRONT")` | Automatic stub handling |
| `_get_unadjusted_stub_date()` | `Schedule(stub="LONGFRONT")` | Long stub support |
| `_check_regular_swap()` | `Schedule()` with calendar | Business day integration |

### Step-by-Step Migration Example

#### Original Legacy Code:
```python
# LEGACY - DO NOT USE
from rateslib.scheduling import (
    _get_unadjusted_roll,
    _generate_regular_schedule_unadjusted,
    _check_unadjusted_regular_swap
)

# Get roll date
roll_date = _get_unadjusted_roll(
    ueffective=dt(2022, 2, 28),
    utermination=dt(2023, 2, 28),
    eom=True
)

# Generate schedule
dates = list(_generate_regular_schedule_unadjusted(
    ueffective=dt(2022, 2, 28),
    utermination=dt(2023, 2, 28),
    frequency="M",
    roll="eom"
))

# Validate schedule
is_valid = _check_unadjusted_regular_swap(
    ueffective=dt(2022, 2, 28),
    utermination=dt(2023, 2, 28),
    frequency="M",
    eom=True,
    roll=NoInput(0)
)
```

#### Migrated Modern Code:
```python
# MODERN PUBLIC API - USE THIS
from rateslib import Schedule
from datetime import datetime as dt

# Create schedule (validation is automatic)
schedule = Schedule(
    effective=dt(2022, 2, 28),
    termination=dt(2023, 2, 28),
    frequency="M",
    roll="eom"
)

# Get all information from single object
dates = schedule.dates
roll_date = dates[0] if dates else None
n_periods = schedule.n_periods
is_valid = len(dates) > 0  # Constructor would have failed if invalid

print(f"Schedule with {n_periods} periods")
print(f"First roll date: {roll_date}")
print(f"All dates: {dates}")
```

## Modern Schedule Features

### Advanced Functionality Not Available in Legacy Code

#### 1. Business Day Integration
```python
# Modern API includes calendar support
schedule = Schedule(
    effective=dt(2022, 6, 6),
    termination=dt(2022, 12, 5),
    frequency="Q",
    modifier="MF",  # Modified Following
    calendar="NYC"  # New York holidays
)
```

#### 2. Payment Lag Support
```python
# Separate accrual and payment dates
schedule = Schedule(
    effective=dt(2022, 1, 15),
    termination=dt(2025, 1, 15),
    frequency="Q",
    payment_lag=2,  # 2 business day lag
    calendar="NYC"
)

accrual_dates = schedule.dates
payment_dates = schedule.payment_dates
```

#### 3. Tenor-Based Construction
```python
# String tenors (not possible with legacy functions)
schedule = Schedule(
    effective="2D",    # 2 days from eval_date
    termination="5Y",  # 5 years from effective
    frequency="Q",
    eval_date=dt(2024, 1, 15)
)
```

#### 4. Multiple Evaluation Modes
```python
# Different alignment conventions
swap_schedule = Schedule(
    effective="1Y", termination="10Y", frequency="S",
    eval_mode="swaps_align",
    eval_date=dt(2024, 3, 15)
)

swaption_schedule = Schedule(
    effective="1Y", termination="10Y", frequency="S",
    eval_mode="swaptions_align",  # Different convention
    eval_date=dt(2024, 3, 15)
)
```

## Why Migration is Critical

### 1. **Stability**: Private functions can change or be removed without notice
### 2. **Features**: Public API has more functionality and better error handling  
### 3. **Support**: Only public API is officially supported and documented
### 4. **Performance**: Modern API uses optimized Rust backend
### 5. **Integration**: Seamlessly works with other rateslib components

## Migration Testing Strategy

```python
def test_migration_compatibility():
    """Ensure migrated code produces same results as legacy"""
    
    # Test parameters
    effective = dt(2022, 3, 15)
    termination = dt(2023, 3, 15)
    frequency = "M"
    
    # Modern API
    schedule = Schedule(
        effective=effective,
        termination=termination,  
        frequency=frequency,
        eom=False
    )
    modern_dates = schedule.dates
    
    # Verify key properties
    assert len(modern_dates) >= 12  # Monthly for 1 year
    assert modern_dates[0] >= effective
    assert modern_dates[-1] <= termination
    
    # Check monthly spacing
    for i in range(1, len(modern_dates)):
        diff = modern_dates[i] - modern_dates[i-1]
        assert 28 <= diff.days <= 31  # Monthly variation
    
    print(f"Migration test passed: {len(modern_dates)} dates generated")
```

## Usage Recommendation

### ❌ DO NOT USE THIS SCRIPT
```bash
# This will break in future versions
python ../scripts/examples/coding/scheduling.py  # DEPRECATED
```

### ✅ USE THE MODERN EQUIVALENT
```bash
# Use the updated version instead
python ../scripts/examples/coding_2/Scheduling.py  # CURRENT
```

## Recommended Learning Path

1. **Read**: `/home/peter/rateslib/scripts/examples/coding_2/Scheduling.md` - Complete modern documentation
2. **Study**: `/home/peter/rateslib/scripts/examples/coding_2/Scheduling.py` - Working examples
3. **Practice**: Create your own schedules using the public `Schedule` class
4. **Migrate**: Update any existing code that uses private functions

## Summary

This legacy script demonstrates important scheduling concepts but uses deprecated private APIs. The functionality has been completely replaced by the modern `Schedule` class which provides:

- ✅ **Public API stability**
- ✅ **Enhanced functionality** 
- ✅ **Better error handling**
- ✅ **Performance optimizations**
- ✅ **Comprehensive testing**
- ✅ **Official support**

**Action Required**: Migrate any production code using these private functions to the public `Schedule` API immediately.
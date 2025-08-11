# scheduling.py Documentation

## Overview
Demonstrates schedule generation with various conventions and adjustments.

## Known Issues
⚠️ **This script uses private functions that are not part of the public API:**
- `_get_unadjusted_roll()`
- `_get_rollday()`
- Other private methods starting with `_`

These are internal implementation details and should not be used directly.

## Correct Usage
Use the public `Schedule` class instead:

```python
# Instead of private functions:
# _get_unadjusted_roll(...)  # WRONG

# Use public API:
schedule = Schedule(
    effective=dt(2022, 1, 1),
    termination=dt(2025, 1, 1),
    frequency="Q",
    roll="EOM"
)
dates = schedule.dates  # Get all dates
```

## What the Script Demonstrates
Despite using private APIs, it shows:
1. Roll day calculation
2. Schedule generation
3. Stub period handling
4. Calendar adjustments

## Migration Guide
| Private Function | Public Replacement |
|-----------------|-------------------|
| `_get_unadjusted_roll()` | `Schedule()` constructor |
| `_get_rollday()` | Built into `Schedule` |
| Direct attribute access | Use properties |

## Usage (Not Recommended)
This script should be updated to use public APIs before use.

## Recommended Alternative
See `coding_2/Scheduling.py` for proper public API usage.
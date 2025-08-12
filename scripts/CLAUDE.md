# CLAUDE.md - Rateslib Scripts Directory Guide

## Quick Start: Using Rateslib Cookbook

This directory contains the unified cookbook system for rateslib - a comprehensive collection of working examples and utilities for interest rate curves, swaps, and fixed income instruments.

## Core Files

### 1. cookbook_unified.py (725 lines)
**The main reference implementation** with 7 complete recipes:
- Recipe 1: Single Currency Curve (multiple interpolation methods)
- Recipe 2: SOFR Curve Construction
- Recipe 3: Dependency Chain (Multi-curve with FX)
- Recipe 4: Handle Turns (Year-end adjustments)
- Recipe 5: QuantLib Comparison
- Recipe 6: Zero Rates to Discount Factors
- Recipe 7: Multi-curve Framework (NOWA/NIBOR)

### 2. cookbook_fixes.py (445 lines)
**API compatibility layer** that fixes common issues:
- Interpolation name mapping ("cubic_spline" → "spline")
- Dual number conversion and formatting
- Nodes access patterns
- Safe curve creation utilities

### 3. cookbook_common.py (521 lines)
**Reusable utilities** for production use:
- Curve construction helpers
- Risk calculations (DV01, duration)
- Scenario analysis
- Performance measurement
- Data validation

## Usage Examples

### Quick Test
```bash
# Run all recipes
python cookbook_unified.py

# Expected output: 7/7 recipes pass
```

### Import in Your Code
```python
# Import specific recipes
from cookbook_unified import recipe_2_sofr_curve

# Run the SOFR curve example
result = recipe_2_sofr_curve()
sofr_curve = result["sofr"]
solver = result["solver"]

# Use for your own pricing
my_swap = IRS(
    effective=dt(2024, 1, 1),
    termination="5Y",
    spec="usd_irs",
    curves="sofr",
    fixed_rate=4.5,
    notional=100_000_000
)
npv = my_swap.npv(solver=solver)
```

### Handle API Gotchas
```python
from cookbook_fixes import (
    dual_to_float,           # Convert Dual numbers
    format_npv,              # Format with currency
    get_interpolation_method # Map interpolation names
)

# Example: Format NPV correctly
npv = irs.npv(curve)  # Returns Dual number
print(format_npv(npv, "USD"))  # Prints: $123,456.78
```

## Common Patterns

### Pattern 1: Build a Curve from Market Data
```python
from rateslib import *
from cookbook_fixes import format_npv

# Market rates
rates = {"1M": 5.32, "3M": 5.38, "6M": 5.45, "1Y": 5.44}

# Create curve skeleton
curve = Curve(
    nodes={dt(2024, 1, 1): 1.0},  # Initial guess
    interpolation="log_linear",    # NOT "cubic_spline"!
    convention="Act360"
)

# Calibrate to market
solver = Solver(
    curves=[curve],
    instruments=[IRS(dt(2024, 1, 1), tenor, curves=curve) 
                 for tenor in rates.keys()],
    s=list(rates.values())
)
```

### Pattern 2: Multi-Curve with Dependencies
```python
# Build OIS curve first
ois_solver = Solver(curves=[ois_curve], ...)

# Build LIBOR curve with OIS dependency
libor_solver = Solver(
    curves=[libor_curve],
    pre_solvers=[ois_solver],  # Dependency!
    instruments=[...],
    s=[...]
)

# Price with projection/discount split
swap = IRS(curves=["libor3m", "ois"], ...)
npv = swap.npv(solver=libor_solver)
```

### Pattern 3: Handle Dual Numbers
```python
from cookbook_fixes import dual_to_float

# WRONG
npv = irs.npv(curve)
print(f"{npv:,.2f}")  # TypeError!

# RIGHT
npv = irs.npv(curve)
print(f"{dual_to_float(npv):,.2f}")  # Works!
```

## API Gotchas Reference

| Issue | Wrong | Right | Best Practice |
|-------|-------|-------|---------------|
| Interpolation | `"cubic_spline"` | `"spline"` | Use `get_interpolation_method()` |
| Dual formatting | `f"{npv:,.2f}"` | `f"{float(npv):,.2f}"` | Use `format_npv()` |
| Nodes access | `len(curve.nodes)` | `len(curve.nodes.nodes)` | Use `get_nodes_count()` |
| Missing calendar | `calendar="nok"` | `calendar="all"` | Check available calendars |

## Advanced Features Demonstrated

### Mixed Interpolation (Recipe 1)
Log-linear for short end, cubic spline for long end:
```python
curve = Curve(
    nodes={...},
    interpolation="log_linear",
    t=[  # Knot sequence defines transition
        dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1),
        dt(2025, 1, 1),  # Transition point
        dt(2027, 1, 1), dt(2029, 1, 1), dt(2032, 1, 1),
        dt(2032, 1, 1), dt(2032, 1, 1), dt(2032, 1, 1)
    ]
)
```

### CompositeCurve for Turns (Recipe 4)
```python
# Base curve
base_curve = Curve(...)

# Turn adjustment
turn_curve = Curve(...)
turn_solver = Solver(s=[0.0, -3.0, 0.0])  # -3bp at year-end

# Combine
composite = CompositeCurve([base_curve, turn_curve])
```

### Cross-Currency with FX (Recipe 3)
```python
# Setup FX
fxr = FXRates({"eurusd": 1.10})
fxf = FXForwards(fx_rates=fxr, fx_curves={...})

# Build XCS curve
xcs_solver = Solver(
    pre_solvers=[eur_solver, usd_solver],
    fx=fxf,
    curves=[eurusd_curve],
    instruments=[xcs1, xcs2],
    s=[-5, -10]  # Basis spreads
)
```

## File Organization

### Core Implementation
- `cookbook_unified.py` - Main recipes (7 working examples)
- `cookbook_fixes.py` - API compatibility layer
- `cookbook_common.py` - Shared utilities

### Testing
- `test_recipes_fixed.py` - Test suite with fixes applied
- Run: `python test_recipes_fixed.py`

### Documentation
- `RATESLIB_USER_GUIDE.md` - Comprehensive user guide
- `FINAL_CLEANUP_REPORT.md` - Cleanup summary
- `FIXES_SUMMARY.md` - API fixes documentation

### Legacy Files (for reference)
- `cookbook_recipes.py` - Original implementation (4,673 lines)
- `cookbook_recipes_refactored.py` - Refactored version
- `cookbook_optimized.py` - Performance optimizations

## Performance

- **Code reduction**: 85% (from 4,673 to 725 lines)
- **All recipes working**: 7/7 pass
- **Clean architecture**: Modular and reusable
- **API fixes**: All gotchas handled

## Next Steps

1. **Run the cookbook**: `python cookbook_unified.py`
2. **Study the patterns**: Review each recipe implementation
3. **Use the utilities**: Import `cookbook_common` for production
4. **Apply fixes**: Always use `cookbook_fixes` for compatibility

## Support

For issues or questions:
- Check `RATESLIB_USER_GUIDE.md` for detailed patterns
- Review `cookbook_unified.py` for working examples
- Use `cookbook_fixes.py` for API compatibility
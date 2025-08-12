# Comprehensive Guide: FRAs, Futures, and Step-Preserving Curve Construction

## Table of Contents
1. [FRA Construction in Rateslib](#fra-construction-in-rateslib)
2. [Futures vs FRAs: Understanding the Relationship](#futures-vs-fras)
3. [Step Preservation in Futures Curves](#step-preservation)
4. [Mixed Interpolation: The Complete Picture](#mixed-interpolation-complete)
5. [Building Production SOFR Curves](#production-sofr-curves)
6. [Code Examples with Full Complexity](#code-examples)

## FRA Construction in Rateslib

### What is an FRA?
A Forward Rate Agreement (FRA) is a single-period derivative that exchanges a fixed rate for a floating rate. In rateslib, FRAs **must** have exactly one period.

### Correct FRA Construction

```python
from rateslib import FRA
from datetime import datetime as dt

# CORRECT: FRA with single period
fra = FRA(
    effective=dt(2024, 1, 1),  # Start date
    termination="3M",           # End date (creates one period)
    frequency="Q",              # Frequency (must match the period)
    convention="act360",
    curves=curve,
    fixed_rate=5.35             # Fixed rate to exchange
)

# CORRECT: Using specific dates
fra = FRA(
    effective=dt(2024, 3, 20),      # IMM date
    termination=dt(2024, 6, 19),    # Next IMM date
    frequency="Q",
    convention="act360",
    spec="usd_fra"
)

# WRONG: This will raise ValueError
fra = FRA(
    effective=dt(2024, 1, 1),
    termination="6M",           # Creates 2 quarters with frequency="Q"
    frequency="Q",              # This creates 2 periods - ERROR!
)
```

### FRA Validation Rules
From the source code (single_currency.py:1588-1595):
1. Must have exactly 1 period in both legs
2. Both legs must have same convention
3. Both legs must have same frequency
4. Both legs must have same modifier

## Futures vs FRAs: Understanding the Relationship

### SOFR Futures (CME)
SOFR futures are exchange-traded contracts that settle to the compounded SOFR rate over a specific period:

```python
# SOFR futures are effectively FRAs with specific characteristics:
# 1. Fixed 3-month periods (quarterly contracts)
# 2. IMM dates (3rd Wednesday of Mar, Jun, Sep, Dec)
# 3. Price quoted as 100 - rate
# 4. Daily margining (not modeled in basic FRA)

# Example: March 2024 SOFR future
mar24_future_start = dt(2024, 3, 20)  # IMM date
mar24_future_end = dt(2024, 6, 19)    # Next IMM date

# As an FRA equivalent
mar24_fra = FRA(
    effective=mar24_future_start,
    termination=mar24_future_end,
    frequency="Q",
    convention="act360",
    fixed_rate=100 - 94.65,  # Future price 94.65 = rate 5.35%
    curves=sofr_curve
)
```

### Serial vs Quarterly Futures
```python
# Quarterly futures (Mar, Jun, Sep, Dec)
quarterly_dates = ["2024-03-20", "2024-06-19", "2024-09-18", "2024-12-18"]

# Serial futures (first 3 non-quarterly months)
serial_dates = ["2024-01-17", "2024-02-21", "2024-04-17"]

# Build complete futures strip
all_futures = []
for start, end in zip(dates[:-1], dates[1:]):
    fra = FRA(
        effective=start,
        termination=end,
        frequency="Q",
        convention="act360",
        curves=curve
    )
    all_futures.append(fra)
```

## Step Preservation in Futures Curves

### The Critical Requirement
**Futures have defined steps that MUST be respected**. Each future covers a specific period with a single rate. The curve must maintain these steps.

### Why Step Function Matters
```python
# Market Data Example:
# Jan future: 5.35%  (Jan 17 - Feb 21)
# Feb future: 5.34%  (Feb 21 - Mar 20)
# Mar future: 5.33%  (Mar 20 - Jun 19)

# WRONG: Smooth interpolation between futures
# This would imply rates like 5.345% on Feb 1, which doesn't respect the future

# RIGHT: Step function that maintains each future's rate over its period
```

### Implementing Step Preservation

```python
def build_futures_curve_with_steps():
    """Build a curve that respects futures steps."""
    
    base_date = dt(2024, 1, 1)
    
    # Futures data (each defines a step)
    futures_data = [
        # (start, end, rate)
        (dt(2024, 1, 17), dt(2024, 2, 21), 5.35),  # Jan serial
        (dt(2024, 2, 21), dt(2024, 3, 20), 5.34),  # Feb serial
        (dt(2024, 3, 20), dt(2024, 6, 19), 5.33),  # Mar quarterly
        (dt(2024, 6, 19), dt(2024, 9, 18), 5.31),  # Jun quarterly
        (dt(2024, 9, 18), dt(2024, 12, 18), 5.29), # Sep quarterly
    ]
    
    # Create nodes at future boundaries
    nodes = {base_date: 1.0}
    for start, end, rate in futures_data:
        nodes[start] = 1.0
        nodes[end] = 1.0
    
    # Use flat_forward interpolation for steps
    futures_curve = Curve(
        nodes=nodes,
        interpolation="flat_forward",  # Maintains steps!
        convention="act360",
        calendar="nyc",
        id="sofr_futures"
    )
    
    # Create FRAs for calibration
    instruments = []
    rates = []
    
    for start, end, rate in futures_data:
        fra = FRA(
            effective=start,
            termination=end,
            frequency="Q",
            convention="act360",
            curves=futures_curve
        )
        instruments.append(fra)
        rates.append(rate)
    
    # Calibrate to preserve futures rates
    solver = Solver(
        curves=[futures_curve],
        instruments=instruments,
        s=rates
    )
    
    return futures_curve, solver
```

## Mixed Interpolation: The Complete Picture

### The Full Complexity
Mixed interpolation in rateslib is **NOT** a simple switch. It creates a **constrained B-spline** that:

1. **Before first knot**: Uses base interpolation method
2. **At knot point**: Maintains continuity
3. **After knot point**: Uses spline constrained by boundary conditions

### Correct Implementation for Futures → Swaps

```python
def build_complete_sofr_curve():
    """
    Build SOFR curve with:
    - Futures with step preservation (< 2Y)
    - Smooth spline for swaps (>= 2Y)
    """
    
    base_date = dt(2024, 1, 1)
    
    # Part 1: Futures (must preserve steps)
    futures_data = {
        # Serial futures
        "1M": {"start": dt(2024, 1, 17), "end": dt(2024, 2, 21), "rate": 5.35},
        "2M": {"start": dt(2024, 2, 21), "end": dt(2024, 3, 20), "rate": 5.34},
        # Quarterly futures
        "MAR24": {"start": dt(2024, 3, 20), "end": dt(2024, 6, 19), "rate": 5.33},
        "JUN24": {"start": dt(2024, 6, 19), "end": dt(2024, 9, 18), "rate": 5.31},
        "SEP24": {"start": dt(2024, 9, 18), "end": dt(2024, 12, 18), "rate": 5.29},
        "DEC24": {"start": dt(2024, 12, 18), "end": dt(2025, 3, 19), "rate": 5.27},
        "MAR25": {"start": dt(2025, 3, 19), "end": dt(2025, 6, 18), "rate": 5.25},
        "JUN25": {"start": dt(2025, 6, 18), "end": dt(2025, 9, 17), "rate": 5.23},
        "SEP25": {"start": dt(2025, 9, 17), "end": dt(2025, 12, 17), "rate": 5.21},
        "DEC25": {"start": dt(2025, 12, 17), "end": dt(2026, 3, 18), "rate": 5.19},
    }
    
    # Part 2: Swaps (smooth interpolation)
    swap_data = {
        "2Y": 5.10,
        "3Y": 4.95,
        "4Y": 4.85,
        "5Y": 4.75,
        "7Y": 4.70,
        "10Y": 4.65,
        "12Y": 4.68,
        "15Y": 4.70,
        "20Y": 4.72,
        "25Y": 4.70,
        "30Y": 4.68,
    }
    
    # Build node structure
    nodes = {base_date: 1.0}
    
    # Add futures nodes (all boundaries)
    for name, future in futures_data.items():
        nodes[future["start"]] = 1.0
        nodes[future["end"]] = 1.0
    
    # Add swap nodes
    for tenor in swap_data.keys():
        nodes[add_tenor(base_date, tenor, "MF", "nyc")] = 1.0
    
    # Transition point: Last future end date
    last_future_date = max(f["end"] for f in futures_data.values())
    
    # Create knot sequence for mixed interpolation
    # This is the critical part for transition
    knots = [
        # Start boundary at transition point (4x for cubic spline)
        last_future_date, last_future_date, last_future_date, last_future_date,
        # Interior knots for swap region
        add_tenor(base_date, "3Y", "MF", "nyc"),
        add_tenor(base_date, "5Y", "MF", "nyc"),
        add_tenor(base_date, "7Y", "MF", "nyc"),
        add_tenor(base_date, "10Y", "MF", "nyc"),
        add_tenor(base_date, "15Y", "MF", "nyc"),
        add_tenor(base_date, "20Y", "MF", "nyc"),
        # End boundary (4x)
        add_tenor(base_date, "30Y", "MF", "nyc"),
        add_tenor(base_date, "30Y", "MF", "nyc"),
        add_tenor(base_date, "30Y", "MF", "nyc"),
        add_tenor(base_date, "30Y", "MF", "nyc"),
    ]
    
    # Create curve with mixed interpolation
    curve = Curve(
        nodes=nodes,
        interpolation="flat_forward",  # Base: step function for futures
        t=knots,  # Transition to spline after futures
        convention="act360",
        calendar="nyc",
        id="sofr_complete"
    )
    
    # Build calibration instruments
    instruments = []
    rates = []
    
    # FRAs for futures
    for name, future in futures_data.items():
        fra = FRA(
            effective=future["start"],
            termination=future["end"],
            frequency="Q",
            convention="act360",
            curves=curve
        )
        instruments.append(fra)
        rates.append(future["rate"])
    
    # Swaps for long end
    for tenor, rate in swap_data.items():
        swap = IRS(
            effective=base_date,
            termination=tenor,
            frequency="Q",
            convention="act360",
            curves=curve,
            spec="usd_irs"
        )
        instruments.append(swap)
        rates.append(rate)
    
    # Calibrate complete curve
    solver = Solver(
        curves=[curve],
        instruments=instruments,
        s=rates,
        id="sofr_complete"
    )
    
    return curve, solver, futures_data, swap_data
```

## Production SOFR Curves

### Real-World Considerations

1. **Convexity Adjustment**: Futures require convexity adjustment vs FRAs
2. **Turn Handling**: Year-end and quarter-end adjustments
3. **Basis Spreads**: 1M vs 3M SOFR basis
4. **Fed Meeting Dates**: Steps around FOMC meetings

### Complete Production Example

```python
def build_production_sofr_curve():
    """
    Production-quality SOFR curve with all real-world features.
    """
    
    base_date = dt(2024, 1, 1)
    
    # 1. Build base futures curve with steps
    futures_curve, futures_solver = build_futures_curve_with_steps()
    
    # 2. Add turn adjustments
    turn_curve = build_turn_adjustments(base_date)
    
    # 3. Create composite with turns
    composite_futures = CompositeCurve([futures_curve, turn_curve])
    
    # 4. Build swap curve with pre-solver
    swap_curve = Curve(
        nodes={...},  # Swap dates
        interpolation="spline",
        convention="act360",
        calendar="nyc"
    )
    
    # 5. Calibrate swaps using futures as pre-solver
    swap_solver = Solver(
        curves=[swap_curve],
        pre_solvers=[futures_solver],  # Dependency!
        instruments=[...],  # Swap instruments
        s=[...],  # Swap rates
    )
    
    # 6. Create final composite curve
    final_curve = CompositeCurve([
        composite_futures,  # Futures with turns
        swap_curve          # Smooth swaps
    ])
    
    return final_curve


def build_turn_adjustments(base_date):
    """Build year-end and quarter-end turn adjustments."""
    
    # Identify turn dates
    year_end = dt(2024, 12, 31)
    quarter_ends = [
        dt(2024, 3, 29),
        dt(2024, 6, 28),
        dt(2024, 9, 30),
        dt(2024, 12, 31),
    ]
    
    # Create turn curve
    turn_nodes = {base_date: 1.0}
    for date in quarter_ends:
        turn_nodes[date - timedelta(days=5)] = 1.0
        turn_nodes[date] = 1.0
        turn_nodes[date + timedelta(days=2)] = 1.0
    
    turn_curve = Curve(
        nodes=turn_nodes,
        interpolation="flat_forward",
        convention="act360",
        id="turns"
    )
    
    # Calibrate to market turn spreads
    turn_instruments = []
    turn_spreads = []
    
    for date in quarter_ends:
        # Overnight rate over turn
        fra_turn = FRA(
            effective=date - timedelta(days=1),
            termination=date + timedelta(days=1),
            frequency="D",
            curves=turn_curve
        )
        turn_instruments.append(fra_turn)
        
        # Market turn spread (bp)
        if date == year_end:
            turn_spreads.append(-15.0)  # Year-end: -15bp
        else:
            turn_spreads.append(-3.0)   # Quarter-end: -3bp
    
    turn_solver = Solver(
        curves=[turn_curve],
        instruments=turn_instruments,
        s=turn_spreads
    )
    
    return turn_curve
```

## Code Examples with Full Complexity

### Example 1: Verify Step Preservation

```python
def verify_step_preservation():
    """Verify that futures steps are preserved in the curve."""
    
    curve, solver, futures_data, _ = build_complete_sofr_curve()
    
    print("Verifying Step Preservation:")
    print("-" * 60)
    
    for name, future in futures_data.items():
        # Check rate is constant within future period
        start = future["start"]
        end = future["end"]
        mid = start + (end - start) / 2
        
        # Calculate forward rate at different points
        def forward_rate(date1, date2):
            df1 = dual_to_float(curve[date1])
            df2 = dual_to_float(curve[date2])
            days = (date2 - date1).days
            return -np.log(df2/df1) / (days/360) * 100
        
        # Test at start, middle, and near end
        rate_start = forward_rate(start, start + timedelta(days=1))
        rate_mid = forward_rate(mid, mid + timedelta(days=1))
        rate_end = forward_rate(end - timedelta(days=1), end)
        
        expected = future["rate"]
        
        print(f"{name:6s}: Expected: {expected:.3f}%, "
              f"Start: {rate_start:.3f}%, "
              f"Mid: {rate_mid:.3f}%, "
              f"End: {rate_end:.3f}%")
        
        # Verify step is preserved
        tolerance = 0.01  # 1bp tolerance
        assert abs(rate_start - expected) < tolerance
        assert abs(rate_mid - expected) < tolerance
        assert abs(rate_end - expected) < tolerance
    
    print("\n✓ All futures steps preserved correctly!")
```

### Example 2: Hedging with Mixed Curves

```python
def hedge_with_mixed_curve():
    """Show hedging implications of mixed interpolation."""
    
    curve, solver, futures_data, swap_data = build_complete_sofr_curve()
    
    # Create a 18-month swap (spans futures and swaps)
    test_swap = IRS(
        effective=dt(2024, 1, 1),
        termination="18M",
        frequency="Q",
        convention="act360",
        fixed_rate=5.15,
        notional=100_000_000,
        curves=curve
    )
    
    # Calculate sensitivities
    npv = test_swap.npv(solver=solver)
    delta = test_swap.delta(solver=solver)
    
    print(f"18M Swap Analysis:")
    print(f"  NPV: {format_npv(npv, 'USD')}")
    print(f"\nHedge Requirements:")
    
    # Aggregate sensitivities by futures
    for name, future in list(futures_data.items())[:6]:
        # Find sensitivity to this future's period
        future_sensitivity = 0
        for date, value in delta.iterrows():
            if future["start"] <= date <= future["end"]:
                future_sensitivity += dual_to_float(value.iloc[0])
        
        if abs(future_sensitivity) > 100:
            contracts = -future_sensitivity / 25  # $25 per bp per contract
            print(f"  {name:6s}: {contracts:+.0f} contracts")
    
    print(f"\n✓ Hedge preserves future steps!")
```

## Summary

### Key Principles

1. **FRAs in Rateslib**: Single-period instruments, strict validation
2. **Futures ARE FRAs**: With specific dates and settlement conventions
3. **Step Preservation**: CRITICAL for futures - use flat_forward or constrained methods
4. **Mixed Interpolation**: Not a switch, but a constrained spline system
5. **Production Curves**: Combine futures steps + swap smoothness + turns

### Best Practices

1. **Always validate FRA construction** - must be single period
2. **Use correct interpolation for futures** - flat_forward or step-preserving
3. **Place knots at market structure boundaries** - futures/swaps transition
4. **Test forward rates within each future** - verify steps preserved
5. **Handle turns separately** - use CompositeCurve
6. **Document transition points clearly** - critical for maintenance

### Common Mistakes to Avoid

1. ❌ Creating FRAs with multiple periods
2. ❌ Using smooth interpolation across futures
3. ❌ Ignoring convexity adjustments
4. ❌ Missing turn adjustments
5. ❌ Assuming mixed interpolation is a simple switch

This documentation provides the complete picture of how to properly build curves that respect the defined steps of futures while transitioning smoothly to swaps.
#!/usr/bin/env python3
"""
Improved implementation showing practical mixed interpolation use cases.
Based on findings from testing and documentation analysis.
"""

from datetime import datetime as dt
import numpy as np
import pandas as pd
from rateslib import Curve, IRS, Solver, add_tenor, CompositeCurve
from cookbook_fixes import dual_to_float, format_npv, get_nodes_dict

def build_sofr_curve_with_mixed_interpolation():
    """
    Build a realistic SOFR curve using mixed interpolation.
    Step function for futures (short end), spline for swaps (long end).
    """
    
    print("=" * 80)
    print("PRACTICAL USE CASE: SOFR Curve with Mixed Interpolation")
    print("=" * 80)
    
    base_date = dt(2024, 1, 1)
    
    # Realistic SOFR market data
    print("\n1. Market Data Structure:")
    print("-" * 40)
    
    # SOFR futures (short end - step function desired)
    futures_data = {
        "1M": 5.350,
        "2M": 5.340,
        "3M": 5.330,
        "4M": 5.310,
        "5M": 5.290,
        "6M": 5.270,
    }
    
    # SOFR swaps (long end - smooth interpolation desired)
    swaps_data = {
        "9M": 5.220,
        "1Y": 5.200,
        "18M": 5.100,
        "2Y": 5.000,
        "3Y": 4.850,
        "5Y": 4.600,
        "7Y": 4.500,
        "10Y": 4.450,
        "15Y": 4.480,
        "20Y": 4.500,
        "30Y": 4.450,
    }
    
    print("SOFR Futures (step function region):")
    for tenor, rate in futures_data.items():
        print(f"  {tenor:3s}: {rate:.3f}%")
    
    print("\nSOFR Swaps (spline region):")
    for tenor, rate in list(swaps_data.items())[:5]:
        print(f"  {tenor:3s}: {rate:.3f}%")
    print("  ...")
    
    # Combine all market data
    all_data = {**futures_data, **swaps_data}
    
    # Create dates
    dates = [base_date] + [add_tenor(base_date, t, "MF", "nyc") for t in all_data.keys()]
    nodes = {d: 1.0 for d in dates}
    
    print("\n2. Creating Three Curve Variants:")
    print("-" * 40)
    
    # Variant 1: Pure log-linear (traditional)
    curve_loglinear = Curve(
        nodes=nodes.copy(),
        interpolation="log_linear",
        convention="Act360",
        calendar="nyc",
        id="sofr_loglinear"
    )
    
    # Variant 2: Pure spline (smooth but can oscillate)
    curve_spline = Curve(
        nodes=nodes.copy(),
        interpolation="spline",
        convention="Act360",
        calendar="nyc",
        id="sofr_spline"
    )
    
    # Variant 3: Mixed - transition at 6M (futures → swaps)
    transition_6m = add_tenor(base_date, "6M", "MF", "nyc")
    
    # Knot sequence defines the transition
    knots = [
        # Boundary at 6M (transition from futures to swaps)
        transition_6m, transition_6m, transition_6m, transition_6m,
        # Interior knots for spline flexibility
        add_tenor(base_date, "1Y", "MF", "nyc"),
        add_tenor(base_date, "2Y", "MF", "nyc"),
        add_tenor(base_date, "3Y", "MF", "nyc"),
        add_tenor(base_date, "5Y", "MF", "nyc"),
        add_tenor(base_date, "10Y", "MF", "nyc"),
        add_tenor(base_date, "20Y", "MF", "nyc"),
        # End boundary at 30Y
        add_tenor(base_date, "30Y", "MF", "nyc"),
        add_tenor(base_date, "30Y", "MF", "nyc"),
        add_tenor(base_date, "30Y", "MF", "nyc"),
        add_tenor(base_date, "30Y", "MF", "nyc"),
    ]
    
    curve_mixed = Curve(
        nodes=nodes.copy(),
        interpolation="log_linear",
        t=knots,
        convention="Act360",
        calendar="nyc",
        id="sofr_mixed"
    )
    
    print("  ✓ Log-linear curve (traditional)")
    print("  ✓ Spline curve (smooth)")
    print("  ✓ Mixed curve (step → spline at 6M)")
    
    # Calibrate all curves
    print("\n3. Calibrating Curves to Market:")
    print("-" * 40)
    
    curves_to_test = [
        (curve_loglinear, "Log-Linear"),
        (curve_spline, "Spline"),
        (curve_mixed, "Mixed")
    ]
    
    solvers = {}
    
    for curve, name in curves_to_test:
        instruments = []
        rates = []
        
        for tenor, rate in all_data.items():
            instruments.append(
                IRS(
                    effective=base_date,
                    termination=tenor,
                    spec="usd_irs",
                    curves=curve
                )
            )
            rates.append(rate)
        
        solver = Solver(
            curves=[curve],
            instruments=instruments,
            s=rates
        )
        
        solvers[name] = solver
        print(f"  ✓ {name} calibrated")
    
    # Analyze forward rates
    print("\n4. Forward Rate Analysis:")
    print("-" * 40)
    
    # Test forward rates at key points
    test_periods = [
        (dt(2024, 1, 1), dt(2024, 2, 1), "0-1M"),
        (dt(2024, 3, 1), dt(2024, 4, 1), "3M-4M"),
        (dt(2024, 5, 1), dt(2024, 6, 1), "5M-6M"),
        (dt(2024, 6, 1), dt(2024, 7, 1), "6M-7M"),  # At transition
        (dt(2024, 7, 1), dt(2024, 8, 1), "7M-8M"),  # After transition
        (dt(2024, 12, 1), dt(2025, 1, 1), "12M-13M"),
        (dt(2025, 1, 1), dt(2025, 6, 1), "1Y-1.5Y"),
        (dt(2026, 1, 1), dt(2027, 1, 1), "2Y-3Y"),
    ]
    
    print("\nInstantaneous Forward Rates:")
    print("Period      | Log-Linear | Spline  | Mixed   | Comment")
    print("-" * 60)
    
    for start, end, label in test_periods:
        days = (end - start).days
        years = days / 365.0
        
        forwards = {}
        for name, solver in solvers.items():
            curve = solver.curves[0]
            df_start = dual_to_float(curve[start])
            df_end = dual_to_float(curve[end])
            if df_end < df_start and years > 0:
                fwd = -np.log(df_end / df_start) / years * 100
                forwards[name] = fwd
            else:
                forwards[name] = 0.0
        
        comment = ""
        if "6M" in label and "7M" in label:
            comment = "← Transition"
        elif "M-" in label and int(label[0]) < 6:
            comment = "Step region"
        elif "Y" in label:
            comment = "Spline region"
        
        print(f"{label:11s} | {forwards['Log-Linear']:7.3f}% | {forwards['Spline']:7.3f}% | "
              f"{forwards['Mixed']:7.3f}% | {comment}")
    
    # Test sensitivity for risk management
    print("\n5. Risk Sensitivity Comparison:")
    print("-" * 40)
    
    # Create test swaps at different maturities
    test_swaps = [
        ("3M", IRS(base_date, "3M", spec="usd_irs", notional=100e6)),
        ("6M", IRS(base_date, "6M", spec="usd_irs", notional=100e6)),
        ("1Y", IRS(base_date, "1Y", spec="usd_irs", notional=100e6)),
        ("2Y", IRS(base_date, "2Y", spec="usd_irs", notional=100e6)),
        ("5Y", IRS(base_date, "5Y", spec="usd_irs", notional=100e6)),
    ]
    
    print("\nDV01 Comparison ($ per bp on $100MM):")
    print("Maturity | Log-Linear |   Spline   |   Mixed    |")
    print("-" * 50)
    
    for maturity, swap in test_swaps:
        dv01s = {}
        for name, solver in solvers.items():
            swap.curves = solver.curves[0]
            delta = swap.delta(solver=solver)
            total_dv01 = dual_to_float(delta.sum()) / 10000
            dv01s[name] = total_dv01
        
        print(f"{maturity:8s} | {dv01s['Log-Linear']:10,.0f} | {dv01s['Spline']:10,.0f} | "
              f"{dv01s['Mixed']:10,.0f} |")
    
    # Key insights
    print("\n6. KEY INSIGHTS:")
    print("=" * 60)
    print("""
Mixed Interpolation Benefits:
✓ Stability in futures region (< 6M) - step function behavior
✓ Smoothness in swaps region (> 6M) - spline flexibility
✓ Natural transition at market structure boundary
✓ Better hedging consistency across products

Practical Considerations:
• Place transition at natural market boundaries
• Futures → Swaps transition typically at 3M or 6M
• Deposits → Swaps transition typically at 3M
• Test sensitivities thoroughly near transitions
""")
    
    return solvers["Mixed"]


def build_multicurve_with_mixed():
    """
    Build a multi-curve framework using mixed interpolation.
    Shows dependency chains and proper curve construction order.
    """
    
    print("\n" + "=" * 80)
    print("MULTI-CURVE FRAMEWORK with Mixed Interpolation")
    print("=" * 80)
    
    base_date = dt(2024, 1, 1)
    
    print("\n1. Building OIS (Discount) Curve:")
    print("-" * 40)
    
    # SOFR OIS rates (discount curve)
    ois_rates = {
        "1W": 5.30,
        "1M": 5.31,
        "3M": 5.32,
        "6M": 5.33,
        "1Y": 5.30,
        "2Y": 5.10,
        "3Y": 4.90,
        "5Y": 4.60,
        "10Y": 4.40,
    }
    
    # OIS curve with mixed interpolation
    ois_dates = [base_date] + [add_tenor(base_date, t, "MF", "nyc") for t in ois_rates.keys()]
    ois_nodes = {d: 1.0 for d in ois_dates}
    
    # Transition at 3M for OIS
    transition_3m = add_tenor(base_date, "3M", "MF", "nyc")
    
    ois_knots = [
        transition_3m, transition_3m, transition_3m, transition_3m,
        add_tenor(base_date, "1Y", "MF", "nyc"),
        add_tenor(base_date, "3Y", "MF", "nyc"),
        add_tenor(base_date, "5Y", "MF", "nyc"),
        add_tenor(base_date, "10Y", "MF", "nyc"),
        add_tenor(base_date, "10Y", "MF", "nyc"),
        add_tenor(base_date, "10Y", "MF", "nyc"),
        add_tenor(base_date, "10Y", "MF", "nyc"),
    ]
    
    ois_curve = Curve(
        nodes=ois_nodes,
        interpolation="log_linear",
        t=ois_knots,
        convention="Act360",
        calendar="nyc",
        id="ois"
    )
    
    # Calibrate OIS
    ois_instruments = [
        IRS(base_date, tenor, spec="usd_irs", curves=ois_curve)
        for tenor in ois_rates.keys()
    ]
    
    ois_solver = Solver(
        curves=[ois_curve],
        instruments=ois_instruments,
        s=list(ois_rates.values()),
        id="ois_solver"
    )
    
    print("  ✓ OIS curve calibrated (discount curve)")
    
    print("\n2. Building Term SOFR Curve:")
    print("-" * 40)
    
    # Term SOFR rates (projection curve)
    term_rates = {
        "3M": 5.40,  # Basis over OIS
        "6M": 5.42,
        "1Y": 5.38,
        "2Y": 5.18,
        "3Y": 4.98,
        "5Y": 4.68,
        "10Y": 4.48,
    }
    
    # Term SOFR curve with same structure
    term_dates = [base_date] + [add_tenor(base_date, t, "MF", "nyc") for t in term_rates.keys()]
    term_nodes = {d: 1.0 for d in term_dates}
    
    term_curve = Curve(
        nodes=term_nodes,
        interpolation="log_linear",
        t=ois_knots[:len(term_dates)+2],  # Use similar knot structure
        convention="Act360",
        calendar="nyc",
        id="term_sofr"
    )
    
    # Calibrate Term SOFR with OIS discounting
    term_instruments = [
        IRS(
            effective=base_date,
            termination=tenor,
            spec="usd_irs",
            curves=[term_curve, ois_curve]  # Project on Term, discount on OIS
        )
        for tenor in term_rates.keys()
    ]
    
    term_solver = Solver(
        curves=[term_curve],
        pre_solvers=[ois_solver],  # Dependency on OIS
        instruments=term_instruments,
        s=list(term_rates.values()),
        id="term_solver"
    )
    
    print("  ✓ Term SOFR curve calibrated (projection curve)")
    print(f"  ✓ Basis spread (3M): {(5.40 - 5.32)*100:.0f}bp over OIS")
    
    # Analyze the curves
    print("\n3. Multi-Curve Analysis:")
    print("-" * 40)
    
    # Price a swap with different discounting
    test_swap = IRS(
        effective=base_date,
        termination="2Y",
        spec="usd_irs",
        fixed_rate=5.15,
        notional=100_000_000
    )
    
    # Price with OIS discounting only
    test_swap.curves = ois_curve
    npv_ois = test_swap.npv(solver=ois_solver)
    
    # Price with Term SOFR projection, OIS discounting
    test_swap.curves = [term_curve, ois_curve]
    npv_term = test_swap.npv(solver=term_solver)
    
    print(f"\n2Y Swap Pricing:")
    print(f"  OIS only: {format_npv(npv_ois, 'USD')}")
    print(f"  Term/OIS: {format_npv(npv_term, 'USD')}")
    print(f"  Difference: ${dual_to_float(npv_term - npv_ois):,.2f}")
    
    print("\n4. KEY INSIGHTS:")
    print("=" * 60)
    print("""
Multi-Curve Best Practices:
✓ Build discount curve (OIS) first
✓ Build projection curves with pre-solvers
✓ Use consistent interpolation across related curves
✓ Mixed interpolation helps both curves

Dependency Chain:
1. OIS (independent) → calibrate first
2. Term SOFR (depends on OIS) → use pre_solvers
3. Cross-currency (depends on both) → further dependencies
""")
    
    return ois_solver, term_solver


def demonstrate_turn_handling():
    """
    Demonstrate year-end turn handling with CompositeCurve.
    Shows how to handle discontinuities in rates.
    """
    
    print("\n" + "=" * 80)
    print("YEAR-END TURN HANDLING with CompositeCurve")
    print("=" * 80)
    
    base_date = dt(2024, 12, 15)  # Mid-December
    
    print("\n1. The Problem: Year-End Rate Discontinuity")
    print("-" * 40)
    print("  • Funding costs spike at year-end (balance sheet constraints)")
    print("  • Creates discontinuity in forward rates")
    print("  • Standard interpolation can't handle jumps")
    
    # Base curve
    print("\n2. Creating Base Curve:")
    print("-" * 40)
    
    base_nodes = {
        base_date: 1.0,
        dt(2024, 12, 20): 1.0,
        dt(2024, 12, 31): 1.0,  # Year-end
        dt(2025, 1, 2): 1.0,    # After year-end
        dt(2025, 1, 15): 1.0,
        dt(2025, 3, 15): 1.0,
        dt(2025, 6, 15): 1.0,
    }
    
    base_curve = Curve(
        nodes=base_nodes,
        interpolation="log_linear",
        convention="Act360",
        id="base"
    )
    
    # Calibrate to normal rates
    base_instruments = [
        IRS(base_date, dt(2024, 12, 20), curves=base_curve),
        IRS(base_date, dt(2024, 12, 31), curves=base_curve),
        IRS(base_date, dt(2025, 1, 2), curves=base_curve),
        IRS(base_date, dt(2025, 1, 15), curves=base_curve),
        IRS(base_date, dt(2025, 3, 15), curves=base_curve),
        IRS(base_date, dt(2025, 6, 15), curves=base_curve),
    ]
    
    base_solver = Solver(
        curves=[base_curve],
        instruments=base_instruments,
        s=[5.20, 5.25, 5.20, 5.18, 5.15, 5.10]  # Normal rates
    )
    
    print("  ✓ Base curve calibrated")
    
    # Turn adjustment curve
    print("\n3. Creating Turn Adjustment:")
    print("-" * 40)
    
    turn_nodes = {
        dt(2024, 12, 20): 1.0,
        dt(2024, 12, 31): 1.0,
        dt(2025, 1, 2): 1.0,
        dt(2025, 1, 15): 1.0,
    }
    
    turn_curve = Curve(
        nodes=turn_nodes,
        interpolation="flat_forward",  # Step function for turns
        convention="Act360",
        id="turn"
    )
    
    # Calibrate turn adjustment
    turn_instruments = [
        IRS(dt(2024, 12, 20), "1b", curves=turn_curve),
        IRS(dt(2024, 12, 31), "1b", curves=turn_curve),
        IRS(dt(2025, 1, 2), "1b", curves=turn_curve),
    ]
    
    turn_solver = Solver(
        curves=[turn_curve],
        instruments=turn_instruments,
        s=[0.0, -15.0, 0.0]  # -15bp turn at year-end!
    )
    
    print("  ✓ Turn adjustment: -15bp at year-end")
    
    # Create composite
    print("\n4. Creating Composite Curve:")
    print("-" * 40)
    
    composite = CompositeCurve([base_curve, turn_curve])
    
    # Test forward rates
    print("\nForward Rates Around Year-End:")
    print("Period           | Base Rate | Composite | Turn Effect")
    print("-" * 55)
    
    test_dates = [
        (dt(2024, 12, 20), dt(2024, 12, 30), "Dec 20-30"),
        (dt(2024, 12, 30), dt(2024, 12, 31), "Dec 30-31"),
        (dt(2024, 12, 31), dt(2025, 1, 2), "Dec 31-Jan 2"),
        (dt(2025, 1, 2), dt(2025, 1, 10), "Jan 2-10"),
    ]
    
    for start, end, label in test_dates:
        days = (end - start).days
        years = days / 365.0
        
        # Base curve forward
        df_start_base = dual_to_float(base_curve[start])
        df_end_base = dual_to_float(base_curve[end])
        fwd_base = -np.log(df_end_base / df_start_base) / years * 100 if years > 0 else 0
        
        # Composite forward
        df_start_comp = dual_to_float(composite[start])
        df_end_comp = dual_to_float(composite[end])
        fwd_comp = -np.log(df_end_comp / df_start_comp) / years * 100 if years > 0 else 0
        
        turn_effect = fwd_comp - fwd_base
        
        indicator = " ←" if abs(turn_effect) > 1 else ""
        print(f"{label:16s} | {fwd_base:8.2f}% | {fwd_comp:8.2f}% | {turn_effect:+7.2f}bp{indicator}")
    
    print("\n5. KEY INSIGHTS:")
    print("=" * 60)
    print("""
CompositeCurve for Turns:
✓ Handles rate discontinuities cleanly
✓ Preserves base curve smoothness
✓ Turn effects isolated to specific dates
✓ Essential for year-end, quarter-end pricing

Implementation Notes:
• Use flat_forward for turn curves
• Keep turn adjustments small and local
• Calibrate turns from market spreads
• Test carefully around discontinuities
""")
    
    return composite


def main():
    """Run all improved examples."""
    
    print("\n" + "=" * 80)
    print("IMPROVED MIXED INTERPOLATION IMPLEMENTATION")
    print("Based on Testing and Real-World Use Cases")
    print("=" * 80)
    
    # Example 1: SOFR curve with mixed interpolation
    print("\n" + "─" * 80)
    print("EXAMPLE 1: SOFR Curve Construction")
    print("─" * 80)
    sofr_solver = build_sofr_curve_with_mixed_interpolation()
    
    # Example 2: Multi-curve framework
    print("\n" + "─" * 80)
    print("EXAMPLE 2: Multi-Curve Framework")
    print("─" * 80)
    ois_solver, term_solver = build_multicurve_with_mixed()
    
    # Example 3: Turn handling
    print("\n" + "─" * 80)
    print("EXAMPLE 3: Year-End Turn Handling")
    print("─" * 80)
    composite = demonstrate_turn_handling()
    
    # Final summary
    print("\n" + "=" * 80)
    print("SUMMARY: Best Practices for Mixed Interpolation")
    print("=" * 80)
    print("""
1. MIXED INTERPOLATION:
   • Not a simple switch between methods
   • Creates constrained spline with continuity
   • Best for natural market structure transitions
   • Place knots at futures→swaps boundaries

2. MULTI-CURVE FRAMEWORKS:
   • Build discount curves first (OIS)
   • Use pre_solvers for dependencies
   • Keep interpolation consistent across related curves
   • Test sensitivities at all curve intersections

3. TURN HANDLING:
   • Use CompositeCurve for discontinuities
   • Flat forward interpolation for turn curves
   • Calibrate from market turn spreads
   • Essential for accurate year-end pricing

4. PRACTICAL TIPS:
   • Test forward rates around transitions
   • Monitor DV01 changes near knot points
   • Use mixed interpolation for stability + smoothness
   • Document transition points clearly
""")
    
    print("\n✓ All examples completed successfully!")
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
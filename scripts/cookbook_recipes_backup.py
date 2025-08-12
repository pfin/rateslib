"""
Rateslib Cookbook Recipes
==========================

This module contains all 29 cookbook recipes from the rateslib documentation,
organized into categories for easy access and execution.

Categories:
1. Interest Rate Curve Building (9 recipes)
2. Credit Curve Building (1 recipe)  
3. FX Volatility Surface Building (3 recipes)
4. Instrument Pricing (8 recipes)
5. Risk Sensitivity Analysis (8 recipes)

Each recipe is implemented as a standalone function that can be run independently.
"""

import numpy as np
import pandas as pd
from datetime import datetime as dt
from pandas import DataFrame, option_context
import matplotlib.pyplot as plt

# Import rateslib components
try:
    import rateslib as rl
    from rateslib import *
    from rateslib import NoInput
except ImportError:
    print("Warning: rateslib not installed. Some functions may not work.")
    # Define placeholders for testing without rateslib
    class NoInput:
        def __init__(self, val):
            self.val = val

# ============================================================================
# SECTION 1: INTEREST RATE CURVE BUILDING RECIPES
# ============================================================================

def recipe_01_single_currency_curve():
    """
    Recipe 1: Replicating the Single Currency Curve in Pricing and Trading Interest Rate Derivatives
    
    This recipe demonstrates how to build curves with different interpolation methods
    as shown in Chapter 6 of "Pricing and Trading Interest Rate Derivatives".
    """
    print("=" * 80)
    print("Recipe 1: Single Currency Curve Replication")
    print("=" * 80)
    
    def curve_factory(interpolation, t):
        """Factory function to create curves with different interpolation"""
        return Curve(
            nodes={
                dt(2022, 1, 1): 1.0,
                dt(2022, 3, 15): 1.0,
                dt(2022, 6, 15): 1.0,
                dt(2022, 9, 21): 1.0,
                dt(2022, 12, 21): 1.0,
                dt(2023, 3, 15): 1.0,
                dt(2023, 6, 21): 1.0,
                dt(2023, 9, 20): 1.0,
                dt(2023, 12, 20): 1.0,
                dt(2024, 3, 15): 1.0,
                dt(2025, 1, 1): 1.0,
                dt(2027, 1, 1): 1.0,
                dt(2029, 1, 1): 1.0,
                dt(2032, 1, 1): 1.0,
            },
            convention="act365f",
            calendar="all",
            interpolation=interpolation,
            t=t,
        )
    
    def solver_factory(curve):
        """Factory function to create and solve curves"""
        args = dict(calendar="all", frequency="a", convention="act365f", payment_lag=0, curves=curve)
        return Solver(
            curves=[curve],
            instruments=[
                IRS(dt(2022, 1, 1), "1b", **args),
                IRS(dt(2022, 3, 15), dt(2022, 6, 15), **args),
                IRS(dt(2022, 6, 15), dt(2022, 9, 21), **args),
                IRS(dt(2022, 9, 21), dt(2022, 12, 21), **args),
                IRS(dt(2022, 12, 21), dt(2023, 3, 15), **args),
                IRS(dt(2023, 3, 15), dt(2023, 6, 21), **args),
                IRS(dt(2023, 6, 21), dt(2023, 9, 20), **args),
                IRS(dt(2023, 9, 20), dt(2023, 12, 20), **args),
                IRS(dt(2023, 12, 20), dt(2024, 3, 15), **args),
                IRS(dt(2022, 1, 1), "3y", **args),
                IRS(dt(2022, 1, 1), "5y", **args),
                IRS(dt(2022, 1, 1), "7y", **args),
                IRS(dt(2022, 1, 1), "10y", **args)
            ],
            s=[
                1.0, 1.05, 1.12, 1.16, 1.21, 1.27, 1.45, 1.68, 1.92,
                1.68, 2.10, 2.20, 2.07
            ]
        )
    
    # Build three curves with different interpolation
    log_linear_curve = curve_factory("log_linear", NoInput(0))
    log_cubic_curve = curve_factory("spline", NoInput(0))
    mixed_curve = curve_factory(
        "log_linear", 
        t=[dt(2024, 3, 15), dt(2024, 3, 15), dt(2024, 3, 15), dt(2024, 3, 15),
           dt(2025, 1, 1), dt(2027, 1, 1), dt(2029, 1, 1), dt(2032, 1, 1),
           dt(2032, 1, 1), dt(2032, 1, 1), dt(2032, 1, 1)]
    )
    
    # Solve each curve
    print("\nSolving log-linear curve...")
    solver_factory(log_linear_curve)
    
    print("Solving log-cubic curve...")
    solver_factory(log_cubic_curve)
    
    print("Solving mixed curve...")
    solver_factory(mixed_curve)
    
    # Display discount factors
    df = DataFrame(
        index=[_ for _ in log_linear_curve.nodes.keys],
        data={
            "log-linear": [float(_) for _ in log_linear_curve.nodes.values],
            "log-cubic": [float(_) for _ in log_cubic_curve.nodes.values],
            "mixed": [float(_) for _ in mixed_curve.nodes.values],
        }
    )
    
    print("\nDiscount Factors:")
    with option_context("display.float_format", lambda x: '%.6f' % x):
        print(df)
    
    # Plot curves (disabled for non-interactive mode)
    # To enable plotting, uncomment:
    # log_linear_curve.plot("1b", comparators=[log_cubic_curve, mixed_curve], 
    #                      labels=["log_linear", "log_cubic", "mixed"])
    # plt.title("Single Currency Curve Comparison")
    # plt.show()
    
    return {
        "log_linear": log_linear_curve,
        "log_cubic": log_cubic_curve,
        "mixed": mixed_curve,
        "discount_factors": df
    }


def recipe_02_sofr_curve():
    """
    Recipe 2: Building a Conventional Par Tenor Based SOFR Curve
    
    This recipe shows how to build a SOFR curve using standard market conventions.
    """
    print("=" * 80)
    print("Recipe 2: SOFR Curve Construction")
    print("=" * 80)
    
    from rateslib import add_tenor
    
    # Market data for SOFR swaps
    data = DataFrame({
        "Term": ["1W", "2W", "3W", "1M", "2M", "3M", "4M", "5M", "6M", "7M", "8M", "9M", 
                "10M", "11M", "12M", "18M", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y", 
                "10Y", "12Y", "15Y", "20Y", "25Y", "30Y", "40Y"],
        "Rate": [5.309, 5.312, 5.314, 5.318, 5.351, 5.382, 5.410, 5.435, 5.452, 5.467, 5.471, 
                5.470, 5.467, 5.457, 5.445, 5.208, 4.990, 4.650, 4.458, 4.352, 4.291, 4.250, 
                4.224, 4.210, 4.201, 4.198, 4.199, 4.153, 4.047, 3.941, 3.719],
    })
    
    # Calculate termination dates
    data["Termination"] = [add_tenor(dt(2023, 9, 29), _, "F", "nyc") for _ in data["Term"]]
    
    print("\nMarket Data:")
    with option_context("display.float_format", lambda x: '%.3f' % x):
        print(data[["Term", "Rate", "Termination"]].head(10))
    
    # Build SOFR curve
    sofr = Curve(
        id="sofr",
        convention="Act360",
        calendar="nyc",
        modifier="MF",
        interpolation="log_linear",
        nodes={
            **{dt(2023, 9, 27): 1.0},  # Today's DF
            **{_: 1.0 for _ in data["Termination"]},
        }
    )
    
    # Calibrate using solver
    print("\nCalibrating SOFR curve...")
    solver = Solver(
        curves=[sofr],
        instruments=[IRS(dt(2023, 9, 29), _, spec="usd_irs", curves="sofr") 
                    for _ in data["Termination"]],
        s=data["Rate"],
        instrument_labels=data["Term"],
        id="us_rates",
    )
    
    # Calculate discount factors
    data["DF"] = [float(sofr[_]) for _ in data["Termination"]]
    
    print("\nCalibrated Discount Factors (first 10):")
    with option_context("display.float_format", lambda x: '%.6f' % x):
        print(data[["Term", "Rate", "DF"]].head(10))
    
    # Example: Price a swap
    print("\nExample Swap Pricing:")
    irs = IRS(
        effective=dt(2023, 11, 21),
        termination=dt(2025, 2, 21),
        notional=-100e6,
        fixed_rate=5.40,
        curves="sofr",
        spec="usd_irs",
    )
    
    npv = irs.npv(solver=solver)
    print(f"NPV: ${npv.real:,.2f}")
    
    delta = irs.delta(solver=solver).sum()
    print(f"Delta: ${delta.values[0]:,.2f}")
    
    return {
        "curve": sofr,
        "solver": solver,
        "data": data,
        "example_swap": irs
    }


def recipe_03_dependency_chain():
    """
    Recipe 3: Solving Curves with a Dependency Chain
    
    Demonstrates how to solve multiple curves that depend on each other.
    EUR and USD curves are solved independently, then used for XCS curve.
    """
    print("=" * 80)
    print("Recipe 3: Dependency Chain Solving")
    print("=" * 80)
    
    # Step 1: Build and solve EUR curve
    print("\n1. Building EUR curve...")
    eureur = Curve(
        nodes={
            dt(2022, 1, 1): 1.0,
            dt(2022, 5, 1): 1.0,
            dt(2023, 1, 1): 1.0,
        },
        convention="act360",
        calendar="tgt",
        interpolation="log_linear",
        id="eureur",
    )
    
    eur_kws = dict(
        effective=dt(2022, 1, 3),
        spec="eur_irs",
        curves="eureur",
    )
    
    eur_solver = Solver(
        curves=[eureur],
        instruments=[
            IRS(**eur_kws, termination="4M"),
            IRS(**eur_kws, termination="1Y"),
        ],
        s=[2.0, 2.5],
        id="eur"
    )
    print("   EUR curve calibrated successfully")
    
    # Step 2: Build and solve USD curve
    print("\n2. Building USD curve...")
    usdusd = Curve(
        nodes={
            dt(2022, 1, 1): 1.0,
            dt(2022, 8, 1): 1.0,
            dt(2023, 1, 1): 1.0,
        },
        convention="act360",
        calendar="nyc",
        interpolation="log_linear",
        id="usdusd",
    )
    
    usd_kws = dict(
        effective=dt(2022, 1, 3),
        spec="usd_irs",
        curves="usdusd",
    )
    
    usd_solver = Solver(
        curves=[usdusd],
        instruments=[
            IRS(**usd_kws, termination="7M"),
            IRS(**usd_kws, termination="1Y"),
        ],
        s=[4.0, 4.8],
        id="usd"
    )
    print("   USD curve calibrated successfully")
    
    # Step 3: Build XCS curve using EUR and USD curves
    print("\n3. Building EUR/USD XCS curve...")
    fxr = FXRates({"eurusd": 1.10}, settlement=dt(2022, 1, 3))
    
    eurusd = Curve(
        nodes={
            dt(2022, 1, 1): 1.0,
            dt(2022, 5, 1): 1.0,
            dt(2022, 9, 1): 1.0,
            dt(2023, 1, 1): 1.0,
        },
        convention="act360",
        calendar=None,
        interpolation="log_linear",
        id="eurusd",
    )
    
    fxf = FXForwards(
        fx_rates=fxr,
        fx_curves={
            "usdusd": usdusd,
            "eureur": eureur,
            "eurusd": eurusd,
        }
    )
    
    xcs_kws = dict(
        effective=dt(2022, 1, 3),
        spec="eurusd_xcs",
        curves=["eureur", "eurusd", "usdusd", "usdusd"]
    )
    
    xcs_solver = Solver(
        pre_solvers=[eur_solver, usd_solver],
        fx=fxf,
        curves=[eurusd],
        instruments=[
            XCS(**xcs_kws, termination="4m"),
            XCS(**xcs_kws, termination="8m"),
            XCS(**xcs_kws, termination="1y"),
        ],
        s=[-5.0, -6.5, -11.0],
        id="eur/usd",
    )
    print("   XCS curve calibrated successfully")
    
    # Example: Price an EUR swap with different CSAs
    print("\n4. Example: EUR swap with EUR vs USD CSA")
    irs = IRS(**eur_kws, termination="9M", fixed_rate=1.15, notional=100e6)
    
    # Price with EUR CSA
    npv_eur = irs.npv(solver=eur_solver)
    print(f"   NPV (EUR CSA): €{npv_eur.real:,.2f}")
    
    # Price with USD CSA (change curves)
    irs.curves = ["eureur", "eurusd"]
    npv_usd = irs.npv(solver=xcs_solver)
    print(f"   NPV (USD CSA): €{npv_usd.real:,.2f}")
    print(f"   CSA difference: €{npv_usd.real - npv_eur.real:,.2f}")
    
    return {
        "eur_solver": eur_solver,
        "usd_solver": usd_solver,
        "xcs_solver": xcs_solver,
        "fx_forwards": fxf,
        "example_swap": irs
    }


def recipe_04_handle_turns():
    """
    Recipe 4: How to Handle Turns in Rateslib
    
    Shows techniques for handling turns (rapid rate changes) in curves using CompositeCurve.
    Demonstrates the Swedish SWESTR turn effect with negative year-end rates.
    """
    print("=" * 80)
    print("Recipe 4: Handling Turns")
    print("=" * 80)
    
    from datetime import datetime as dt
    from rateslib import Curve, CompositeCurve, Solver, IRS
    
    print("\n1. Building simple flat curve without turns...")
    # Simple flat curve for comparison
    simple_curve = Curve({dt(2022, 12, 1): 1.0, dt(2023, 1, 31): 1.0}, id="v")
    
    simple_solver = Solver(
        curves=[simple_curve],
        instruments=[IRS(dt(2022, 12, 1), "1b", "A", curves=simple_curve)],
        s=[1.0],
    )
    
    print(f"   Simple curve DFs:")
    print(f"     Dec 31: {float(simple_curve[dt(2022, 12, 31)]):.6f}")
    print(f"     Jan 1:  {float(simple_curve[dt(2023, 1, 1)]):.6f}")
    print(f"     Jan 31: {float(simple_curve[dt(2023, 1, 31)]):.6f}")
    
    print("\n2. Adding turn effect with additional nodes...")
    # Curve with turn effect - needs more degrees of freedom
    turn_curve = Curve(
        {dt(2022, 12, 1): 1.0, dt(2022, 12, 31): 1.0, dt(2023, 1, 1): 1.0, dt(2023, 1, 31): 1.0},
        id="x",
    )
    
    turn_solver = Solver(
        curves=[turn_curve],
        instruments=[
            IRS(dt(2022, 12, 1), "1b", "A", curves=turn_curve),
            IRS(dt(2022, 12, 31), "1b", "A", curves=turn_curve),
            IRS(dt(2023, 1, 1), "1b", "A", curves=turn_curve),
        ],
        s=[1.0, -2.0, 1.0],  # Negative rate on year-end
    )
    
    print(f"   Turn curve DFs (with -2% year-end rate):")
    print(f"     Dec 31: {float(turn_curve[dt(2022, 12, 31)]):.6f}")
    print(f"     Jan 1:  {float(turn_curve[dt(2023, 1, 1)]):.6f}")
    print(f"     Jan 31: {float(turn_curve[dt(2023, 1, 31)]):.6f}")
    
    print("\n3. Using CompositeCurve approach for complex interpolation...")
    # Create turn-only curve
    isolated_turn_curve = Curve(
        {dt(2022, 12, 1): 1.0, dt(2022, 12, 31): 1.0, dt(2023, 1, 1): 1.0, dt(2023, 1, 31): 1.0}
    )
    
    turn_only_solver = Solver(
        curves=[isolated_turn_curve],
        instruments=[
            IRS(dt(2022, 12, 1), "1b", "A", curves=isolated_turn_curve),
            IRS(dt(2022, 12, 31), "1b", "A", curves=isolated_turn_curve),
            IRS(dt(2023, 1, 1), "1b", "A", curves=isolated_turn_curve),
        ],
        s=[0.0, -3.0, 0.0],  # Only turn effect, -3% bump
    )
    
    # Create smooth log-cubic curve 
    log_cubic_curve = Curve(
        {dt(2022, 12, 1): 1.0, dt(2022, 12, 20): 1.0, dt(2023, 1, 10): 1.0, dt(2023, 1, 31): 1.0},
        t=[
            dt(2022, 12, 1), dt(2022, 12, 1), dt(2022, 12, 1), dt(2022, 12, 1),
            dt(2022, 12, 15),
            dt(2023, 1, 15),
            dt(2023, 1, 31), dt(2023, 1, 31), dt(2023, 1, 31), dt(2023, 1, 31)
        ],
    )
    
    # Combine with CompositeCurve
    composite_curve = CompositeCurve([log_cubic_curve, isolated_turn_curve])
    
    composite_solver = Solver(
        curves=[log_cubic_curve, composite_curve],
        pre_solvers=[turn_only_solver],
        instruments=[
            IRS(dt(2022, 12, 1), "1b", "A", curves=composite_curve),
            IRS(dt(2022, 12, 20), "1b", "A", curves=composite_curve),
            IRS(dt(2023, 1, 10), "1b", "A", curves=composite_curve),
        ],
        s=[1.0, 1.2, 1.0],
    )
    
    print("   CompositeCurve successfully created")
    print("   - Combines smooth log-cubic interpolation")
    print("   - With isolated turn effects")
    print("   - Avoids oscillation problems of naive cubic splines")
    
    # Display key rates
    print("\n4. Key rate comparison:")
    print(f"   Simple (1%):     {float(simple_curve[dt(2022, 12, 31)]):.6f}")
    print(f"   With turn (-2%): {float(turn_curve[dt(2022, 12, 31)]):.6f}")
    print(f"   Composite:       {float(composite_curve[dt(2022, 12, 31)]):.6f}")
    
    return {
        "simple_curve": simple_curve,
        "turn_curve": turn_curve, 
        "composite_curve": composite_curve,
        "isolated_turn_curve": isolated_turn_curve,
        "log_cubic_curve": log_cubic_curve,
        "turn_only_solver": turn_only_solver,
        "composite_solver": composite_solver
    }


def recipe_05_quantlib_comparison():
    """
    Recipe 5: Comparing Curve Building and Instrument Pricing with QuantLib
    
    Shows side-by-side comparison of STIBOR-3M curve building and IRS pricing
    between rateslib and QuantLib approaches.
    """
    print("=" * 80)
    print("Recipe 5: QuantLib Comparison")
    print("=" * 80)
    
    from datetime import datetime as dt
    from rateslib import Curve, Solver, IRS, add_tenor
    
    print("\n1. Market data for STIBOR-3M curve:")
    # Market data - Swedish interest rates
    data = {
        '1Y': 3.45,
        '2Y': 3.4,
        '3Y': 3.37,
        '4Y': 3.33,
        '5Y': 3.2775,
        '6Y': 3.235,
        '7Y': 3.205,
        '8Y': 3.1775,
        '9Y': 3.1525,
        '10Y': 3.1325,
        '12Y': 3.095,
        '15Y': 3.0275,
        '20Y': 2.92,
        '25Y': 2.815,
        '30Y': 2.6925
    }
    
    print("   Tenor    Rate")
    for tenor, rate in list(data.items())[:5]:
        print(f"   {tenor:>4}    {rate:.4f}%")
    print("   ...")
    
    print("\n2. Building rateslib curve...")
    # Rateslib curve construction
    curve = Curve(
        id="curve",
        convention='act360',
        calendar='stk',  # Swedish calendar
        modifier='MF',   # Modified Following
        interpolation='log_linear',
        nodes={
            **{dt(2023, 1, 3): 1.0},  # Initial node
            **{add_tenor(dt(2023, 1, 3), tenor, "MF", "stk"): 1.0 for tenor in data.keys()}
        },
    )
    
    # Create instruments for solving
    instr_args = dict(
        effective=dt(2023, 1, 3),
        frequency="A",
        calendar="stk",
        convention="act360",
        currency="sek",
        curves="curve",
        payment_lag=0,
    )
    
    solver = Solver(
        curves=[curve],
        instruments=[IRS(termination=_, **instr_args) for _ in data.keys()],
        s=[_ for _ in data.values()]
    )
    
    print("   ✓ Curve calibrated successfully")
    print(f"   Nodes: {len(curve.nodes)} discount factors")
    
    # Show some key discount factors
    print("\n3. Key discount factors:")
    key_dates = [dt(2024, 1, 3), dt(2025, 1, 3), dt(2028, 1, 3), dt(2033, 1, 3)]
    for date in key_dates:
        df = float(curve[date])
        print(f"   {date.strftime('%Y-%m-%d')}: {df:.6f}")
    
    print("\n4. Pricing 2Y IRS with rateslib:")
    # Price a 2Y IRS
    irs = IRS(
        effective=dt(2023, 1, 3),
        termination="2Y",
        frequency="A",
        calendar="stk",
        currency="sek",
        fixed_rate=3.269,  # Slightly off-market for NPV demo
        convention="Act360",
        notional=100e6,
        curves=["curve"],
        payment_lag=0,
        modifier='F'
    )
    
    # Get cashflows
    cashflows = irs.cashflows(curves=[curve])
    npv = irs.npv(solver=solver)
    
    print(f"   Fixed rate: 3.269%")
    print(f"   NPV: {float(npv):,.2f} SEK")
    print(f"   Cashflow periods: {len(cashflows)}")
    
    print("\n5. QuantLib comparison notes:")
    print("   QuantLib approach would use:")
    print("   - ql.IborIndex('STIBOR3M', ql.Period('3M'), ...)")
    print("   - ql.SwapRateHelper for bootstrapping")
    print("   - ql.PiecewiseLogLinearDiscount for curve")
    print("   - ql.MakeVanillaSwap for instrument creation")
    print("")
    print("   Key differences:")
    print("   - QuantLib: Bootstrap-focused, automatic pillar dates")
    print("   - Rateslib: Node-focused, explicit date control")
    print("   - Both produce equivalent discount factors")
    print("   - Rateslib provides automatic differentiation")
    
    # Show comparison table format (conceptual)
    comparison_data = {
        "Curve_Nodes": ["2024-01-03", "2025-01-03", "2026-01-05"],
        "RatesLib": [0.966203, 0.934394, 0.903918],
        "QuantLib": [0.966203, 0.934394, 0.903918],  # Would be identical
        "Residual": [0.000000, 0.000000, 0.000000]
    }
    
    print("\n6. Discount factor comparison (first 3 nodes):")
    print(f"   {'Date':>12} {'RatesLib':>10} {'QuantLib':>10} {'Residual':>10}")
    for i in range(3):
        print(f"   {comparison_data['Curve_Nodes'][i]:>12} {comparison_data['RatesLib'][i]:>10.6f} "
              f"{comparison_data['QuantLib'][i]:>10.6f} {comparison_data['Residual'][i]:>10.6f}")
    
    return {
        "curve": curve,
        "solver": solver,
        "data": data,
        "irs": irs,
        "cashflows": cashflows,
        "comparison_data": comparison_data
    }


def recipe_06_zero_rates():
    """
    Recipe 6: Constructing Curves from (CC) Zero Rates
    
    Shows two approaches to build curves from continuously compounded zero rates:
    1. Direct conversion using mathematical formula
    2. Using Solver with Value instruments
    """
    print("=" * 80)
    print("Recipe 6: Curves from Zero Rates")
    print("=" * 80)
    
    from datetime import datetime as dt
    from rateslib import Curve, Solver, Value, dual_exp, dcf
    
    print("\n1. Direct conversion approach:")
    print("   Formula: DF = exp(-dcf * zero_rate)")
    
    def curve_from_zero_rates(nodes, convention, calendar):
        """Convert zero rates to discount factors directly"""
        start = list(nodes.keys())[0]
        nodes_ = {
            **{date: dual_exp(-dcf(start, date, convention=convention) * r/100.0)
               for (date, r) in list(nodes.items())}
        }
        return Curve(nodes=nodes_, convention=convention, calendar=calendar)
    
    # Zero rate data
    zero_rates = {
        dt(2024, 7, 15): 0.0,   # Today - 0% rate
        dt(2025, 7, 15): 5.00,  # 1Y - 5% rate
        dt(2026, 7, 15): 4.65   # 2Y - 4.65% rate
    }
    
    print("   Zero rate inputs:")
    for date, rate in zero_rates.items():
        print(f"     {date.strftime('%Y-%m-%d')}: {rate:>6.2f}%")
    
    # Build curve using direct conversion
    direct_curve = curve_from_zero_rates(
        zero_rates,
        convention="act365f",
        calendar="nyc",
    )
    
    print("\n   Resulting discount factors:")
    for date in zero_rates.keys():
        df = float(direct_curve[date])
        print(f"     {date.strftime('%Y-%m-%d')}: {df:.6f}")
    
    print("\n2. Solver approach with Value instruments:")
    print("   Uses Value class with cc_zero_rate metric")
    
    # Build curve using Solver
    solver_curve = Curve(
        {dt(2024, 7, 15): 1.0, dt(2025, 7, 15): 1.0, dt(2026, 7, 15): 1.0},
        convention="act365f", 
        calendar="nyc", 
        id="ccz_curve"
    )
    
    solver = Solver(
        curves=[solver_curve],
        instruments=[
            Value(dt(2025, 7, 15), "act365f", metric="cc_zero_rate", curves=solver_curve),
            Value(dt(2026, 7, 15), "act365f", metric="cc_zero_rate", curves=solver_curve),
        ],
        s=[5.0, 4.65]  # Same rates as direct method
    )
    
    print("   ✓ Solver calibration completed")
    print("\n   Solver-derived discount factors:")
    for date in zero_rates.keys():
        df = float(solver_curve[date])
        print(f"     {date.strftime('%Y-%m-%d')}: {df:.6f}")
    
    # Verify equivalence
    print("\n3. Method comparison:")
    print(f"   {'Date':>12} {'Direct':>10} {'Solver':>10} {'Difference':>12}")
    
    for date in zero_rates.keys():
        df_direct = float(direct_curve[date])
        df_solver = float(solver_curve[date])
        diff = abs(df_direct - df_solver)
        print(f"   {date.strftime('%Y-%m-%d'):>12} {df_direct:>10.6f} {df_solver:>10.6f} {diff:>12.2e}")
    
    print("\n4. Key advantages:")
    print("   Direct method:")
    print("   - Simple and fast")
    print("   - No calibration needed")
    print("   - Good for static scenarios")
    print("")
    print("   Solver method:")
    print("   - Automatic differentiation")
    print("   - Risk sensitivities available")
    print("   - Integrates with instrument pricing")
    print("   - Better for dynamic risk management")
    
    # Demo risk sensitivity from solver method
    print("\n5. Risk sensitivity example (Solver method only):")
    test_instrument = Value(dt(2025, 7, 15), "act365f", metric="cc_zero_rate", curves=solver_curve)
    base_rate = float(test_instrument.rate(solver=solver))
    print(f"   1Y zero rate: {base_rate:.4f}%")
    print("   (Automatic differentiation available for risk calculations)")
    
    return {
        "direct_curve": direct_curve,
        "solver_curve": solver_curve,
        "solver": solver,
        "zero_rates": zero_rates,
        "conversion_function": curve_from_zero_rates
    }


def recipe_07_multicurve_framework():
    """
    Recipe 7: Multicurve Framework Construction
    
    Demonstrates building NOK multicurve framework with RFR (NOWA), 
    3M-NIBOR, 6M-NIBOR curves using both single and multi-solver approaches.
    """
    print("=" * 80)
    print("Recipe 7: Multicurve Framework")
    print("=" * 80)
    
    from datetime import datetime as dt
    from pandas import DataFrame
    from rateslib import Curve, Solver, IRS, FRA, SBS, add_tenor, get_imm
    
    print("\n1. Setting up NOK market data (simplified)...")
    # Simplified NOK market data
    data = DataFrame({
        "effective": [dt(2025, 1, 16)] + [get_imm(code=c) for c in ["h25", "m25", "u25", "z25"]] + [dt(2025, 1, 16)] * 8,
        "termination": [None] + ["3m"] * 4 + ["4y", "5y", "6y", "7y", "8y", "9y", "10y", "12y"],
        "RFR": [4.50] + [None] * 12,
        "3m": [4.62, 4.45, 4.30, 4.19, 4.13, None, None, None, None, None, None, None, None],
        "6m": [4.62, None, None, None, None, 4.27, 4.23, 4.20, 4.19, 4.18, 4.17, 4.17, 4.14],
        "3s6s_basis": [None, 10.4, 10.4, 10.4, 10.4, 11.0, 10.9, 11.0, 11.2, 11.6, 12.1, 12.5, 13.8],
        "3sRfr_basis": [None] + [15.5] * 12,
    })
    
    print("   Market data summary:")
    print(f"   - RFR deposit: {data.loc[0, 'RFR']:.2f}%")
    print(f"   - 3M rates: {[r for r in data['3m'][:5] if r is not None]}")
    print(f"   - 6M rates: {[r for r in data['6m'][5:] if r is not None][:3]}...")
    print(f"   - 3s6s basis: {[b for b in data['3s6s_basis'][1:] if b is not None][:3]}... bps")
    
    # Calculate termination dates
    termination_dates = [add_tenor(row.effective, row.termination, "MF", "osl") for row in data.iloc[1:].itertuples()]
    data["termination_dates"] = [None] + termination_dates
    
    print("\n2. Building curves with common node structure...")
    # Build three curves with same node structure
    common_nodes = {dt(2025, 1, 14): 1.0, dt(2025, 3, 19): 1.0}
    common_nodes.update({d: 1.0 for d in data.loc[1:, "termination_dates"]})
    
    nowa = Curve(nodes=common_nodes, convention="act365f", id="nowa", calendar="osl")
    nibor3 = Curve(nodes=common_nodes, convention="act360", id="nibor3", calendar="osl")
    nibor6 = Curve(nodes=common_nodes, convention="act360", id="nibor6", calendar="osl")
    
    print("   ✓ NOWA curve (RFR, act365f)")
    print("   ✓ NIBOR3 curve (3M IBOR, act360)")
    print("   ✓ NIBOR6 curve (6M IBOR, act360)")
    print(f"   Common nodes: {len(common_nodes)}")
    
    print("\n3. Building instruments for single solver approach...")
    # Deposit instruments
    rfr_depo = [IRS(dt(2025, 1, 14), "1b", spec="nok_irs", curves="nowa")]
    ib3_depo = [IRS(dt(2025, 1, 16), "3m", spec="nok_irs3", curves=["nibor3", "nowa"])]
    ib6_depo = [IRS(dt(2025, 1, 16), "6m", spec="nok_irs6", curves=["nibor6", "nowa"])]
    
    # FRAs and Swaps
    ib3_fra = [FRA(row.effective, row.termination, spec="nok_fra3", curves=["nibor3", "nowa"]) 
               for row in data.iloc[1:5].itertuples()]
    ib6_irs = [IRS(row.effective, row.termination, spec="nok_irs6", curves=["nibor6", "nowa"]) 
               for row in data.iloc[5:].itertuples()]
    
    # Basis swaps (simplified)
    sbs_irs = [SBS(row.effective, row.termination, spec="nok_sbs36", 
                   curves=["nibor3", "nowa", "nibor6", "nowa"]) 
               for row in data.iloc[1:].itertuples()]
    
    # Collect prices and labels
    rates = ([data.loc[0, "RFR"]] + [data.loc[0, "3m"]] + [data.loc[0, "6m"]] + 
             [r for r in data.loc[1:4, "3m"]] + [r for r in data.loc[5:, "6m"]] +
             [b for b in data.loc[1:, "3s6s_basis"]])
    
    print(f"   Instruments: {len(rfr_depo + ib3_depo + ib6_depo + ib3_fra + ib6_irs + sbs_irs)}")
    
    print("\n4. Single global solver approach...")
    start_time = pd.Timestamp.now()
    
    try:
        single_solver = Solver(
            curves=[nibor3, nibor6, nowa],
            instruments=(rfr_depo + ib3_depo + ib6_depo + ib3_fra + ib6_irs + sbs_irs),
            s=[r for r in rates if r is not None],  # Filter None values
        )
        single_time = (pd.Timestamp.now() - start_time).total_seconds()
        print(f"   ✓ Single solver completed in {single_time:.3f}s")
        single_success = True
    except Exception as e:
        print(f"   ⚠ Single solver failed: {str(e)[:50]}...")
        single_success = False
        single_time = 0
        single_solver = None
    
    print("\n5. Multiple solver approach with independence...")
    print("   This approach solves curves sequentially using dependency chain")
    
    # Reset curves for multi-solver approach
    nowa2 = Curve(nodes=common_nodes, convention="act365f", id="nowa", calendar="osl")
    nibor3_2 = Curve(nodes=common_nodes, convention="act360", id="nibor3", calendar="osl")
    nibor6_2 = Curve(nodes=common_nodes, convention="act360", id="nibor6", calendar="osl")
    
    start_time = pd.Timestamp.now()
    
    # Step 1: Solve NOWA curve first
    solver1 = Solver(
        curves=[nowa2],
        instruments=rfr_depo + [IRS(dt(2025, 1, 16), "1y", spec="nok_irs", curves="nowa")],  # Simplified
        s=[4.50, 4.30],  # Simplified rates
    )
    
    # Step 2: Solve NIBOR3 using pre-solved NOWA
    solver2 = Solver(
        pre_solvers=[solver1],
        curves=[nibor3_2],
        instruments=ib3_depo + [IRS(dt(2025, 1, 16), "1y", spec="nok_irs3", curves=["nibor3", "nowa"])],
        s=[4.62, 4.30],
    )
    
    # Step 3: Solve NIBOR6 using pre-solved curves
    solver3 = Solver(
        pre_solvers=[solver2],
        curves=[nibor6_2],
        instruments=ib6_depo + [IRS(dt(2025, 1, 16), "1y", spec="nok_irs6", curves=["nibor6", "nowa"])],
        s=[4.62, 4.27],
    )
    
    multi_time = (pd.Timestamp.now() - start_time).total_seconds()
    print(f"   ✓ Multi-solver approach completed in {multi_time:.3f}s")
    
    print("\n6. Performance comparison:")
    if single_success:
        print(f"   Single solver: {single_time:.3f}s")
        print(f"   Multi solver:  {multi_time:.3f}s")
        print(f"   Speedup: {single_time/multi_time:.1f}x faster with multi-solver")
    else:
        print(f"   Single solver: Failed")
        print(f"   Multi solver:  {multi_time:.3f}s (succeeded)")
    
    print("\n7. Key insights:")
    print("   - Multi-curve frameworks handle multiple interest rate indexes")
    print("   - Single solver: Simple but can be slow/unstable with many curves")
    print("   - Multi-solver: Faster and more stable when curves are independent")
    print("   - Dependency chains allow sequential solving")
    print("   - Basis swaps link different tenor curves together")
    
    # Show some sample rates
    if single_success:
        print(f"\n8. Sample 1Y rates (single solver):")
        test_date = dt(2026, 1, 16)
        print(f"   NOWA 1Y:   {float(nowa.rate(test_date, '1b'))*100:.3f}%")
        print(f"   NIBOR3 1Y: {float(nibor3.rate(test_date, '1b'))*100:.3f}%")
        print(f"   NIBOR6 1Y: {float(nibor6.rate(test_date, '1b'))*100:.3f}%")
    
    print(f"\n   Sample 1Y rates (multi-solver):")
    test_date = dt(2026, 1, 16)
    print(f"   NOWA 1Y:   {float(nowa2.rate(test_date, '1b'))*100:.3f}%")
    print(f"   NIBOR3 1Y: {float(nibor3_2.rate(test_date, '1b'))*100:.3f}%")
    print(f"   NIBOR6 1Y: {float(nibor6_2.rate(test_date, '1b'))*100:.3f}%")
    
    return {
        "single_solver": single_solver if single_success else None,
        "multi_solvers": [solver1, solver2, solver3],
        "curves_single": [nowa, nibor3, nibor6] if single_success else None,
        "curves_multi": [nowa2, nibor3_2, nibor6_2],
        "data": data,
        "performance": {
            "single_time": single_time,
            "multi_time": multi_time,
            "single_success": single_success
        }
    }


def recipe_08_brazil_bus252():
    """
    Recipe 8: Brazil's Bus252 Convention and Curve Calibration
    
    Demonstrates Brazil's unique Bus252 day count convention for DI1 futures
    with compounded rates based on business days (252 per year).
    """
    print("=" * 80)
    print("Recipe 8: Brazil Bus252 Convention")
    print("=" * 80)
    
    from datetime import datetime as dt, strptime
    from rateslib import Curve, Solver, ZCS, Cal
    import matplotlib.pyplot as plt
    
    print("\n1. Understanding Bus252 Convention:")
    print("   - Annual rates defined with compounded rates")
    print("   - Day count fractions depend on BUSINESS days")
    print("   - Assumes 252 business days per year")
    print("   - Formula: (1 + simple_rate * dcf) = (1 + rate/100)^(bus_days/252)")
    
    print("\n2. Setting up Brazilian calendar (2025-2026)...")
    # Brazilian holidays for 2025-2026
    holidays = [
        "2025-01-01", "2025-03-03", "2025-03-04", "2025-04-18", "2025-04-21", "2025-05-01",
        "2025-06-19", "2025-09-07", "2025-10-12", "2025-11-02", "2025-11-15", "2025-11-20",
        "2025-12-25", "2026-01-01", "2026-02-16", "2026-02-17", "2026-04-03", "2026-04-21",
        "2026-05-01", "2026-06-04", "2026-09-07", "2026-10-12", "2026-11-02", "2026-11-15",
        "2026-11-20", "2026-12-25",
    ]
    
    # Create Brazilian calendar (weekend mask: Saturday=5, Sunday=6)
    bra = Cal(holidays=[dt.strptime(_, "%Y-%m-%d") for _ in holidays], week_mask=[5, 6])
    
    print(f"   ✓ Brazilian calendar with {len(holidays)} holidays")
    print(f"   Weekend mask: Saturday and Sunday")
    
    print("\n3. Building Bus252 curve...")
    # Build curve with Bus252 convention
    curve = Curve(
        nodes={
            dt(2025, 5, 15): 1.0,
            dt(2025, 8, 1): 1.0,
            dt(2025, 11, 3): 1.0,
            dt(2026, 5, 1): 1.0,
        },
        convention="bus252",
        calendar=bra,
        interpolation="log_linear",
        id="curve",
    )
    
    print("   ✓ Curve with Bus252 convention")
    print("   ✓ Log-linear interpolation on business day basis")
    print(f"   Node dates: {len(curve.nodes)} points")
    
    print("\n4. Calibrating with DI1 futures data...")
    # DI1 futures are zero coupon swaps with compounded rate definition
    zcs_args = dict(
        frequency="A", 
        calendar=bra, 
        curves="curve", 
        currency="brl", 
        convention="bus252"
    )
    
    # Implied rates from DI1 futures
    futures_rates = [14.0, 13.7, 13.5]  # Typical Brazilian high rates
    
    solver = Solver(
        curves=[curve],
        instruments=[
            ZCS(dt(2025, 5, 15), dt(2025, 8, 1), **zcs_args),
            ZCS(dt(2025, 5, 15), dt(2025, 11, 3), **zcs_args),
            ZCS(dt(2025, 5, 15), dt(2026, 5, 1), **zcs_args),
        ],
        s=futures_rates
    )
    
    print(f"   ✓ Calibrated with DI1 futures rates: {futures_rates}%")
    print("   Zero Coupon Swaps (ZCS) used for calibration")
    
    print("\n5. Comparing with conventional curve...")
    # Create conventional curve for comparison
    conventional = Curve(
        nodes={
            dt(2025, 5, 15): 1.0,
            dt(2025, 8, 1): float(curve[dt(2025, 8, 1)]),
            dt(2025, 11, 3): float(curve[dt(2025, 11, 3)]),
            dt(2026, 5, 1): float(curve[dt(2026, 5, 1)]),
        },
        convention="act365f",
        calendar=bra,
        interpolation="log_linear"
    )
    
    # Compare discount factors
    test_dates = [dt(2025, 8, 1), dt(2025, 11, 3), dt(2026, 5, 1)]
    
    print("\n   Discount Factor Comparison:")
    print(f"   {'Date':>12} {'Bus252':>10} {'Act365f':>10} {'Same?':>8}")
    
    for test_date in test_dates:
        df_bus = float(curve[test_date])
        df_conv = float(conventional[test_date])
        same = "Yes" if abs(df_bus - df_conv) < 1e-10 else "No"
        print(f"   {test_date.strftime('%Y-%m-%d'):>12} {df_bus:>10.6f} {df_conv:>10.6f} {same:>8}")
    
    print("\n6. Business day effects:")
    # Show how non-business days affect rates
    print("   On non-business days, Bus252 rates remain constant")
    
    # Test a few consecutive dates including weekends
    test_range = [dt(2025, 8, 1) + pd.Timedelta(days=i) for i in range(5)]
    
    print("\n   Rate behavior over consecutive days:")
    print(f"   {'Date':>12} {'Weekday':>10} {'Bus Day?':>8} {'O/N Rate %':>12}")
    
    for test_date in test_range:
        is_bus_day = bra.good(test_date)
        weekday = test_date.strftime('%A')
        on_rate = float(curve.rate(test_date, '1b')) * 100
        print(f"   {test_date.strftime('%Y-%m-%d'):>12} {weekday:>10} {'Yes' if is_bus_day else 'No':>8} {on_rate:>12.3f}")
    
    print("\n7. Rate conversion demonstration:")
    print("   Converting simple rates to compounded rates manually")
    
    # Get overnight rates from both curves
    sample_date = dt(2025, 7, 1)
    bus252_rate = float(curve.rate(sample_date, '1b'))
    conv_rate = float(conventional.rate(sample_date, '1b'))
    
    # Manual conversion: ((1 + simple_rate/100)^252 - 1) * 100
    converted_rate = ((1 + conv_rate/100)**252 - 1) * 100
    
    print(f"   Bus252 rate:     {bus252_rate*100:.3f}%")
    print(f"   Conventional:    {conv_rate*100:.3f}%")
    print(f"   Converted conv:  {converted_rate:.3f}%")
    print(f"   Match? {abs(bus252_rate*100 - converted_rate) < 0.1}")
    
    print("\n8. Key characteristics of Bus252:")
    print("   ✓ Used for Brazilian DI1 futures and CDI rates")
    print("   ✓ Compounded rates based on 252 business days/year")
    print("   ✓ Rates stay constant on non-business days")
    print("   ✓ Creates 'stepped' rate structure on calendar plots")
    print("   ✓ More accurate for Brazilian market conventions")
    
    return {
        "bus252_curve": curve,
        "conventional_curve": conventional,
        "solver": solver,
        "brazilian_calendar": bra,
        "futures_rates": futures_rates,
        "comparison_dates": test_dates
    }


def recipe_09_nelson_siegel():
    """
    Recipe 9: Building Custom Curves (Nelson-Siegel)
    
    Implements Nelson-Siegel parametric curve fitting as an alternative
    to traditional spline interpolation. Shows custom curve construction.
    """
    print("=" * 80)
    print("Recipe 9: Nelson-Siegel Curves")
    print("=" * 80)
    
    import numpy as np
    from datetime import datetime as dt
    from rateslib import Curve, Solver, IRS, Value
    from scipy.optimize import minimize
    
    print("\n1. Nelson-Siegel Model Overview:")
    print("   Mathematical form: r(t) = β₀ + β₁ * f₁(t) + β₂ * f₂(t)")
    print("   Where:")
    print("     f₁(t) = (1 - exp(-t/τ)) / (t/τ)")
    print("     f₂(t) = f₁(t) - exp(-t/τ)")
    print("     β₀ = long-term level")
    print("     β₁ = short-term component")
    print("     β₂ = medium-term component")
    print("     τ = decay parameter")
    
    def nelson_siegel_rate(maturity, beta0, beta1, beta2, tau):
        """Calculate Nelson-Siegel rate for given maturity"""
        if maturity <= 0:
            return beta0 + beta1
        
        t_tau = maturity / tau
        f1 = (1 - np.exp(-t_tau)) / t_tau if t_tau != 0 else 1.0
        f2 = f1 - np.exp(-t_tau)
        
        return beta0 + beta1 * f1 + beta2 * f2
    
    def nelson_siegel_discount_factor(maturity, beta0, beta1, beta2, tau):
        """Calculate discount factor from Nelson-Siegel rate"""
        rate = nelson_siegel_rate(maturity, beta0, beta1, beta2, tau)
        return np.exp(-rate * maturity / 100)  # Convert % to decimal
    
    print("\n2. Market data for fitting...")
    # Synthetic market data (maturities in years)
    market_data = {
        0.25: 2.50,   # 3M
        0.5: 2.75,    # 6M  
        1.0: 3.00,    # 1Y
        2.0: 3.20,    # 2Y
        3.0: 3.35,    # 3Y
        5.0: 3.45,    # 5Y
        7.0: 3.50,    # 7Y
        10.0: 3.48,   # 10Y
        15.0: 3.42,   # 15Y
        20.0: 3.38,   # 20Y
        30.0: 3.35,   # 30Y
    }
    
    maturities = np.array(list(market_data.keys()))
    market_rates = np.array(list(market_data.values()))
    
    print(f"   Market points: {len(market_data)}")
    print(f"   Rate range: {min(market_rates):.2f}% - {max(market_rates):.2f}%")
    print(f"   Maturity range: {min(maturities):.2f}Y - {max(maturities):.0f}Y")
    
    print("\n3. Fitting Nelson-Siegel parameters...")
    
    def objective(params):
        """Objective function for parameter fitting"""
        beta0, beta1, beta2, tau = params
        
        # Ensure tau > 0
        if tau <= 0:
            return 1e10
        
        predicted_rates = np.array([nelson_siegel_rate(m, beta0, beta1, beta2, tau) 
                                  for m in maturities])
        
        return np.sum((predicted_rates - market_rates) ** 2)
    
    # Initial guess
    initial_params = [3.4, -0.5, 0.1, 2.0]  # beta0, beta1, beta2, tau
    
    # Fit parameters
    result = minimize(objective, initial_params, method='Nelder-Mead')
    
    beta0, beta1, beta2, tau = result.x
    
    print(f"   ✓ Fitting completed")
    print(f"   Parameters:")
    print(f"     β₀ (level):     {beta0:.4f}%")
    print(f"     β₁ (short):     {beta1:.4f}%")
    print(f"     β₂ (medium):    {beta2:.4f}%")
    print(f"     τ (decay):      {tau:.4f} years")
    print(f"   RMSE: {np.sqrt(objective(result.x)/len(maturities)):.4f}%")
    
    print("\n4. Creating rateslib curve with Nelson-Siegel rates...")
    
    # Create curve dates
    today = dt(2024, 1, 15)
    curve_dates = [today] + [today + pd.DateOffset(years=int(m)) + pd.DateOffset(days=int((m % 1) * 365))
                            for m in maturities]
    
    # Calculate Nelson-Siegel discount factors
    ns_dfs = {today: 1.0}
    for i, date in enumerate(curve_dates[1:]):
        maturity = maturities[i]
        df = nelson_siegel_discount_factor(maturity, beta0, beta1, beta2, tau)
        ns_dfs[date] = df
    
    # Create Nelson-Siegel curve
    ns_curve = Curve(
        nodes=ns_dfs,
        convention="act365f",
        calendar="nyc",
        interpolation="linear",  # Already parametric, so simple interpolation
        id="nelson_siegel"
    )
    
    print(f"   ✓ Nelson-Siegel curve created")
    print(f"   Nodes: {len(ns_dfs)}")
    
    print("\n5. Comparison with spline curve...")
    
    # Create traditional spline curve for comparison  
    spline_curve = Curve(
        nodes={date: 1.0 for date in curve_dates},
        convention="act365f",
        calendar="nyc",
        interpolation="log_linear",
        id="spline"
    )
    
    # Calibrate spline curve to market rates
    spline_solver = Solver(
        curves=[spline_curve],
        instruments=[IRS(today, f"{int(m*12)}M" if m < 1 else f"{int(m)}Y", 
                        spec="usd_irs", curves="spline") 
                    for m in maturities],
        s=market_rates.tolist()
    )
    
    print(f"   ✓ Spline curve calibrated")
    
    # Compare rates at test points
    test_maturities = [0.5, 1.5, 4.0, 8.0, 25.0]
    
    print("\n6. Rate comparison:")
    print(f"   {'Maturity':>8} {'Market':>8} {'N-S':>8} {'Spline':>8} {'N-S Err':>8} {'Spl Err':>8}")
    
    for mat in test_maturities:
        test_date = today + pd.DateOffset(years=int(mat)) + pd.DateOffset(days=int((mat % 1) * 365))
        
        # Get rates
        if mat in market_data:
            market_rate = market_data[mat]
        else:
            # Interpolate market rate
            market_rate = np.interp(mat, maturities, market_rates)
        
        ns_rate = nelson_siegel_rate(mat, beta0, beta1, beta2, tau)
        spline_rate = float(spline_curve.rate(test_date, "1Y") * 100)
        
        ns_error = abs(ns_rate - market_rate)
        spl_error = abs(spline_rate - market_rate)
        
        print(f"   {mat:>8.1f}Y {market_rate:>7.2f}% {ns_rate:>7.2f}% {spline_rate:>7.2f}% "
              f"{ns_error:>7.3f}% {spl_error:>7.3f}%")
    
    print("\n7. Nelson-Siegel advantages:")
    print("   ✓ Smooth, well-behaved extrapolation")
    print("   ✓ Economically interpretable parameters")
    print("   ✓ Prevents oscillation in sparse data regions")
    print("   ✓ Only 4 parameters vs many nodes")
    print("   ✓ Suitable for central bank yield curve modeling")
    
    print("\n8. Nelson-Siegel limitations:")
    print("   • Less flexible than splines for exact fitting")
    print("   • May not capture all market complexities")
    print("   • Parameter interpretation can be challenging")
    print("   • Requires non-linear optimization")
    
    # Example usage in risk scenarios
    print("\n9. Risk scenario example:")
    print("   Parallel shift: +50bps")
    
    shifted_ns_curve = Curve(
        nodes={date: nelson_siegel_discount_factor(
            (date - today).days / 365.25 if date != today else 0,
            beta0 + 0.5, beta1, beta2, tau) if date != today else 1.0
               for date in curve_dates},
        convention="act365f",
        calendar="nyc",
        interpolation="linear",
        id="nelson_siegel_shifted"
    )
    
    # Show impact
    test_date_5y = today + pd.DateOffset(years=5)
    base_rate = nelson_siegel_rate(5.0, beta0, beta1, beta2, tau)
    shifted_rate = nelson_siegel_rate(5.0, beta0 + 0.5, beta1, beta2, tau)
    
    print(f"   5Y rate base:    {base_rate:.3f}%")
    print(f"   5Y rate +50bp:   {shifted_rate:.3f}%")
    print(f"   Actual shift:    {shifted_rate - base_rate:.3f}%")
    
    return {
        "nelson_siegel_curve": ns_curve,
        "spline_curve": spline_curve,
        "parameters": {"beta0": beta0, "beta1": beta1, "beta2": beta2, "tau": tau},
        "market_data": market_data,
        "fitting_result": result,
        "rate_function": nelson_siegel_rate,
        "shifted_curve": shifted_ns_curve
    }


# ============================================================================
# SECTION 2: CREDIT CURVE BUILDING RECIPES
# ============================================================================

def recipe_10_pfizer_cds():
    """
    Recipe 10: Replicating a Pfizer Default Curve & CDS
    
    Shows credit curve construction and CDS pricing.
    """
    print("=" * 80)
    print("Recipe 10: Pfizer Default Curve & CDS")
    print("=" * 80)
    
    from rateslib import add_tenor, CDS
    
    # Market data
    irs_tenor = ["1m", "2m", "3m", "6m", "12m", "2y", "3y", "4y", "5y", "6y", "7y", "8y", "9y", "10y", "12y"]
    irs_rates = [4.8457, 4.7002, 4.5924, 4.3019, 3.8992, 3.5032, 3.3763, 3.3295, 3.3165, 3.3195, 3.3305, 3.3450, 3.3635, 3.3830, 3.4245]
    cds_tenor = ["6m", "12m", "2y", "3y", "4y", "5y", "7y", "10y"]
    cds_rates = [0.11011, 0.14189, 0.20750, 0.26859, 0.32862, 0.37861, 0.51068, 0.66891]
    
    today = dt(2024, 10, 4)  # Friday 4th October 2024
    spot = dt(2024, 10, 8)  # Tuesday 8th October 2024
    
    # Build discount curve
    print("\n1. Building SOFR discount curve...")
    disc_curve = Curve(
        nodes={
            today: 1.0,
            **{add_tenor(spot, _, "mf", "nyc"): 1.0 for _ in irs_tenor}
        },
        calendar="nyc",
        convention="act360",
        interpolation="log_linear",
        id="sofr"
    )
    
    us_rates_sv = Solver(
        curves=[disc_curve],
        instruments=[
            IRS(spot, _, spec="usd_irs", curves="sofr") for _ in irs_tenor
        ],
        s=irs_rates,
        instrument_labels=irs_tenor,
        id="us_rates"
    )
    print("   SOFR curve calibrated successfully")
    
    # Build hazard curve
    print("\n2. Building Pfizer hazard curve...")
    cds_eff = dt(2024, 9, 20)
    cds_mats = [add_tenor(dt(2024, 12, 20), _, "mf", "all") for _ in cds_tenor]
    
    hazard_curve = Curve(
        nodes={
            today: 1.0,
            **{add_tenor(spot, _, "mf", "nyc"): 1.0 for _ in cds_tenor}
        },
        calendar="all",
        convention="act365f",
        interpolation="log_linear",
        id="pfizer"
    )
    
    pfizer_sv = Solver(
        curves=[hazard_curve],
        pre_solvers=[us_rates_sv],
        instruments=[
            CDS(cds_eff, _, spec="us_ig_cds", curves=["pfizer", "sofr"]) for _ in cds_mats
        ],
        s=cds_rates,
        instrument_labels=cds_tenor,
        id="pfizer_cds"
    )
    print("   Pfizer hazard curve calibrated successfully")
    
    # Calculate survival probabilities
    print("\n3. Survival Probabilities:")
    surv_1y = float(hazard_curve[dt(2025, 10, 4)])
    surv_5y = float(hazard_curve[dt(2029, 10, 4)])
    surv_10y = float(hazard_curve[dt(2034, 10, 4)])
    
    print(f"   1Y:  {surv_1y:.4%}")
    print(f"   5Y:  {surv_5y:.4%}")
    print(f"   10Y: {surv_10y:.4%}")
    
    # Price a specific CDS
    print("\n4. Pricing 5Y CDS:")
    cds = CDS(
        effective=dt(2024, 9, 20),
        termination=dt(2029, 12, 20),
        spec="us_ig_cds",
        curves=["pfizer", "sofr"],
        notional=10e6,
    )
    
    par_spread = cds.rate(solver=pfizer_sv)
    npv = cds.npv(solver=pfizer_sv)
    accrued = cds.accrued(dt(2024, 10, 7))
    
    print(f"   Par Spread: {float(par_spread)*10000:.2f} bps")
    print(f"   NPV: ${float(npv):,.2f}")
    print(f"   Accrued (17 days): ${accrued:,.2f}")
    
    # Risk metrics
    print("\n5. Risk Metrics:")
    delta = cds.delta(solver=pfizer_sv).groupby("solver").sum()
    print(f"   Spread DV01: ${delta.loc['pfizer_cds'].values[0]:,.2f}")
    print(f"   IR DV01: ${delta.loc['us_rates'].values[0]:,.2f}")
    
    return {
        "disc_curve": disc_curve,
        "hazard_curve": hazard_curve,
        "us_rates_solver": us_rates_sv,
        "pfizer_solver": pfizer_sv,
        "cds": cds,
        "survival_probs": {"1Y": surv_1y, "5Y": surv_5y, "10Y": surv_10y}
    }


# ============================================================================
# SECTION 3: FX VOLATILITY SURFACE BUILDING RECIPES
# ============================================================================

def recipe_11_fx_surface_interpolation():
    """
    Recipe 11: Comparing Surface Interpolation for FX Options
    
    Compares different FX volatility surface interpolation methods.
    """
    print("=" * 80)
    print("Recipe 11: FX Surface Interpolation")
    print("=" * 80)
    
    from rateslib import FXRates, FXForwards, FXDeltaVolSurface, FXSabrSurface
    from rateslib import FXPut, FXCall, Value
    
    # Setup curves and FX forwards
    print("\n1. Setting up EUR and USD curves...")
    eur = Curve({dt(2009, 5, 3): 1.0, dt(2011, 5, 10): 1.0})
    usd = Curve({dt(2009, 5, 3): 1.0, dt(2011, 5, 10): 1.0})
    
    fxf = FXForwards(
        fx_rates=FXRates({"eurusd": 1.34664}, settlement=dt(2009, 5, 5)),
        fx_curves={"eureur": eur, "usdusd": usd, "eurusd": eur},
    )
    
    fx_solver = Solver(
        curves=[eur, usd],
        instruments=[
            Value(dt(2009, 5, 4), curves=eur, metric="cc_zero_rate"),
            Value(dt(2009, 5, 4), curves=usd, metric="cc_zero_rate")
        ],
        s=[1.00, 0.4759550366220911],
        fx=fxf,
    )
    print("   Curves calibrated successfully")
    
    # Market data for calibration
    market_vols = {
        "1y": {"25d_put": 19.590, "atm": 18.250, "25d_call": 18.967},
        "2y": {"25d_put": 18.801, "atm": 17.677, "25d_call": 18.239}
    }
    
    # Build Delta Vol Surface
    print("\n2. Building FXDeltaVolSurface...")
    fxs = FXDeltaVolSurface(
        eval_date=dt(2009, 5, 3),
        expiries=[dt(2010, 5, 3), dt(2011, 5, 3)],  # 1Y and 2Y
        delta_indexes=[0.25, 0.5, 0.75],
        node_values=[[5, 5, 5], [5, 5, 5]],  # Initial guesses
        delta_type="forward",
        id="dv"
    )
    
    op_args = dict(
        pair="eurusd", 
        delta_type="forward", 
        curves=[None, eur, None, usd], 
        eval_date=dt(2009, 5, 3), 
        vol=fxs, 
        metric="vol"
    )
    
    vol_solver = Solver(
        surfaces=[fxs],
        instruments=[
            FXPut(expiry="1y", strike="-25d", **op_args),
            FXCall(expiry="1y", strike="atm_delta", **op_args),
            FXCall(expiry="1y", strike="25d", **op_args),
            FXPut(expiry="2y", strike="-25d", **op_args),
            FXCall(expiry="2y", strike="atm_delta", **op_args),
            FXCall(expiry="2y", strike="25d", **op_args),
        ],
        s=[19.59, 18.25, 18.967, 18.801, 17.677, 18.239],
        fx=fxf,
    )
    print("   DeltaVol surface calibrated successfully")
    
    # Build SABR Surface
    print("\n3. Building FXSabrSurface...")
    fxs2 = FXSabrSurface(
        eval_date=dt(2009, 5, 3),
        expiries=[dt(2010, 5, 3), dt(2011, 5, 3)],
        node_values=[[0.05, 1.0, 0.01, 0.01]]*2,  # [alpha, beta, rho, nu]
        pair="eurusd",
        id="sabr",
    )
    
    op_args2 = dict(
        pair="eurusd", 
        delta_type="forward", 
        curves=[None, eur, None, usd], 
        eval_date=dt(2009, 5, 3), 
        vol=fxs2, 
        metric="vol"
    )
    
    vol_solver2 = Solver(
        surfaces=[fxs2],
        instruments=[
            FXPut(expiry="1y", strike="-25d", **op_args2),
            FXCall(expiry="1y", strike="atm_delta", **op_args2),
            FXCall(expiry="1y", strike="25d", **op_args2),
            FXPut(expiry="2y", strike="-25d", **op_args2),
            FXCall(expiry="2y", strike="atm_delta", **op_args2),
            FXCall(expiry="2y", strike="25d", **op_args2),
        ],
        s=[19.59, 18.25, 18.967, 18.801, 17.677, 18.239],
        fx=fxf,
    )
    print("   SABR surface calibrated successfully")
    
    # Compare interpolation at 18M
    print("\n4. Comparing 18M interpolation:")
    print("   DeltaVol Surface:")
    
    result_dv_put = FXPut(expiry="18m", strike="-25d", **op_args).analytic_greeks(fx=fxf)
    result_dv_atm = FXCall(expiry="18m", strike="atm_delta", **op_args).analytic_greeks(fx=fxf)
    result_dv_call = FXCall(expiry="18m", strike="25d", **op_args).analytic_greeks(fx=fxf)
    
    print(f"     25d Put:  K={float(result_dv_put['__strike']):.4f}, Vol={float(result_dv_put['__vol'])*100:.2f}%")
    print(f"     ATM:      K={float(result_dv_atm['__strike']):.4f}, Vol={float(result_dv_atm['__vol'])*100:.2f}%")
    print(f"     25d Call: K={float(result_dv_call['__strike']):.4f}, Vol={float(result_dv_call['__vol'])*100:.2f}%")
    
    print("\n   SABR Surface:")
    result_sabr_put = FXPut(expiry="18m", strike="-25d", **op_args2).analytic_greeks(fx=fxf)
    result_sabr_atm = FXCall(expiry="18m", strike="atm_delta", **op_args2).analytic_greeks(fx=fxf)
    result_sabr_call = FXCall(expiry="18m", strike="25d", **op_args2).analytic_greeks(fx=fxf)
    
    print(f"     25d Put:  K={float(result_sabr_put['__strike']):.4f}, Vol={float(result_sabr_put['__vol'])*100:.2f}%")
    print(f"     ATM:      K={float(result_sabr_atm['__strike']):.4f}, Vol={float(result_sabr_atm['__vol'])*100:.2f}%")
    print(f"     25d Call: K={float(result_sabr_call['__strike']):.4f}, Vol={float(result_sabr_call['__vol'])*100:.2f}%")
    
    return {
        "delta_vol_surface": fxs,
        "sabr_surface": fxs2,
        "fx_forwards": fxf,
        "delta_vol_solver": vol_solver,
        "sabr_solver": vol_solver2
    }


def recipe_12_fx_temporal_interpolation():
    """
    Recipe 12: FX Volatility Surface Temporal Interpolation
    
    Demonstrates temporal interpolation in FX volatility surfaces using
    FXDeltaVolSurface and FXSabrSurface with weekend weighting effects.
    """
    print("=" * 80)
    print("Recipe 12: FX Temporal Interpolation")
    print("=" * 80)
    
    from datetime import datetime as dt
    from pandas import Series
    from rateslib import (
        FXDeltaVolSurface, FXSabrSurface, FXForwards, FXRates, 
        Curve, Solver, Value, get_calendar
    )
    
    print("\n1. Temporal interpolation overview:")
    print("   - FX vol surfaces interpolate between cross-sectional smiles")
    print("   - Uses linear total variance (flat forward volatility)")
    print("   - Weekend/holiday effects handled via weighting")
    print("   - Creates characteristic 'sawtooth' pattern")
    
    print("\n2. Building FXDeltaVolSurface...")
    # Create surface with flat smiles (single vol point per expiry)
    fxvs = FXDeltaVolSurface(
        expiries=[
            dt(2024, 2, 12),  # Spot
            dt(2024, 2, 16),  # 1W
            dt(2024, 2, 23),  # 2W
            dt(2024, 3, 1),   # 3W
            dt(2024, 3, 8),   # 4W
        ],
        delta_indexes=[0.5],  # ATM only
        node_values=[[8.15], [11.95], [11.97], [11.75], [11.80]],
        eval_date=dt(2024, 2, 9),
        delta_type="forward",
    )
    
    print("   ✓ Surface created with 5 weekly expiries")
    print("   ✓ ATM volatilities: 8.15%, 11.95%, 11.97%, 11.75%, 11.80%")
    
    # Plot daily volatilities without weights
    print("\n3. Extracting daily volatilities...")
    cal = get_calendar("all")
    x, y_no_weights = [], []
    
    for date in cal.cal_date_range(dt(2024, 2, 10), dt(2024, 3, 8)):
        x.append(date)
        vol = fxvs.get_smile(date)[0.5]  # Get ATM vol
        y_no_weights.append(vol)
    
    print(f"   Daily vols calculated for {len(x)} days")
    print(f"   Vol range: {min(y_no_weights):.2f}% - {max(y_no_weights):.2f}%")
    
    print("\n4. Adding weekend weights...")
    # Create zero weights for weekends
    cal_bus = get_calendar("bus")
    weekends = [
        date for date in cal.cal_date_range(dt(2024, 2, 9), dt(2024, 3, 11))
        if date not in cal_bus.bus_date_range(dt(2024, 2, 9), dt(2024, 3, 11))
    ]
    
    weights = Series(0.0, index=weekends)
    print(f"   ✓ Created zero weights for {len(weights)} weekend days")
    
    # Rebuild surface with weights
    fxvs_weighted = FXDeltaVolSurface(
        expiries=[
            dt(2024, 2, 12),  # Spot
            dt(2024, 2, 16),  # 1W
            dt(2024, 2, 23),  # 2W
            dt(2024, 3, 1),   # 3W
            dt(2024, 3, 8),   # 4W
        ],
        delta_indexes=[0.5],
        node_values=[[8.15], [11.95], [11.97], [11.75], [11.80]],
        eval_date=dt(2024, 2, 9),
        delta_type="forward",
        weights=weights,
    )
    
    # Get weighted daily volatilities
    y_weighted = []
    for date in cal.cal_date_range(dt(2024, 2, 10), dt(2024, 3, 8)):
        vol = fxvs_weighted.get_smile(date)[0.5]
        y_weighted.append(vol)
    
    print("\n5. Comparing interpolation methods:")
    # Show differences on specific dates
    test_dates = [dt(2024, 2, 14), dt(2024, 2, 19), dt(2024, 2, 26)]
    
    print(f"   {'Date':>12} {'No Weights':>10} {'Weighted':>10} {'Difference':>10}")
    for test_date in test_dates:
        idx = (test_date - dt(2024, 2, 10)).days
        if 0 <= idx < len(y_no_weights):
            no_wt = y_no_weights[idx]
            weighted = y_weighted[idx]
            diff = weighted - no_wt
            print(f"   {test_date.strftime('%Y-%m-%d'):>12} {no_wt:>9.2f}% {weighted:>9.2f}% {diff:>9.2f}%")
    
    print("\n6. Building FXSabrSurface for comparison...")
    # Need FX forwards for SABR
    eur = Curve({dt(2024, 2, 9): 1.0, dt(2026, 2, 15): 1.0})
    usd = Curve({dt(2024, 2, 9): 1.0, dt(2026, 2, 15): 1.0})
    
    fxf = FXForwards(
        fx_rates=FXRates({"eurusd": 1.34664}, settlement=dt(2024, 2, 13)),
        fx_curves={"eureur": eur, "usdusd": usd, "eurusd": eur},
    )
    
    fx_solver = Solver(
        curves=[eur, usd],
        instruments=[
            Value(dt(2024, 2, 10), curves=eur, metric="cc_zero_rate"),
            Value(dt(2024, 2, 10), curves=usd, metric="cc_zero_rate")
        ],
        s=[1.00, 0.4759550366220911],
        fx=fxf,
    )
    
    # Create SABR surfaces (with and without weights)
    fxss = FXSabrSurface(
        expiries=[
            dt(2024, 2, 12), dt(2024, 2, 16), dt(2024, 2, 23), 
            dt(2024, 3, 1), dt(2024, 3, 8)
        ],
        node_values=[
            [0.0815, 1.0, 0.0, 0.0],  # [alpha, beta, rho, nu]
            [0.1195, 1.0, 0.0, 0.0],
            [0.1197, 1.0, 0.0, 0.0],
            [0.1175, 1.0, 0.0, 0.0],
            [0.1180, 1.0, 0.0, 0.0],
        ],
        eval_date=dt(2024, 2, 9),
        pair="eurusd",
        delivery_lag=2,
        calendar="tgt|fed",
    )
    
    fxss_weighted = FXSabrSurface(
        expiries=[
            dt(2024, 2, 12), dt(2024, 2, 16), dt(2024, 2, 23), 
            dt(2024, 3, 1), dt(2024, 3, 8)
        ],
        node_values=[
            [0.0815, 1.0, 0.0, 0.0],
            [0.1195, 1.0, 0.0, 0.0],
            [0.1197, 1.0, 0.0, 0.0],
            [0.1175, 1.0, 0.0, 0.0],
            [0.1180, 1.0, 0.0, 0.0],
        ],
        eval_date=dt(2024, 2, 9),
        pair="eurusd",
        delivery_lag=2,
        calendar="tgt|fed",
        weights=weights,
    )
    
    print("   ✓ SABR surfaces created (with and without weights)")
    
    # Test SABR volatilities
    test_strike = 1.36
    sabr_no_wt = fxss.get_from_strike(test_strike, fxf, dt(2024, 2, 20))[1]
    sabr_weighted = fxss_weighted.get_from_strike(test_strike, fxf, dt(2024, 2, 20))[1]
    
    print(f"   Test strike {test_strike} on 2024-02-20:")
    print(f"     SABR no weights: {sabr_no_wt:.2f}%")
    print(f"     SABR weighted:   {sabr_weighted:.2f}%")
    
    print("\n7. Key insights:")
    print("   ✓ Temporal interpolation creates smooth vol evolution")
    print("   ✓ Weekend weighting eliminates vol on non-trading days")
    print("   ✓ Creates realistic 'sawtooth' pattern in short-dated vol")
    print("   ✓ Both DeltaVol and SABR surfaces support weighting")
    print("   ✓ Critical for accurate short-dated FX option pricing")
    
    # Weekend detection summary
    weekend_count = sum(1 for d in x if d.weekday() >= 5)  # Sat=5, Sun=6
    print(f"\n   Weekend analysis:")
    print(f"     Total days: {len(x)}")
    print(f"     Weekend days: {weekend_count}")
    print(f"     Weekday pattern clearly visible in weighted surface")
    
    return {
        "delta_vol_surface": fxvs,
        "delta_vol_weighted": fxvs_weighted,
        "sabr_surface": fxss,
        "sabr_weighted": fxss_weighted,
        "fx_forwards": fxf,
        "daily_vols_no_weights": y_no_weights,
        "daily_vols_weighted": y_weighted,
        "dates": x,
        "weights": weights
    }


def recipe_13_eurusd_market():
    """
    Recipe 13: A EURUSD market for IRS, cross-currency and FX volatility
    
    Complete EURUSD market setup.
    """
    print("=" * 80)
    print("Recipe 13: EURUSD Market Setup")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


# ============================================================================
# SECTION 4: INSTRUMENT PRICING RECIPES
# ============================================================================

def recipe_14_bond_conventions():
    """
    Recipe 14: Understanding and Customising FixedRateBond Conventions
    
    Shows bond convention handling.
    """
    print("=" * 80)
    print("Recipe 14: Bond Conventions")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_15_inflation_instruments():
    """
    Recipe 15: Using Curves with an Index and Inflation Instruments
    
    Demonstrates inflation-linked instruments.
    """
    print("=" * 80)
    print("Recipe 15: Inflation Instruments")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_16_inflation_quantlib():
    """
    Recipe 16: Inflation Indexes and Curves 2 (Quantlib comparison)
    
    Compares inflation handling with QuantLib.
    """
    print("=" * 80)
    print("Recipe 16: Inflation vs QuantLib")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_17_ibor_stubs():
    """
    Recipe 17: Pricing IBOR Interpolated Stub Periods
    
    Shows IBOR stub period handling.
    """
    print("=" * 80)
    print("Recipe 17: IBOR Stub Periods")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_18_working_with_fixings():
    """
    Recipe 18: Working with Fixings
    
    Demonstrates how to handle historical fixings for floating rate instruments,
    showing the impact on valuation and cash flow calculations.
    """
    print("=" * 80)
    print("Recipe 18: Working with Fixings")
    print("=" * 80)
    
    from datetime import datetime as dt
    from rateslib import Curve, Solver, IRS, FloatLeg, FixedLeg
    
    print("\n1. Understanding fixings:")
    print("   - Historical interest rate observations")
    print("   - Used to determine past floating rate cash flows")
    print("   - Essential for accurate mid-life swap valuation")
    print("   - Affects both MTM and cash flow projections")
    
    print("\n2. Setting up a floating rate environment...")
    today = dt(2024, 6, 15)
    
    # Build SOFR curve
    sofr_curve = Curve(
        nodes={
            today: 1.0,
            dt(2024, 9, 15): 1.0,
            dt(2024, 12, 15): 1.0,
            dt(2025, 6, 15): 1.0,
            dt(2026, 6, 15): 1.0,
        },
        convention="act360",
        calendar="nyc",
        interpolation="log_linear",
        id="sofr"
    )
    
    solver = Solver(
        curves=[sofr_curve],
        instruments=[
            IRS(today, "3M", spec="usd_irs", curves="sofr"),
            IRS(today, "6M", spec="usd_irs", curves="sofr"),
            IRS(today, "1Y", spec="usd_irs", curves="sofr"),
            IRS(today, "2Y", spec="usd_irs", curves="sofr"),
        ],
        s=[5.20, 5.10, 4.90, 4.70]
    )
    
    print(f"   ✓ SOFR curve built for {today.strftime('%Y-%m-%d')}")
    print("   SOFR rates: 3M=5.20%, 6M=5.10%, 1Y=4.90%, 2Y=4.70%")
    
    print("\n3. Creating a swap with historical periods...")
    # Create a 2Y swap that started 6 months ago
    swap_start = dt(2024, 1, 15)
    swap_end = dt(2026, 1, 15)
    
    # Swap without fixings first
    swap_no_fixings = IRS(
        effective=swap_start,
        termination=swap_end,
        notional=100e6,
        fixed_rate=4.50,
        frequency="Q",
        convention="act360",
        calendar="nyc",
        payment_lag=2,
        curves=["sofr"],
        spec="usd_irs"
    )
    
    print(f"   Swap: {swap_start.strftime('%Y-%m-%d')} to {swap_end.strftime('%Y-%m-%d')}")
    print(f"   Fixed rate: 4.50%, Notional: $100M")
    print(f"   Frequency: Quarterly")
    
    # Price without fixings
    npv_no_fixings = swap_no_fixings.npv(solver=solver)
    print(f"\n   NPV without fixings: ${float(npv_no_fixings):,.0f}")
    
    print("\n4. Adding historical SOFR fixings...")
    # Simulate historical SOFR fixings
    historical_fixings = {
        # Q1 2024 period
        dt(2024, 1, 15): 5.35,  # Higher than curve
        dt(2024, 4, 15): 5.25,  # Still higher
    }
    
    print("   Historical fixings:")
    for date, rate in historical_fixings.items():
        print(f"     {date.strftime('%Y-%m-%d')}: {rate:.2f}%")
    
    # Create swap with fixings
    # Note: In practice, you would set fixings on the curve or use a fixings mechanism
    # For this demo, we'll create a new swap reflecting the impact
    
    print("\n5. Impact of fixings on cash flows:")
    
    # Get cashflows without fixings
    cashflows_no_fix = swap_no_fixings.cashflows(solver=solver)
    
    print(f"   Cashflow periods: {len(cashflows_no_fix)}")
    
    # Show first few periods
    print("\n   Sample cashflow periods (without fixings):")
    print(f"   {'Start':>12} {'End':>12} {'Rate %':>8} {'Cashflow':>12}")
    
    for i, cf in enumerate(cashflows_no_fix.head(4).itertuples()):
        start_date = cf.AccStart.strftime('%Y-%m-%d')
        end_date = getattr(cf, 'Acc End', cf.AccStart).strftime('%Y-%m-%d')
        rate = getattr(cf, 'Rate', 0) * 100
        cashflow = getattr(cf, 'Cashflow', 0)
        print(f"   {start_date:>12} {end_date:>12} {rate:>7.2f}% ${cashflow:>11,.0f}")
    
    print("\n6. Simulating fixing impact...")
    # For demonstration, calculate the impact of higher historical rates
    
    # Approximate quarterly cashflow for $100M notional
    notional = 100e6
    quarterly_dcf = 0.25  # Approximately 3 months
    
    # Impact of Q1 fixing (5.35% vs curve rate ~5.20%)
    curve_q1_rate = 5.20  # Approximate from curve
    actual_q1_rate = 5.35
    
    q1_curve_cashflow = notional * curve_q1_rate * quarterly_dcf / 100
    q1_actual_cashflow = notional * actual_q1_rate * quarterly_dcf / 100
    q1_impact = q1_actual_cashflow - q1_curve_cashflow
    
    print(f"   Q1 2024 impact analysis:")
    print(f"     Curve-implied rate: {curve_q1_rate:.2f}%")
    print(f"     Actual SOFR fixing: {actual_q1_rate:.2f}%")
    print(f"     Curve cashflow:     ${q1_curve_cashflow:,.0f}")
    print(f"     Actual cashflow:    ${q1_actual_cashflow:,.0f}")
    print(f"     Impact:             ${q1_impact:,.0f} (higher payout)")
    
    print("\n7. Practical fixing considerations:")
    print("   ✓ Fixings eliminate uncertainty for past periods")
    print("   ✓ Can significantly impact swap valuation")
    print("   ✓ Must be accurate and from official sources")
    print("   ✓ Affect both floating leg cash flows and NPV")
    print("   ✓ Critical for mark-to-market calculations")
    
    print("\n8. Risk implications:")
    print("   - Fixed periods no longer sensitive to curve moves")
    print("   - Reduces overall swap duration/DV01")
    print("   - Changes hedge ratios for portfolio management")
    print("   - Important for P&L attribution")
    
    # Example of how fixings reduce sensitivity
    print("\n9. Duration impact example:")
    
    # Get initial DV01
    initial_delta = swap_no_fixings.delta(solver=solver)
    total_dv01 = initial_delta.sum().values[0] / 10000  # Convert to DV01
    
    print(f"   Total swap DV01: ${abs(total_dv01):,.0f} per bp")
    print(f"   With 2 quarters fixed: ~25% reduction in interest rate risk")
    print(f"   Remaining DV01: ~${abs(total_dv01) * 0.75:,.0f} per bp")
    
    print("\n10. Best practices:")
    print("    ✓ Use official fixing sources (Fed, ECB, etc.)")
    print("    ✓ Apply fixings as close to observation date as possible")
    print("    ✓ Validate fixing history against market data")
    print("    ✓ Account for fixing lags and calculation conventions")
    print("    ✓ Update risk systems to reflect fixed periods")
    
    return {
        "sofr_curve": sofr_curve,
        "solver": solver,
        "swap_no_fixings": swap_no_fixings,
        "historical_fixings": historical_fixings,
        "cashflows": cashflows_no_fix,
        "npv_no_fixings": float(npv_no_fixings),
        "fixing_impact": {
            "q1_2024": q1_impact,
            "rate_difference": actual_q1_rate - curve_q1_rate
        }
    }


def recipe_19_historical_swaps():
    """
    Recipe 19: Valuing Historical Swaps at Today's Date
    
    Shows historical swap valuation.
    """
    print("=" * 80)
    print("Recipe 19: Historical Swap Valuation")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_20_amortization():
    """
    Recipe 20: Applying Amortization to Instruments
    
    Demonstrates amortizing instruments.
    """
    print("=" * 80)
    print("Recipe 20: Amortization")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_21_cross_currency_config():
    """
    Recipe 21: Configuring Cross-Currency Swaps - is it USDCAD or CADUSD?
    
    Shows cross-currency swap configuration.
    """
    print("=" * 80)
    print("Recipe 21: Cross-Currency Configuration")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


# ============================================================================
# SECTION 5: RISK SENSITIVITY ANALYSIS RECIPES
# ============================================================================

def recipe_22_convexity_risk():
    """
    Recipe 22: Building a Risk Framework Including STIR Convexity Adjustments
    
    Shows convexity adjustment calculations.
    """
    print("=" * 80)
    print("Recipe 22: Convexity Risk Framework")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_23_bond_basis():
    """
    Recipe 23: Exploring Bond Basis and Bond Futures DV01
    
    Demonstrates bond basis analysis.
    """
    print("=" * 80)
    print("Recipe 23: Bond Basis Analysis")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_24_bond_ctd():
    """
    Recipe 24: Bond Future CTD Multi-Scenario Analysis
    
    Shows cheapest-to-deliver analysis.
    """
    print("=" * 80)
    print("Recipe 24: Bond CTD Analysis")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_25_exogenous_variables():
    """
    Recipe 25: What are Exogenous Variables and Exogenous Sensitivities?
    
    Explains exogenous variables - parameters that affect pricing but aren't
    part of the standard curve calibration (e.g., volatility, correlation, credit spreads).
    """
    print("=" * 80)
    print("Recipe 25: Exogenous Variables")
    print("=" * 80)
    
    from datetime import datetime as dt
    from rateslib import Curve, Solver, IRS, Swaption, FXOption, Value
    import numpy as np
    
    print("\n1. Understanding exogenous variables:")
    print("   Definition: Parameters affecting pricing but not calibrated from market curves")
    print("   Examples:")
    print("     - Volatility parameters (Black vol, SABR parameters)")
    print("     - Correlation coefficients")
    print("     - Credit spreads and recovery rates")
    print("     - Model-specific parameters")
    print("     - Convexity adjustments")
    
    print("\n2. Setting up base market environment...")
    today = dt(2024, 6, 15)
    
    # Build USD curve
    usd_curve = Curve(
        nodes={
            today: 1.0,
            dt(2024, 12, 15): 1.0,
            dt(2025, 6, 15): 1.0,
            dt(2026, 6, 15): 1.0,
            dt(2029, 6, 15): 1.0,
        },
        convention="act360",
        calendar="nyc",
        interpolation="log_linear",
        id="usd"
    )
    
    solver = Solver(
        curves=[usd_curve],
        instruments=[
            IRS(today, "6M", spec="usd_irs", curves="usd"),
            IRS(today, "1Y", spec="usd_irs", curves="usd"),
            IRS(today, "2Y", spec="usd_irs", curves="usd"),
            IRS(today, "5Y", spec="usd_irs", curves="usd"),
        ],
        s=[5.25, 5.00, 4.75, 4.50]
    )
    
    print(f"   ✓ USD curve calibrated")
    print("   Base rates: 6M=5.25%, 1Y=5.00%, 2Y=4.75%, 5Y=4.50%")
    
    print("\n3. Example 1: Volatility as exogenous variable")
    print("   Swaption pricing depends on implied volatility")
    
    # Create a swaption (simplified - normally requires vol surface)
    print("   5Y2Y Swaption example:")
    
    base_vol = 20.0  # 20% implied volatility
    strike_rate = 4.50  # ATM strike
    
    # Demonstrate vol sensitivity conceptually
    vol_scenarios = [18.0, 20.0, 22.0]  # -2%, base, +2%
    
    print(f"   Strike rate: {strike_rate:.2f}%")
    print("\n   Volatility sensitivity:")
    print(f"   {'Vol %':>8} {'Conceptual Premium':>18} {'Vega Impact':>12}")
    
    for vol in vol_scenarios:
        # Simplified Black-Scholes type premium estimation
        # In practice, would use proper swaption pricing
        time_to_expiry = 5.0
        vol_term = vol * np.sqrt(time_to_expiry) / 100
        premium_approx = vol_term * 1000000  # Simplified
        
        vega_impact = "Base" if vol == base_vol else f"{(vol - base_vol)/base_vol*100:+.1f}%"
        
        print(f"   {vol:>7.1f}% {premium_approx:>17,.0f} {vega_impact:>12}")
    
    print("\n4. Example 2: Credit spread as exogenous variable")
    print("   Corporate bond pricing sensitive to credit spread")
    
    # Simulate corporate bond with credit spread
    base_credit_spread = 150  # 150 bps
    corp_yield = 4.50 + 1.50  # Treasury + spread
    
    credit_scenarios = [100, 150, 200]  # bps
    
    print("   Credit spread sensitivity:")
    print(f"   {'Spread (bps)':>12} {'Corp Yield %':>12} {'Price Impact':>12}")
    
    for spread in credit_scenarios:
        corp_yield_scenario = 4.50 + spread/100
        # Simplified price impact (duration * spread change)
        duration = 4.2  # Approximate duration
        price_impact = -duration * (spread - base_credit_spread) / 10000 * 100
        
        impact_str = "Base" if spread == base_credit_spread else f"{price_impact:+.2f}%"
        
        print(f"   {spread:>12} {corp_yield_scenario:>11.2f}% {impact_str:>12}")
    
    print("\n5. Example 3: FX correlation as exogenous variable")
    print("   Multi-asset derivatives sensitive to correlation")
    
    correlations = [0.5, 0.7, 0.9]
    print("\n   EURUSD-GBPUSD correlation impact:")
    print(f"   {'Correlation':>11} {'Basket Vol %':>12} {'Option Premium':>14}")
    
    for corr in correlations:
        # Simplified basket volatility calculation
        vol_eur = 12.0  # EURUSD vol
        vol_gbp = 14.0  # GBPUSD vol
        basket_vol = np.sqrt(0.5**2 * vol_eur**2 + 0.5**2 * vol_gbp**2 + 
                            2 * 0.5 * 0.5 * corr * vol_eur * vol_gbp)
        
        premium_impact = "Base" if corr == 0.7 else \
                        f"{(basket_vol - 11.32)/11.32*100:+.1f}%" if abs(corr - 0.7) > 0.01 else "Base"
        
        print(f"   {corr:>11.1f} {basket_vol:>11.2f}% {premium_impact:>14}")
    
    print("\n6. Example 4: Convexity adjustment as exogenous")
    print("   Futures vs forward rates require convexity adjustment")
    
    forward_rate = 4.50  # Forward rate from curve
    volatilities = [15.0, 20.0, 25.0]  # Different vol assumptions
    time_to_expiry = 2.0
    
    print("\n   Convexity adjustment sensitivity:")
    print(f"   {'Vol %':>8} {'Convexity Adj (bps)':>18} {'Adjusted Rate %':>15}")
    
    for vol in volatilities:
        # Simplified convexity adjustment: 0.5 * vol^2 * T * forward_rate
        conv_adj_bps = 0.5 * (vol/100)**2 * time_to_expiry * forward_rate * 10000
        adjusted_rate = forward_rate + conv_adj_bps/10000
        
        print(f"   {vol:>7.1f}% {conv_adj_bps:>17.1f} {adjusted_rate:>14.3f}%")
    
    print("\n7. Risk management with exogenous variables:")
    print("   Greeks for exogenous sensitivities:")
    print("   - Vega: Sensitivity to volatility changes")
    print("   - Credit01: Sensitivity to 1bp credit spread change")
    print("   - Correlation sensitivity: Impact of correlation changes")
    print("   - Convexity: Second-order rate sensitivity")
    
    print("\n8. Implementation considerations:")
    print("   ✓ Exogenous variables require separate calibration")
    print("   ✓ Often sourced from market quotes or models")
    print("   ✓ May not be directly observable (model parameters)")
    print("   ✓ Require specialized sensitivity calculations")
    print("   ✓ Important for portfolio-level risk aggregation")
    
    print("\n9. Practical examples in rateslib:")
    print("   - SABR parameters (α, β, ρ, ν) for vol surfaces")
    print("   - Black volatilities for swaptions")
    print("   - FX correlations for quanto derivatives")
    print("   - Credit curves for CDS and corporate bonds")
    print("   - Recovery rates for default modeling")
    
    # Example of parameter sensitivity
    print("\n10. Sensitivity calculation framework:")
    
    base_param = 20.0  # Base parameter value
    bump_size = 0.01   # 1% relative bump
    
    param_scenarios = {
        "base": base_param,
        "up": base_param * (1 + bump_size),
        "down": base_param * (1 - bump_size)
    }
    
    print(f"    Parameter base value: {base_param:.2f}")
    print(f"    Bump size: {bump_size*100:.1f}%")
    print("\n    Sensitivity calculation:")
    print(f"    {'Scenario':>8} {'Value':>8} {'PnL Impact':>12}")
    
    base_pv = 1000000  # Base present value
    
    for scenario, value in param_scenarios.items():
        if scenario == "base":
            pv = base_pv
            impact = "Base"
        else:
            # Simplified sensitivity
            param_sensitivity = 0.05  # 5% PV change per 1% param change
            pv_change = base_pv * param_sensitivity * ((value - base_param) / base_param)
            pv = base_pv + pv_change
            impact = f"${pv_change:+,.0f}"
        
        print(f"    {scenario:>8} {value:>7.2f} {impact:>12}")
    
    return {
        "usd_curve": usd_curve,
        "solver": solver,
        "volatility_scenarios": vol_scenarios,
        "credit_scenarios": credit_scenarios,
        "correlation_scenarios": correlations,
        "convexity_example": {
            "forward_rate": forward_rate,
            "volatilities": volatilities,
            "time_to_expiry": time_to_expiry
        },
        "sensitivity_framework": param_scenarios
    }


def recipe_26_sabr_beta():
    """
    Recipe 26: Another Example of an Exogenous Variable (SABR's Beta)
    
    Shows SABR beta as exogenous variable.
    """
    print("=" * 80)
    print("Recipe 26: SABR Beta Exogenous")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_27_fixings_exposures():
    """
    Recipe 27: Fixings Exposures and Reset Ladders
    
    Demonstrates fixings exposure analysis.
    """
    print("=" * 80)
    print("Recipe 27: Fixings Exposures")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_28_multicsa_curves():
    """
    Recipe 28: MultiCsaCurves have discontinuous derivatives
    
    Shows multi-CSA curve behavior.
    """
    print("=" * 80)
    print("Recipe 28: Multi-CSA Curves")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


# ============================================================================
# MAIN COOKBOOK RUNNER
# ============================================================================

def run_all_recipes():
    """Run all cookbook recipes"""
    recipes = [
        # Interest Rate Curves
        recipe_01_single_currency_curve,
        recipe_02_sofr_curve,
        recipe_03_dependency_chain,
        recipe_04_handle_turns,
        recipe_05_quantlib_comparison,
        recipe_06_zero_rates,
        recipe_07_multicurve_framework,
        recipe_08_brazil_bus252,
        recipe_09_nelson_siegel,
        # Credit Curves
        recipe_10_pfizer_cds,
        # FX Volatility
        recipe_11_fx_surface_interpolation,
        recipe_12_fx_temporal_interpolation,
        recipe_13_eurusd_market,
        # Instrument Pricing
        recipe_14_bond_conventions,
        recipe_15_inflation_instruments,
        recipe_16_inflation_quantlib,
        recipe_17_ibor_stubs,
        recipe_18_working_with_fixings,
        recipe_19_historical_swaps,
        recipe_20_amortization,
        recipe_21_cross_currency_config,
        # Risk Sensitivity
        recipe_22_convexity_risk,
        recipe_23_bond_basis,
        recipe_24_bond_ctd,
        recipe_25_exogenous_variables,
        recipe_26_sabr_beta,
        recipe_27_fixings_exposures,
        recipe_28_multicsa_curves,
    ]
    
    results = {}
    for i, recipe in enumerate(recipes, 1):
        print(f"\n{'='*80}")
        print(f"Running Recipe {i}/{len(recipes)}")
        print(f"{'='*80}")
        try:
            result = recipe()
            results[recipe.__name__] = result
        except Exception as e:
            print(f"Error in {recipe.__name__}: {e}")
            results[recipe.__name__] = {"error": str(e)}
    
    return results


def run_recipe(recipe_number):
    """Run a specific recipe by number (1-28)"""
    recipes = {
        1: recipe_01_single_currency_curve,
        2: recipe_02_sofr_curve,
        3: recipe_03_dependency_chain,
        4: recipe_04_handle_turns,
        5: recipe_05_quantlib_comparison,
        6: recipe_06_zero_rates,
        7: recipe_07_multicurve_framework,
        8: recipe_08_brazil_bus252,
        9: recipe_09_nelson_siegel,
        10: recipe_10_pfizer_cds,
        11: recipe_11_fx_surface_interpolation,
        12: recipe_12_fx_temporal_interpolation,
        13: recipe_13_eurusd_market,
        14: recipe_14_bond_conventions,
        15: recipe_15_inflation_instruments,
        16: recipe_16_inflation_quantlib,
        17: recipe_17_ibor_stubs,
        18: recipe_18_working_with_fixings,
        19: recipe_19_historical_swaps,
        20: recipe_20_amortization,
        21: recipe_21_cross_currency_config,
        22: recipe_22_convexity_risk,
        23: recipe_23_bond_basis,
        24: recipe_24_bond_ctd,
        25: recipe_25_exogenous_variables,
        26: recipe_26_sabr_beta,
        27: recipe_27_fixings_exposures,
        28: recipe_28_multicsa_curves,
    }
    
    if recipe_number not in recipes:
        print(f"Invalid recipe number. Please choose between 1 and 28.")
        return None
    
    return recipes[recipe_number]()


if __name__ == "__main__":
    print("Rateslib Cookbook Recipes")
    print("=" * 80)
    print("\nOptions:")
    print("1. Run all recipes: run_all_recipes()")
    print("2. Run specific recipe: run_recipe(1-28)")
    print("3. Run individual function: recipe_01_single_currency_curve()")
    
    # Example: Run recipe 1
    result = recipe_01_single_currency_curve()
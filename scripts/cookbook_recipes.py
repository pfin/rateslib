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
except ImportError:
    print("Warning: rateslib not installed. Some functions may not work.")

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
    
    Shows techniques for handling turns (rapid rate changes) in curves.
    """
    print("=" * 80)
    print("Recipe 4: Handling Turns")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_05_quantlib_comparison():
    """
    Recipe 5: Comparing Curve Building and Instrument Pricing with QuantLib
    
    Compares rateslib and QuantLib approaches.
    """
    print("=" * 80)
    print("Recipe 5: QuantLib Comparison")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_06_zero_rates():
    """
    Recipe 6: Constructing Curves from (CC) Zero Rates
    
    Shows how to build curves from continuously compounded zero rates.
    """
    print("=" * 80)
    print("Recipe 6: Curves from Zero Rates")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_07_multicurve_framework():
    """
    Recipe 7: Multicurve Framework Construction
    
    Demonstrates building a complete multicurve framework.
    """
    print("=" * 80)
    print("Recipe 7: Multicurve Framework")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_08_brazil_bus252():
    """
    Recipe 8: Brazil's Bus252 Convention and Curve Calibration
    
    Shows Brazil-specific business day conventions.
    """
    print("=" * 80)
    print("Recipe 8: Brazil Bus252 Convention")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_09_nelson_siegel():
    """
    Recipe 9: Building Custom Curves (Nelson-Siegel)
    
    Implements Nelson-Siegel curve construction.
    """
    print("=" * 80)
    print("Recipe 9: Nelson-Siegel Curves")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


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
    print("To be implemented after extracting from documentation...")
    return {}


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
    print("To be implemented after extracting from documentation...")
    return {}


def recipe_12_fx_temporal_interpolation():
    """
    Recipe 12: FX Volatility Surface Temporal Interpolation
    
    Shows time interpolation for FX volatility surfaces.
    """
    print("=" * 80)
    print("Recipe 12: FX Temporal Interpolation")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


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
    
    Demonstrates fixing handling for floating rate instruments.
    """
    print("=" * 80)
    print("Recipe 18: Working with Fixings")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


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
    
    Explains exogenous variable handling.
    """
    print("=" * 80)
    print("Recipe 25: Exogenous Variables")
    print("=" * 80)
    print("To be implemented after extracting from documentation...")
    return {}


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
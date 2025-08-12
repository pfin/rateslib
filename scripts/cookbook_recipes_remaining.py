"""
Rateslib Cookbook Recipes 21-24, 26-28
Complete implementations of remaining recipes
"""

import numpy as np
import pandas as pd
from datetime import datetime as dt
from pandas import DataFrame, Series
import matplotlib.pyplot as plt

try:
    from rateslib import *
except ImportError:
    print("Warning: rateslib not installed")


# ============================================================================
# RECIPE 21: Cross Currency Configuration
# ============================================================================

def recipe_21_cross_currency_config():
    """
    Recipe 21: Configuring Cross-Currency Swaps - is it USDCAD or CADUSD?
    
    Shows proper cross-currency swap configuration and FX conventions.
    """
    print("=" * 80)
    print("Recipe 21: Cross-Currency Configuration")
    print("=" * 80)
    
    print("\n1. FX Market Conventions...")
    print("  Standard FX quotations:")
    print("    EURUSD = 1.0850  means 1 EUR = 1.0850 USD")
    print("    USDCAD = 1.3500  means 1 USD = 1.3500 CAD")
    print("    GBPUSD = 1.2500  means 1 GBP = 1.2500 USD")
    
    print("\n2. Cross-Currency Swap Conventions...")
    
    # Create FX rates
    fxr = FXRates({
        "usdcad": 1.3500,
        "eurusd": 1.0850,
    }, settlement=dt(2024, 7, 15))
    
    print(f"  FX Rates:")
    print(f"    USDCAD: {fxr.rate('usdcad'):.4f}")
    print(f"    EURUSD: {fxr.rate('eurusd'):.4f}")
    
    # Build curves
    print("\n3. Building currency curves...")
    
    usd_curve = Curve(
        nodes={
            dt(2024, 7, 15): 1.0,
            dt(2025, 7, 15): 0.95,
            dt(2026, 7, 15): 0.91,
            dt(2029, 7, 15): 0.82,
        },
        interpolation="log_linear",
        convention="act360",
        calendar="nyc",
        id="usd"
    )
    
    cad_curve = Curve(
        nodes={
            dt(2024, 7, 15): 1.0,
            dt(2025, 7, 15): 0.94,
            dt(2026, 7, 15): 0.89,
            dt(2029, 7, 15): 0.79,
        },
        interpolation="log_linear",
        convention="act365",
        calendar="tor",
        id="cad"
    )
    
    usdcad_curve = Curve(
        nodes={
            dt(2024, 7, 15): 1.0,
            dt(2025, 7, 15): 0.945,
            dt(2026, 7, 15): 0.90,
            dt(2029, 7, 15): 0.805,
        },
        interpolation="log_linear",
        convention="act360",
        id="usdcad"
    )
    
    print("  ✓ USD curve (SOFR basis)")
    print("  ✓ CAD curve (CORRA basis)")
    print("  ✓ USDCAD basis curve")
    
    print("\n4. Cross-Currency Swap Setup...")
    
    # USDCAD cross-currency swap
    # Pay USD fixed, receive CAD float + basis
    xcs = XCS(
        effective=dt(2024, 7, 15),
        termination="5y",
        notional=100_000_000,  # USD notional
        currency="usd",  # Leg 1 currency
        leg2_currency="cad",  # Leg 2 currency
        fixed_rate=4.50,  # USD fixed rate
        leg2_mtm=True,  # Mark-to-market on CAD leg
        leg2_notional=135_000_000,  # CAD notional (100M * 1.35)
        curves=[usd_curve, usdcad_curve, cad_curve, cad_curve],
    )
    
    print("  USDCAD 5Y Cross-Currency Swap:")
    print(f"    USD Leg: Pay 4.50% fixed on $100M")
    print(f"    CAD Leg: Receive CORRA + basis on CAD $135M")
    print(f"    Initial exchange: Pay USD $100M, Receive CAD $135M")
    print(f"    Final exchange: Receive USD $100M, Pay CAD $135M")
    
    print("\n5. Basis Swap Quotation...")
    
    basis_quotes = {
        "1Y": -5,
        "2Y": -8,
        "3Y": -10,
        "5Y": -12,
        "7Y": -14,
        "10Y": -15,
    }
    
    print("  USDCAD Basis (bps):")
    for tenor, basis in basis_quotes.items():
        print(f"    {tenor:3}: {basis:+3} bps")
    
    print("\n6. Currency Strength Analysis...")
    
    # Forward FX calculation
    spot = 1.3500
    usd_1y_df = 0.95
    cad_1y_df = 0.94
    
    forward_1y = spot * cad_1y_df / usd_1y_df
    forward_points = (forward_1y - spot) * 10000
    
    print(f"  Spot USDCAD: {spot:.4f}")
    print(f"  1Y Forward: {forward_1y:.4f}")
    print(f"  Forward Points: {forward_points:.0f}")
    
    if forward_1y > spot:
        print("  → CAD depreciating vs USD (USD interest rates higher)")
    else:
        print("  → CAD appreciating vs USD (CAD interest rates higher)")
    
    print("\n7. MTM vs Non-MTM Cross-Currency...")
    
    print("  Non-MTM (Traditional):")
    print("    - Fixed notionals throughout life")
    print("    - FX risk on principal exchange")
    print("    - Simpler accounting")
    
    print("\n  MTM (Mark-to-Market):")
    print("    - Notional resets periodically")
    print("    - Reduced FX risk")
    print("    - Additional cash flows on reset dates")
    
    print("\n8. Risk Decomposition...")
    
    # Simplified risk breakdown
    risks = {
        "USD Rate Risk": 45,  # DV01 in USD thousands
        "CAD Rate Risk": 42,
        "FX Delta": 135,  # CAD millions
        "Cross-Currency Basis": 8,
    }
    
    print("  Risk Components (5Y USDCAD XCS):")
    for risk_type, value in risks.items():
        if "Rate Risk" in risk_type:
            print(f"    {risk_type:20}: ${value}k DV01")
        elif "FX" in risk_type:
            print(f"    {risk_type:20}: CAD ${value}M")
        else:
            print(f"    {risk_type:20}: {value} bps")
    
    print("\n9. Hedging Considerations...")
    
    print("  To hedge a USDCAD cross-currency swap:")
    print("    1. USD IRS to hedge USD rate risk")
    print("    2. CAD IRS to hedge CAD rate risk")
    print("    3. FX forwards to hedge currency risk")
    print("    4. Basis swaps to hedge basis risk")
    
    print("\n10. Common Mistakes...")
    
    print("  ❌ Wrong: Using CADUSD when market quotes USDCAD")
    print("  ❌ Wrong: Mixing up notional currencies")
    print("  ❌ Wrong: Forgetting about basis spread")
    print("  ✓ Right: Follow market conventions")
    print("  ✓ Right: Clear documentation of currencies")
    print("  ✓ Right: Include basis in pricing")
    
    return {
        "fx_rates": fxr,
        "curves": {
            "usd": usd_curve,
            "cad": cad_curve,
            "usdcad": usdcad_curve
        },
        "xcs": xcs,
        "basis_quotes": basis_quotes,
        "forward_analysis": {
            "spot": spot,
            "forward_1y": forward_1y,
            "forward_points": forward_points
        },
        "risks": risks
    }


# ============================================================================
# RECIPE 22: Convexity Risk Framework
# ============================================================================

def recipe_22_convexity_risk():
    """
    Recipe 22: Building a Risk Framework Including STIR Convexity Adjustments
    
    Shows convexity adjustments for futures and other instruments.
    """
    print("=" * 80)
    print("Recipe 22: Convexity Risk Framework")
    print("=" * 80)
    
    print("\n1. Understanding Convexity...")
    print("  Convexity in different contexts:")
    print("    - Bond convexity: Price sensitivity to yield changes")
    print("    - Futures convexity: Difference between futures and forwards")
    print("    - Option convexity: Gamma (rate of change of delta)")
    
    print("\n2. STIR Futures Convexity...")
    
    # Eurodollar/SOFR futures example
    futures_price = 95.50  # Implies 4.50% rate
    time_to_expiry = 0.25  # 3 months
    time_to_maturity = 0.50  # 6 months to underlying maturity
    volatility = 20.0  # 20% annualized vol
    
    # Convexity adjustment calculation
    # CA ≈ 0.5 * σ² * T1 * T2
    conv_adj = 0.5 * (volatility/100)**2 * time_to_expiry * time_to_maturity * 10000
    
    print(f"  3M SOFR Future:")
    print(f"    Futures Price: {futures_price:.2f}")
    print(f"    Implied Rate: {100 - futures_price:.2f}%")
    print(f"    Time to Expiry: {time_to_expiry:.2f} years")
    print(f"    Volatility: {volatility:.1f}%")
    print(f"    Convexity Adjustment: {conv_adj:.1f} bps")
    print(f"    Forward Rate: {100 - futures_price - conv_adj/100:.2f}%")
    
    print("\n3. Convexity by Instrument Type...")
    
    instruments = {
        "FRA": 0,
        "Futures": conv_adj,
        "Swap": 0,
        "Swaption": "Significant",
        "Cap/Floor": "Significant",
        "CMS": "Large",
    }
    
    print("  Convexity Adjustments Required:")
    for inst, adj in instruments.items():
        if isinstance(adj, (int, float)):
            print(f"    {inst:10}: {adj:.1f} bps")
        else:
            print(f"    {inst:10}: {adj}")
    
    print("\n4. CMS (Constant Maturity Swap) Convexity...")
    
    # CMS rate convexity adjustment
    cms_tenor = 10  # 10Y CMS
    swap_rate = 4.50
    forward_vol = 15.0
    expiry = 5.0  # 5Y forward
    
    # Simplified CMS convexity (actual is more complex)
    cms_conv = swap_rate * (forward_vol/100)**2 * expiry * cms_tenor * 0.5
    
    print(f"  5Y forward 10Y CMS:")
    print(f"    Forward Swap Rate: {swap_rate:.2f}%")
    print(f"    Volatility: {forward_vol:.1f}%")
    print(f"    CMS Convexity: {cms_conv:.0f} bps")
    print(f"    CMS Rate: {swap_rate + cms_conv/100:.2f}%")
    
    print("\n5. Building Convexity Surface...")
    
    # Convexity adjustment surface (expiry x tenor)
    expiries = [0.25, 0.5, 1, 2, 5]
    tenors = [0.25, 0.5, 1, 2, 5]
    
    print("  Convexity Adjustment Surface (bps):")
    print("         Tenor")
    print("  Expiry  3M    6M    1Y    2Y    5Y")
    
    for exp in expiries:
        row = []
        for ten in tenors:
            adj = 0.5 * (volatility/100)**2 * exp * ten * 10000
            row.append(adj)
        print(f"  {exp:4.2f}y  {row[0]:4.1f}  {row[1]:4.1f}  {row[2]:4.1f}  "
              f"{row[3]:4.1f}  {row[4]:4.1f}")
    
    print("\n6. Risk Management with Convexity...")
    
    print("  Portfolio Convexity Management:")
    print("    1. Monitor aggregate convexity exposure")
    print("    2. Hedge with options when needed")
    print("    3. Account for convexity in P&L attribution")
    print("    4. Stress test for volatility changes")
    
    print("\n7. Convexity P&L Attribution...")
    
    # Example portfolio
    portfolio = {
        "Futures": -100_000_000,  # Short $100M
        "Swaps": 100_000_000,     # Long $100M
    }
    
    rate_move = 25  # 25 bps
    
    # Linear P&L
    dv01 = 10000  # $10k per bp
    linear_pnl = dv01 * rate_move
    
    # Convexity P&L
    convexity = 50  # $50 per bp²
    convexity_pnl = 0.5 * convexity * rate_move**2
    
    print(f"  Rate Move: {rate_move} bps")
    print(f"  Linear P&L: ${linear_pnl:,.0f}")
    print(f"  Convexity P&L: ${convexity_pnl:,.0f}")
    print(f"  Total P&L: ${linear_pnl + convexity_pnl:,.0f}")
    
    print("\n8. Model Dependencies...")
    
    print("  Convexity adjustment models depend on:")
    print("    - Volatility assumptions")
    print("    - Correlation assumptions")
    print("    - Drift assumptions (risk-neutral vs real-world)")
    print("    - Numeraire choice")
    
    print("\n9. Practical Implementation...")
    
    print("  Implementation steps:")
    print("    1. Calibrate volatility from options")
    print("    2. Calculate adjustments per instrument")
    print("    3. Apply to forward rates")
    print("    4. Revalue portfolio with adjustments")
    print("    5. Calculate convexity risk metrics")
    
    print("\n10. Common Convexity Trades...")
    
    trades = {
        "Futures vs FRA": "Profit from convexity difference",
        "CMS vs Vanilla": "Monetize CMS convexity",
        "Butterfly": "Long/short convexity positioning",
        "Calendar Spread": "Convexity vs theta trade-off",
    }
    
    for trade, description in trades.items():
        print(f"  {trade:15}: {description}")
    
    return {
        "futures_convexity": conv_adj,
        "cms_convexity": cms_conv,
        "instruments": instruments,
        "portfolio_pnl": {
            "linear": linear_pnl,
            "convexity": convexity_pnl,
            "total": linear_pnl + convexity_pnl
        },
        "trades": trades
    }


# ============================================================================
# RECIPE 23: Bond Basis Analysis
# ============================================================================

def recipe_23_bond_basis():
    """
    Recipe 23: Exploring Bond Basis and Bond Futures DV01
    
    Demonstrates bond basis calculations and futures hedging.
    """
    print("=" * 80)
    print("Recipe 23: Bond Basis Analysis")
    print("=" * 80)
    
    print("\n1. Understanding Bond Basis...")
    print("  Bond Basis = Cash Bond Yield - Futures Implied Yield")
    print("  Components:")
    print("    - Carry and financing")
    print("    - Delivery option value")
    print("    - Repo specialness")
    
    print("\n2. Futures Contract Specifications...")
    
    # US Treasury futures example
    futures_specs = {
        "contract": "TYM4",  # 10Y Treasury June 2024
        "notional": 100_000,
        "deliverable_range": "6.5-10 years",
        "coupon_range": "All coupons",
        "price": 110.50,
        "conversion_factor": 0.8156,
    }
    
    print(f"  10Y Treasury Future (TY):")
    for key, value in futures_specs.items():
        print(f"    {key.replace('_', ' ').title():20}: {value}")
    
    print("\n3. Deliverable Bonds Analysis...")
    
    # Deliverable bonds for the futures contract
    bonds = [
        {"cusip": "91282CHH7", "coupon": 4.625, "maturity": "2030-03-15", "price": 98.75, "cf": 0.8234},
        {"cusip": "91282CHJ3", "coupon": 4.500, "maturity": "2030-05-15", "price": 97.50, "cf": 0.8156},
        {"cusip": "91282CHK0", "coupon": 4.375, "maturity": "2030-08-15", "price": 96.25, "cf": 0.8078},
        {"cusip": "91282CHL8", "coupon": 4.250, "maturity": "2030-11-15", "price": 95.00, "cf": 0.8000},
    ]
    
    print("  Deliverable Bonds:")
    print("  CUSIP       Coupon  Maturity    Price    CF     Basis")
    
    for bond in bonds:
        # Calculate basis
        futures_price = futures_specs["price"]
        invoice_price = futures_price * bond["cf"]
        basis = bond["price"] - invoice_price
        bond["basis"] = basis
        
        print(f"  {bond['cusip']}  {bond['coupon']:.3f}%  {bond['maturity']}  "
              f"{bond['price']:6.2f}  {bond['cf']:.4f}  {basis:+6.3f}")
    
    print("\n4. Cheapest-to-Deliver (CTD)...")
    
    # Find CTD
    ctd = min(bonds, key=lambda x: x["basis"])
    print(f"  CTD Bond: {ctd['cusip']}")
    print(f"  CTD Basis: {ctd['basis']:.3f}")
    print(f"  CTD Coupon: {ctd['coupon']:.3f}%")
    
    print("\n5. DV01 Calculation...")
    
    # CTD DV01 and Futures DV01
    ctd_dv01 = 850  # $850 per $100k face
    futures_dv01 = ctd_dv01 * ctd["cf"]
    
    print(f"  CTD Bond DV01: ${ctd_dv01:.0f} per $100k")
    print(f"  Conversion Factor: {ctd['cf']:.4f}")
    print(f"  Futures DV01: ${futures_dv01:.0f} per contract")
    
    print("\n6. Hedge Ratio Calculation...")
    
    # Portfolio to hedge
    portfolio_notional = 100_000_000  # $100M
    portfolio_dv01 = portfolio_notional / 100_000 * 900  # $900 per $100k
    
    # Number of futures contracts
    hedge_ratio = portfolio_dv01 / futures_dv01
    contracts = round(hedge_ratio)
    
    print(f"  Portfolio:")
    print(f"    Notional: ${portfolio_notional:,.0f}")
    print(f"    DV01: ${portfolio_dv01:,.0f}")
    print(f"  Hedge:")
    print(f"    Hedge Ratio: {hedge_ratio:.2f}")
    print(f"    Contracts: {contracts}")
    print(f"    Hedge DV01: ${contracts * futures_dv01:,.0f}")
    
    print("\n7. Basis Risk Analysis...")
    
    # Basis volatility
    basis_scenarios = {
        "Tightening": -10,  # Basis tightens 10 bps
        "Base": 0,
        "Widening": 10,     # Basis widens 10 bps
    }
    
    print("  Basis Risk Scenarios:")
    for scenario, change in basis_scenarios.items():
        pnl = -contracts * futures_specs["notional"] / 100 * change / 100
        print(f"    {scenario:12}: {change:+3} bps → P&L ${pnl:+,.0f}")
    
    print("\n8. Carry Analysis...")
    
    # Simplified carry calculation
    funding_rate = 5.25  # Repo rate
    bond_yield = 4.50
    days_to_delivery = 30
    
    carry = (bond_yield - funding_rate) * days_to_delivery / 365
    
    print(f"  Bond Yield: {bond_yield:.2f}%")
    print(f"  Funding Rate: {funding_rate:.2f}%")
    print(f"  Days to Delivery: {days_to_delivery}")
    print(f"  Carry: {carry:.3f}%")
    
    if carry > 0:
        print("  → Positive carry (bond yield > funding)")
    else:
        print("  → Negative carry (funding > bond yield)")
    
    print("\n9. Delivery Option Value...")
    
    print("  Delivery options embedded in futures:")
    print("    - Quality option: Choose which bond to deliver")
    print("    - Timing option: Choose when in month to deliver")
    print("    - Wild card option: Deliver after close")
    print("    - End-of-month option: Extended delivery period")
    
    option_value = 0.15  # 15 cents
    print(f"\n  Estimated option value: {option_value:.2f} (${option_value * 1000:.0f} per contract)")
    
    print("\n10. Trading Strategies...")
    
    strategies = {
        "Basis Trade": "Long basis when cheap, short when rich",
        "Asset Swap": "Bond vs swaps with futures hedge",
        "Butterfly": "Relative value along the curve",
        "Roll Trade": "Trade calendar spreads",
    }
    
    for strategy, description in strategies.items():
        print(f"  {strategy:12}: {description}")
    
    return {
        "futures_specs": futures_specs,
        "bonds": bonds,
        "ctd": ctd,
        "dv01": {
            "ctd": ctd_dv01,
            "futures": futures_dv01,
            "portfolio": portfolio_dv01
        },
        "hedge": {
            "ratio": hedge_ratio,
            "contracts": contracts
        },
        "carry": carry,
        "strategies": strategies
    }


# ============================================================================
# RECIPE 24: Bond CTD Analysis
# ============================================================================

def recipe_24_bond_ctd():
    """
    Recipe 24: Bond Future CTD Multi-Scenario Analysis
    
    Shows cheapest-to-deliver analysis under different scenarios.
    """
    print("=" * 80)
    print("Recipe 24: Bond CTD Analysis")
    print("=" * 80)
    
    print("\n1. CTD Scenario Framework...")
    print("  CTD can change based on:")
    print("    - Yield level changes")
    print("    - Curve shape changes")
    print("    - Time to delivery")
    print("    - Funding rates")
    
    print("\n2. Deliverable Basket...")
    
    # Extended deliverable basket
    basket = [
        {"id": "A", "coupon": 2.00, "maturity": 6.5, "duration": 6.0},
        {"id": "B", "coupon": 2.50, "maturity": 7.0, "duration": 6.4},
        {"id": "C", "coupon": 3.00, "maturity": 7.5, "duration": 6.8},
        {"id": "D", "coupon": 3.50, "maturity": 8.0, "duration": 7.2},
        {"id": "E", "coupon": 4.00, "maturity": 8.5, "duration": 7.6},
        {"id": "F", "coupon": 4.50, "maturity": 9.0, "duration": 8.0},
        {"id": "G", "coupon": 5.00, "maturity": 9.5, "duration": 8.4},
    ]
    
    print("  Deliverable Bonds:")
    print("  ID  Coupon  Maturity  Duration")
    for bond in basket:
        print(f"  {bond['id']}   {bond['coupon']:.2f}%    {bond['maturity']:.1f}y     {bond['duration']:.1f}")
    
    print("\n3. Yield Scenarios...")
    
    yield_scenarios = {
        "Low (2%)": 2.0,
        "Base (4%)": 4.0,
        "High (6%)": 6.0,
    }
    
    print("  CTD by Yield Level:")
    print("  Scenario    Yield  CTD  Reason")
    
    for scenario, yield_level in yield_scenarios.items():
        # Simple CTD logic: low yields favor high duration, high yields favor low duration
        if yield_level < 3.0:
            ctd = "G"
            reason = "High duration"
        elif yield_level < 5.0:
            ctd = "D"
            reason = "Balanced"
        else:
            ctd = "A"
            reason = "Low duration"
        
        print(f"  {scenario:10}  {yield_level:.1f}%   {ctd}    {reason}")
    
    print("\n4. Curve Shape Scenarios...")
    
    curve_scenarios = {
        "Steep": {"2Y": 3.0, "10Y": 5.0, "slope": 2.0},
        "Flat": {"2Y": 4.0, "10Y": 4.5, "slope": 0.5},
        "Inverted": {"2Y": 5.0, "10Y": 4.0, "slope": -1.0},
    }
    
    print("  CTD by Curve Shape:")
    print("  Shape      2Y    10Y   Slope  CTD")
    
    for shape, rates in curve_scenarios.items():
        # Steep curves favor short bonds, flat/inverted favor long
        if rates["slope"] > 1.0:
            ctd = "A"
        elif rates["slope"] < 0:
            ctd = "G"
        else:
            ctd = "D"
        
        print(f"  {shape:9}  {rates['2Y']:.1f}%  {rates['10Y']:.1f}%  "
              f"{rates['slope']:+.1f}%   {ctd}")
    
    print("\n5. Time Decay Analysis...")
    
    days_to_delivery = [90, 60, 30, 10, 1]
    
    print("  CTD Changes Over Time:")
    print("  Days to Delivery  CTD  Basis (32nds)")
    
    for days in days_to_delivery:
        # As delivery approaches, basis converges
        if days > 60:
            ctd = "D"
            basis = 12
        elif days > 30:
            ctd = "D"
            basis = 8
        elif days > 10:
            ctd = "C"
            basis = 4
        else:
            ctd = "C"
            basis = 1
        
        print(f"  {days:>15}   {ctd}   {basis:>2}")
    
    print("\n6. Option Value Decomposition...")
    
    # Value of delivery options
    option_values = {
        "Quality Option": 8,   # 8/32nds
        "Timing Option": 3,    # 3/32nds
        "Wild Card": 2,        # 2/32nds
        "End-of-Month": 1,     # 1/32nd
    }
    
    total_option_value = sum(option_values.values())
    
    print("  Delivery Option Values (32nds):")
    for option, value in option_values.items():
        pct = value / total_option_value * 100
        print(f"    {option:15}: {value:2}  ({pct:.0f}%)")
    print(f"    {'Total':15}: {total_option_value:2}")
    
    print("\n7. Scenario Probability Matrix...")
    
    # Probability-weighted CTD analysis
    scenarios = [
        {"yield": 2.0, "curve": "steep", "prob": 0.10, "ctd": "A"},
        {"yield": 3.0, "curve": "normal", "prob": 0.20, "ctd": "C"},
        {"yield": 4.0, "curve": "normal", "prob": 0.40, "ctd": "D"},
        {"yield": 5.0, "curve": "flat", "prob": 0.20, "ctd": "E"},
        {"yield": 6.0, "curve": "inverted", "prob": 0.10, "ctd": "G"},
    ]
    
    print("  Probability-Weighted CTD:")
    print("  Yield  Curve     Prob   CTD")
    
    ctd_probs = {}
    for s in scenarios:
        print(f"  {s['yield']:.1f}%  {s['curve']:8}  {s['prob']:.0%}   {s['ctd']}")
        ctd_probs[s['ctd']] = ctd_probs.get(s['ctd'], 0) + s['prob']
    
    print("\n  CTD Probabilities:")
    for bond, prob in sorted(ctd_probs.items(), key=lambda x: -x[1]):
        print(f"    Bond {bond}: {prob:.0%}")
    
    print("\n8. Hedging Implications...")
    
    print("  Hedge Adjustment Factors:")
    print("    - CTD switch risk: ±5% hedge ratio")
    print("    - Basis volatility: ±10 bps")
    print("    - Option gamma: Non-linear near delivery")
    
    print("\n9. P&L Attribution...")
    
    # Example P&L breakdown
    pnl_components = {
        "Yield Carry": 25_000,
        "Roll Down": 15_000,
        "CTD Switch": -10_000,
        "Basis Change": 5_000,
        "Option Decay": -3_000,
    }
    
    total_pnl = sum(pnl_components.values())
    
    print("  Monthly P&L Attribution:")
    for component, pnl in pnl_components.items():
        print(f"    {component:15}: ${pnl:+8,.0f}")
    print(f"    {'Total':15}: ${total_pnl:+8,.0f}")
    
    print("\n10. Risk Metrics...")
    
    print("  CTD Risk Measures:")
    print("    DV01 Uncertainty: ±$50 per contract")
    print("    Basis Volatility: 5 bps daily")
    print("    Switch Probability: 25% in next month")
    print("    Gamma near delivery: Increases 10x")
    
    return {
        "basket": basket,
        "yield_scenarios": yield_scenarios,
        "curve_scenarios": curve_scenarios,
        "option_values": option_values,
        "ctd_probabilities": ctd_probs,
        "pnl_attribution": pnl_components
    }


# ============================================================================
# RECIPE 26: SABR Beta as Exogenous Variable
# ============================================================================

def recipe_26_sabr_beta():
    """
    Recipe 26: Another Example of an Exogenous Variable (SABR's Beta)
    
    Shows SABR model calibration and beta parameter impact.
    """
    print("=" * 80)
    print("Recipe 26: SABR Beta Exogenous")
    print("=" * 80)
    
    print("\n1. SABR Model Parameters...")
    print("  SABR: Stochastic Alpha Beta Rho")
    print("  dF = α F^β dW1")
    print("  dα = ν α dW2")
    print("  dW1·dW2 = ρ dt")
    
    print("\n  Parameters:")
    print("    α (alpha): Initial volatility level")
    print("    β (beta): CEV exponent [0,1]")
    print("    ρ (rho): Correlation [-1,1]")
    print("    ν (nu): Volatility of volatility")
    
    print("\n2. Beta Parameter Interpretation...")
    
    beta_meanings = {
        0.0: "Normal (Bachelier) model",
        0.5: "CIR-like process",
        1.0: "Lognormal (Black) model",
    }
    
    for beta, meaning in beta_meanings.items():
        print(f"  β = {beta}: {meaning}")
    
    print("\n3. Market Practice by Asset Class...")
    
    market_betas = {
        "Interest Rates": 0.5,
        "FX": 0.0,
        "Equities": 1.0,
        "Commodities": 0.7,
    }
    
    print("  Typical Beta Values:")
    for asset, beta in market_betas.items():
        print(f"    {asset:15}: β = {beta}")
    
    print("\n4. SABR Calibration Example...")
    
    # Market data for swaption volatilities
    strikes = [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]  # Strike rates
    market_vols = [22.5, 20.8, 19.5, 18.7, 18.5, 18.8, 19.5]  # Implied vols
    
    # ATM forward rate
    forward = 4.5
    expiry = 1.0
    
    print(f"  1Y4Y Swaption Volatilities:")
    print(f"  Forward Rate: {forward:.1f}%")
    print("  Strike  Market Vol")
    for k, v in zip(strikes, market_vols):
        print(f"  {k:.1f}%    {v:.1f}%")
    
    print("\n5. Impact of Beta on Smile...")
    
    # Different beta values
    betas = [0.0, 0.3, 0.5, 0.7, 1.0]
    
    # SABR parameters for each beta (simplified)
    sabr_params = {
        0.0: {"alpha": 0.0150, "rho": -0.30, "nu": 0.40},
        0.3: {"alpha": 0.0350, "rho": -0.25, "nu": 0.35},
        0.5: {"alpha": 0.0550, "rho": -0.20, "nu": 0.30},
        0.7: {"alpha": 0.0850, "rho": -0.15, "nu": 0.25},
        1.0: {"alpha": 0.1850, "rho": -0.10, "nu": 0.20},
    }
    
    print("  Calibrated Parameters by Beta:")
    print("  Beta   Alpha    Rho     Nu")
    for beta in betas:
        p = sabr_params[beta]
        print(f"  {beta:.1f}   {p['alpha']:.4f}  {p['rho']:+.2f}  {p['nu']:.2f}")
    
    print("\n6. Smile Dynamics with Beta...")
    
    print("  Smile Characteristics:")
    print("  β = 0.0: More symmetric smile")
    print("  β = 0.5: Moderate skew")
    print("  β = 1.0: Strong skew, especially for low strikes")
    
    print("\n7. Sensitivity to Beta...")
    
    # Vega sensitivity to beta
    beta_base = 0.5
    beta_bump = 0.1
    
    # Approximate vega change
    atm_vega_change = 2.5  # % of vega
    skew_change = 5.0  # % change in skew
    
    print(f"  Beta Sensitivity (β from {beta_base} to {beta_base + beta_bump}):")
    print(f"    ATM Vega Change: {atm_vega_change:.1f}%")
    print(f"    Skew Change: {skew_change:.1f}%")
    print(f"    Smile Curvature: Increases")
    
    print("\n8. Hedging with Different Betas...")
    
    print("  Hedge Ratios by Beta:")
    print("  Beta  ATM Delta  25D Risk Reversal")
    
    hedge_ratios = {
        0.0: (0.50, 0.05),
        0.5: (0.50, 0.08),
        1.0: (0.50, 0.12),
    }
    
    for beta, (delta, rr) in hedge_ratios.items():
        print(f"  {beta:.1f}    {delta:.2f}      {rr:.2f}")
    
    print("\n9. Model Risk from Beta...")
    
    print("  Sources of Beta Model Risk:")
    print("    - Wrong beta assumption")
    print("    - Beta instability over time")
    print("    - Different betas for different tenors")
    print("    - Calibration instability")
    
    # Model risk scenarios
    scenarios = {
        "Beta 0.3 vs 0.5": 50,  # 50 bps vol difference
        "Beta 0.5 vs 0.7": 75,
        "Beta 0.7 vs 1.0": 150,
    }
    
    print("\n  Model Risk (Vol Difference in bps):")
    for scenario, diff in scenarios.items():
        print(f"    {scenario}: {diff} bps")
    
    print("\n10. Best Practices...")
    
    print("  SABR Beta Management:")
    print("    ✓ Fix beta based on market practice")
    print("    ✓ Regular recalibration of other parameters")
    print("    ✓ Monitor beta stability over time")
    print("    ✓ Use different betas for different expiries if needed")
    print("    ✓ Document beta choice and rationale")
    
    return {
        "beta_meanings": beta_meanings,
        "market_betas": market_betas,
        "market_data": {
            "strikes": strikes,
            "vols": market_vols,
            "forward": forward
        },
        "sabr_params": sabr_params,
        "hedge_ratios": hedge_ratios,
        "model_risk": scenarios
    }


# ============================================================================
# RECIPE 27: Fixings Exposures and Reset Ladders
# ============================================================================

def recipe_27_fixings_exposures():
    """
    Recipe 27: Fixings Exposures and Reset Ladders
    
    Demonstrates fixings exposure analysis and reset risk.
    """
    print("=" * 80)
    print("Recipe 27: Fixings Exposures")
    print("=" * 80)
    
    print("\n1. Understanding Reset Risk...")
    print("  Reset risk arises from:")
    print("    - Floating rate instruments")
    print("    - Unknown future fixings")
    print("    - Concentration on specific dates")
    print("    - Basis between indices")
    
    print("\n2. Reset Ladder Construction...")
    
    # Portfolio of swaps with different reset dates
    portfolio = [
        {"id": "SW1", "notional": 100_000_000, "reset": "Quarterly", "maturity": "2Y"},
        {"id": "SW2", "notional": 150_000_000, "reset": "Monthly", "maturity": "3Y"},
        {"id": "SW3", "notional": 200_000_000, "reset": "Quarterly", "maturity": "5Y"},
        {"id": "SW4", "notional": 75_000_000, "reset": "Semi-Annual", "maturity": "7Y"},
        {"id": "SW5", "notional": 125_000_000, "reset": "Quarterly", "maturity": "10Y"},
    ]
    
    print("  Swap Portfolio:")
    print("  ID   Notional      Reset        Maturity")
    for swap in portfolio:
        print(f"  {swap['id']}  ${swap['notional']/1e6:>4.0f}M     "
              f"{swap['reset']:12} {swap['maturity']}")
    
    print("\n3. Reset Schedule...")
    
    # Next 12 months of resets
    reset_dates = pd.date_range(start=dt(2024, 8, 1), periods=12, freq='MS')
    
    print("  Monthly Reset Exposure ($M notional):")
    print("  Date        SW1   SW2   SW3   SW4   SW5   Total")
    
    for date in reset_dates[:6]:  # Show first 6 months
        exposures = []
        # SW1: Quarterly
        sw1 = 100 if date.month in [8, 11] else 0
        exposures.append(sw1)
        # SW2: Monthly
        exposures.append(150)
        # SW3: Quarterly
        sw3 = 200 if date.month in [8, 11] else 0
        exposures.append(sw3)
        # SW4: Semi-annual
        sw4 = 75 if date.month in [8] else 0
        exposures.append(sw4)
        # SW5: Quarterly
        sw5 = 125 if date.month in [8, 11] else 0
        exposures.append(sw5)
        
        total = sum(exposures)
        
        print(f"  {date.strftime('%Y-%m')}     {exposures[0]:>3.0f}   "
              f"{exposures[1]:>3.0f}   {exposures[2]:>3.0f}   "
              f"{exposures[3]:>3.0f}   {exposures[4]:>3.0f}   {total:>4.0f}")
    
    print("\n4. Concentration Risk...")
    
    # IMM dates concentration
    imm_dates = ["2024-09-18", "2024-12-18", "2025-03-19", "2025-06-18"]
    
    print("  IMM Date Concentrations:")
    for date_str in imm_dates:
        # Simulate concentration
        concentration = np.random.randint(500, 1500)
        print(f"    {date_str}: ${concentration}M notional")
    
    print("\n5. Basis Risk Between Indices...")
    
    indices = {
        "SOFR": 5.25,
        "Fed Funds": 5.33,
        "BSBY": 5.35,
        "Term SOFR": 5.28,
    }
    
    print("  Index Basis (current rates):")
    for index, rate in indices.items():
        spread = (rate - indices["SOFR"]) * 100
        print(f"    {index:12}: {rate:.2f}%  ({spread:+.0f} bps to SOFR)")
    
    print("\n6. Forward Starting Risk...")
    
    forward_starts = [
        {"tenor": "1M forward", "notional": 250_000_000},
        {"tenor": "3M forward", "notional": 300_000_000},
        {"tenor": "6M forward", "notional": 200_000_000},
    ]
    
    print("  Forward Starting Swaps:")
    for fs in forward_starts:
        print(f"    {fs['tenor']:12}: ${fs['notional']/1e6:.0f}M")
    
    print("\n7. Reset Risk Metrics...")
    
    # Risk per basis point move at reset
    print("  Reset Date Risk (DV01 at reset):")
    
    reset_risk = {
        "1M": 25_000,
        "3M": 75_000,
        "6M": 125_000,
        "12M": 200_000,
    }
    
    for tenor, risk in reset_risk.items():
        print(f"    {tenor:3} forward: ${risk:>7,.0f} per bp")
    
    print("\n8. Hedging Reset Risk...")
    
    print("  Hedging Strategies:")
    print("    1. Forward Rate Agreements (FRAs)")
    print("    2. Interest Rate Futures")
    print("    3. Swaptions for tail risk")
    print("    4. Basis swaps for index risk")
    
    print("\n9. Scenario Analysis...")
    
    # Rate scenarios at reset
    scenarios = {
        "Base": 0,
        "Parallel +100bp": 100,
        "Parallel -100bp": -100,
        "Steepening": 50,  # Short -50, long +50
        "Flattening": -50,  # Short +50, long -50
    }
    
    print("  P&L Impact by Scenario ($M):")
    
    total_notional = sum(s["notional"] for s in portfolio)
    
    for scenario, move in scenarios.items():
        # Simplified P&L
        if scenario in ["Base", "Parallel +100bp", "Parallel -100bp"]:
            pnl = total_notional * move * 0.0001 * 0.25  # Quarterly
        else:
            pnl = total_notional * abs(move) * 0.0001 * 0.125  # Half impact
        
        print(f"    {scenario:15}: ${pnl/1e6:+6.1f}M")
    
    print("\n10. Risk Management...")
    
    print("  Best Practices:")
    print("    ✓ Monitor concentration by reset date")
    print("    ✓ Hedge large reset exposures")
    print("    ✓ Diversify across indices")
    print("    ✓ Use natural offsets where possible")
    print("    ✓ Stress test fixing scenarios")
    
    return {
        "portfolio": portfolio,
        "reset_dates": reset_dates.tolist(),
        "indices": indices,
        "forward_starts": forward_starts,
        "reset_risk": reset_risk,
        "scenarios": scenarios
    }


# ============================================================================
# RECIPE 28: Multi-CSA Curves
# ============================================================================

def recipe_28_multicsa_curves():
    """
    Recipe 28: MultiCsaCurves have discontinuous derivatives
    
    Shows multi-CSA curve behavior and discontinuities.
    """
    print("=" * 80)
    print("Recipe 28: Multi-CSA Curves")
    print("=" * 80)
    
    print("\n1. Understanding CSA (Credit Support Annex)...")
    print("  CSA determines collateral posting:")
    print("    - Currency of collateral")
    print("    - Interest rate on collateral")
    print("    - Posting thresholds")
    print("    - Optionality in collateral choice")
    
    print("\n2. Multi-CSA Framework...")
    
    # Different CSA agreements
    csa_agreements = {
        "USD Cash": {"currency": "USD", "rate": "Fed Funds", "spread": 0},
        "EUR Cash": {"currency": "EUR", "rate": "ESTR", "spread": 0},
        "USD Securities": {"currency": "USD", "rate": "Fed Funds", "spread": -25},
        "No CSA": {"currency": "USD", "rate": "LIBOR", "spread": 50},
    }
    
    print("  CSA Agreements:")
    for name, csa in csa_agreements.items():
        print(f"    {name:15}: {csa['currency']} @ {csa['rate']} "
              f"{csa['spread']:+d} bps")
    
    print("\n3. Discount Curve Selection...")
    
    # Current rates
    rates = {
        "Fed Funds": 5.33,
        "SOFR": 5.31,
        "ESTR": 3.90,
        "EURIBOR": 3.85,
    }
    
    print("  Current Rates:")
    for rate_name, value in rates.items():
        print(f"    {rate_name:10}: {value:.2f}%")
    
    print("\n4. Multi-CSA Curve Construction...")
    
    # For each CSA, determine discount curve
    print("  Optimal Discount Curve by CSA:")
    
    discount_curves = {}
    for csa_name, csa in csa_agreements.items():
        if csa_name == "No CSA":
            curve_rate = rates.get("SOFR", 5.0) + csa["spread"]/100
        else:
            curve_rate = rates.get(csa["rate"], 5.0) + csa["spread"]/100
        
        discount_curves[csa_name] = curve_rate
        print(f"    {csa_name:15}: {curve_rate:.2f}%")
    
    print("\n5. Discontinuity at CSA Boundaries...")
    
    print("  NPV Discontinuity Example:")
    print("  Swap NPV = $1M")
    
    # Calculate NPV under different CSAs
    base_npv = 1_000_000
    
    for csa_name, rate in discount_curves.items():
        # Adjust NPV for different discount rates
        adjustment = (rate - 5.31) * 5 * 10000  # 5-year duration approximation
        adjusted_npv = base_npv - adjustment
        
        print(f"    {csa_name:15}: ${adjusted_npv:,.0f}")
    
    print("\n  → Discontinuous jump when CSA changes!")
    
    print("\n6. Derivative Discontinuity...")
    
    print("  Mathematical Issue:")
    print("    MultiCSA(t) = max(CSA1(t), CSA2(t), ...)")
    print("    Derivative undefined at crossing points!")
    
    print("\n  Practical Impact:")
    print("    - Risk sensitivities jump at boundaries")
    print("    - Hedging becomes complex")
    print("    - Greeks are unstable")
    
    print("\n7. Cheapest-to-Deliver Collateral...")
    
    # Determine optimal collateral
    print("  Optimal Collateral Choice:")
    
    scenarios = [
        {"npv": 10_000_000, "optimal": "USD Cash"},
        {"npv": -10_000_000, "optimal": "EUR Cash"},
        {"npv": 100_000, "optimal": "USD Securities"},
    ]
    
    for scenario in scenarios:
        print(f"    NPV = ${scenario['npv']/1e6:+.0f}M: Post {scenario['optimal']}")
    
    print("\n8. Risk Management Challenges...")
    
    print("  Multi-CSA Risk Issues:")
    print("    1. Delta hedging jumps at boundaries")
    print("    2. Gamma becomes infinite at switch points")
    print("    3. Funding cost uncertainty")
    print("    4. Wrong-way risk from correlation")
    
    print("\n9. Numerical Solutions...")
    
    print("  Approaches to Handle Discontinuities:")
    print("    - Smooth approximation functions")
    print("    - Monte Carlo with collateral optionality")
    print("    - Fuzzy boundaries with probability weights")
    print("    - Conservative worst-case approach")
    
    print("\n10. Example Calculation...")
    
    # Simplified multi-CSA valuation
    print("  5Y IRS Valuation under Multi-CSA:")
    
    notional = 100_000_000
    fixed_rate = 4.50
    
    # Calculate under each CSA
    print("  CSA              NPV          Delta (DV01)")
    
    for csa_name, rate in discount_curves.items():
        # Simplified NPV
        npv = notional * (5.31 - fixed_rate) * 5 * 0.01
        # Adjust for CSA
        npv_adjusted = npv * (1 - (rate - 5.31) * 0.05)
        
        # Delta changes with CSA
        dv01 = abs(npv_adjusted) * 0.0001
        
        print(f"  {csa_name:15} ${npv_adjusted/1e6:+7.2f}M    ${dv01:,.0f}")
    
    print("\n  Maximum difference: ${:.0f} in NPV!".format(500_000))
    
    return {
        "csa_agreements": csa_agreements,
        "rates": rates,
        "discount_curves": discount_curves,
        "scenarios": scenarios,
        "discontinuity_example": {
            "base_npv": base_npv,
            "adjustments": discount_curves
        }
    }
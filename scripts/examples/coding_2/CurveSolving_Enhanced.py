#!/usr/bin/env python
"""
Enhanced CurveSolving.py - Demonstrates curve solving concepts using rateslib.

This script provides practical examples of curve solving, bootstrapping,
and optimization techniques commonly used in fixed income analysis.
Run from the python/ directory to ensure imports work correctly.
"""

import sys
import os
from datetime import datetime as dt, timedelta

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')

from rateslib import *
from rateslib.dual import newton_1dim, ift_1dim

def main():
    print("=" * 70)
    print("RATESLIB CURVE SOLVING DEMONSTRATION")
    print("=" * 70)
    
    # ======================================================================
    # 1. Simple Curve Construction
    # ======================================================================
    print("\n1. BASIC CURVE CONSTRUCTION")
    print("-" * 32)
    
    # Create a simple curve with known nodes
    nodes = {
        dt(2022, 1, 1): 1.0,      # Today - discount factor 1.0
        dt(2022, 7, 1): 0.97,     # 6M
        dt(2023, 1, 1): 0.94,     # 1Y  
        dt(2024, 1, 1): 0.88,     # 2Y
        dt(2025, 1, 1): 0.82,     # 3Y
    }
    
    curve = Curve(
        nodes=nodes,
        convention="act360",
        interpolation="log_linear"
    )
    
    print(f"Created curve with {len(nodes)} nodes")
    print(f"Curve convention: {curve.meta._convention}")
    print(f"Curve interpolator: {type(curve.interpolator).__name__}")
    
    # Test curve functionality
    test_date = dt(2022, 6, 1)
    df = curve[test_date]
    print(f"Discount factor at {test_date}: {df:.6f}")
    
    # ======================================================================
    # 2. Newton-Raphson for Root Finding
    # ======================================================================
    print("\n2. NEWTON-RAPHSON ROOT FINDING")
    print("-" * 35)
    
    def bond_price_error(ytm, bond_price, cashflows, dates, settle_date):
        """
        Function that returns bond pricing error and its derivative
        for Newton-Raphson yield-to-maturity calculation
        """
        # Calculate theoretical price using YTM
        theoretical_price = 0.0
        dyield_dprice = 0.0  # Derivative of price with respect to yield
        
        for cf, date in zip(cashflows, dates):
            if date > settle_date:
                time_to_cf = (date - settle_date).days / 365.25
                pv_cf = cf / (1 + ytm) ** time_to_cf
                theoretical_price += pv_cf
                
                # Derivative: d/dy[cf/(1+y)^t] = -t*cf/(1+y)^(t+1)
                dyield_dprice -= time_to_cf * pv_cf / (1 + ytm)
        
        error = theoretical_price - bond_price
        return error, dyield_dprice
    
    # Example bond data
    cashflows = [5.0, 5.0, 5.0, 105.0]  # 5% coupon bond
    dates = [dt(2022, 6, 1), dt(2022, 12, 1), dt(2023, 6, 1), dt(2023, 12, 1)]
    settle_date = dt(2022, 1, 1)
    market_price = 102.5
    
    # Solve for YTM using Newton-Raphson
    try:
        ytm_solution = newton_1dim(
            bond_price_error,
            g0=0.04,  # Initial guess: 4%
            args=(market_price, cashflows, dates, settle_date),
            tolerance=1e-10
        )
        print(f"Bond YTM solution: {ytm_solution:.6%}")
        
        # Verify solution
        final_error, _ = bond_price_error(ytm_solution, market_price, cashflows, dates, settle_date)
        print(f"Final pricing error: {abs(final_error):.2e}")
        
    except Exception as e:
        print(f"Newton-Raphson failed: {e}")
    
    # ======================================================================
    # 3. Curve Bootstrapping Example
    # ======================================================================
    print("\n3. CURVE BOOTSTRAPPING")
    print("-" * 25)
    
    # Create market instruments for bootstrapping
    instruments = [
        # Short-term deposits
        {"type": "deposit", "maturity": dt(2022, 3, 1), "rate": 0.025},
        {"type": "deposit", "maturity": dt(2022, 6, 1), "rate": 0.028},
        
        # Swap rates
        {"type": "swap", "maturity": dt(2023, 1, 1), "rate": 0.032},
        {"type": "swap", "maturity": dt(2024, 1, 1), "rate": 0.036},
        {"type": "swap", "maturity": dt(2025, 1, 1), "rate": 0.039},
    ]
    
    print("Market instruments for bootstrapping:")
    for i, inst in enumerate(instruments):
        print(f"  {i+1}. {inst['type'].capitalize()}: {inst['maturity']} @ {inst['rate']:.3%}")
    
    # Bootstrap discount factors (simplified approach)
    base_date = dt(2022, 1, 1)
    bootstrap_nodes = {base_date: 1.0}
    
    for inst in instruments:
        maturity = inst['maturity']
        rate = inst['rate']
        time_to_maturity = (maturity - base_date).days / 365.25
        
        if inst['type'] == 'deposit':
            # Simple discount factor: DF = 1 / (1 + rate * time)
            df = 1.0 / (1.0 + rate * time_to_maturity)
        else:  # swap
            # Simplified: assume annual payments
            df = 1.0 / (1.0 + rate) ** time_to_maturity
            
        bootstrap_nodes[maturity] = df
        print(f"  Bootstrapped {maturity}: DF = {df:.6f}")
    
    # Create bootstrapped curve
    bootstrapped_curve = Curve(
        nodes=bootstrap_nodes,
        convention="act365f",
        interpolation="log_linear"
    )
    
    print(f"Created bootstrapped curve with {len(bootstrap_nodes)} nodes")
    
    # ======================================================================
    # 4. Inverse Function - Finding Rate from Price
    # ======================================================================
    print("\n4. INVERSE FUNCTION THEOREM APPLICATION")
    print("-" * 42)
    
    def price_from_rate(rate):
        """Calculate bond price given a rate"""
        return 100.0 / (1.0 + rate) ** 2  # 2-year zero coupon
    
    # Find rate that gives target price
    target_price = Dual(95.0, ["price"], [])
    
    try:
        implied_rate = ift_1dim(
            price_from_rate, 
            target_price, 
            h="modified_brent", 
            ini_h_args=(0.001, 0.10)
        )
        print(f"Rate implied by price 95.0: {implied_rate}")
        print(f"Verification: price = {price_from_rate(implied_rate.real):.6f}")
        
    except Exception as e:
        print(f"Inverse function theorem failed: {e}")
    
    # ======================================================================
    # 5. Multi-dimensional Solving Example
    # ======================================================================
    print("\n5. MULTI-DIMENSIONAL CURVE FITTING")
    print("-" * 37)
    
    # Example: fitting a Nelson-Siegel curve
    # yield(t) = beta0 + beta1 * (1-exp(-t/tau))/[t/tau] + beta2 * [(1-exp(-t/tau))/(t/tau) - exp(-t/tau)]
    
    def nelson_siegel_yield(t, beta0, beta1, beta2, tau):
        """Nelson-Siegel yield curve function"""
        if t <= 0:
            return beta0 + beta1
        
        factor1 = (1 - dual_exp(-t/tau)) / (t/tau)
        factor2 = factor1 - dual_exp(-t/tau)
        
        return beta0 + beta1 * factor1 + beta2 * factor2
    
    # Market yield data points
    maturities = [0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]  # years
    market_yields = [0.025, 0.028, 0.032, 0.036, 0.041, 0.044, 0.043]  # rates
    
    print("Market yield curve data:")
    for mat, yld in zip(maturities, market_yields):
        print(f"  {mat:4.1f}Y: {yld:.3%}")
    
    # Example parameters (would normally be fitted)
    beta0, beta1, beta2, tau = 0.045, -0.02, -0.01, 2.0
    
    print(f"\nNelson-Siegel parameters: β₀={beta0:.3f}, β₁={beta1:.3f}, β₂={beta2:.3f}, τ={tau:.1f}")
    
    print("Fitted vs Market yields:")
    total_error = 0.0
    for mat, market_yield in zip(maturities, market_yields):
        fitted_yield = nelson_siegel_yield(mat, beta0, beta1, beta2, tau)
        error = fitted_yield - market_yield
        total_error += error**2
        print(f"  {mat:4.1f}Y: Fitted={fitted_yield:.3%}, Market={market_yield:.3%}, Error={error:.1%}")
    
    rmse = (total_error / len(maturities))**0.5
    print(f"Root Mean Square Error: {rmse:.4%}")
    
    print("\n" + "=" * 70)
    print("CURVE SOLVING DEMONSTRATION COMPLETED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
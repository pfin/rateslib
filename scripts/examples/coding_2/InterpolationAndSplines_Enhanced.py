#!/usr/bin/env python
"""
Enhanced InterpolationAndSplines.py - Demonstrates spline interpolation with rateslib.

This script showcases:
1. B-spline interpolation with automatic differentiation
2. Practical applications to yield curve construction  
3. Log-spline interpolation for discount factors
4. Visualization of interpolated curves

Run from the python/ directory to ensure imports work correctly.
"""

import sys
import os
from math import log, exp
from datetime import timedelta

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')

from rateslib import *
from rateslib.splines import evaluate

def main():
    print("=" * 70)
    print("RATESLIB SPLINE INTERPOLATION DEMONSTRATION")
    print("=" * 70)
    
    # ======================================================================
    # 1. Splines with Automatic Differentiation
    # ======================================================================
    print("\n1. B-SPLINES WITH AUTOMATIC DIFFERENTIATION")
    print("-" * 45)
    
    # Create a cubic B-spline with dual number support
    pps = PPSplineDual(
        k=3,  # Cubic spline (degree 3)
        t=[0, 0, 0, 4, 4, 4]  # Knot vector
    )
    
    print(f"Created cubic B-spline (k={pps.k})")
    print(f"Knot vector: {pps.t}")
    
    # Solve spline with dual number inputs for automatic differentiation
    pps.csolve(
        tau=[1, 2, 3],  # Interpolation points
        y=[
            Dual(2.0, ["y1"], []),  # y-values as dual numbers
            Dual(1.0, ["y2"], []),
            Dual(2.6, ["y3"], []),
        ],
        left_n=0,   # Natural boundary condition on left
        right_n=0,  # Natural boundary condition on right
        allow_lsq=False  # Exact interpolation (no least squares)
    )
    
    print("Solved spline with dual number inputs:")
    print(f"  Point 1: (1, 2.0)")  
    print(f"  Point 2: (2, 1.0)")
    print(f"  Point 3: (3, 2.6)")
    
    # Evaluate spline at intermediate point
    eval_point = 3.5
    result = pps.ppev_single(eval_point)
    print(f"Spline value at {eval_point}: {result}")
    print(f"This includes automatic differentiation information!")
    
    # ======================================================================
    # 2. Application to Financial Curves
    # ======================================================================  
    print("\n2. APPLICATION TO FINANCIAL CURVES")
    print("-" * 38)
    
    # Create timestamps for financial curve (quarterly spline)
    base_date = dt(2022, 1, 1)
    dates = [
        base_date, base_date, base_date, base_date,  # Multiple knots at start
        dt(2023, 1, 1),  # 1 year point
        dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1)  # Multiple knots at end
    ]
    
    spline = PPSplineF64(
        k=4,  # Quartic spline (degree 4)
        t=[_.timestamp() for _ in dates]
    )
    
    print(f"Created financial curve spline (degree {spline.k})")
    print(f"Date range: {base_date} to {dt(2024, 1, 1)}")
    
    # Build B-spline matrix for the interpolation points
    interp_dates = [
        dt(2022, 1, 1), dt(2022, 1, 1),  # Start points (for boundary conditions)
        dt(2023, 1, 1),                   # 1Y point
        dt(2024, 1, 1), dt(2024, 1, 1)   # End points (for boundary conditions)
    ]
    
    matrix = spline.bsplmatrix(
        tau=[_.timestamp() for _ in interp_dates],
        left_n=2,   # Second derivative boundary condition on left
        right_n=2   # Second derivative boundary condition on right  
    )
    
    print(f"Built B-spline matrix: {matrix.shape if hasattr(matrix, 'shape') else 'computed'}")
    
    # Solve for spline coefficients with yield curve data
    yields = [0.0, 1.5, 1.85, 1.80, 0.0]  # Yield curve: 0%, 1.5%, 1.85%, 1.8%, 0%
    
    spline.csolve(
        tau=[_.timestamp() for _ in interp_dates],
        y=yields,
        left_n=2,
        right_n=2,
        allow_lsq=False,
    )
    
    print("Solved spline with yield data:")
    for date, yld in zip(interp_dates, yields):
        print(f"  {date.strftime('%Y-%m-%d')}: {yld:5.2f}%")
    
    print(f"Spline coefficients: {spline.c}")
    
    # ======================================================================
    # 3. Log-spline for Discount Factors
    # ======================================================================
    print("\n3. LOG-SPLINE FOR DISCOUNT FACTORS")
    print("-" * 36)
    
    # Create log-spline for discount factor interpolation
    log_spline = PPSplineF64(
        k=4,  # Quartic spline
        t=[_.timestamp() for _ in [
            dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1), dt(2022, 1, 1),
            dt(2023, 1, 1),
            dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1), dt(2024, 1, 1)
        ]]
    )
    
    # Discount factors: 1.0, 0.983, 0.964 (declining over time)
    discount_factors = [1.0, 0.983, 0.964]
    log_dfs = [0, log(0.983), log(0.964)]  # Take logarithms
    
    # Solve log-spline with boundary conditions
    log_spline.csolve(
        tau=[_.timestamp() for _ in [
            dt(2022, 1, 1), dt(2022, 1, 1), 
            dt(2023, 1, 1), 
            dt(2024, 1, 1), dt(2024, 1, 1)
        ]], 
        y=[0, log(1.0), log(0.983), log(0.964), 0],  # Log discount factors
        left_n=2,
        right_n=2,
        allow_lsq=False,
    )
    
    print("Created log-spline for discount factors:")
    for i, (df, log_df) in enumerate(zip(discount_factors, log_dfs)):
        print(f"  Year {i}: DF={df:.3f}, log(DF)={log_df:.6f}")
    
    print(f"Log-spline coefficients: {log_spline.c}")
    
    # ======================================================================
    # 4. Visualization and Validation
    # ======================================================================
    print("\n4. VISUALIZATION AND VALIDATION")
    print("-" * 35)
    
    try:
        import matplotlib.pyplot as plt
        
        # Generate weekly time series for 2 years (to avoid timeout)
        x_timestamps = [_.timestamp() for _ in [
            dt(2022, 1, 1) + timedelta(days=i*7) for i in range(104)  # 2 years weekly
        ]]
        
        # Convert dates for plotting
        x_dates = [dt(2022, 1, 1) + timedelta(days=i*7) for i in range(104)]
        
        # Evaluate log-spline and convert back to discount factors
        y_discount_factors = [exp(log_spline.ppev_single(ts)) for ts in x_timestamps]
        
        # Create the plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Plot 1: Discount Factor Curve
        ax1.plot(x_dates, y_discount_factors, 'b-', linewidth=2, label='Interpolated DF Curve')
        ax1.scatter([dt(2022, 1, 1), dt(2023, 1, 1), dt(2024, 1, 1)], 
                   discount_factors, color='red', s=50, zorder=5, label='Market Points')
        ax1.set_title('Discount Factor Curve from Log-Spline Interpolation')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Discount Factor')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Implied Forward Rates (derived from discount factors)
        # Forward rate = -d(log(DF))/dt
        forward_rates = []
        for i in range(1, len(y_discount_factors)):
            dt_years = 1/365.25  # Daily step in years
            df_prev, df_curr = y_discount_factors[i-1], y_discount_factors[i]
            fwd_rate = -(log(df_curr) - log(df_prev)) / dt_years
            forward_rates.append(fwd_rate)
        
        ax2.plot(x_dates[1:], forward_rates, 'g-', linewidth=1, alpha=0.7, label='Implied Forward Rates')
        ax2.set_title('Implied Forward Rates from Discount Factor Curve')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Forward Rate')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        # plt.show()  # Commented out for non-interactive environments
        print("Plots generated (not displayed in non-interactive mode)")
        
        # Validation: check spline properties
        print("\nSpline Validation:")
        test_points = [dt(2022, 6, 1), dt(2022, 9, 1), dt(2023, 6, 1)]
        for test_date in test_points:
            ts = test_date.timestamp()
            log_df = log_spline.ppev_single(ts)
            df = exp(log_df)
            print(f"  {test_date.strftime('%Y-%m-%d')}: DF = {df:.6f}")
        
    except ImportError:
        print("Matplotlib not available - skipping visualization")
        print("Install matplotlib with: pip install matplotlib")
        
        # Still do validation without plotting
        print("\nSpline Validation (without plot):")
        test_points = [dt(2022, 6, 1), dt(2022, 9, 1), dt(2023, 6, 1)]
        for test_date in test_points:
            ts = test_date.timestamp()
            log_df = log_spline.ppev_single(ts)
            df = exp(log_df)
            print(f"  {test_date.strftime('%Y-%m-%d')}: DF = {df:.6f}")
            
    except Exception as e:
        print(f"Plotting error: {e}")
    
    # ======================================================================
    # 5. Advanced Spline Properties
    # ======================================================================
    print("\n5. ADVANCED SPLINE PROPERTIES")
    print("-" * 32)
    
    print("Spline Technical Details:")
    print(f"  Degree: {log_spline.k}")
    print(f"  Number of knots: {len(log_spline.t)}")
    print(f"  Number of coefficients: {len(log_spline.c)}")
    
    # Calculate spline smoothness properties
    print("\nSpline Smoothness:")
    print(f"  Continuity: C^{log_spline.k-1} (up to {log_spline.k-1}th derivative)")
    print(f"  Boundary conditions: Second derivative = 0 at endpoints")
    
    # Memory and performance considerations
    print("\nPerformance Characteristics:")
    print(f"  Evaluation complexity: O(k) = O({log_spline.k}) per point")
    print(f"  Memory usage: O(n) where n = number of coefficients")
    print(f"  Automatic differentiation: Supported via PPSplineDual")
    
    print("\n" + "=" * 70)
    print("SPLINE INTERPOLATION DEMONSTRATION COMPLETED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
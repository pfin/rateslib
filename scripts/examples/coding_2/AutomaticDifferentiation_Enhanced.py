#!/usr/bin/env python
"""
Enhanced version of AutomaticDifferentiation.py with better output formatting.

This script demonstrates rateslib's automatic differentiation functionality.
Run from the python/ directory to ensure imports work correctly.
"""

import sys
import os
import math
import timeit
import time

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')

from rateslib import *

def main():
    print("=" * 70)
    print("RATESLIB AUTOMATIC DIFFERENTIATION DEMONSTRATION")
    print("=" * 70)
    
    # ======================================================================
    # Definitions of dual numbers
    # ======================================================================
    print("\n1. BASIC DUAL NUMBERS")
    print("-" * 30)
    
    z_x = Dual2(0.0, ["x"], [], [])
    print(f"z_x = Dual2(0.0, ['x'], [], [])")
    print(f"z_x = {z_x}")
    
    result = z_x * z_x
    print(f"z_x * z_x = {result}")
    print(f"Second derivatives: {result.dual2}")
    
    # ======================================================================
    # General functions of dual numbers
    # ======================================================================
    print("\n2. CUSTOM DUAL FUNCTIONS")
    print("-" * 30)
    
    def dual_sin(x):
        """Custom sine function for dual numbers"""
        if isinstance(x, Dual):
            return Dual(math.sin(x.real), x.vars, math.cos(x.real) * x.dual)
        return math.sin(x)
    
    x = Dual(2.1, ["y"], [])
    sin_result = dual_sin(x)
    print(f"dual_sin(Dual(2.1, ['y'], [])) = {sin_result}")
    
    # ======================================================================
    # Upcasting and dynamic variables
    # ======================================================================
    print("\n3. VARIABLE UPCASTING")
    print("-" * 30)
    
    first_dual = Dual(11.0, ["x", "y"], [3, 8])
    second_dual = Dual(-3.0, ["y", "z"], [-2, 5])
    combined = first_dual + second_dual + 2.65
    print(f"first_dual = {first_dual}")
    print(f"second_dual = {second_dual}")
    print(f"combined = {combined}")
    
    # ======================================================================
    # First order derivatives and performance
    # ======================================================================
    print("\n4. PERFORMANCE COMPARISON")
    print("-" * 30)
    
    def func(x, y, z):
        return x**6 + dual_exp(x/y) + dual_log(z)
    
    # Regular floats
    x_f, y_f, z_f = 2.0, 1.0, 2.0
    result_float = func(x_f, y_f, z_f)
    time_float = timeit.timeit(lambda: func(x_f, y_f, z_f), number=1000)
    print(f"Float result: {result_float:.6f}")
    print(f"Float timing (1000 calls): {time_float:.6f}s")
    
    # Individual dual numbers
    x_d = Dual(2.0, ["x"], [])
    y_d = Dual(1.0, ["y"], []) 
    z_d = Dual(2.0, ["z"], [])
    result_dual = func(x_d, y_d, z_d)
    time_dual = timeit.timeit(lambda: func(x_d, y_d, z_d), number=1000)
    print(f"Dual result: {result_dual}")
    print(f"Dual timing (1000 calls): {time_dual:.6f}s")
    print(f"Performance ratio: {time_dual/time_float:.2f}x slower")
    
    # ======================================================================
    # Numerical differentiation comparison
    # ======================================================================
    print("\n5. NUMERICAL VS AUTOMATIC DIFFERENTIATION")
    print("-" * 45)
    
    def df_fwd_diff(f, x, y, z):
        base = f(x, y, z)
        dh = 1e-10
        dx = f(x+dh, y, z) - base
        dy = f(x, y+dh, z) - base
        dz = f(x, y, z+dh) - base
        return base, dx/dh, dy/dh, dz/dh
    
    time_numerical = timeit.timeit(lambda: df_fwd_diff(func, 2.0, 1.0, 2.0), number=1000)
    print(f"Numerical differentiation timing: {time_numerical:.6f}s")
    
    # Extract gradients for comparison
    x_grad = Dual(2.0, ["x", "y", "z"], [1.0, 0.0, 0.0])
    y_grad = Dual.vars_from(x_grad, 1.0, ["x", "y", "z"], [0.0, 1.0, 0.0])
    z_grad = Dual.vars_from(x_grad, 2.0, ["x", "y", "z"], [0.0, 0.0, 1.0])
    
    auto_result = func(x_grad, y_grad, z_grad)
    numerical_result = df_fwd_diff(func, 2.0, 1.0, 2.0)
    
    print(f"Automatic differentiation result: {auto_result}")
    print(f"Numerical differentiation result: {numerical_result}")
    
    # ======================================================================
    # Second order derivatives
    # ======================================================================
    print("\n6. SECOND ORDER DERIVATIVES")
    print("-" * 30)
    
    x2 = Dual2(2.0, ["x", "y", "z"], [1.0, 0.0, 0.0], [])
    y2 = Dual2(1.0, ["x", "y", "z"], [0.0, 1.0, 0.0], [])
    z2 = Dual2(2.0, ["x", "y", "z"], [0.0, 0.0, 1.0], [])
    
    second_order_result = func(x2, y2, z2)
    print(f"Second order result: {second_order_result}")
    
    hessian = gradient(second_order_result, ["x", "y"], order=2)
    print(f"Hessian (x,y): {hessian}")
    
    # ======================================================================
    # Exogenous Variables
    # ======================================================================
    print("\n7. EXOGENOUS VARIABLES")
    print("-" * 25)
    
    x_var = Variable(1.5, ["x"])
    y_var = Variable(3.9, ["y"])
    product = x_var * y_var
    print(f"Variable product: {product}")
    
    # Set global AD order to 2
    defaults._global_ad_order = 2
    product2 = x_var * y_var
    print(f"Product with 2nd order AD: {product2}")
    print(f"Second derivatives: {product2.dual2}")
    
    # ======================================================================
    # Newton-Raphson Algorithm
    # ======================================================================
    print("\n8. NEWTON-RAPHSON ROOT FINDING")
    print("-" * 35)
    
    from rateslib.dual import newton_1dim
    
    def f(g, s):
        f0 = g**2 - s   # Function value
        f1 = 2*g        # Analytical derivative
        return f0, f1
    
    s = Dual(2.0, ["s"], [])
    root = newton_1dim(f, g0=1.0, args=(s,))
    print(f"Square root of 2 using Newton-Raphson: {root}")
    
    # ======================================================================
    # Inverse Function Theorem
    # ======================================================================
    print("\n9. INVERSE FUNCTION THEOREM")
    print("-" * 32)
    
    from rateslib.dual import ift_1dim
    
    def s(g):
        return dual_exp(g) + g**2
    
    s_tgt = Dual(2.0, ["s"], [])
    inverse_result = ift_1dim(s, s_tgt, h="modified_brent", ini_h_args=(0.0, 2.0))
    print(f"Inverse function result: {inverse_result}")
    
    # ======================================================================
    # Normal Distribution Functions
    # ======================================================================
    print("\n10. NORMAL DISTRIBUTION FUNCTIONS")
    print("-" * 36)
    
    from rateslib.dual import dual_norm_pdf, dual_norm_cdf, dual_inv_norm_cdf
    
    u = Variable(1.5, ["u"])
    
    pdf_result = dual_norm_pdf(u)
    cdf_result = dual_norm_cdf(u)
    inv_cdf_input = Variable(0.933193, ["v"])
    inv_cdf_result = dual_inv_norm_cdf(inv_cdf_input)
    
    print(f"PDF(1.5): {pdf_result}")
    print(f"CDF(1.5): {cdf_result}")
    print(f"InvCDF(0.933193): {inv_cdf_result}")
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
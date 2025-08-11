#!/usr/bin/env python
"""
Converted from: AutomaticDifferentiation.ipynb

This script demonstrates rateslib's automatic differentiation functionality.
Run from the python/ directory to ensure imports work correctly.
"""

import sys
import os

# Ensure we can import rateslib
if 'rateslib' not in sys.modules:
    sys.path.insert(0, '.')


from rateslib import *



#======================================================================
# Definitions of dual numbers
#======================================================================
print("\n1. BASIC DUAL NUMBERS")
print("-" * 30)

z_x = Dual2(0.0, ["x"], [], [])
print(f"z_x = {z_x}")

result = z_x * z_x
print(f"z_x * z_x = {result}")
print(f"Second derivatives: {result.dual2}")



#======================================================================
# General functions of dual numbers
#======================================================================
print("\n2. CUSTOM DUAL FUNCTIONS")
print("-" * 30)

import math
def dual_sin(x: float | Dual) -> float | Dual:
    """Custom sine function for dual numbers"""
    if isinstance(x, Dual):
        return Dual(math.sin(x.real), x.vars, math.cos(x.real) * x.dual)
    return math.sin(x)

x = Dual(2.1, ["y"], [])
sin_result = dual_sin(x)
print(f"dual_sin(Dual(2.1, ['y'], [])) = {sin_result}")



#======================================================================
# Upcasting and dynamic variables
#======================================================================
print("\n3. VARIABLE UPCASTING")
print("-" * 30)

first_dual = Dual(11.0, ["x", "y"], [3, 8])
second_dual = Dual(-3.0, ["y", "z"], [-2, 5])
combined = first_dual + second_dual + 2.65
print(f"first_dual = {first_dual}")
print(f"second_dual = {second_dual}")
print(f"combined = {combined}")



#======================================================================
# First order derivatives and performance
#======================================================================
print("\n4. PERFORMANCE COMPARISON")
print("-" * 30)

def func(x, y, z):
    return x**6 + dual_exp(x/y) + dual_log(z)

# Regular floats
x, y, z = 2.0, 1.0, 2.0
result_float = func(x, y, z)
print(f"Float result: {result_float:.6f}")

# Timing: func(x, y, z)
import timeit
time_float = timeit.timeit(lambda: func(x, y, z), number=1000)
print(f'Float timing (1000 calls): {time_float:.6f}s')


# Individual dual numbers
x, y, z = Dual(2.0, ["x"], []), Dual(1.0, ["y"], []), Dual(2.0, ["z"], [])
result_dual = func(x, y, z)
print(f"\nDual result: {result_dual}")

# Timing: func(x, y, z)
time_dual = timeit.timeit(lambda: func(x, y, z), number=1000)
print(f'Dual timing (1000 calls): {time_dual:.6f}s')


x = Dual(2.0, ["x", "y", "z"], [1.0, 0.0, 0.0])
y = Dual(1.0, ["x", "y", "z"], [0.0, 1.0, 0.0])
z = Dual(2.0, ["x", "y", "z"], [0.0, 0.0, 1.0])


# Timing: func(x, y, z)
import timeit
print('Timing:', timeit.timeit(lambda: func(x, y, z), number=1000))


x = Dual(2.0, ["x", "y", "z"], [1.0, 0.0, 0.0])
y = Dual.vars_from(x, 1.0, ["x", "y", "z"], [0.0, 1.0, 0.0])
z = Dual.vars_from(x, 2.0, ["x", "y", "z"], [0.0, 0.0, 1.0])


# Timing: func(x, y, z)
import timeit
print('Timing:', timeit.timeit(lambda: func(x, y, z), number=1000))



#======================================================================
# Numerical differentiation
#======================================================================
print("\n5. NUMERICAL VS AUTOMATIC DIFFERENTIATION")
print("-" * 45)


def df_fwd_diff(f, x, y, z):
    base = f(x, y, z)
    dh = 1e-10
    dx = f(x+dh, y, z) - base
    dy = f(x, y+dh, z) - base
    dz = f(x, y, z+dh) - base
    return base, dx/dh, dy/dh, dz/dh

# Timing: df_fwd_diff(func, 2.0, 1.0, 2.0)
import timeit
print('Timing:', timeit.timeit(lambda: df_fwd_diff(func, 2.0, 1.0, 2.0), number=1000))



#======================================================================
# Functions with execution line delay
#======================================================================


import time
def func_complex(x, y, z):
    time.sleep(0.000025)
    return x**6 + dual_exp(x/y) + dual_log(z)

# Timing: func_complex(2.0, 1.0, 2.0)
import timeit
print('Timing:', timeit.timeit(lambda: func_complex(2.0, 1.0, 2.0), number=1000))


# Timing: func_complex(x, y, z)
import timeit
print('Timing:', timeit.timeit(lambda: func_complex(x, y, z), number=1000))


# Timing: df_fwd_diff(func_complex, 2.0, 1.0, 2.0)
import timeit
print('Timing:', timeit.timeit(lambda: df_fwd_diff(func_complex, 2.0, 1.0, 2.0), number=1000))



#======================================================================
# Second order derivatives
#======================================================================
print("\n6. SECOND ORDER DERIVATIVES")
print("-" * 30)


x = Dual2(2.0, ["x", "y", "z"], [1.0, 0.0, 0.0], [])
y = Dual2(1.0, ["x", "y", "z"], [0.0, 1.0, 0.0], [])
z = Dual2(2.0, ["x", "y", "z"], [0.0, 0.0, 1.0], [])
second_order_result = func(x, y, z)
print(f"Second order result: {second_order_result}")

hessian = gradient(second_order_result, ["x", "y"], order=2)
print(f"Hessian (x,y): {hessian}")


# Timing: func(x, y, z)
import timeit
print('Timing:', timeit.timeit(lambda: func(x, y, z), number=1000))



#======================================================================
# Exogenous Variables
#======================================================================
print("\n7. EXOGENOUS VARIABLES")
print("-" * 25)


x = Variable(1.5, ["x"])
y = Variable(3.9, ["y"])
product = x * y
print(f"Variable product: {product}")

defaults._global_ad_order = 2
product2 = x * y
print(f"Product with 2nd order AD: {product2}")
print(f"Second derivatives: {product2.dual2}")



#======================================================================
# One Dimensional Newton-Raphson Algorithm
#======================================================================
print("\n8. NEWTON-RAPHSON ROOT FINDING")
print("-" * 35)


from rateslib.dual import newton_1dim

def f(g, s):
    f0 = g**2 - s   # Function value
    f1 = 2*g        # Analytical derivative is required
    return f0, f1

s = Dual(2.0, ["s"], [])
root = newton_1dim(f, g0=1.0, args=(s,))
print(f"Square root of 2 using Newton-Raphson: {root}")



#======================================================================
# One Dimensional Inverse Function Theorem
#======================================================================
print("\n9. INVERSE FUNCTION THEOREM")
print("-" * 32)


from rateslib.dual import ift_1dim

def s(g):
    return dual_exp(g) + g**2

s_tgt = Dual(2.0, ["s"], [])
inverse_result = ift_1dim(s, s_tgt, h="modified_brent", ini_h_args=(0.0, 2.0))
print(f"Inverse function result: {inverse_result}")



#======================================================================
# Normal functions
#======================================================================
print("\n10. NORMAL DISTRIBUTION FUNCTIONS")
print("-" * 36)


from rateslib.dual import dual_norm_pdf, dual_norm_cdf, dual_inv_norm_cdf


u = Variable(1.5, ["u"])
pdf_result = dual_norm_pdf(u)
cdf_result = dual_norm_cdf(u)
inv_cdf_result = dual_inv_norm_cdf(Variable(0.933193, ["v"]))

print(f"PDF(1.5): {pdf_result}")
print(f"CDF(1.5): {cdf_result}")
print(f"InvCDF(0.933193): {inv_cdf_result}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("AUTOMATIC DIFFERENTIATION DEMONSTRATION COMPLETED!")
    print("=" * 70)
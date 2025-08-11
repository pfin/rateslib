#!/usr/bin/env python
"""
Converted from: AutomaticDifferentiation.ipynb

This script demonstrates rateslib functionality.
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


z_x = Dual2(0.0, ["x"], [], [])
z_x


z_x * z_x


(z_x * z_x).dual2



#======================================================================
# General functions of dual numbers
#======================================================================


import math
def dual_sin(x: float | Dual) -> float | Dual:
    if isinstance(x, Dual):
        return Dual(math.sin(x.real), x.vars, math.cos(x.real) * x.dual)
    return math.sin(x)


x = Dual(2.1, ["y"], [])
dual_sin(x)



#======================================================================
# Upcasting and dynamic variables
#======================================================================


first_dual = Dual(11.0, ["x", "y"], [3, 8])
second_dual = Dual(-3.0, ["y", "z"], [-2, 5])
first_dual + second_dual + 2.65



#======================================================================
# First order derivatives and performance
#======================================================================


def func(x, y, z):
    return x**6 + dual_exp(x/y) + dual_log(z)

x, y, z = 2.0, 1.0, 2.0
func(x, y, z)


# Timing: func(x, y, z)
import timeit
print('Timing:', timeit.timeit(lambda: func(x, y, z), number=1000))


x, y, z = Dual(2.0, ["x"], []), Dual(1.0, ["y"], []), Dual(2.0, ["z"], [])
func(x, y, z)


# Timing: func(x, y, z)
import timeit
print('Timing:', timeit.timeit(lambda: func(x, y, z), number=1000))


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


x = Dual2(2.0, ["x", "y", "z"], [1.0, 0.0, 0.0], [])
y = Dual2(1.0, ["x", "y", "z"], [0.0, 1.0, 0.0], [])
z = Dual2(2.0, ["x", "y", "z"], [0.0, 0.0, 1.0], [])
func(x, y, z)


gradient(func(x, y, z), ["x", "y"], order=2)


# Timing: func(x, y, z)
import timeit
print('Timing:', timeit.timeit(lambda: func(x, y, z), number=1000))



#======================================================================
# Exogenous Variables
#======================================================================


x = Variable(1.5, ["x"])
y = Variable(3.9, ["y"])
x * y


defaults._global_ad_order = 2


x * y


(x * y).dual2



#======================================================================
# One Dimensional Newton-Raphson Algorithm
#======================================================================


from rateslib.dual import newton_1dim

def f(g, s):
    f0 = g**2 - s   # Function value
    f1 = 2*g        # Analytical derivative is required
    return f0, f1

s = Dual(2.0, ["s"], [])
newton_1dim(f, g0=1.0, args=(s,))



#======================================================================
# One Dimensional Inverse Function Theorem
#======================================================================


from rateslib.dual import ift_1dim

def s(g):
    return dual_exp(g) + g**2

s_tgt = Dual(2.0, ["s"], [])
ift_1dim(s, s_tgt, h="modified_brent", ini_h_args=(0.0, 2.0))



#======================================================================
# Normal functions
#======================================================================


from rateslib.dual import dual_norm_pdf, dual_norm_cdf, dual_inv_norm_cdf


dual_norm_pdf(Variable(1.5, ["u"]))


dual_norm_cdf(Variable(1.5, ["u"]))


dual_inv_norm_cdf(Variable(0.933193, ["v"]))


if __name__ == "__main__":
    print("Script completed successfully!")
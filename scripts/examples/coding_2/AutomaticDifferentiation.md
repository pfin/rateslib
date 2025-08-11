# AutomaticDifferentiation.py Documentation

## Overview
Demonstrates rateslib's automatic differentiation capabilities using dual numbers for exact derivative calculations.

## Key Concepts
- **Dual Numbers**: Numbers that carry both value and derivative information
- **Dual**: First-order derivatives
- **Dual2**: Second-order derivatives (includes Hessian)
- **Variable**: Exogenous variables with dynamic AD order

## Sections

### 1. Definitions of Dual Numbers
Creates basic dual numbers and demonstrates multiplication with derivative tracking.

### 2. General Functions of Dual Numbers
Shows how to create custom functions (like `dual_sin`) that work with dual numbers.

### 3. Upcasting and Dynamic Variables
Demonstrates how dual numbers with different variable sets combine automatically.

### 4. First Order Derivatives and Performance
Compares performance between:
- Pure float calculations
- Individual dual variables
- Combined dual variables with full gradient

Performance impact: ~3-5x slower than pure floats.

### 5. Numerical Differentiation
Compares automatic differentiation with finite difference methods.

### 6. Second Order Derivatives
Shows Dual2 usage for calculating Hessian matrices.

### 7. Exogenous Variables
Demonstrates Variable class with global AD order control.

### 8. Newton-Raphson Algorithm
Uses automatic differentiation for root finding with exact derivatives.

### 9. Inverse Function Theorem
Finds input values that produce target outputs.

### 10. Normal Distribution Functions
Shows dual-aware statistical functions: PDF, CDF, inverse CDF.

## Usage
```bash
cd python/
python ../scripts/examples/coding_2/AutomaticDifferentiation.py
```

## Example Output
The script demonstrates various AD operations but produces minimal output in original form.
Key results include gradients, Hessians, and performance comparisons.
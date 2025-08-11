# AutomaticDifferentiation.py Documentation

## Overview
Demonstrates rateslib's automatic differentiation capabilities using dual numbers for exact derivative calculations. This implementation showcases a hybrid Python/Rust architecture where core dual number operations are implemented in Rust for performance while maintaining a Python interface for ease of use.

## Mathematical Foundation

### Dual Number Algebra
Dual numbers extend real numbers by introducing an infinitesimal element ε where ε² = 0. A dual number has the form:

```
a + b·ε
```

where `a` is the real part (function value) and `b` is the dual part (derivative information).

#### Algebraic Operations
For dual numbers u = a + b·ε and v = c + d·ε:

- **Addition**: (a + b·ε) + (c + d·ε) = (a + c) + (b + d)·ε
- **Multiplication**: (a + b·ε) × (c + d·ε) = ac + (ad + bc)·ε
- **Division**: (a + b·ε) ÷ (c + d·ε) = (a/c) + ((bc - ad)/c²)·ε
- **Power**: (a + b·ε)^n = a^n + (n·a^(n-1)·b)·ε

#### Chain Rule Implementation
For composite functions f(g(x)), the chain rule states:
```
(f ∘ g)'(x) = f'(g(x)) × g'(x)
```

In dual number arithmetic, if g(x) = u + v·ε, then:
```
f(g(x)) = f(u) + f'(u)·v·ε
```

### Second-Order Dual Numbers (Dual2)
Extend to second derivatives using dual numbers of the form:
```
a + b·ε₁ + c·ε₂ + d·ε₁ε₂
```

where:
- `a` = function value
- `b` = first partial derivatives
- `c` = pure second derivatives (∂²f/∂x²)
- `d` = mixed second derivatives (∂²f/∂x∂y)

#### Hessian Matrix Construction
The Hessian matrix H for function f(x₁, x₂, ..., xₙ) is:
```
H = [∂²f/∂xᵢ∂xⱼ]
```

Rateslib's Dual2 automatically constructs this matrix through algebraic operations.

## Key Concepts

### Core Types
- **Dual**: First-order AD with gradient vector ∇f
- **Dual2**: Second-order AD with Hessian matrix H
- **Variable**: Dynamic AD order determined by global settings
- **ADOrder**: Enum controlling differentiation order (Zero, One, Two)

### Variable Management
The system uses a sophisticated variable tagging system:
- Variables are identified by string names (["x", "y", "z"])
- Automatic upcasting combines different variable sets
- Memory-efficient sparse representation for gradients

## Sections Analysis

### 1. Basic Dual Number Operations
```python
z_x = Dual2(0.0, ["x"], [], [])
result = z_x * z_x  # Computes x² with derivatives
```
Demonstrates the fundamental property that d/dx(x²) = 2x at x=0 gives derivative=0.

### 2. Custom Function Implementation
The `dual_sin` function shows how to extend mathematical functions:
```python
def dual_sin(x: float | Dual) -> float | Dual:
    if isinstance(x, Dual):
        return Dual(math.sin(x.real), x.vars, math.cos(x.real) * x.dual)
    return math.sin(x)
```

Mathematical principle: If f(x) = sin(x), then f'(x) = cos(x).

### 3. Variable Upcasting and Sparse Representation
When dual numbers with different variable sets combine:
```python
first_dual = Dual(11.0, ["x", "y"], [3, 8])    # ∂f/∂x=3, ∂f/∂y=8
second_dual = Dual(-3.0, ["y", "z"], [-2, 5])  # ∂g/∂y=-2, ∂g/∂z=5
combined = first_dual + second_dual             # Automatic variable union
```

Result: Variables ["x", "y", "z"] with gradients [3, 6, 5] where ∂(f+g)/∂y = 8+(-2) = 6.

### 4. Performance Analysis
Computational complexity analysis:

| Operation Type | Time Complexity | Memory Usage | Performance Factor |
|---------------|-----------------|--------------|-------------------|
| Float | O(1) | O(1) | 1.0x |
| Dual (n vars) | O(n) | O(n) | 3-5x |
| Dual2 (n vars) | O(n²) | O(n²) | 5-10x |

The performance overhead is acceptable for functions with expensive evaluations (financial models, numerical simulations).

### 5. Numerical vs Automatic Differentiation
Comparison of differentiation methods:

#### Finite Difference (Forward)
```
f'(x) ≈ (f(x + h) - f(x)) / h
```
- **Accuracy**: O(h) truncation error + O(1/h) roundoff error
- **Optimal h**: √(machine epsilon) ≈ 1.49×10⁻⁸
- **Function Evaluations**: n+1 for n variables

#### Automatic Differentiation
- **Accuracy**: Machine precision (no truncation error)
- **Function Evaluations**: 1 (regardless of number of variables)
- **Memory**: Linear in number of variables

### 6. Hessian Matrix Computation
Second-order derivatives enable:
- **Optimization**: Newton-Raphson methods with quadratic convergence
- **Risk Management**: Portfolio convexity analysis
- **Uncertainty Quantification**: Error propagation in nonlinear models

### 7. Global AD Order Management
```python
defaults._global_ad_order = 2
```
Allows dynamic switching between differentiation orders, crucial for:
- Memory optimization in large systems
- Conditional differentiation based on required accuracy

### 8. Newton-Raphson Root Finding
Demonstrates quadratic convergence:
```
x_{n+1} = x_n - f(x_n)/f'(x_n)
```

With automatic derivatives, no need for manual derivative calculations or finite difference approximations.

### 9. Inverse Function Theorem Application
For finding x such that f(x) = target:
- Uses Modified Brent's method with AD-computed derivatives
- Combines bracketing robustness with derivative acceleration
- Critical for yield curve bootstrapping and option implied volatility

### 10. Statistical Functions with AD
Normal distribution functions (PDF, CDF, inverse CDF) with derivative propagation enable:
- **Option Pricing**: Greeks calculation (delta, gamma, vega)
- **Risk Management**: VaR and Expected Shortfall derivatives
- **Calibration**: Parameter sensitivity in statistical models

## Computational Finance Applications

### Risk Management
- **Portfolio Greeks**: Automatic computation of sensitivities
- **VaR Derivatives**: Sensitivity of Value-at-Risk to market parameters
- **Stress Testing**: Derivative-based linear approximations

### Yield Curve Construction
- **Bootstrap Sensitivity**: Derivatives w.r.t. input market rates
- **Parallel Shifts**: DV01 calculation across curve tenors  
- **Key Rate Durations**: Sensitivity to individual benchmark rates

### Option Pricing
- **Black-Scholes Greeks**: Delta, gamma, theta, vega, rho automatically
- **Exotic Options**: Path-dependent derivatives with AD
- **Model Calibration**: Parameter gradients for optimization

### Credit Risk Models
- **PD Sensitivity**: Probability of default derivatives
- **LGD Models**: Loss given default parameter sensitivity
- **CVA/DVA**: Credit valuation adjustment derivatives

## Performance Optimization Strategies

### Memory Management
- **Sparse Gradients**: Only track active variables
- **Variable Pooling**: Reuse variable name arrays
- **Order Conversion**: Dynamic switching between Dual and Dual2

### Computational Efficiency
- **Rust Implementation**: Core operations in compiled Rust
- **SIMD Optimization**: Vector operations where applicable
- **Lazy Evaluation**: Defer gradient computation until needed

### Numerical Stability
- **Condition Number Monitoring**: Detect ill-conditioned Jacobians
- **Scaling**: Normalize variables to similar magnitudes
- **Regularization**: Add small diagonal terms for stability

## Advanced Topics

### Multivariate Chain Rule
For f(g(x,y), h(x,y)):
```
∂f/∂x = (∂f/∂g)(∂g/∂x) + (∂f/∂h)(∂h/∂x)
∂f/∂y = (∂f/∂g)(∂g/∂y) + (∂f/∂h)(∂h/∂y)
```

### Reverse Mode AD (Not Implemented)
Current implementation uses forward mode. Reverse mode would be more efficient for functions with many inputs and few outputs.

### Higher-Order Derivatives
Extension to third and fourth-order derivatives for:
- **Volatility Surface Modeling**: Higher-order Greeks
- **Taylor Series**: Improved local approximations
- **Sensitivity Analysis**: Non-linear parameter relationships

## Usage Examples

### Basic Usage
```bash
cd python/
python ../scripts/examples/coding_2/AutomaticDifferentiation.py
```

### Performance Benchmarking
The script includes timing comparisons showing:
- Pure float operations: baseline performance
- AD with individual variables: 3-5x overhead
- AD with combined variables: similar overhead with full gradient

### Memory Profiling
Variable management efficiency demonstrated through:
- Dynamic variable set expansion
- Memory-efficient gradient storage
- Automatic garbage collection of unused variables

## Key Results
- **Gradient Accuracy**: Machine precision vs finite difference approximation
- **Performance Trade-off**: 3-5x slower for exact derivatives
- **Memory Scaling**: Linear in number of active variables
- **Convergence**: Quadratic for Newton-Raphson with exact derivatives

This implementation represents state-of-the-art automatic differentiation for quantitative finance, combining mathematical rigor with computational efficiency.
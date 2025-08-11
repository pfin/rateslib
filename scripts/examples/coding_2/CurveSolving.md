# CurveSolving.py Documentation

## Overview
Demonstrates advanced numerical methods for fixed income curve construction, including bootstrapping procedures, root-finding algorithms, and parametric curve fitting. This documentation covers the mathematical foundations and practical implementation of curve calibration in rateslib's ecosystem.

## Mathematical Foundations

### Curve Construction Problem
Given market instruments with known prices P₁, P₂, ..., Pₙ, find the curve parameters that satisfy:
```
f(θ, instrument_i) = P_i  for all i ∈ {1, 2, ..., n}
```
where θ represents the curve parameters (discount factors, rates, or model parameters).

### Key Numerical Concepts
- **Bootstrapping**: Sequential construction exploiting instrument maturity ordering
- **Newton-Raphson**: Second-order convergent root finding using exact derivatives
- **Inverse Function Theorem (IFT)**: Mathematical framework for parameter inversion
- **Parametric Models**: Reduced-dimension curve representations (Nelson-Siegel, Svensson)

## Algorithmic Architecture

### Bootstrap Procedure
```
Market Data → Sort by Maturity → Sequential Solve → Curve Construction
     ↓              ↓                  ↓              ↓
  Deposits     Order Instruments   Node by Node    Interpolation
    Swaps      ↓                       ↓          ↓
   Futures    Liquid → Illiquid      Jacobian   Complete Curve
```

### Newton-Raphson Implementation
```python
def newton_solve(f, df_dx, x0, tolerance=1e-12, max_iter=100):
    """
    Solve f(x) = 0 using Newton-Raphson with analytical derivatives
    
    f: objective function
    df_dx: analytical derivative of f
    x0: initial guess
    """
    for i in range(max_iter):
        fx = f(x0)
        if abs(fx) < tolerance:
            return x0
        dfx = df_dx(x0)
        x0 = x0 - fx / dfx
    raise ConvergenceError()
```

### Automatic Differentiation Integration
Rateslib's dual number system provides exact derivatives for:
- **Bond pricing functions**: Yield-to-maturity calculations
- **Swap valuation**: Present value sensitivities
- **Forward rate agreements**: Rate sensitivity analysis

## Sections

### 1. Basic Curve Construction
Creates a simple curve with known discount factor nodes and tests interpolation.

### 2. Newton-Raphson Root Finding
Implements bond YTM calculation using Newton-Raphson with exact derivatives.
- Function: `bond_price_error(ytm, bond_price, cashflows, dates, settle_date)`
- Returns pricing error and its derivative

### 3. Curve Bootstrapping
Demonstrates building a curve from market instruments:
- Short-term deposits
- Swap rates
- Sequential discount factor calculation

### 4. Inverse Function Application
Uses IFT to find rates that produce target prices:
- Example: 2-year zero coupon bond
- Find rate given price of 95.0

### 5. Multi-dimensional Curve Fitting: Nelson-Siegel Model

#### Mathematical Formulation
The Nelson-Siegel model represents yield curves with a parsimonious parametric form:

```
y(t) = β₀ + β₁ * (1-exp(-t/τ))/(t/τ) + β₂ * [(1-exp(-t/τ))/(t/τ) - exp(-t/τ)]
```

#### Parameter Interpretation
- **β₀** (Level): Long-term yield level as t → ∞
- **β₁** (Slope): Short-term vs long-term spread (y(0) - y(∞) = -β₁)
- **β₂** (Curvature): Medium-term hump, peaks at t ≈ τ
- **τ** (Decay): Controls location of curvature maximum

#### Optimization Framework
```python
def nelson_siegel_objective(params, market_yields, maturities):
    """
    Minimize sum of squared errors between model and market yields
    
    params: [β₀, β₁, β₂, τ]
    market_yields: observed market rates
    maturities: corresponding time to maturity
    """
    model_yields = nelson_siegel_yield(maturities, *params)
    return sum((market - model)**2 for market, model in zip(market_yields, model_yields))
```

## Implementation Patterns in Rateslib

### Custom Curve Classes
Following the `_BaseCurve` pattern for parametric curves:

```python
class NelsonSiegelCurve(_BaseCurve):
    def __init__(self, beta0, beta1, beta2, tau):
        self.params = (beta0, beta1, beta2, tau)
    
    def __getitem__(self, date):
        # Convert date to maturity and return discount factor
        t = self._time_to_maturity(date)
        rate = nelson_siegel_yield(t, *self.params)
        return exp(-rate * t / 100)
```

### Integration with Solver Module
```python
from rateslib.solver import Solver

# Calibrate Nelson-Siegel to market instruments
solver = Solver(
    instruments=market_instruments,
    curves=[ns_curve],
    method="least_squares"
)
calibrated_curve = solver.solve()
```

### Multi-Curve Environments
```python
# Simultaneous calibration of multiple curves
discount_curve = Curve(discount_instruments)
forward_curve = NelsonSiegelCurve(initial_params)

solver = Solver(
    curves=[discount_curve, forward_curve],
    instruments=all_instruments
)
```

## Advanced Numerical Techniques

### Robust Bootstrap Procedures
```python
def robust_bootstrap(instruments, initial_curve):
    """
    Bootstrap with outlier detection and stability checks
    """
    for instrument in sorted(instruments, key=lambda x: x.maturity):
        try:
            calibrate_node(curve, instrument)
        except ConvergenceError:
            # Fall back to interpolation or skip instrument
            handle_failed_calibration(instrument)
```

### Regularization for Ill-Conditioned Problems
```python
def regularized_solve(jacobian, residuals, lambda_reg=1e-6):
    """
    Tikhonov regularization for numerical stability
    """
    A = jacobian.T @ jacobian + lambda_reg * np.eye(jacobian.shape[1])
    b = jacobian.T @ residuals
    return np.linalg.solve(A, b)
```

### Constraint Handling
```python
def constrained_newton(objective, constraints, x0):
    """
    Newton method with inequality constraints (discount factors > 0)
    """
    # Implement barrier methods or projected gradients
    pass
```

## Performance Considerations

### Computational Complexity
- **Bootstrap**: O(n) for n instruments (sequential)
- **Global fitting**: O(n³) for Newton methods
- **Parameter sensitivity**: O(n²) with automatic differentiation

### Numerical Stability
- **Condition number monitoring**: Detect ill-conditioned Jacobians
- **Regularization parameters**: Balance fit quality vs stability
- **Multiple initial guesses**: Global optimization considerations

### Memory Management
- **Sparse matrix structures**: For large curve systems
- **Incremental updates**: Avoid full recalibration when possible
- **Caching strategies**: Store expensive intermediate calculations

## Integration Points

### Market Data Feeds
```python
class MarketDataAdapter:
    """Adapt various market data formats to rateslib instruments"""
    
    def to_deposits(self, rates_dict):
        return [FixedRateDeposit(...) for rate in rates_dict]
    
    def to_swaps(self, swap_rates):
        return [InterestRateSwap(...) for rate in swap_rates]
```

### Risk Management Integration
```python
def curve_sensitivity_analysis(base_curve, shock_size=1e-4):
    """Compute curve sensitivities for risk management"""
    sensitivities = {}
    
    for node_date in base_curve.nodes:
        shocked_curve = base_curve.shift_node(node_date, shock_size)
        sensitivities[node_date] = compute_portfolio_pv_change(shocked_curve)
    
    return sensitivities
```

### Historical Analysis
```python
def curve_evolution_analysis(historical_curves):
    """Analyze curve shape evolution over time"""
    shape_metrics = []
    
    for curve in historical_curves:
        level = curve.rate(curve.nodes.initial, "10Y")
        slope = curve.rate(curve.nodes.initial, "10Y") - curve.rate(curve.nodes.initial, "2Y")
        curvature = compute_butterfly_spread(curve)
        
        shape_metrics.append((level, slope, curvature))
    
    return analyze_pca(shape_metrics)
```

## Usage Examples

### Basic Bootstrap
```bash
cd python/
python ../scripts/examples/coding_2/CurveSolving.py
```

### Key Functions and Classes
- **`newton_1dim`**: Univariate Newton-Raphson solver
- **`ift_1dim`**: Inverse function theorem application
- **`nelson_siegel_yield`**: Parametric yield curve evaluation
- **`bootstrap_curve`**: Sequential curve construction
- **`calibrate_to_market`**: Global optimization wrapper

### Example Market Data Configuration
```python
market_config = {
    "deposits": {
        "3M": 2.50,    # 3-month deposit rate
        "6M": 2.80,    # 6-month deposit rate
    },
    "swaps": {
        "1Y": 3.20,    # 1-year swap rate
        "2Y": 3.60,    # 2-year swap rate  
        "3Y": 3.90,    # 3-year swap rate
        "5Y": 4.10,    # 5-year swap rate
        "10Y": 4.25,   # 10-year swap rate
    }
}
```

## Error Handling and Diagnostics

### Common Convergence Issues
- **Poor initial guesses**: Use market-based starting values
- **Ill-conditioned systems**: Apply regularization techniques
- **Non-monotonic curves**: Check instrument ordering and quality

### Diagnostic Tools
```python
def curve_diagnostics(curve, instruments):
    """Comprehensive curve quality assessment"""
    diagnostics = {
        "max_pricing_error": max(abs(instrument.npv(curve)) for instrument in instruments),
        "curve_smoothness": assess_curve_smoothness(curve),
        "monotonicity_violations": check_forward_rate_monotonicity(curve),
        "extrapolation_stability": test_extrapolation_bounds(curve)
    }
    return diagnostics
```
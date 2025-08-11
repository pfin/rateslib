# Mathematical Foundations of Rateslib

## Core Mathematical Concepts

### 1. Time Value of Money

#### Present Value Formula
```
PV = Σ(CF_t / (1 + r)^t)

Where:
- PV = Present Value
- CF_t = Cash flow at time t
- r = Discount rate
- t = Time period
```

#### Continuous Compounding
```
PV = CF × e^(-r×t)

Forward Rate: F(t₁,t₂) = (DF(t₁)/DF(t₂) - 1) / (t₂ - t₁)
Instantaneous Forward: f(t) = -∂ln(DF(t))/∂t
```

### 2. Yield Curve Mathematics

#### Nelson-Siegel Model
```
y(τ) = β₀ + β₁ × ((1 - e^(-τ/λ))/(τ/λ)) + β₂ × ((1 - e^(-τ/λ))/(τ/λ) - e^(-τ/λ))

Parameters:
- β₀: Long-term level (asymptotic value)
- β₁: Short-term component (slope)
- β₂: Medium-term component (curvature)
- λ: Decay factor
- τ: Time to maturity
```

#### Svensson Extension
```
y(τ) = β₀ + β₁ × φ₁(τ) + β₂ × φ₂(τ) + β₃ × φ₃(τ)

Where:
φ₁(τ) = (1 - e^(-τ/λ₁))/(τ/λ₁)
φ₂(τ) = φ₁(τ) - e^(-τ/λ₁)
φ₃(τ) = (1 - e^(-τ/λ₂))/(τ/λ₂) - e^(-τ/λ₂)
```

### 3. Interpolation Methods

#### Linear Interpolation
```
y = y₁ + (x - x₁) × (y₂ - y₁)/(x₂ - x₁)

In log space (log-linear):
ln(y) = ln(y₁) + (x - x₁) × (ln(y₂) - ln(y₁))/(x₂ - x₁)
```

#### Cubic Spline Interpolation
```
S_i(x) = a_i + b_i(x - x_i) + c_i(x - x_i)² + d_i(x - x_i)³

Constraints:
- S_i(x_i) = y_i (interpolation)
- S_i(x_{i+1}) = y_{i+1} (continuity)
- S'_i(x_{i+1}) = S'_{i+1}(x_{i+1}) (smooth first derivative)
- S''_i(x_{i+1}) = S''_{i+1}(x_{i+1}) (smooth second derivative)
```

#### B-Spline Basis Functions
```
B_{i,0}(t) = 1 if t_i ≤ t < t_{i+1}, 0 otherwise

B_{i,k}(t) = ((t - t_i)/(t_{i+k} - t_i)) × B_{i,k-1}(t) + 
             ((t_{i+k+1} - t)/(t_{i+k+1} - t_{i+1})) × B_{i+1,k-1}(t)

Spline: S(t) = Σ c_i × B_{i,k}(t)
```

### 4. Automatic Differentiation

#### Dual Numbers
```
Dual number: a + bε, where ε² = 0

Operations:
(a + bε) + (c + dε) = (a + c) + (b + d)ε
(a + bε) × (c + dε) = ac + (ad + bc)ε
exp(a + bε) = e^a + be^aε
ln(a + bε) = ln(a) + (b/a)ε
```

#### Second-Order Dual (Dual2)
```
Dual2: a + bε + cε²/2

Chain rule application:
f(g(x)) → f'(g(x)) × g'(x) (first derivative)
         f''(g(x)) × g'(x)² + f'(g(x)) × g''(x) (second derivative)
```

### 5. Bond Mathematics

#### Price-Yield Relationship
```
P = Σ(C/(1+y/f)^(t×f)) + FV/(1+y/f)^(T×f)

Where:
- P = Bond price
- C = Coupon payment
- y = Yield to maturity
- f = Frequency
- FV = Face value
- T = Maturity
```

#### Duration and Convexity
```
Modified Duration: D_mod = -(1/P) × (∂P/∂y)
                         = (1/(1+y/f)) × Σ(t × CF_t × DF_t)/P

Macaulay Duration: D_mac = Σ(t × CF_t × DF_t)/P

Convexity: C = (1/P) × (∂²P/∂y²)
             = (1/P) × Σ(t × (t+1/f) × CF_t × DF_t)/(1+y/f)²

Price approximation:
ΔP/P ≈ -D_mod × Δy + 0.5 × C × (Δy)²
```

#### DV01 and PV01
```
DV01 = -∂P/∂y × 0.0001
     = Price change for 1 basis point move

PV01 = |DV01| (absolute value)
```

### 6. Swap Mathematics

#### Swap Rate Formula
```
Par Swap Rate: s = (1 - DF_T) / Σ(DF_i × τ_i)

Where:
- DF_i = Discount factor at time i
- τ_i = Day count fraction for period i
- T = Maturity
```

#### Forward Swap Rate
```
Forward Swap Rate: s(t₀,T₁,T₂) = (DF(t₀,T₁) - DF(t₀,T₂)) / A(t₀,T₁,T₂)

Annuity: A(t₀,T₁,T₂) = Σ τ_i × DF(t₀,t_i)
```

### 7. Option Pricing

#### Black-Scholes for FX Options
```
d₁ = [ln(S/K) + (r_d - r_f + σ²/2)T] / (σ√T)
d₂ = d₁ - σ√T

Call: C = S×e^(-r_f×T)×N(d₁) - K×e^(-r_d×T)×N(d₂)
Put:  P = K×e^(-r_d×T)×N(-d₂) - S×e^(-r_f×T)×N(-d₁)

Where:
- S = Spot rate
- K = Strike
- r_d = Domestic rate
- r_f = Foreign rate
- σ = Volatility
- T = Time to expiry
- N() = Cumulative normal distribution
```

#### Greeks
```
Delta (Δ): ∂V/∂S
Gamma (Γ): ∂²V/∂S²
Vega (ν): ∂V/∂σ
Theta (Θ): -∂V/∂t
Rho (ρ): ∂V/∂r

Second-order Greeks:
Vanna: ∂²V/∂S∂σ = ∂Delta/∂σ
Volga: ∂²V/∂σ² = ∂Vega/∂σ
Charm: ∂²V/∂S∂t = -∂Delta/∂t
```

### 8. SABR Model

#### Stochastic Volatility Dynamics
```
dF = α × F^β × dW₁
dα = ν × α × dW₂
dW₁ × dW₂ = ρ × dt

SABR Formula (Hagan approximation):
σ_SABR(K,F) = (α/(F×K)^((1-β)/2)) × z/χ(z) × {1 + correction terms}

Where:
z = (ν/α) × (F×K)^((1-β)/2) × ln(F/K)
χ(z) = ln[(√(1-2ρz+z²) + z - ρ)/(1-ρ)]
```

### 9. FX Mathematics

#### Interest Rate Parity
```
Forward Rate: F = S × (1 + r_d × T)/(1 + r_f × T)

In continuous time:
F = S × e^((r_d - r_f) × T)

Forward Points: FP = (F - S) × 10000 (for 4-decimal pairs)
```

#### Cross Rate Calculation
```
Direct: EUR/USD = 1.10, USD/JPY = 150
Cross: EUR/JPY = EUR/USD × USD/JPY = 1.10 × 150 = 165

Triangulation with bid-ask:
EUR/JPY_bid = EUR/USD_bid × USD/JPY_bid
EUR/JPY_ask = EUR/USD_ask × USD/JPY_ask
```

### 10. Numerical Methods

#### Newton-Raphson Method
```
x_{n+1} = x_n - f(x_n)/f'(x_n)

For yield calculation:
y_{n+1} = y_n - (P(y_n) - P_market)/(-D_mod × P(y_n))

Convergence: Quadratic (error ∝ error²)
```

#### Levenberg-Marquardt Algorithm
```
Δx = -(J^T J + λI)^(-1) J^T r

Where:
- J = Jacobian matrix
- r = Residual vector
- λ = Damping parameter
- I = Identity matrix

Adaptive λ:
- Decrease λ if step reduces error
- Increase λ if step increases error
```

### 11. Day Count Conventions

#### Common Conventions
```
Actual/360: DCF = Days/360
Actual/365: DCF = Days/365
Actual/Actual ISDA: DCF = Days/DaysInYear
30/360: DCF = (360×(Y₂-Y₁) + 30×(M₂-M₁) + (D₂-D₁))/360

Business/252: DCF = BusinessDays/252
```

### 12. Risk Metrics

#### Value at Risk (VaR)
```
Parametric VaR: VaR_α = μ - σ × Φ^(-1)(α)

Where:
- μ = Expected return
- σ = Standard deviation
- Φ^(-1) = Inverse normal CDF
- α = Confidence level
```

#### Credit Valuation Adjustment (CVA)
```
CVA = Σ EE(t_i) × PD(t_{i-1}, t_i) × LGD × DF(t_i)

Where:
- EE = Expected Exposure
- PD = Probability of Default
- LGD = Loss Given Default
- DF = Discount Factor
```

### 13. Matrix Operations for Curves

#### Spline Matrix System
```
[4 1 0 ... 0] [m₁]   [3(y₂-y₀)]
[1 4 1 ... 0] [m₂]   [3(y₃-y₁)]
[0 1 4 ... 0] [m₃] = [3(y₄-y₂)]
[... ... ...]  [...]   [...]
[0 0 0 ... 4] [mₙ]   [3(yₙ-yₙ₋₂)]

Tridiagonal system solved in O(n) time
```

### 14. Optimization Constraints

#### Arbitrage-Free Conditions
```
Forward Rate Positivity: f(t₁,t₂) > 0 ∀ t₁ < t₂

No Calendar Arbitrage: σ²(T₁)×T₁ < σ²(T₂)×T₂ for T₁ < T₂

Put-Call Parity: C - P = S×e^(-r_f×T) - K×e^(-r_d×T)
```

### 15. Performance Formulas

#### Sharpe Ratio
```
Sharpe = (R_p - R_f) / σ_p

Where:
- R_p = Portfolio return
- R_f = Risk-free rate
- σ_p = Portfolio standard deviation
```

#### Information Ratio
```
IR = (R_p - R_b) / TE

Where:
- R_b = Benchmark return
- TE = Tracking error (std of excess returns)
```

## Implementation in Rateslib

These mathematical foundations are implemented throughout rateslib with:

1. **Exact Derivatives**: Via automatic differentiation (Dual/Dual2)
2. **Numerical Stability**: Careful handling of edge cases
3. **Performance**: Rust acceleration for intensive calculations
4. **Accuracy**: Double precision with controlled rounding
5. **Validation**: Extensive testing against known results

The combination of mathematical rigor and efficient implementation makes rateslib suitable for production trading systems and risk management applications.
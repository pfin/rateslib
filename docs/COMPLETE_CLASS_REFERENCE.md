# Complete Class Reference for Rateslib

## Table of Contents
1. [Core Base Classes](#core-base-classes)
2. [Curves Module](#curves-module)
3. [Instruments Module](#instruments-module)
4. [FX Module](#fx-module)
5. [Legs Module](#legs-module)
6. [Scheduling Module](#scheduling-module)
7. [Dual Numbers Module](#dual-numbers-module)
8. [Solver Module](#solver-module)

---

## Core Base Classes

### `_WithState` Mixin
```python
class _WithState:
    """State management mixin for caching and validation"""
    
    Properties:
        _state: dict  # Internal state dictionary
        _state_version: int  # Version counter for invalidation
    
    Methods:
        _validate_state() -> bool
        _update_state(**kwargs) -> None
        _invalidate_state() -> None
        _get_state_key() -> tuple
```

### `_WithCache` Mixin
```python
class _WithCache:
    """Caching mixin for expensive computations"""
    
    Properties:
        _cache: dict  # Results cache
        _cache_enabled: bool  # Toggle caching
    
    Methods:
        _cache_key(*args) -> tuple
        _get_cached(key: tuple) -> Any
        _set_cached(key: tuple, value: Any) -> None
        _clear_cache() -> None
```

---

## Curves Module

### `Curve` (Base Class)
```python
class Curve(_WithState, _WithCache):
    """Base curve class for all interest rate curves"""
    
    Parameters:
        nodes: dict[datetime, float]  # Date-rate pairs
        interpolation: str  # 'linear', 'log_linear', 'linear_index', 'cubic_spline'
        ad: int  # Automatic differentiation order (0, 1, 2)
        id: str  # Optional identifier
        t: list[float]  # Optional knot sequence for splines
    
    Methods:
        rate(date: datetime, tenor: str = None) -> float | Dual
        df(date: datetime) -> float | Dual
        shift(basis_points: float) -> Curve
        plot(**kwargs) -> matplotlib.Figure
```

### `LineCurve`
```python
class LineCurve(Curve):
    """Linear interpolation curve"""
    
    Additional Methods:
        _interpolate(t: float) -> float
        _log_interpolate(t: float) -> float
```

### `IndexCurve`
```python
class IndexCurve(Curve):
    """Index-based curve with fixing history"""
    
    Additional Parameters:
        index_base: float  # Base index value
        index_lag: int  # Publication lag in months
    
    Methods:
        index_value(date: datetime) -> float
        index_ratio(date1: datetime, date2: datetime) -> float
```

### `CompositeCurve`
```python
class CompositeCurve(Curve):
    """Composite of multiple curves with different interpolations"""
    
    Parameters:
        curves: list[Curve]  # Component curves
        boundaries: list[datetime]  # Transition dates
    
    Methods:
        _select_curve(date: datetime) -> Curve
        _blend_at_boundary(date: datetime) -> float
```

### `ProxyCurve`
```python
class ProxyCurve(Curve):
    """Proxy curve linking to another curve with spread"""
    
    Parameters:
        curve: Curve  # Reference curve
        spread: float | Curve  # Basis spread
        id: str
    
    Methods:
        _apply_spread(rate: float) -> float
```

---

## Instruments Module

### `FixedRateBond`
```python
class FixedRateBond(BaseBond):
    """Fixed rate bond instrument"""
    
    Parameters:
        effective: datetime  # Start date
        termination: datetime  # Maturity date
        frequency: str  # Payment frequency ('A', 'S', 'Q', 'M')
        coupon: float  # Annual coupon rate
        convention: str  # Day count convention
        calendar: str | Cal  # Holiday calendar
        currency: str  # Currency code
        notional: float  # Face value
        amortization: float  # Amortization rate
        stub: str  # Stub type ('ShortFront', 'ShortBack', etc.)
    
    Methods:
        price(curves: dict | Curve) -> float
        ytm() -> float
        duration(curves: dict | Curve) -> float
        convexity(curves: dict | Curve) -> float
        dv01(curves: dict | Curve) -> float
        accrued_interest(settlement: datetime) -> float
        cash_flows(curves: dict | Curve) -> DataFrame
```

### `FloatRateBond`
```python
class FloatRateBond(BaseBond):
    """Floating rate bond instrument"""
    
    Additional Parameters:
        index_tenor: str  # Reference rate tenor
        fixings: dict[datetime, float]  # Historical fixings
        spread: float  # Spread over index
        floor: float  # Rate floor
        cap: float  # Rate cap
    
    Methods:
        forecast_rate(date: datetime, curves: dict) -> float
        reset_dates() -> list[datetime]
```

### `IRS` (Interest Rate Swap)
```python
class IRS(BaseSwap):
    """Vanilla interest rate swap"""
    
    Parameters:
        effective: datetime
        termination: datetime | str  # Date or tenor
        frequency: str  # Fixed leg frequency
        leg2_frequency: str  # Float leg frequency
        fixed_rate: float  # Fixed leg rate
        float_spread: float  # Float leg spread
        notional: float
        currency: str
        leg2_currency: str  # For cross-currency
    
    Methods:
        npv(curves: dict) -> float | Dual
        rate(curves: dict) -> float  # Par swap rate
        spread(curves: dict) -> float  # Par spread
        cashflows(curves: dict) -> tuple[DataFrame, DataFrame]
        delta(curves: dict) -> dict[str, float]
```

### `FRA` (Forward Rate Agreement)
```python
class FRA(BaseDerivative):
    """Forward rate agreement"""
    
    Parameters:
        effective: datetime
        termination: datetime
        frequency: str
        rate: float  # FRA rate
        notional: float
    
    Methods:
        npv(curves: dict) -> float
        forward_rate(curves: dict) -> float
```

### `FXSwap`
```python
class FXSwap(BaseDerivative):
    """FX swap instrument"""
    
    Parameters:
        pair: str  # Currency pair (e.g., 'EURUSD')
        near_date: datetime
        far_date: datetime
        near_points: float  # Near leg forward points
        far_points: float  # Far leg forward points
        notional: float
    
    Methods:
        npv(fx_rates: FXRates, curves: dict) -> float
        implied_points(fx_rates: FXRates, curves: dict) -> tuple[float, float]
```

### `FXOption`
```python
class FXOption(BaseOption):
    """FX vanilla option"""
    
    Parameters:
        pair: str
        expiry: datetime
        delivery: datetime
        strike: float
        option_type: str  # 'call' or 'put'
        notional: float
        premium_ccy: str  # Premium currency
    
    Methods:
        price(spot: float, vol: float, curves: dict) -> float
        delta(spot: float, vol: float, curves: dict) -> float
        gamma(spot: float, vol: float, curves: dict) -> float
        vega(spot: float, vol: float, curves: dict) -> float
        theta(spot: float, vol: float, curves: dict) -> float
```

---

## FX Module

### `FXRates`
```python
class FXRates:
    """FX spot rates container with triangulation"""
    
    Parameters:
        rates: dict[str, float]  # e.g., {'EURUSD': 1.10}
        settlement: datetime
        base: str  # Base currency for triangulation
    
    Properties:
        currencies: list[str]  # Available currencies
        pairs: list[str]  # Available pairs
    
    Methods:
        rate(pair: str) -> float | Dual
        convert(amount: float, from_ccy: str, to_ccy: str) -> float
        convert_positions(positions: dict[str, float], base: str) -> Dual
        update(rates: dict) -> None
        triangulate(from_ccy: str, to_ccy: str) -> float
        _check_arbitrage() -> bool
```

### `FXForwards`
```python
class FXForwards:
    """FX forward rates calculator"""
    
    Parameters:
        fx_rates: FXRates | dict
        curves: dict[str, Curve]  # Interest rate curves per currency
    
    Methods:
        rate(pair: str, settlement: datetime) -> float
        points(pair: str, settlement: datetime) -> float
        implied_yield(pair: str, settlement: datetime) -> float
```

---

## Legs Module

### `FixedLeg`
```python
class FixedLeg(BaseLeg):
    """Fixed rate leg of a swap"""
    
    Parameters:
        effective: datetime
        termination: datetime
        frequency: str
        notional: float | list[float]  # Can be amortizing
        coupon: float | list[float]  # Can vary by period
        currency: str
        convention: str
        calendar: str
    
    Methods:
        cash_flows(curves: dict = None) -> DataFrame
        npv(curves: dict) -> float | Dual
        duration(curves: dict) -> float
        analytic_delta(curves: dict) -> float
```

### `FloatLeg`
```python
class FloatLeg(BaseLeg):
    """Floating rate leg of a swap"""
    
    Additional Parameters:
        float_spread: float
        fixing_method: str  # 'ibor', 'rfr_daily', 'rfr_payment'
        fixings: dict[datetime, float]
        index_tenor: str
        lookback: int  # For RFR legs
    
    Methods:
        forecast_fixings(curves: dict) -> dict[datetime, float]
        reset_dates() -> list[datetime]
```

### `IndexLeg`
```python
class IndexLeg(BaseLeg):
    """Inflation-indexed leg"""
    
    Parameters:
        index_base: float
        index_curve: IndexCurve
        index_lag: int  # months
        floor: float
        cap: float
    
    Methods:
        index_ratios() -> list[float]
        real_cash_flows() -> DataFrame
```

---

## Scheduling Module

### `Schedule`
```python
class Schedule:
    """Payment schedule generator"""
    
    Parameters:
        effective: datetime
        termination: datetime
        frequency: str  # 'A', 'S', 'Q', 'M', 'W', 'D'
        calendar: str | Cal
        modifier: str  # Business day adjustment ('MF', 'F', 'P', etc.)
        eval_date: datetime
        roll: int | str  # Roll day (1-31) or 'eom', 'imm'
        stub: str  # 'ShortFront', 'ShortBack', 'LongFront', 'LongBack'
    
    Properties:
        dates: list[datetime]  # Unadjusted schedule dates
        adjusted_dates: list[datetime]  # Business day adjusted dates
        
    Methods:
        dcf(convention: str) -> list[float]  # Day count fractions
        is_regular() -> bool  # Check if all periods are regular
```

### `Tenor`
```python
class Tenor:
    """Tenor arithmetic and manipulation"""
    
    Parameters:
        tenor_str: str  # e.g., '3M', '2Y6M'
    
    Properties:
        months: int
        years: int
        days: int
    
    Methods:
        add_to(date: datetime) -> datetime
        subtract_from(date: datetime) -> datetime
        to_days(reference: datetime = None) -> int
        __add__(other: Tenor) -> Tenor
        __mul__(scalar: int) -> Tenor
```

---

## Dual Numbers Module

### `Dual`
```python
class Dual:
    """First-order automatic differentiation"""
    
    Parameters:
        real: float  # Real part
        vars: list[str]  # Variable names
        dual: list[float]  # Dual parts (derivatives)
    
    Properties:
        gradient: dict[str, float]  # Named derivatives
    
    Methods:
        __add__, __sub__, __mul__, __truediv__  # Arithmetic
        exp(), log(), sqrt(), power()  # Math functions
        sin(), cos(), tan()  # Trig functions
```

### `Dual2`
```python
class Dual2:
    """Second-order automatic differentiation"""
    
    Additional Parameters:
        dual2: list[list[float]]  # Second derivatives (Hessian)
    
    Properties:
        hessian: dict[tuple[str, str], float]  # Named second derivatives
    
    Methods:
        # Same as Dual plus second-order propagation
```

### `Variable`
```python
class Variable:
    """Named variable for AD"""
    
    Parameters:
        value: float
        name: str
    
    Methods:
        to_dual() -> Dual
        to_dual2() -> Dual2
```

### `gradient`
```python
def gradient(dual: Dual, vars: list[str]) -> dict[str, float]:
    """Extract gradients for specific variables"""
```

---

## Solver Module

### `Solver`
```python
class Solver:
    """Multi-dimensional root finder and optimizer"""
    
    Parameters:
        curves: list[Curve]
        instruments: list[BaseInstrument]
        weights: list[float]
        algorithm: str  # 'newton', 'levenberg', 'trust_region'
        max_iter: int
        tolerance: float
    
    Methods:
        solve() -> dict[str, Curve]
        residuals() -> list[float]
        jacobian() -> np.ndarray
```

### `FXSolver`
```python
class FXSolver:
    """FX triangle arbitrage solver"""
    
    Parameters:
        currencies: list[str]
        constraints: list[tuple[str, str, float]]  # Known rates
    
    Methods:
        solve() -> FXRates
        find_arbitrage() -> list[tuple[str, ...]]
```

---

## Utility Classes

### `defaults`
```python
class defaults:
    """Global configuration singleton"""
    
    Properties:
        base_currency: str = 'USD'
        base_calendar: str = 'nyc'
        curve_caching: bool = True
        dual_precision: float = 1e-8
    
    Methods:
        @classmethod
        reset() -> None
```

### `NoInput`
```python
class NoInput:
    """Sentinel for unset parameters"""
    
    Usage:
        def func(param=NoInput(0)):
            if param is NoInput.blank:
                # Parameter was not provided
```

---

## Class Hierarchies

### Instrument Hierarchy
```
BaseInstrument
├── BaseBond
│   ├── FixedRateBond
│   ├── FloatRateBond
│   └── IndexLinkedBond
├── BaseSwap
│   ├── IRS
│   ├── OIS
│   ├── XCCY
│   └── InflationSwap
├── BaseOption
│   ├── FXOption
│   ├── Swaption
│   └── CapFloor
└── BaseDerivative
    ├── FRA
    ├── FXSwap
    └── CDS
```

### Curve Hierarchy
```
Curve (ABC)
├── LineCurve
├── IndexCurve
├── CompositeCurve
├── ProxyCurve
└── SplineCurve
    ├── CubicSpline
    └── BSplineCurve
```

### Leg Hierarchy
```
BaseLeg (ABC)
├── FixedLeg
├── FloatLeg
├── IndexLeg
├── ZeroLeg
└── CustomLeg
```

---

## Important Implementation Notes

1. **Automatic Differentiation**: All numerical operations support AD when `ad` parameter is set
2. **Caching**: Results are cached by default, disable with `defaults.curve_caching = False`
3. **Thread Safety**: Objects are not thread-safe, use separate instances per thread
4. **Memory Management**: Large portfolios should use `clear_cache()` periodically
5. **Rust Acceleration**: Performance-critical paths automatically use Rust implementations

This reference covers the primary classes and methods in rateslib. For detailed parameter descriptions and advanced usage, refer to the inline documentation and example scripts.
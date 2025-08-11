# Rateslib Architecture

## Class Hierarchy Diagram

```mermaid
classDiagram
    %% Core Mixins and Base Classes
    class _WithCache {
        <<mixin>>
        +_cache: dict
        +_clear_cache()
    }
    
    class _WithState {
        <<mixin>>
        +_state: int
        +_validate_states()
    }
    
    class _WithOperations {
        <<mixin>>
        +shift(spread)
        +roll(tenor)
        +translate(date)
    }
    
    class _WithMutability {
        <<mixin>>
        +_mutable: bool
        +_set_mutable()
    }
    
    %% Curve Hierarchy
    class _BaseCurve {
        <<abstract>>
        +nodes: dict
        +convention: str
        +calendar: Calendar
        +rate(date, tenor)
        +df(date)
    }
    
    class Curve {
        +interpolation: str
        +t: list
        +c: list
        +_set_ad_order(order)
    }
    
    class LineCurve {
        +interpolation: "linear"
        +gradient: float
    }
    
    class CompositeCurve {
        +curves: tuple
        +rate(date, tenor)
    }
    
    class MultiCsaCurve {
        +curves: list
        +csa_map: dict
    }
    
    %% Instrument Hierarchy
    class Metrics {
        +fixed_rate: float
        +float_spread: float
        +leg1: Leg
        +leg2: Leg
        +npv(curves, fx)
        +rate(curves)
        +delta(curves)
    }
    
    class BaseInstrument {
        <<abstract>>
        +curves: dict
        +spec: dict
    }
    
    class IRS {
        <<Interest Rate Swap>>
        +effective: date
        +termination: date
        +frequency: str
    }
    
    class FRA {
        <<Forward Rate Agreement>>
        +effective: date
        +termination: date
    }
    
    class XCS {
        <<Cross Currency Swap>>
        +leg1_currency: str
        +leg2_currency: str
    }
    
    %% Leg Hierarchy
    class BaseLeg {
        +periods: list
        +schedule: Schedule
        +npv(curves)
        +cashflows(curves)
    }
    
    class FixedLeg {
        +fixed_rate: float
        +notional: float
    }
    
    class FloatLeg {
        +float_spread: float
        +fixing_method: str
    }
    
    class IndexLeg {
        +index_base: float
        +index_method: str
    }
    
    %% Period Classes
    class BasePeriod {
        +start: date
        +end: date
        +dcf: float
    }
    
    class FixedPeriod {
        +fixed_rate: float
        +cashflow(curves)
    }
    
    class FloatPeriod {
        +float_spread: float
        +rate(curves)
    }
    
    %% Dual Number Classes
    class Dual {
        +real: float
        +dual: float
        +__add__()
        +__mul__()
        +exp()
    }
    
    class Dual2 {
        +real: float
        +dual1: float
        +dual2: float
    }
    
    class Variable {
        +value: float
        +gradient()
    }
    
    %% FX Classes
    class FXRates {
        +pairs: dict
        +base: str
        +rate(pair)
        +convert(amount, from, to)
    }
    
    class FXForwards {
        +fx_rates: FXRates
        +curves: dict
        +rate(pair, tenor)
    }
    
    %% Solver
    class Solver {
        +curves: dict
        +instruments: list
        +s: array
        +iterate()
        +solve()
    }
    
    %% Relationships
    _WithCache <|-- _BaseCurve
    _WithState <|-- _BaseCurve
    _WithOperations <|-- _BaseCurve
    _BaseCurve <|-- Curve
    _BaseCurve <|-- LineCurve
    _WithMutability <|-- Curve
    _WithMutability <|-- LineCurve
    
    Curve <|-- CompositeCurve
    Curve <|-- MultiCsaCurve
    
    Metrics <|-- BaseInstrument
    BaseInstrument <|-- IRS
    BaseInstrument <|-- FRA
    BaseInstrument <|-- XCS
    
    BaseLeg <|-- FixedLeg
    BaseLeg <|-- FloatLeg
    BaseLeg <|-- IndexLeg
    
    BasePeriod <|-- FixedPeriod
    BasePeriod <|-- FloatPeriod
    
    BaseInstrument o-- BaseLeg : has legs
    BaseLeg o-- BasePeriod : has periods
    Solver o-- Curve : calibrates
    Solver o-- BaseInstrument : uses
    FXForwards o-- FXRates : uses
    FXForwards o-- Curve : uses
```

## Key Design Patterns

### 1. Mixin Architecture
The codebase uses multiple mixins to compose functionality:
- `_WithCache`: Provides caching capabilities for expensive computations
- `_WithState`: Manages state validation across operations
- `_WithOperations`: Adds curve transformation operations (shift, roll, translate)
- `_WithMutability`: Controls whether objects can be modified

### 2. Dual Number System
Automatic differentiation is implemented through:
- `Dual`: First-order derivatives
- `Dual2`: Second-order derivatives
- `Variable`: Gradient tracking
- All mathematical operations are overloaded to propagate derivatives

### 3. Curve Composition
- `Curve`: Base implementation with various interpolation methods
- `LineCurve`: Specialized linear interpolation
- `CompositeCurve`: Sums multiple curves
- `MultiCsaCurve`: Handles multiple collateral agreements

### 4. Instrument-Leg-Period Hierarchy
Financial instruments are decomposed into:
1. **Instruments**: High-level contracts (IRS, FRA, XCS)
2. **Legs**: Payment streams (Fixed, Float, Index)
3. **Periods**: Individual payment periods with cashflow calculations

### 5. FX Integration
- `FXRates`: Spot FX rates with conversion
- `FXForwards`: Forward FX rates using interest rate differentials
- Deep integration with curves for cross-currency instruments

### 6. Solver Pattern
- Calibrates curves to match market instrument prices
- Uses Newton-Raphson with automatic differentiation
- Handles multiple curves and instruments simultaneously

## Data Flow

```mermaid
graph TD
    A[Market Data] --> B[Curves]
    B --> C[Instruments]
    C --> D[Legs]
    D --> E[Periods]
    E --> F[Cashflows]
    F --> G[NPV/Price]
    
    H[Solver] --> B
    G --> H
    
    I[FXRates] --> C
    I --> F
    
    J[Dual Numbers] --> B
    J --> C
    J --> H
```

## Python-Rust Integration

```mermaid
graph LR
    subgraph Python
        PyCurve[Curve]
        PyInst[Instruments]
        PySolver[Solver]
    end
    
    subgraph Rust["Rust (via PyO3)"]
        RsInterp[Interpolation]
        RsDual[Dual Arithmetic]
        RsCal[Calendars]
        RsFX[FX Calculations]
    end
    
    PyCurve --> RsInterp
    PyCurve --> RsDual
    PyInst --> RsCal
    PyInst --> RsFX
    PySolver --> RsDual
```

## Module Dependencies

```mermaid
graph TD
    curves --> dual
    curves --> scheduling
    instruments --> curves
    instruments --> legs
    instruments --> periods
    legs --> periods
    periods --> dual
    solver --> curves
    solver --> instruments
    solver --> dual
    fx --> curves
    instruments --> fx
```

## Detailed Component Analysis

### Curve System Architecture

```mermaid
classDiagram
    class CompositeCurve {
        +curves: tuple[_BaseCurve]
        +rate(date) : sum of all curve rates
    }

    class MultiCsaCurve {
        +curves: list[Curve]
        +rate(date) : max rate among curves
    }

    class ShiftedCurve {
        +obj: _BaseCurve
        +spread: DualTypes
        +rate(date) : original + spread
    }

    class RolledCurve {
        +obj: _BaseCurve
        +roll_days: int
        +rate(date) : time-shifted rate
    }

    class TranslatedCurve {
        +obj: _BaseCurve
        +start: datetime
        +rate(date) : date-adjusted rate
    }

    _BaseCurve <|-- CompositeCurve
    _BaseCurve <|-- MultiCsaCurve
    _BaseCurve <|-- ShiftedCurve
    _BaseCurve <|-- RolledCurve
    _BaseCurve <|-- TranslatedCurve
```

### FX System Architecture

```mermaid
flowchart TD
    A[FX Market Data] --> B[FXRates Object]
    B --> C[Spot FX Pairs]
    C --> D[FXForwards Creation]
    
    D --> E[Local Currency Curves<br/>usdusd, eureur]
    D --> F[Cross-Currency Curves<br/>eurusd, nokeur]
    
    E --> G[Interest Rate Parity]
    F --> G
    
    G --> H[Forward FX Rate<br/>f = w_dom:for / v_for:for * F_spot]
    
    H --> I[Currency Conversion]
    H --> J[FX Swap Points]
    H --> K[Position Analysis]
    
    I --> L[Dual Number Output<br/>with Sensitivities]
    J --> L
    K --> M[Risk Decomposition]
```

### Instrument NPV Calculation Flow

```mermaid
sequenceDiagram
    participant Client
    participant Instrument
    participant Leg1
    participant Leg2
    participant Period
    participant Curve
    participant FX
    
    Client->>Instrument: npv(curves, fx)
    
    Instrument->>Leg1: npv(curves, fx)
    Instrument->>Leg2: npv(curves, fx)
    
    Leg1->>Period: For each period
    Period->>Period: cashflow()
    Period->>Curve: df(payment_date)
    Period->>FX: convert(amount, ccy, base)
    Period-->>Leg1: discounted cashflow
    
    Leg2->>Period: For each period
    Period->>Period: cashflow()
    Period->>Curve: df(payment_date)
    Period->>FX: convert(amount, ccy, base)
    Period-->>Leg2: discounted cashflow
    
    Leg1-->>Instrument: sum(cashflows)
    Leg2-->>Instrument: sum(cashflows)
    
    Instrument-->>Client: leg1_npv + leg2_npv
```

### Sensitivity Calculation Architecture

```mermaid
graph TB
    subgraph "Automatic Differentiation"
        A[Dual Numbers] --> B[First-order derivatives]
        C[Dual2 Numbers] --> D[Second-order derivatives]
        E[Variable] --> F[Gradient tracking]
    end
    
    subgraph "Risk Metrics"
        G[Delta] --> H[Price sensitivity to rate changes]
        I[Gamma] --> J[Convexity/second-order risk]
        K[Cross-gamma] --> L[Cross-curve sensitivities]
    end
    
    subgraph "Implementation"
        M[Curve nodes as Variables]
        N[FX rates as Variables]
        O[NPV calculation with Dual math]
        P[Extract gradients from result]
    end
    
    A --> G
    C --> I
    E --> K
    M --> O
    N --> O
    O --> P
    P --> H
    P --> J
    P --> L
```

## Performance Optimizations

### Caching Strategy
- `_WithCache` mixin provides automatic memoization
- Curve lookups cached to avoid repeated interpolation
- State validation ensures cache consistency

### Rust Acceleration Points
1. **Interpolation**: All interpolation methods implemented in Rust
2. **Date Arithmetic**: Calendar calculations in Rust
3. **Dual Arithmetic**: Core dual number operations in Rust
4. **FX Calculations**: Currency conversion logic optimized

### Parallel Computation Opportunities
- Multiple curve calibrations can run in parallel
- Independent leg calculations parallelizable
- Sensitivity bumps naturally parallel
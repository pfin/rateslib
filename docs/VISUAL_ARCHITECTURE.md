# Rateslib Visual Architecture Documentation

## System-Wide Architecture Overview

```mermaid
graph TB
    subgraph "Python API Layer"
        API[Public API]
        Instruments[Instruments]
        Curves[Curves]
        FX[FX System]
        Scheduling[Scheduling]
    end
    
    subgraph "Core Engine"
        Dual[Dual Numbers]
        Solver[Solvers]
        Cache[Cache System]
        State[State Management]
    end
    
    subgraph "Rust Acceleration Layer"
        RustCore[Rust Core via PyO3]
        RustInterp[Interpolation]
        RustMath[Mathematics]
        RustCal[Calendars]
        RustDual[Dual Arithmetic]
    end
    
    subgraph "Data Layer"
        Market[Market Data]
        Historical[Historical Data]
        Config[Configuration]
    end
    
    API --> Instruments
    API --> Curves
    API --> FX
    API --> Scheduling
    
    Instruments --> Dual
    Instruments --> Solver
    Curves --> Cache
    Curves --> State
    
    Dual --> RustDual
    Solver --> RustMath
    Cache --> RustCore
    State --> RustCore
    
    FX --> RustCore
    Scheduling --> RustCal
    
    Market --> API
    Historical --> API
    Config --> API
```

## Detailed Component Interactions

### 1. Curve Construction Pipeline

```mermaid
sequenceDiagram
    participant User
    participant Curve
    participant Solver
    participant Instruments
    participant RustCore
    participant Cache
    
    User->>Curve: Initialize with nodes
    Curve->>Cache: Check for existing data
    
    alt Cache miss
        Curve->>Solver: Request calibration
        Solver->>Instruments: Price instruments
        loop For each instrument
            Instruments->>RustCore: Calculate with dual numbers
            RustCore-->>Instruments: Return sensitivities
        end
        Instruments-->>Solver: Return pricing errors
        Solver->>Solver: Optimize parameters
        Solver-->>Curve: Return calibrated nodes
        Curve->>Cache: Store results
    else Cache hit
        Cache-->>Curve: Return cached data
    end
    
    Curve-->>User: Return calibrated curve
```

### 2. FX System Graph Theory

```mermaid
graph LR
    subgraph "Currency Graph"
        USD((USD))
        EUR((EUR))
        GBP((GBP))
        JPY((JPY))
        CHF((CHF))
        
        USD ---|1.10| EUR
        USD ---|0.80| GBP
        USD ---|150| JPY
        EUR ---|0.90| CHF
        GBP ---|1.20| EUR
    end
    
    subgraph "Path Finding"
        Start[EUR/JPY?]
        Path1[EUR→USD→JPY]
        Path2[EUR→GBP→USD→JPY]
        Select[Select Shortest]
    end
    
    subgraph "Triangulation"
        Rate1[Get EUR/USD]
        Rate2[Get USD/JPY]
        Calc[Multiply Rates]
        Result[EUR/JPY Rate]
    end
    
    Start --> Path1
    Start --> Path2
    Path1 --> Select
    Path2 --> Select
    Select --> Rate1
    Rate1 --> Rate2
    Rate2 --> Calc
    Calc --> Result
```

### 3. Automatic Differentiation Flow

```mermaid
flowchart TD
    subgraph "Dual Number Structure"
        Real[Real Value]
        Dual1[First Derivatives]
        Dual2[Second Derivatives]
    end
    
    subgraph "Operations"
        Add[Addition: (a+b, da+db, d²a+d²b)]
        Mul[Multiplication: (a×b, a×db+b×da, ...)]
        Exp[Exponential: (e^a, e^a×da, ...)]
        Log[Logarithm: (ln(a), da/a, ...)]
    end
    
    subgraph "Application"
        Price[Option Price]
        Delta[∂P/∂S = Delta]
        Gamma[∂²P/∂S² = Gamma]
        Vega[∂P/∂σ = Vega]
    end
    
    Real --> Add
    Dual1 --> Add
    Dual2 --> Add
    
    Add --> Mul
    Mul --> Exp
    Exp --> Log
    
    Log --> Price
    Price --> Delta
    Price --> Gamma
    Price --> Vega
```

## Performance Architecture

### Memory Layout and Caching Strategy

```mermaid
graph TD
    subgraph "Memory Hierarchy"
        L1[L1: Hot Path Cache<br/>~32KB, <1ns]
        L2[L2: Curve Cache<br/>~256KB, ~4ns]
        L3[L3: Shared Cache<br/>~8MB, ~12ns]
        RAM[RAM: Full Data<br/>~GB, ~100ns]
    end
    
    subgraph "Cache Strategy"
        Hot[Frequently Used<br/>Curves & Rates]
        Warm[Recent Calculations<br/>& Interpolations]
        Cold[Historical Data<br/>& Rare Curves]
    end
    
    subgraph "Rust Optimization"
        SIMD[SIMD Operations]
        Vectorized[Vectorized Math]
        Parallel[Parallel Processing]
    end
    
    Hot --> L1
    Warm --> L2
    Cold --> L3
    L3 --> RAM
    
    L1 --> SIMD
    L2 --> Vectorized
    L3 --> Parallel
```

### Computational Complexity Analysis

```mermaid
graph LR
    subgraph "Operations Complexity"
        Linear[Linear Interpolation<br/>O(log n)]
        Spline[Spline Evaluation<br/>O(log n)]
        Solving[Curve Solving<br/>O(n² × m)]
        FXPath[FX Path Finding<br/>O(V + E)]
    end
    
    subgraph "Optimization Techniques"
        Binary[Binary Search<br/>for Nodes]
        Cache[Result Caching<br/>O(1) lookup]
        Precomp[Pre-computation<br/>of Coefficients]
        Rust[Rust Acceleration<br/>10-100x speedup]
    end
    
    Linear --> Binary
    Spline --> Precomp
    Solving --> Cache
    FXPath --> Rust
```

## Instrument Pricing Architecture

### Bond Pricing Pipeline

```mermaid
flowchart LR
    subgraph "Input Data"
        Bond[Bond Definition]
        Curve[Yield Curve]
        Calendar[Calendar]
    end
    
    subgraph "Schedule Generation"
        Dates[Payment Dates]
        DCF[Day Count Fractions]
        Adjust[Business Day Adj]
    end
    
    subgraph "Cash Flow Generation"
        Coupons[Coupon Payments]
        Principal[Principal Payment]
        Accrued[Accrued Interest]
    end
    
    subgraph "Discounting"
        DF[Discount Factors]
        PV[Present Values]
        NPV[Net Present Value]
    end
    
    subgraph "Analytics"
        YTM[Yield to Maturity]
        Duration[Duration/Convexity]
        Risk[Risk Measures]
    end
    
    Bond --> Dates
    Calendar --> Dates
    Dates --> DCF
    DCF --> Adjust
    
    Adjust --> Coupons
    Adjust --> Principal
    Coupons --> Accrued
    
    Curve --> DF
    Coupons --> PV
    Principal --> PV
    DF --> PV
    
    PV --> NPV
    NPV --> YTM
    NPV --> Duration
    Duration --> Risk
```

### Swap Valuation Architecture

```mermaid
flowchart TD
    subgraph "Swap Structure"
        Fixed[Fixed Leg]
        Float[Floating Leg]
        Notional[Notional Schedule]
    end
    
    subgraph "Rate Determination"
        Forecast[Forecast Curve]
        Discount[Discount Curve]
        Fixing[Historical Fixings]
    end
    
    subgraph "Valuation"
        FixedPV[Fixed Leg PV]
        FloatPV[Float Leg PV]
        SwapPV[Swap NPV]
    end
    
    subgraph "Sensitivities"
        DV01[DV01/PV01]
        ParRate[Par Swap Rate]
        Greeks[Greeks via AD]
    end
    
    Fixed --> FixedPV
    Float --> FloatPV
    Notional --> FixedPV
    Notional --> FloatPV
    
    Discount --> FixedPV
    Forecast --> FloatPV
    Discount --> FloatPV
    Fixing --> FloatPV
    
    FixedPV --> SwapPV
    FloatPV --> SwapPV
    
    SwapPV --> DV01
    SwapPV --> ParRate
    SwapPV --> Greeks
```

## State Management Pattern

```mermaid
stateDiagram-v2
    [*] --> Uninitialized
    
    Uninitialized --> Initializing: set_nodes()
    Initializing --> Valid: validate()
    
    Valid --> Calculating: calculate()
    Calculating --> Cached: store_result()
    
    Cached --> Valid: clear_cache()
    Valid --> Invalid: modify_nodes()
    Invalid --> Valid: recalibrate()
    
    Valid --> [*]: destroy()
    Cached --> [*]: destroy()
    
    state Valid {
        [*] --> Ready
        Ready --> Computing: request
        Computing --> Ready: complete
    }
    
    state Cached {
        [*] --> Fresh
        Fresh --> Stale: timeout
        Stale --> Fresh: refresh
    }
```

## Multi-Currency Portfolio Architecture

```mermaid
graph TB
    subgraph "Portfolio Structure"
        P1[USD Bonds]
        P2[EUR Swaps]
        P3[JPY Options]
        P4[GBP Futures]
    end
    
    subgraph "FX Layer"
        FXRates[Spot Rates]
        FXForwards[Forward Rates]
        Basis[Cross-Ccy Basis]
    end
    
    subgraph "Curves per Currency"
        USDC[USD Curves]
        EURC[EUR Curves]
        JPYC[JPY Curves]
        GBPC[GBP Curves]
    end
    
    subgraph "Aggregation"
        Convert[Convert to Base]
        Aggregate[Sum Positions]
        Risk[Risk Metrics]
    end
    
    P1 --> USDC
    P2 --> EURC
    P3 --> JPYC
    P4 --> GBPC
    
    USDC --> Convert
    EURC --> Convert
    JPYC --> Convert
    GBPC --> Convert
    
    FXRates --> Convert
    FXForwards --> Convert
    Basis --> Convert
    
    Convert --> Aggregate
    Aggregate --> Risk
```

## Solver Architecture

```mermaid
flowchart TD
    subgraph "Solver Types"
        Newton[Newton-Raphson]
        LM[Levenberg-Marquardt]
        Trust[Trust Region]
        BFGS[BFGS Quasi-Newton]
    end
    
    subgraph "Problem Setup"
        Objective[Objective Function]
        Jacobian[Jacobian Matrix]
        Constraints[Constraints]
    end
    
    subgraph "Iteration"
        Eval[Evaluate f(x)]
        Gradient[Calculate ∇f(x)]
        Direction[Search Direction]
        Step[Line Search]
        Update[Update x]
    end
    
    subgraph "Convergence"
        Check{Converged?}
        Tolerance[|f(x)| < ε]
        MaxIter[iter < max]
    end
    
    Objective --> Eval
    Jacobian --> Gradient
    Constraints --> Direction
    
    Newton --> Direction
    LM --> Direction
    Trust --> Direction
    BFGS --> Direction
    
    Eval --> Gradient
    Gradient --> Direction
    Direction --> Step
    Step --> Update
    Update --> Check
    
    Check -->|No| Eval
    Check -->|Yes| Tolerance
    Tolerance --> MaxIter
```

## Calendar System Architecture

```mermaid
graph LR
    subgraph "Calendar Types"
        Named[Named Calendars<br/>NYC, LDN, TGT]
        Custom[Custom Calendars<br/>User Defined]
        Union[Union Calendars<br/>Multiple Centers]
    end
    
    subgraph "Operations"
        IsBD[Is Business Day?]
        AddBD[Add Business Days]
        Adjust[Adjust Date]
        Roll[Roll Convention]
    end
    
    subgraph "Cache Layer"
        PreCache[Pre-cached Common]
        Dynamic[Dynamic Cache]
        LRU[LRU Eviction]
    end
    
    subgraph "Rust Backend"
        BitSet[BitSet Holidays]
        FastLookup[O(1) Lookup]
        SIMD2[SIMD Date Ops]
    end
    
    Named --> PreCache
    Custom --> Dynamic
    Union --> Dynamic
    
    PreCache --> IsBD
    Dynamic --> IsBD
    
    IsBD --> BitSet
    AddBD --> FastLookup
    Adjust --> SIMD2
    Roll --> FastLookup
```

## Risk System Architecture

```mermaid
flowchart TD
    subgraph "Risk Metrics"
        Market[Market Risk]
        Credit[Credit Risk]
        Liquidity[Liquidity Risk]
    end
    
    subgraph "Sensitivities"
        Delta2[Delta/DV01]
        Gamma2[Gamma/Convexity]
        Vega2[Vega]
        Theta[Theta]
        Rho[Rho]
    end
    
    subgraph "Calculation Methods"
        Analytical[Analytical]
        Numerical[Numerical Bumping]
        AD[Automatic Diff]
        MC[Monte Carlo]
    end
    
    subgraph "Aggregation"
        Portfolio[Portfolio Level]
        Book[Book Level]
        Firm[Firm Level]
    end
    
    Market --> Delta2
    Market --> Gamma2
    Market --> Vega2
    
    Delta2 --> Analytical
    Delta2 --> AD
    Gamma2 --> Numerical
    Vega2 --> AD
    
    Analytical --> Portfolio
    Numerical --> Portfolio
    AD --> Portfolio
    
    Portfolio --> Book
    Book --> Firm
```

## Data Flow Architecture

```mermaid
graph TD
    subgraph "Data Sources"
        Bloomberg[Bloomberg]
        Reuters[Reuters]
        Files[CSV/JSON Files]
        API[REST APIs]
    end
    
    subgraph "Data Processing"
        Validate[Validation]
        Clean[Cleaning]
        Transform[Transformation]
        Enrich[Enrichment]
    end
    
    subgraph "Storage"
        Memory[In-Memory]
        Cache2[Redis Cache]
        DB[Database]
        Files2[File System]
    end
    
    subgraph "Consumption"
        Pricing[Pricing Engine]
        Risk2[Risk Engine]
        Reports[Reporting]
        Analytics[Analytics]
    end
    
    Bloomberg --> Validate
    Reuters --> Validate
    Files --> Validate
    API --> Validate
    
    Validate --> Clean
    Clean --> Transform
    Transform --> Enrich
    
    Enrich --> Memory
    Enrich --> Cache2
    Enrich --> DB
    
    Memory --> Pricing
    Memory --> Risk2
    Cache2 --> Reports
    DB --> Analytics
```

## Summary

This visual architecture documentation reveals rateslib's sophisticated design:

1. **Hybrid Architecture**: Seamless Python/Rust integration via PyO3
2. **Performance Optimization**: Multi-level caching and SIMD operations
3. **Mathematical Rigor**: Automatic differentiation throughout
4. **Scalability**: Efficient state management and parallel processing
5. **Flexibility**: Composable components with clean interfaces

The architecture supports institutional-grade fixed income analytics while maintaining code clarity and performance.
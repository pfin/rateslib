# FXRates.py Documentation

## Overview
Demonstrates foreign exchange rate calculations, triangulation, and forward FX pricing using interest rate parity. This module showcases the sophisticated FX framework in rateslib that handles multi-currency scenarios with automatic differentiation for risk calculation.

## Key Concepts
- **FX Triangulation**: Calculate cross rates through intermediate currencies using no-arbitrage principles
- **Interest Rate Parity**: Forward FX pricing based on covered interest rate parity theory
- **Dual Number Integration**: Automatic differentiation for FX sensitivities (Greeks)
- **Settlement Date Consistency**: All FX rates must share common settlement dates
- **Position Management**: Multi-currency portfolio valuation and hedging

## Mathematical Framework

### FX Rate Matrix Structure
The FX rate system maintains an n×n matrix for n currencies, where:
```
FX_ij = Rate from currency i to currency j
FX_ji = 1 / FX_ij (reciprocal relationship)
FX_ik = FX_ij × FX_jk (triangulation through intermediate currency j)
```

### Interest Rate Parity Formula
Forward FX rates follow covered interest rate parity:
```
F(t) = S × [DF_foreign(t) / DF_domestic(t)]
```
Where:
- F(t) = Forward rate at time t
- S = Spot rate
- DF = Discount factor from respective curves

### Cross-Currency Basis Integration
When cross-currency curves differ from local curves:
```
F(t) = S × [DF_foreign:domestic(t) / DF_domestic:domestic(t)]
```

## Class Architecture Diagrams

### FXRates Class Structure
```
FXRates
├── fx_array: np.ndarray[n×n]     # Full rate matrix
├── currencies: Dict[str, int]    # Currency index mapping
├── base: str                     # Base currency (index 0)
├── settlement: datetime          # Common settlement date
├── obj: FXRatesObj              # Rust backend object
└── Methods:
    ├── rate(pair: str) -> float
    ├── convert(amount, from, to) -> float
    ├── convert_positions(amounts, base) -> float
    ├── positions(value, base) -> List[float]
    ├── restate(pairs) -> FXRates
    └── update(rates) -> None
```

### FXForwards Class Structure
```
FXForwards
├── fx_rates: FXRates | List[FXRates]  # Settlement-specific rates
├── fx_curves: Dict[str, Curve]        # Discount curves by currency pair
├── currencies: Dict[str, int]         # Multi-currency mapping
├── _paths: Dict                       # Triangulation paths
└── Methods:
    ├── rate(pair, date) -> float
    ├── positions(pv, base) -> array
    └── update() -> None
```

## State Transition Diagrams

### FX Rate Validation Flow
```
Input Rates → Validation → Matrix Construction → Triangulation Check → Object Creation
     ↓              ↓              ↓                    ↓                ↓
[Dict pairs]   [No cycles]   [n×n matrix]        [Consistency]    [FXRates obj]
     ↓              ↓              ↓                    ↓                ↓
Error if:      Error if:      Fill missing        Error if:        Success
- Malformed    - Redundant    cross rates         - Arbitrage
- Missing      - Inverse
- Invalid      pairs
```

### Forward Rate Calculation Flow
```
Spot Rate → Curve Lookup → Discount Factors → Forward Calculation → Cache Result
    ↓            ↓              ↓                    ↓               ↓
[FXRates]   [fx_curves]   [DF_dom, DF_for]    [F = S × DF_r]   [Store]
    ↓            ↓              ↓                    ↓               ↓
From base    By currency    At maturity         Apply parity     For reuse
settlement   pair key       date                formula
```

## FX Triangulation Algorithms

### Direct Path Algorithm
```python
def get_direct_rate(ccy1: str, ccy2: str) -> float:
    """Get rate directly from stored pairs"""
    pair = f"{ccy1}{ccy2}"
    if pair in stored_pairs:
        return stored_pairs[pair]
    elif f"{ccy2}{ccy1}" in stored_pairs:
        return 1.0 / stored_pairs[f"{ccy2}{ccy1}"]
    else:
        return None  # Requires triangulation
```

### Triangulation Path Algorithm
```python
def triangulate_rate(ccy1: str, ccy2: str, base: str) -> float:
    """Calculate cross rate through base currency"""
    rate_1_to_base = get_rate_to_base(ccy1, base)
    rate_2_to_base = get_rate_to_base(ccy2, base)
    return rate_1_to_base / rate_2_to_base
```

### Multi-Hop Triangulation
For complex currency networks, the system uses Dijkstra-like shortest path:
```python
def find_shortest_path(from_ccy: str, to_ccy: str) -> List[str]:
    """Find minimum-hop path between currencies"""
    # Graph traversal through available currency pairs
    # Minimizes calculation error accumulation
```

## Real-World Use Cases

### 1. Multi-Currency Portfolio Valuation
```python
# Portfolio with EUR, GBP, JPY positions
fxr = FXRates({
    "eurusd": 1.0850,
    "gbpusd": 1.2650,
    "usdjpy": 149.50
}, settlement=dt(2024, 1, 15))

# Convert all positions to USD base
positions = [1_000_000, 500_000, 50_000_000]  # EUR, GBP, JPY
total_usd = fxr.convert_positions(positions, "usd")
```

### 2. Forward Hedging Strategy
```python
# 6-month EUR/USD hedge
fxf = FXForwards(fx_rates, fx_curves)
forward_6m = fxf.rate("eurusd", dt(2024, 7, 15))

# Hedge a 1M EUR receivable
hedge_rate = forward_6m
hedge_notional = 1_000_000  # EUR
usd_receivable = hedge_notional * hedge_rate
```

### 3. Cross-Currency Basis Trading
```python
# Exploit basis differences in EUR/USD vs EUR/GBP/USD
implied_eurgbp = fxf.rate("eurusd", date) / fxf.rate("gbpusd", date)
market_eurgbp = fxf.rate("eurgbp", date)
basis_opportunity = implied_eurgbp - market_eurgbp
```

### 4. Risk Management with Greeks
```python
# FX delta calculation using automatic differentiation
fxr._set_ad_order(1)  # Enable first-order derivatives
portfolio_value = fxr.convert_positions(positions, "usd")

# Extract FX sensitivities
fx_deltas = gradient(portfolio_value, ["fx_eurusd", "fx_gbpusd", "fx_usdjpy"])
```

## Financial Mathematics Implementation

### No-Arbitrage Constraints
The system enforces triangle inequality constraints:
```
For currencies A, B, C:
FX_AC ≈ FX_AB × FX_BC (within tolerance)
```

### Settlement Date Handling
Multiple settlement conventions are managed:
```python
# T+2 for major pairs, T+1 for others
fxr_major = FXRates({"eurusd": 1.08}, settlement=dt(2024, 1, 17))  # T+2
fxr_minor = FXRates({"usdcad": 1.35}, settlement=dt(2024, 1, 16))  # T+1

# Forward calculator handles mixed settlements
fxf = FXForwards(fx_rates=[fxr_major, fxr_minor], fx_curves=curves)
```

### Cross-Currency Discounting
Different collateral currencies require different curves:
```python
fx_curves = {
    "usdusd": usd_ois_curve,      # USD cash, USD collateral
    "eureur": eur_ois_curve,      # EUR cash, EUR collateral  
    "eurusd": eur_xccy_curve,     # EUR cash, USD collateral
    "usdeur": usd_xccy_curve      # USD cash, EUR collateral
}
```

## Error Handling and Validation

### Common Error Patterns
1. **Overspecified Markets**: Too many independent rates
2. **Underspecified Markets**: Missing rate connections
3. **Inconsistent Rates**: Arbitrage opportunities
4. **Settlement Mismatches**: Different value dates

### Validation Algorithm
```python
def validate_fx_market(rates: Dict[str, float]) -> bool:
    n_currencies = count_unique_currencies(rates)
    n_pairs = len(rates)
    
    # Must have exactly n-1 independent pairs for n currencies
    if n_pairs != n_currencies - 1:
        raise ValueError("Market specification error")
    
    # Check for arbitrage using triangle inequalities
    check_triangulation_consistency(rates)
```

## Performance Optimizations

### Matrix Caching
The `fx_array` property is cached to avoid repeated conversions:
```python
@cached_property
def fx_array(self) -> np.ndarray:
    """Cache the full n×n FX matrix"""
    return np.array(self.obj.fx_array)
```

### Rust Backend Integration
Performance-critical calculations delegated to Rust:
- Matrix operations for large currency sets
- Dual number arithmetic for derivatives
- Path finding for triangulation

### Automatic Differentiation
Seamless integration with Dual/Dual2 types:
```python
# Forward mode AD for FX sensitivities
fxr._set_ad_order(2)  # Enable second-order derivatives
pv_with_gamma = fxr.convert(amount, "eur", "usd")
# Result contains value, delta, and gamma automatically
```

## Advanced Features

### Position Decomposition
Break down aggregate values into currency-specific positions:
```python
# From aggregated USD value to individual currency amounts
total_usd = Dual(100_000, ["fx_eurusd"], [-50_000])  # With sensitivity
positions = fxr.positions(total_usd, "usd")  # Returns [EUR_amt, USD_amt]
```

### Market Restatement
Convert between different market quoting conventions:
```python
# From crosses to majors
fxr_crosses = FXRates({"eurusd": 1.08, "gbpjpy": 190, "eurjpy": 162})
fxr_majors = fxr_crosses.restate(["eurusd", "usdjpy", "gbpusd"])
```

### Dynamic Updates
Synchronized updates for real-time pricing:
```python
fxf.update([{"eurusd": 1.0851}, {"gbpusd": 1.2655}])  # Live market data
```

## Usage Examples

### Basic FX Operations
```bash
cd python/
python ../scripts/examples/coding_2/FXRates.py
```

### Integration Testing
```python
# Test full workflow
from rateslib import FXRates, FXForwards, Curve, dt

# 1. Create spot rates
fxr = FXRates({"eurusd": 1.08, "gbpusd": 1.26})

# 2. Build forward calculator  
curves = build_curves()  # Helper function
fxf = FXForwards(fxr, curves)

# 3. Price forward contracts
forward_3m = fxf.rate("eurgbp", dt(2024, 4, 15))

# 4. Calculate portfolio sensitivities
fxr._set_ad_order(1)
portfolio_pv = calculate_portfolio(fxf)  # User function
sensitivities = gradient(portfolio_pv, fxr.pairs)
```

## Common Currency Classifications

### Major Pairs (G10 currencies)
- **EURUSD**: Euro/US Dollar (most liquid)
- **GBPUSD**: British Pound/US Dollar  
- **USDJPY**: US Dollar/Japanese Yen
- **USDCHF**: US Dollar/Swiss Franc
- **AUDUSD**: Australian Dollar/US Dollar
- **USDCAD**: US Dollar/Canadian Dollar
- **NZDUSD**: New Zealand Dollar/US Dollar

### Cross Pairs (No USD)
- **EURGBP**: Euro/British Pound
- **EURJPY**: Euro/Japanese Yen  
- **GBPJPY**: British Pound/Japanese Yen
- **EURCHF**: Euro/Swiss Franc
- **GBPCHF**: British Pound/Swiss Franc

### Exotic Pairs (Emerging markets)
- **USDTRY**: US Dollar/Turkish Lira
- **USDZAR**: US Dollar/South African Rand
- **USDMXN**: US Dollar/Mexican Peso
- **USDCNH**: US Dollar/Chinese Yuan (offshore)
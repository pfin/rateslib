# FXRates.py Documentation

## Overview
Demonstrates foreign exchange rate calculations, triangulation, and forward FX pricing using interest rate parity.

## Key Concepts
- **FX Triangulation**: Calculate cross rates through intermediate currencies
- **Interest Rate Parity**: Forward FX = Spot × (1+r_domestic)/(1+r_foreign)
- **FXRates Class**: Manages spot FX rates and cross calculations
- **FXForwards**: Calculates forward FX rates from curves

## Sections

### 1. FXRates Basic Usage
Creates FX rate object and performs conversions:
```python
fxr = FXRates({"eurusd": 1.05, "gbpusd": 1.25})
```

### 2. Cross Rate Calculation
Automatically calculates rates through triangulation:
- Direct rates: Stored explicitly
- Cross rates: Calculated via common currency (usually USD)
- Example: EURGBP = EURUSD / GBPUSD

### 3. Rate Conversion Methods
- `rate("eurusd")`: Get specific pair rate
- `convert(amount, from_ccy, to_ccy)`: Convert amounts
- Handles inverse pairs automatically (USDEUR from EURUSD)

### 4. FX Forwards
Uses interest rate parity for forward pricing:
```
Forward = Spot × (1 + r_domestic × t) / (1 + r_foreign × t)
```
Requires:
- Spot FX rates
- Interest rate curves for both currencies

### 5. Update and Shift Operations
- `update()`: Modify existing rates
- `shift()`: Adjust all rates by percentage
- Maintains triangulation consistency

## Classes
- `FXRates`: Spot FX rate management
- `FXForwards`: Forward FX calculations
- `FXForwardsMatrix`: Multi-currency forward matrix

## Convention
- Always quote as Base/Quote (e.g., EUR/USD)
- EUR/USD = 1.10 means 1 EUR = 1.10 USD
- Inverse: USD/EUR = 1/1.10 = 0.909

## Triangulation Example
Given:
- EUR/USD = 1.10
- GBP/USD = 1.25

Calculate EUR/GBP:
- EUR/GBP = EUR/USD ÷ GBP/USD = 1.10 ÷ 1.25 = 0.88

## Usage
```bash
cd python/
python ../scripts/examples/coding_2/FXRates.py
```

## Common Currency Pairs
- Major pairs: EURUSD, GBPUSD, USDJPY, USDCHF
- Cross pairs: EURGBP, EURJPY, GBPJPY
- Exotic pairs: USDTRY, USDZAR, USDMXN
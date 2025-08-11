# curves.py Documentation

## Overview
Demonstrates fundamental curve operations with emphasis on automatic differentiation and performance optimization. This script serves as a practical introduction to rateslib's curve framework, showing both correct usage patterns and common pitfalls to avoid.

## Known Issues and Best Practices
This script contains examples of **deprecated private API usage** that should be replaced:

### ❌ Incorrect (Private API)
```python
line_curve1._set_ad_order(1)  # DEPRECATED
line_curve2._set_ad_order(1)  # DEPRECATED
```

### ✅ Correct (Public API)  
```python
line_curve1 = LineCurve(..., ad=1)  # RECOMMENDED
line_curve2 = LineCurve(..., ad=1)  # RECOMMENDED
```

## Architectural Insights
This script demonstrates the layered architecture of rateslib curves:
- **API Layer**: Public methods for curve construction and queries
- **State Management**: Automatic cache invalidation and validation
- **Computation Engine**: Rust-accelerated mathematical operations
- **Memory Model**: Efficient storage and reference sharing

## Key Concepts Demonstrated
- **CompositeCurve Mechanics**: How multiple curves are efficiently combined
- **Automatic Differentiation**: Dual number propagation through calculations  
- **Performance Trade-offs**: Strategic approximation vs precision decisions
- **Error Analysis**: Quantitative assessment of computational shortcuts

## Sections

### 1. CompositeCurve with AD
Shows how to enable automatic differentiation:
```python
# Incorrect (private API):
line_curve1._set_ad_order(1)

# Correct (public API):
line_curve1 = LineCurve(..., ad=1)
```

### 2. Error Analysis
Compares approximation errors in composite rates:
- True compounded rates
- Averaged approximations
- Error distribution analysis

### 3. Performance Timing
Benchmarks approximate vs exact calculations:
- Approximate: ~2x faster
- Trade-off: Speed vs accuracy
- Errors typically < 1e-5

### 4. Curve Operations Deep Dive
Comprehensive testing of transformation operations across curve types:

#### Mathematical Operations
- **Shift**: Parallel displacement in rate space
  - Implementation: Creates `ShiftedCurve` wrapper with lazy evaluation
  - Use case: Scenario analysis and stress testing
  - Performance: O(1) creation, original complexity for queries

- **Roll**: Time translation of the entire curve
  - Implementation: `RolledCurve` with date arithmetic
  - Use case: Historical analysis and backtesting
  - Mathematical basis: Preserves curve shape in time

- **Translate**: Reference date adjustment maintaining future values
  - Implementation: `TranslatedCurve` with interpolation adjustments
  - Use case: Portfolio revaluation and reporting date changes
  - Constraint: Some interpolation methods may not support translation

## Technical Debt and Migration Path

### Immediate Corrections Needed
1. **Replace Private API Calls**:
   ```python
   # Current (broken)
   curve._set_ad_order(1)
   
   # Corrected
   curve = Curve(..., ad=1)
   ```

2. **Update Import Statements**:
   ```python
   from rateslib.curves import Curve, LineCurve, CompositeCurve
   ```

3. **Standardize Error Handling**:
   ```python
   try:
       result = curve.rate(date, tenor)
   except ValueError as e:
       # Handle rate calculation errors
       pass
   ```

### Long-term Architecture Improvements
- Migrate to builder pattern for complex curve configurations
- Implement async curve construction for large datasets
- Add type hints for better IDE support and static analysis

## Usage
```bash
cd python/
python ../scripts/examples/coding/curves.py
```
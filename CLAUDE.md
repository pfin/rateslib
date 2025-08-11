# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important File Management Rules

**NEVER create new files unless explicitly asked.** Always prefer modifying existing files:
- If documentation is needed, extend existing docs
- If scripts need enhancement, modify the originals
- If examples are needed, add to existing examples
- Always come up with a plan for file modification first
- Only create new files when specifically requested by the user

## Project Overview

Rateslib is a state-of-the-art fixed income library for Python that provides advanced financial analysis capabilities for interest rates, derivatives, swaps, bonds, and other fixed income instruments. It's a hybrid Python/Rust project using PyO3 for performance-critical components.

## Local Development Setup

### Prerequisites
- Python 3.10+ (tested with 3.12)
- Rust toolchain (installed via rustup)
- Conda or similar environment manager

### Environment Setup
```bash
# Create conda environment with Python 3.12
conda create -n rateslib-dev python=3.12 -y
conda activate rateslib-dev

# Install Rust if not already installed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# Install build tools and dependencies
pip install maturin numpy matplotlib pandas pytest coverage ruff mypy pandas-stubs

# Build the Rust extension (from project root)
maturin develop --release
```

### Working Directory Structure
```
rateslib/
├── python/           # Python source code
│   ├── rateslib/    # Main package
│   └── tests/       # Test suite
├── rust/            # Rust source code
├── Cargo.toml       # Rust configuration
└── pyproject.toml   # Python configuration
```

### Running Code Locally

**IMPORTANT**: To work with rateslib locally without installation, you must be in the `python/` directory:

```bash
cd python
python
>>> import rateslib
>>> print(rateslib.__version__)
2.1.0
```

### Testing

**CRITICAL**: Tests MUST be run from the `python/` directory using `python -m pytest` (not just `pytest`). This ensures the local rateslib module can be imported without installation.

#### Prerequisites for Testing
```bash
# Ensure you're in the project root
cd /path/to/rateslib

# Activate the conda environment
conda activate rateslib-dev

# Navigate to the python directory (REQUIRED)
cd python
```

#### Running Tests

##### Basic Test Execution
```bash
# Run all tests with default output
python -m pytest tests/

# Run all tests with quiet output (dots only)
python -m pytest tests/ -q

# Run all tests with verbose output (show each test name)
python -m pytest tests/ -v

# Run tests with no traceback (useful for clean output)
python -m pytest tests/ --tb=no
```

##### Running Specific Tests
```bash
# Run a specific test file
python -m pytest tests/test_curves.py

# Run a specific test class
python -m pytest tests/test_curves.py::TestCurve

# Run a specific test method
python -m pytest tests/test_curves.py::TestCurve::test_interpolation

# Run tests matching a pattern
python -m pytest tests/ -k "test_fx"

# Run specific test directory
python -m pytest tests/scheduling/
```

##### Test Collection and Discovery
```bash
# Count total tests without running them
python -m pytest tests/ --collect-only -q | tail -1
# Output: 3758 tests collected

# List all test names without running
python -m pytest tests/ --collect-only -q

# Show test collection tree
python -m pytest tests/ --collect-only
```

#### Coverage Analysis

##### Running Tests with Coverage
```bash
# Run all tests with coverage collection
python -m coverage run -m pytest tests/ -q

# Run specific tests with coverage
python -m coverage run -m pytest tests/test_curves.py
```

##### Coverage Reports
```bash
# Generate terminal coverage report
python -m coverage report

# Show only files with missing coverage
python -m coverage report --skip-covered --skip-empty

# Generate detailed HTML coverage report
python -m coverage html
# Open htmlcov/index.html in browser

# Generate XML coverage report (for CI/CD)
python -m coverage xml

# Show coverage for specific files
python -m coverage report --include="rateslib/curves/*"
```

#### Test Results (Verified)

##### Test Statistics
- **Total Tests Collected**: 3,758
- **Tests Passed**: 3,684 ✅
- **Tests Skipped**: 74 ⚠️
- **Warnings**: 10 ⚠️
- **Execution Time**: 
  - Without coverage: ~27-28 seconds
  - With coverage: ~43 seconds

##### Coverage Statistics
- **Overall Coverage**: **97%** 🎯
- **Total Lines**: 20,990
- **Lines Covered**: 20,340
- **Lines Missed**: 650

##### Coverage by Major Module
| Module | Lines | Coverage | Description |
|--------|-------|----------|-------------|
| `legs/` | ~700 | **99%** | Cash flow generation |
| `periods/` | ~1,500 | **97%** | Period calculations |
| `solver.py` | 727 | **98%** | Curve calibration |
| `curves/` | ~1,300 | **97%** | Interest rate curves |
| `instruments/` | ~2,000 | **95%** | Financial instruments |
| `fx/` | ~550 | **98-100%** | FX rates and forwards |
| `dual/` | ~700 | **89%** | Automatic differentiation |
| `scheduling/` | ~500 | **93%** | Date scheduling |

##### Files with Lowest Coverage
1. `_spec_loader.py`: 15% (initialization code)
2. `dual/quadratic.py`: 24% (specialized dual variant)
3. `scheduling/calendars.py`: 81% (calendar implementations)

#### Common Testing Issues and Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'rateslib'` | Ensure you're in the `python/` directory and using `python -m pytest` |
| Tests not collected | Check you're running from `python/` directory |
| Coverage not showing | Use `python -m coverage run -m pytest` (not just `coverage run`) |
| Rust module errors | Rebuild with `maturin develop --release` from project root |

### Code Quality
```bash
# Run linting (configured in pyproject.toml)
ruff check python/

# Format code
ruff format python/

# Type checking
mypy python/ --exclude python/tests
```

### Documentation
```bash
# Build documentation (requires sphinx)
cd docs
sphinx-build -b html source build
```

## Architecture Overview

### Hybrid Python/Rust Design
The codebase uses a hybrid architecture with performance-critical components implemented in Rust and exposed to Python via PyO3:

- **Rust Components** (`rust/`): Core mathematical operations, dual numbers for automatic differentiation, curve interpolation, calendar calculations, and FX rate handling
- **Python Components** (`python/rateslib/`): High-level API, instrument definitions, pricing logic, and user-facing interfaces

### Key Modules

1. **Curves** (`curves/`): Interest rate curve construction and interpolation
   - Base curve classes with caching and state management
   - Multiple interpolation methods (linear, log-linear, cubic spline)
   - Rust-accelerated interpolation functions

2. **Instruments** (`instruments/`): Financial instrument definitions
   - Base classes for all instruments with pricing metrics
   - Specialized modules for bonds, credit derivatives, FX volatility, rates
   - Multi-currency and inflation-linked instruments

3. **Dual Numbers** (`dual/`): Automatic differentiation support
   - Dual and Dual2 types for first and second-order derivatives
   - Full operator overloading and mathematical functions
   - Used throughout for sensitivity calculations

4. **Scheduling** (`scheduling/`): Date generation and calendar logic
   - Business day adjustments and holiday calendars
   - IMM date handling and schedule generation
   - Day count fraction calculations

5. **FX** (`fx/`): Foreign exchange rates and forwards
   - FX rate pairs and conversion logic
   - FX forward curve construction

6. **Legs** (`legs/`): Cash flow leg definitions
   - Fixed, floating, and indexed legs
   - Credit and mark-to-market legs

## Important Design Patterns

1. **State Management**: Classes use `_WithState` and `_WithCache` mixins for efficient caching and state validation
2. **NoInput Pattern**: Uses `NoInput` sentinel values to distinguish unset parameters from None/0 values
3. **Dual Types**: Extensive use of dual numbers for automatic differentiation throughout pricing code
4. **Rust Acceleration**: Performance-critical paths delegated to Rust via PyO3 bindings

## Detailed Module Breakdown

### Core Components (97% Test Coverage)

#### Curves Module (`curves/`) - 97% coverage
- **curves.py**: Main curve implementations with caching (840 lines, 97% coverage)
- **interpolation.py**: Interpolation methods (85 lines, 100% coverage)
- **rs.py**: Rust bindings for performance (74 lines, 89% coverage)
- **utils.py**: Curve utilities and helpers (259 lines, 98% coverage)

#### Instruments Module (`instruments/`) - 95% coverage
- **base.py**: Base instrument classes with pricing metrics (128 lines, 100% coverage)
- **bonds/**: Bond instruments and conventions
  - securities.py: Bond pricing logic (484 lines, 94% coverage)
  - futures.py: Bond futures (248 lines, 94% coverage)
- **rates/**: Interest rate derivatives
  - single_currency.py: Swaps, FRAs (284 lines, 96% coverage)
  - multi_currency.py: Cross-currency swaps (392 lines, 99% coverage)
- **fx_volatility/**: FX options and strategies (95-98% coverage)

#### Dual Numbers (`dual/`) - 89% coverage
- Automatic differentiation implementation
- First and second-order derivatives
- Full mathematical function support
- Integration with NumPy arrays

#### Legs Module (`legs/`) - 99% coverage
- Cash flow generation and pricing
- Fixed, floating, and indexed legs
- Near-complete test coverage

#### Periods Module (`periods/`) - 97% coverage
- Individual period calculations
- Cashflow generation
- Rate calculations and conventions

#### Solver Module (`solver.py`) - 98% coverage
- Curve calibration and optimization
- 727 lines of sophisticated solver logic

### Rust Components (`rust/`)
- **curves/**: Interpolation algorithms
- **dual/**: Dual number arithmetic
- **fx/**: FX rate calculations
- **scheduling/**: Calendar and date logic
- **splines/**: Spline interpolation

All Rust components are exposed via PyO3 bindings and tested through Python test suite.

## Testing Strategy

- Unit tests organized by module in `python/tests/`
- Separate tests for Python and Rust components (e.g., `test_curves.py` vs `test_curvesrs.py`)
- Use pytest fixtures for common test data
- Financial accuracy tests comparing against known results

## Development Notes

- The project uses maturin for building Python wheels with Rust extensions
- Rust code in `rust/` directory with Python bindings exposed via `rust/lib.rs`
- Type stubs (`.pyi` files) provide type hints for Rust modules
- The codebase follows strict type checking with mypy in strict mode
- Ruff is configured for comprehensive linting with specific rule sets enabled

## Notebooks and Examples

### Jupyter Notebooks
The project includes educational Jupyter notebooks in the `notebooks/` directory:
- `coding/` - Basic examples demonstrating core functionality
- `coding_2/` - Advanced examples with detailed explanations

**Note**: Some notebooks use private/internal functions (prefixed with `_`) for educational purposes. These are not part of the public API.

### Running Examples

#### As Notebooks
```bash
cd notebooks
jupyter lab
```

#### As Python Scripts
Notebooks have been converted to standalone Python scripts:

```bash
# From the python/ directory
cd python

# Run individual example
python ../scripts/examples/coding_2/Curves.py

# Run all examples with error handling
python ../scripts/run_all_examples.py
```

### Converting Notebooks to Scripts
To convert new notebooks:
```bash
python scripts/convert_notebooks_v2.py
```

This creates executable Python scripts in `scripts/examples/` that can be run without Jupyter.

### Documentation References

#### Core Documentation
- **Architecture Overview**: `docs/VISUAL_ARCHITECTURE.md` - System diagrams and component interactions
- **Mathematical Reference**: `docs/MATHEMATICAL_FOUNDATIONS.md` - Formulas and theory
- **Class Reference**: `docs/COMPLETE_CLASS_REFERENCE.md` - Complete API reference
- **Documentation Index**: `docs/DOCUMENTATION_SUMMARY.md` - Master index of all documentation

#### Example Script Documentation
- **Script Guide**: `docs/SCRIPT_DOCUMENTATION.md` - Overview of all example scripts
- **Running Examples**: `docs/RUNNING_EXAMPLES.md` - How to run examples with expected output
- **Individual Script Docs**: Each script in `scripts/examples/` has a corresponding `.md` file with detailed documentation
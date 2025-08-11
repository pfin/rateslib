<div style="text-align: center; padding: 2em 0 2em">
    <img src="https://rateslib.readthedocs.io/en/latest/_static/rateslib_logo_big2.png" alt="rateslib">
</div>

<div style="text-align: center">
  <img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Frateslib.com%2Fpy%2Fen%2Flatest%2F_static%2Fbadges.json&query=%24.python&label=Python&color=blue" alt="Python">
  <img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Frateslib.com%2Fpy%2Fen%2Flatest%2F_static%2Fbadges.json&query=%24.pypi&label=PyPi&color=blue" alt="PyPi">
  <img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Frateslib.com%2Fpy%2Fen%2Flatest%2F_static%2Fbadges.json&query=%24.conda&label=Conda&color=blue" alt="Conda">
  <img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Frateslib.com%2Fpy%2Fen%2Flatest%2F_static%2Fbadges.json&query=%24.licence&label=Licence&color=orange" alt="Licence">
  <img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Frateslib.com%2Fpy%2Fen%2Flatest%2F_static%2Fbadges.json&query=%24.status&label=Status&color=orange" alt="Status">
  <img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Frateslib.com%2Fpy%2Fen%2Flatest%2F_static%2Fbadges.json&query=%24.coverage&label=Coverage&color=green" alt="Coverage">
  <img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Frateslib.com%2Fpy%2Fen%2Flatest%2F_static%2Fbadges.json&query=%24.style&label=Code%20Style&color=black" alt="Code Style">
</div>

# Rateslib

``Rateslib`` is a state-of-the-art **fixed income library** designed for Python.
Its purpose is to provide advanced, flexible and efficient fixed income analysis
with a high level, well documented API.

The techniques and object interaction within *rateslib* were inspired by
the requirements of multi-disciplined fixed income teams working, both cooperatively
and independently, within global investment banks.


Licence
=======

This library is released under a **Creative Commons Attribution, Non-Commercial,
No-Derivatives 4.0 International Licence**.


Get Started
===========

Read the documentation at 
[rateslib.com/py](https://rateslib.com/py/)


Development Setup
=================

This section provides instructions for setting up a local development environment from source.

Prerequisites
-------------
- Python 3.10 or higher (Python 3.12 recommended)
- Rust toolchain (for building the performance-critical Rust extensions)
- Conda or another Python environment manager

Quick Start
-----------

1. **Clone the repository**
   ```bash
   git clone https://github.com/attack68/rateslib.git
   cd rateslib
   ```

2. **Create and activate a conda environment**
   ```bash
   conda create -n rateslib-dev python=3.12 -y
   conda activate rateslib-dev
   ```

3. **Install Rust** (if not already installed)
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
   source "$HOME/.cargo/env"
   ```

4. **Install Python dependencies and build tools**
   ```bash
   pip install maturin numpy matplotlib pandas
   pip install pytest coverage ruff mypy pandas-stubs  # For development
   ```

5. **Build the Rust extensions**
   ```bash
   maturin develop --release
   ```

6. **Verify the installation**
   ```bash
   cd python
   python -c "import rateslib; print(rateslib.__version__)"
   ```

Testing
-------

### Prerequisites
Before running tests, ensure you have:
1. Completed the development setup above
2. Built the Rust extensions with `maturin develop --release`
3. Activated your conda environment: `conda activate rateslib-dev`

### Running Tests

**IMPORTANT**: All test commands must be run from the `python/` directory using `python -m pytest`:

```bash
# Navigate to the python directory (REQUIRED)
cd python

# Run all tests
python -m pytest tests/

# Run with different output levels
python -m pytest tests/ -q        # Quiet mode (dots only)
python -m pytest tests/ -v        # Verbose (show test names)
python -m pytest tests/ --tb=no   # No traceback on failures

# Run specific tests
python -m pytest tests/test_curves.py                           # Single file
python -m pytest tests/test_curves.py::TestCurve               # Single class
python -m pytest tests/test_curves.py::TestCurve::test_method  # Single method
python -m pytest tests/ -k "test_fx"                           # Pattern matching
python -m pytest tests/scheduling/                             # Specific directory

# Count tests without running
python -m pytest tests/ --collect-only -q | tail -1
```

### Test Coverage

Generate code coverage reports to see how well the tests cover the codebase:

```bash
# Run tests with coverage measurement
cd python
python -m coverage run -m pytest tests/ -q

# View coverage report in terminal
python -m coverage report

# Generate detailed HTML report
python -m coverage html
# Open htmlcov/index.html in your browser

# Show only files with missing coverage
python -m coverage report --skip-covered --skip-empty
```

### Test Statistics (Current)

**Test Suite:**
- Total tests: 3,758
- Passing: 3,684 ✅
- Skipped: 74
- Execution time: ~27 seconds (43s with coverage)

**Code Coverage: 97%**
- Total lines: 20,990
- Covered: 20,340
- Missing: 650

**Coverage by Module:**
| Module | Coverage | Description |
|--------|----------|-------------|
| `legs/` | 99% | Cash flow legs |
| `solver.py` | 98% | Optimization solver |
| `periods/` | 97% | Period calculations |
| `curves/` | 97% | Rate curves |
| `instruments/` | 95% | Financial instruments |
| `fx/` | 98-100% | FX functionality |

### Troubleshooting Tests

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'rateslib'` | Ensure you're in `python/` directory and using `python -m pytest` |
| Tests not found | Verify you're in the `python/` directory |
| Import errors | Rebuild Rust extensions: `maturin develop --release` |
| Coverage not working | Use `python -m coverage run -m pytest` |

Code Quality
------------

### Linting and Formatting

The project uses `ruff` for linting and code formatting:

```bash
# Check code style issues
cd python
ruff check rateslib/

# Auto-fix issues where possible
ruff check rateslib/ --fix

# Format code
ruff format rateslib/
```

### Type Checking

Use `mypy` for static type checking:

```bash
cd python
mypy rateslib/ --exclude tests
```

Development Workflow
--------------------

When developing locally without installing the package:

1. **Always work from the `python/` directory** to ensure imports work correctly
2. **After Rust changes**, rebuild with `maturin develop --release` from project root
3. **Run tests** from the `python/` directory using `python -m pytest`
4. **Check code quality** with `ruff` and `mypy` before committing
5. **Verify coverage** remains high (>95%) for new code

Project Structure
-----------------
```
rateslib/
├── python/           # Python source code
│   ├── rateslib/    # Main Python package
│   └── tests/       # Test suite
├── rust/            # Rust source code for performance-critical components
├── notebooks/       # Jupyter notebooks with examples
├── Cargo.toml       # Rust dependencies and configuration
├── pyproject.toml   # Python project configuration
└── CLAUDE.md        # Developer guidance for AI assistants
```






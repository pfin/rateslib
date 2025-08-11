# Rateslib Scripts

This directory contains utility scripts and converted examples for the rateslib library.

## Directory Structure

```
scripts/
├── convert_notebooks.py      # Original notebook converter
├── convert_notebooks_v2.py   # Improved notebook converter
├── run_all_examples.py      # Run all example scripts
├── examples/                 # Converted notebook scripts
│   ├── coding/              # Basic examples
│   └── coding_2/            # Advanced examples
└── README.md                # This file
```

## Notebook Conversion

The Jupyter notebooks in the `notebooks/` directory have been converted to Python scripts for easier execution and testing. 

### Important Notes About the Notebooks

Some notebooks use **private/internal functions** (those starting with underscore like `_get_unadjusted_roll`) for educational and testing purposes. These functions are:
- Part of the internal implementation
- Not part of the public API
- Subject to change without notice
- Used in notebooks to demonstrate internal workings

### Running the Scripts

To run the converted scripts:

1. **Navigate to the python directory** (required for imports):
   ```bash
   cd python
   ```

2. **Run individual scripts**:
   ```bash
   python ../scripts/examples/coding_2/Curves.py
   python ../scripts/examples/coding_2/FXRates.py
   ```

3. **Run all examples** (with error handling):
   ```bash
   python ../scripts/run_all_examples.py
   ```

## Example Scripts

### Basic Examples (`coding/`)
- `ch5_fx.py` - Foreign exchange functionality
- `curves.py` - Interest rate curves  
- `scheduling.py` - Date scheduling (uses internal functions)

### Advanced Examples (`coding_2/`)
- `AutomaticDifferentiation.py` - Dual numbers and AD
- `Calendars.py` - Business calendars
- `Cookbook.py` - Common recipes and patterns
- `Curves.py` - Advanced curve operations
- `CurveSolving.py` - Curve calibration
- `FXRates.py` - FX rate handling
- `FXVolatility.py` - FX volatility surfaces
- `Instruments.py` - Financial instruments
- `InterpolationAndSplines.py` - Interpolation methods
- `Legs.py` - Cash flow legs
- `Periods.py` - Period calculations
- `Scheduling.py` - Advanced scheduling

## Scripts with Known Issues

Some scripts use private API functions that may not be accessible:
- `scheduling.py` - Uses `_get_unadjusted_roll`, `_generate_regular_schedule_unadjusted`, etc.

These scripts are preserved for reference but may not run without modification.

## Converting New Notebooks

To convert new notebooks to scripts:

```bash
python scripts/convert_notebooks_v2.py
```

This will:
1. Find all `.ipynb` files in `notebooks/`
2. Convert them to `.py` scripts in `scripts/examples/`
3. Handle magic commands and add print statements
4. Create executable Python scripts

## Development Notes

When creating new examples:
1. Use only public API functions
2. Add proper imports and setup
3. Include comments explaining the functionality
4. Test from the `python/` directory
5. Follow the patterns in CLAUDE.md for proper execution
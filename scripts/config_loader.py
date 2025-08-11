"""
Configuration Loader Module - Load and process YAML configurations for cookbook recipes
"""

import yaml
import numpy as np
from datetime import datetime as dt
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import importlib


class ConfigLoader:
    """Load and process YAML configurations for rateslib instruments and curves"""
    
    def __init__(self, config_dir: str = "../config"):
        """Initialize configuration loader"""
        self.config_dir = Path(config_dir)
        self.configs = {}
        self.rateslib = None
        self._import_rateslib()
    
    def _import_rateslib(self):
        """Import rateslib dynamically"""
        try:
            self.rateslib = importlib.import_module('rateslib')
        except ImportError:
            print("Warning: rateslib not installed")
    
    def load_yaml(self, filename: str) -> Dict:
        """Load a YAML configuration file"""
        if not filename.endswith('.yml') and not filename.endswith('.yaml'):
            filename += '.yml'
        
        filepath = self.config_dir / filename
        if not filepath.exists():
            # Try subdirectories
            for subdir in ['curves', 'surfaces', 'examples', 'instruments']:
                filepath = self.config_dir / subdir / filename
                if filepath.exists():
                    break
        
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filename}")
        
        with open(filepath, 'r') as f:
            config = yaml.safe_load(f)
        
        self.configs[filename] = config
        return config
    
    def parse_date(self, date_input: Union[str, dt]) -> dt:
        """Parse date from string or datetime"""
        if isinstance(date_input, dt):
            return date_input
        if isinstance(date_input, str):
            return dt.strptime(date_input, "%Y-%m-%d")
        raise ValueError(f"Invalid date format: {date_input}")
    
    def build_curve_from_config(self, config: Dict, curve_key: str = 'curve') -> 'Curve':
        """Build a curve from configuration"""
        if not self.rateslib:
            raise ImportError("rateslib not available")
        
        Curve = getattr(self.rateslib, 'Curve')
        
        curve_config = config.get(curve_key, config)
        
        # Parse nodes
        nodes = {}
        if 'nodes' in curve_config:
            for node in curve_config['nodes']:
                date = self.parse_date(node['date'])
                df = node.get('df', 1.0)
                nodes[date] = df
        elif 'base_date' in curve_config:
            # Single node curve
            nodes[self.parse_date(curve_config['base_date'])] = 1.0
        
        # Handle knot sequence for mixed curves
        knot_sequence = None
        if 'knot_sequence' in curve_config:
            knot_sequence = [self.parse_date(d) for d in curve_config['knot_sequence']]
        
        # Create curve
        curve = Curve(
            nodes=nodes,
            id=curve_config.get('id'),
            convention=curve_config.get('convention', 'act365f'),
            calendar=curve_config.get('calendar', 'all'),
            interpolation=curve_config.get('interpolation', 'log_linear'),
            t=knot_sequence
        )
        
        return curve
    
    def build_fx_from_config(self, config: Dict) -> Dict:
        """Build FX rates and forwards from configuration"""
        if not self.rateslib:
            raise ImportError("rateslib not available")
        
        FXRates = getattr(self.rateslib, 'FXRates')
        FXForwards = getattr(self.rateslib, 'FXForwards')
        
        fx_config = config.get('fx_market', config.get('fx', {}))
        
        # Build FX rates
        spot_rates = fx_config.get('spot_rates', {})
        if 'spot' in fx_config and 'pair' in fx_config:
            # Single pair configuration
            spot_rates = {fx_config['pair']: fx_config['spot']}
        
        settlement = self.parse_date(fx_config.get('settlement', dt.today()))
        
        fxr = FXRates(spot_rates, settlement=settlement)
        
        # Build FX forwards if curves are provided
        fxf = None
        if 'curves' in fx_config:
            fx_curves = {}
            for ccy, curve_config in fx_config['curves'].items():
                curve = self.build_curve_from_config({'curve': curve_config})
                fx_curves[f"{ccy}{ccy}"] = curve
            
            fxf = FXForwards(fx_rates=fxr, fx_curves=fx_curves)
        
        return {'fx_rates': fxr, 'fx_forwards': fxf}
    
    def build_surface_from_config(self, config: Dict, surface_type: str = 'delta_vol') -> 'Surface':
        """Build a volatility surface from configuration"""
        if not self.rateslib:
            raise ImportError("rateslib not available")
        
        if surface_type == 'delta_vol':
            FXDeltaVolSurface = getattr(self.rateslib, 'FXDeltaVolSurface')
            surface_config = config.get('delta_vol_surface', config)
            
            expiries = [self.parse_date(d) for d in surface_config['expiries']]
            
            surface = FXDeltaVolSurface(
                eval_date=self.parse_date(surface_config['eval_date']),
                expiries=expiries,
                delta_indexes=surface_config['delta_indexes'],
                node_values=surface_config.get('initial_values', [[5, 5, 5]] * len(expiries)),
                delta_type=surface_config.get('delta_type', 'forward'),
                id=surface_config.get('id')
            )
            
        elif surface_type == 'sabr':
            FXSabrSurface = getattr(self.rateslib, 'FXSabrSurface')
            surface_config = config.get('sabr_surface', config)
            
            expiries = [self.parse_date(d) for d in surface_config['expiries']]
            
            surface = FXSabrSurface(
                eval_date=self.parse_date(surface_config['eval_date']),
                expiries=expiries,
                node_values=surface_config.get('initial_parameters'),
                pair=surface_config.get('pair'),
                id=surface_config.get('id')
            )
        else:
            raise ValueError(f"Unknown surface type: {surface_type}")
        
        return surface
    
    def build_instrument_from_config(self, config: Dict, instrument_type: str) -> Any:
        """Build an instrument from configuration"""
        if not self.rateslib:
            raise ImportError("rateslib not available")
        
        # Map instrument types to classes
        instrument_map = {
            'IRS': 'IRS',
            'FixedRateBond': 'FixedRateBond',
            'FRA': 'FRA',
            'XCS': 'XCS',
            'CDS': 'CDS',
            'FXForward': 'FXForward',
            'FXOption': 'FXOption',
            'FXPut': 'FXPut',
            'FXCall': 'FXCall'
        }
        
        if instrument_type not in instrument_map:
            raise ValueError(f"Unknown instrument type: {instrument_type}")
        
        InstrumentClass = getattr(self.rateslib, instrument_map[instrument_type])
        
        # Process dates
        if 'effective' in config:
            config['effective'] = self.parse_date(config['effective'])
        if 'termination' in config:
            config['termination'] = self.parse_date(config['termination'])
        if 'maturity' in config:
            config['maturity'] = self.parse_date(config['maturity'])
        if 'expiry' in config and not isinstance(config['expiry'], str):
            config['expiry'] = self.parse_date(config['expiry'])
        
        return InstrumentClass(**config)
    
    def build_portfolio_from_config(self, config: Dict) -> Dict:
        """Build a portfolio from configuration"""
        portfolio_config = config.get('portfolio', config)
        
        portfolio = {
            'name': portfolio_config.get('name', 'Portfolio'),
            'base_currency': portfolio_config.get('base_currency', 'USD'),
            'positions': []
        }
        
        # Build positions
        for position in portfolio_config.get('positions', []):
            # Load instrument configuration
            if 'instrument' in position:
                inst_config = config.get(position['instrument'], {})
                if inst_config and 'type' in inst_config:
                    instrument = self.build_instrument_from_config(
                        inst_config, 
                        inst_config['type']
                    )
                    portfolio['positions'].append({
                        'instrument': instrument,
                        'quantity': position.get('quantity', 1),
                        'side': position.get('side', 'long')
                    })
        
        return portfolio
    
    def process_example_config(self, config_file: str) -> Dict:
        """Process a complete example configuration file"""
        config = self.load_yaml(config_file)
        results = {}
        
        # Process curves
        if 'curve' in config or 'curves' in config:
            curves_config = config.get('curves', [config.get('curve')])
            if not isinstance(curves_config, list):
                curves_config = [curves_config]
            
            results['curves'] = []
            for curve_config in curves_config:
                curve = self.build_curve_from_config(curve_config)
                results['curves'].append(curve)
        
        # Process FX
        if 'fx_market' in config or 'fx' in config:
            fx_result = self.build_fx_from_config(config)
            results.update(fx_result)
        
        # Process surfaces
        if 'delta_vol_surface' in config:
            results['delta_vol_surface'] = self.build_surface_from_config(
                config, 'delta_vol'
            )
        
        if 'sabr_surface' in config:
            results['sabr_surface'] = self.build_surface_from_config(
                config, 'sabr'
            )
        
        # Process instruments
        for key in ['bonds', 'swaps', 'cross_currency_swaps', 'fra', 'bond_futures']:
            if key in config:
                results[key] = []
                for inst_config in config[key]:
                    if 'type' in inst_config:
                        instrument = self.build_instrument_from_config(
                            inst_config,
                            inst_config['type']
                        )
                        results[key].append(instrument)
        
        # Process portfolio
        if 'portfolio' in config:
            results['portfolio'] = self.build_portfolio_from_config(config)
        
        return results


def demonstrate_config_loader():
    """Demonstrate configuration loader functionality"""
    print("=" * 80)
    print("Configuration Loader Demonstration")
    print("=" * 80)
    
    loader = ConfigLoader()
    
    # Example 1: Load mixed curve configuration
    print("\n1. Loading Mixed Curve Configuration:")
    try:
        config = loader.load_yaml('mixed_curve')
        curve = loader.build_curve_from_config(config)
        print(f"   Loaded curve: {config['curve']['id']}")
        print(f"   Interpolation: {config['curve']['interpolation']}")
        print(f"   Nodes: {len(curve.nodes)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 2: Load FX volatility configuration
    print("\n2. Loading FX Volatility Configuration:")
    try:
        config = loader.load_yaml('fx_volatility')
        fx_result = loader.build_fx_from_config(config)
        print(f"   FX Pair: {config['fx_market']['pair']}")
        print(f"   Spot: {config['fx_market']['spot']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 3: Load instruments configuration
    print("\n3. Loading Instruments Configuration:")
    try:
        config = loader.load_yaml('instruments')
        results = loader.process_example_config('instruments')
        
        if 'bonds' in results:
            print(f"   Loaded {len(results['bonds'])} bonds")
        if 'swaps' in results:
            print(f"   Loaded {len(results['swaps'])} swaps")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 80)
    print("Configuration loader ready for use in cookbook recipes")
    
    return loader


if __name__ == "__main__":
    demonstrate_config_loader()
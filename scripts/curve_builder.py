"""
Curve Builder Module - Load curves from YAML configuration files
"""

import yaml
import numpy as np
import pandas as pd
from datetime import datetime as dt
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import rateslib as rl
    from rateslib import *
except ImportError:
    print("Warning: rateslib not installed")


class CurveBuilder:
    """Build curves from YAML configuration files"""
    
    def __init__(self, config_dir: str = "../config/curves"):
        """Initialize with configuration directory"""
        self.config_dir = Path(config_dir)
        self.configs = {}
        self.curves = {}
        self.solvers = {}
    
    def load_config(self, config_file: str) -> Dict:
        """Load YAML configuration file"""
        config_path = self.config_dir / config_file
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        self.configs[config_file] = config
        return config
    
    def parse_date(self, date_str: str) -> dt:
        """Parse date string to datetime"""
        if isinstance(date_str, dt):
            return date_str
        return dt.strptime(str(date_str), "%Y-%m-%d")
    
    def build_curve_from_config(self, config: Dict) -> 'Curve':
        """Build a curve from configuration dictionary"""
        curve_config = config.get('curve', {})
        
        # Parse nodes
        nodes = {}
        for node in curve_config.get('nodes', []):
            date = self.parse_date(node['date'])
            df = node.get('df', 1.0)
            nodes[date] = df
        
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
            t=knot_sequence  # This is the key for mixed interpolation
        )
        
        return curve
    
    def build_solver_from_config(self, config: Dict, curve: 'Curve') -> 'Solver':
        """Build a solver from configuration"""
        calib_config = config.get('calibration', {})
        solver_config = config.get('solver', {})
        
        # Build instruments
        instruments = []
        rates = []
        
        for inst in calib_config.get('instruments', []):
            if inst['type'] == 'IRS':
                # Parse dates
                if 'effective' in inst:
                    effective = self.parse_date(inst['effective'])
                else:
                    effective = self.parse_date(config['curve'].get('base_date', dt(2022, 1, 1)))
                
                # Handle termination (can be date or tenor)
                term = inst.get('termination', inst.get('term'))
                
                # Create IRS
                irs = IRS(
                    effective=effective,
                    termination=term,
                    frequency=calib_config.get('frequency', 'a'),
                    convention=config['curve'].get('convention', 'act365f'),
                    calendar=config['curve'].get('calendar', 'all'),
                    payment_lag=calib_config.get('payment_lag', 0),
                    curves=curve
                )
                instruments.append(irs)
                rates.append(inst['rate'])
        
        # Create solver
        solver = Solver(
            curves=[curve],
            instruments=instruments,
            s=rates,
            id=solver_config.get('id'),
            algorithm=solver_config.get('algorithm', 'levenberg_marquardt'),
            tolerance=solver_config.get('tolerance', 1e-12),
            max_iter=solver_config.get('max_iterations', 100)
        )
        
        return solver
    
    def build_mixed_curve(self) -> Dict:
        """Build the mixed curve with sophisticated interpolation"""
        config = self.load_config('mixed_curve.yml')
        
        # Build curve
        curve = self.build_curve_from_config(config)
        
        # Build and run solver
        solver = self.build_solver_from_config(config, curve)
        
        # Store results
        self.curves['mixed'] = curve
        self.solvers['mixed'] = solver
        
        return {
            'curve': curve,
            'solver': solver,
            'config': config
        }
    
    def build_all_curves(self) -> Dict:
        """Build all curves from configuration files"""
        results = {}
        
        # Find all YAML files
        yaml_files = list(self.config_dir.glob("*.yml"))
        
        for yaml_file in yaml_files:
            try:
                config = self.load_config(yaml_file.name)
                
                # Handle different configuration types
                if 'curve' in config:
                    curve = self.build_curve_from_config(config)
                    
                    if 'calibration' in config:
                        solver = self.build_solver_from_config(config, curve)
                        results[yaml_file.stem] = {
                            'curve': curve,
                            'solver': solver,
                            'config': config
                        }
                    else:
                        results[yaml_file.stem] = {
                            'curve': curve,
                            'config': config
                        }
                
                elif 'eur_curve' in config:
                    # Handle dependency chain configuration
                    results[yaml_file.stem] = self.build_dependency_chain(config)
                
            except Exception as e:
                print(f"Error processing {yaml_file.name}: {e}")
                results[yaml_file.stem] = {'error': str(e)}
        
        return results
    
    def build_dependency_chain(self, config: Dict) -> Dict:
        """Build dependency chain from configuration"""
        # Build EUR curve
        eur_config = config['eur_curve']
        eur_nodes = {self.parse_date(n['date']): n['df'] for n in eur_config['nodes']}
        eur_curve = Curve(
            nodes=eur_nodes,
            id=eur_config['id'],
            convention=eur_config['convention'],
            calendar=eur_config['calendar'],
            interpolation=eur_config['interpolation']
        )
        
        # Build USD curve
        usd_config = config['usd_curve']
        usd_nodes = {self.parse_date(n['date']): n['df'] for n in usd_config['nodes']}
        usd_curve = Curve(
            nodes=usd_nodes,
            id=usd_config['id'],
            convention=usd_config['convention'],
            calendar=usd_config['calendar'],
            interpolation=usd_config['interpolation']
        )
        
        # Build XCS curve
        xcs_config = config['xcs_curve']
        xcs_nodes = {self.parse_date(n['date']): n['df'] for n in xcs_config['nodes']}
        xcs_curve = Curve(
            nodes=xcs_nodes,
            id=xcs_config['id'],
            convention=xcs_config['convention'],
            calendar=xcs_config['calendar'],
            interpolation=xcs_config['interpolation']
        )
        
        # Create FX setup
        fx_config = config['fx']
        fxr = FXRates(fx_config['rates'], settlement=self.parse_date(fx_config['settlement']))
        fxf = FXForwards(
            fx_rates=fxr,
            fx_curves={
                'eureur': eur_curve,
                'usdusd': usd_curve,
                'eurusd': xcs_curve
            }
        )
        
        return {
            'eur_curve': eur_curve,
            'usd_curve': usd_curve,
            'xcs_curve': xcs_curve,
            'fx_rates': fxr,
            'fx_forwards': fxf,
            'config': config
        }
    
    def compare_curves(self, curve_names: List[str] = None) -> pd.DataFrame:
        """Compare discount factors across different curves"""
        if curve_names is None:
            curve_names = list(self.curves.keys())
        
        # Get common dates
        all_dates = set()
        for name in curve_names:
            if name in self.curves:
                all_dates.update(self.curves[name].nodes.keys())
        
        all_dates = sorted(all_dates)
        
        # Build comparison dataframe
        data = {}
        for name in curve_names:
            if name in self.curves:
                curve = self.curves[name]
                data[name] = [float(curve[date]) for date in all_dates]
        
        df = pd.DataFrame(data, index=all_dates)
        return df


def demonstrate_mixed_curve():
    """Demonstrate the mixed curve configuration"""
    print("=" * 80)
    print("Mixed Curve Configuration Demo")
    print("=" * 80)
    
    builder = CurveBuilder()
    result = builder.build_mixed_curve()
    
    curve = result['curve']
    config = result['config']
    
    print("\nMixed Curve Configuration:")
    print("-" * 40)
    
    # Show interpolation regions
    regions = config.get('interpolation_regions', {})
    for region_name, region_config in regions.items():
        print(f"\n{region_name.upper()}:")
        print(f"  Method: {region_config['method']}")
        print(f"  Region: {region_config['region']}")
        print(f"  Rationale: {region_config['rationale']}")
    
    print("\n" + "=" * 40)
    print("Key Innovation: Knot Sequence")
    print("=" * 40)
    
    if 'knot_sequence' in config['curve']:
        knots = config['curve']['knot_sequence']
        print(f"Knot sequence defines {len(knots)} transition points:")
        print(f"  Start: {knots[0]} (repeated for spline boundary)")
        print(f"  Transition zone: {knots[4]} to {knots[5]}")
        print(f"  End: {knots[-1]} (repeated for spline boundary)")
    
    return result


def load_and_compare_all():
    """Load all curves and compare them"""
    print("=" * 80)
    print("Loading All Curve Configurations")
    print("=" * 80)
    
    builder = CurveBuilder()
    
    # Load individual curves
    configs_to_load = [
        'log_linear_curve.yml',
        'cubic_spline_curve.yml',
        'mixed_curve.yml'
    ]
    
    for config_file in configs_to_load:
        try:
            config = builder.load_config(config_file)
            curve = builder.build_curve_from_config(config)
            solver = builder.build_solver_from_config(config, curve)
            
            curve_id = config['curve']['id']
            builder.curves[curve_id] = curve
            builder.solvers[curve_id] = solver
            
            print(f"\n✓ Loaded {curve_id}")
            print(f"  Interpolation: {config['curve']['interpolation']}")
            print(f"  Nodes: {len(curve.nodes)}")
            
        except Exception as e:
            print(f"\n✗ Error loading {config_file}: {e}")
    
    # Compare curves
    if len(builder.curves) > 1:
        print("\n" + "=" * 40)
        print("Curve Comparison (Discount Factors)")
        print("=" * 40)
        
        df = builder.compare_curves()
        print(df.head(10))
        
        # Calculate differences
        if 'mixed_curve' in df.columns and 'log_linear_curve' in df.columns:
            df['mixed_vs_linear'] = (df['mixed_curve'] - df['log_linear_curve']) * 10000
            print("\nDifference (mixed vs log-linear) in bps:")
            print(df['mixed_vs_linear'].describe())
    
    return builder


if __name__ == "__main__":
    # Demonstrate mixed curve
    mixed_result = demonstrate_mixed_curve()
    
    print("\n" + "=" * 80)
    
    # Load and compare all curves
    builder = load_and_compare_all()
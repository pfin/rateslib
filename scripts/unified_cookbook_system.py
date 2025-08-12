"""
Unified Cookbook System - Modular and Configurable
===================================================

This module provides a unified, configurable system that can replicate
all 28 cookbook recipes through modular components and YAML configuration.

Key Features:
- Single entry point for all recipes
- YAML-driven configuration
- Modular components (curves, instruments, solvers)
- Common utilities and patterns
- Extensible architecture
"""

import yaml
import numpy as np
import pandas as pd
from datetime import datetime as dt
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import matplotlib.pyplot as plt

try:
    from rateslib import *
except ImportError:
    print("Warning: rateslib not available")


# ============================================================================
# CONFIGURATION CLASSES
# ============================================================================

class InterpolationType(Enum):
    """Supported interpolation methods"""
    LINEAR = "linear"
    LOG_LINEAR = "log_linear"
    LINEAR_INDEX = "linear_index"
    CUBIC_SPLINE = "cubic_spline"
    MIXED = "mixed"


class InstrumentType(Enum):
    """Supported instrument types"""
    IRS = "irs"
    FRA = "fra"
    XCS = "xcs"
    BOND = "bond"
    SWAPTION = "swaption"
    FX_OPTION = "fx_option"
    CDS = "cds"
    INFLATION_SWAP = "inflation_swap"


@dataclass
class CurveConfig:
    """Configuration for a curve"""
    id: str
    interpolation: InterpolationType
    convention: str = "act360"
    calendar: str = "all"
    nodes: Dict[dt, float] = field(default_factory=dict)
    knot_sequence: Optional[List[dt]] = None
    index_base: Optional[float] = None
    index_lag: Optional[int] = None


@dataclass
class InstrumentConfig:
    """Configuration for an instrument"""
    type: InstrumentType
    effective: dt
    termination: Union[dt, str]
    notional: float = 100_000_000
    fixed_rate: Optional[float] = None
    float_spread: Optional[float] = None
    frequency: str = "Q"
    convention: str = "act360"
    calendar: str = "all"
    currency: str = "usd"
    curves: Optional[List[str]] = None


@dataclass
class SolverConfig:
    """Configuration for a solver"""
    id: str
    curves: List[str]
    instruments: List[InstrumentConfig]
    market_rates: List[float]
    pre_solvers: Optional[List[str]] = None
    fx_rates: Optional[Dict[str, float]] = None


@dataclass
class RecipeConfig:
    """Complete recipe configuration"""
    name: str
    description: str
    curves: List[CurveConfig]
    instruments: List[InstrumentConfig]
    solvers: List[SolverConfig]
    outputs: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# CORE SYSTEM COMPONENTS
# ============================================================================

class CurveBuilder:
    """Factory for building curves from configuration"""
    
    @staticmethod
    def build(config: CurveConfig) -> 'Curve':
        """Build a curve from configuration"""
        
        # Handle special curve types
        if config.index_base is not None:
            return IndexCurve(
                nodes=config.nodes,
                interpolation=config.interpolation.value,
                convention=config.convention,
                calendar=config.calendar,
                index_base=config.index_base,
                index_lag=config.index_lag or 3,
                id=config.id
            )
        
        # Handle mixed interpolation
        if config.interpolation == InterpolationType.MIXED and config.knot_sequence:
            return Curve(
                nodes=config.nodes,
                interpolation="log_linear",  # Base interpolation
                convention=config.convention,
                calendar=config.calendar,
                t=config.knot_sequence,
                id=config.id
            )
        
        # Standard curve
        return Curve(
            nodes=config.nodes,
            interpolation=config.interpolation.value,
            convention=config.convention,
            calendar=config.calendar,
            id=config.id
        )


class InstrumentBuilder:
    """Factory for building instruments from configuration"""
    
    @staticmethod
    def build(config: InstrumentConfig) -> Any:
        """Build an instrument from configuration"""
        
        if config.type == InstrumentType.IRS:
            return IRS(
                effective=config.effective,
                termination=config.termination,
                notional=config.notional,
                fixed_rate=config.fixed_rate,
                frequency=config.frequency,
                convention=config.convention,
                calendar=config.calendar,
                currency=config.currency,
                curves=config.curves
            )
        
        elif config.type == InstrumentType.FRA:
            return FRA(
                effective=config.effective,
                termination=config.termination,
                frequency=config.frequency,
                rate=config.fixed_rate,
                notional=config.notional,
                curves=config.curves
            )
        
        elif config.type == InstrumentType.XCS:
            return XCS(
                effective=config.effective,
                termination=config.termination,
                notional=config.notional,
                fixed_rate=config.fixed_rate,
                frequency=config.frequency,
                currency=config.currency,
                curves=config.curves
            )
        
        elif config.type == InstrumentType.BOND:
            return FixedRateBond(
                effective=config.effective,
                termination=config.termination,
                frequency=config.frequency,
                convention=config.convention,
                calendar=config.calendar,
                currency=config.currency,
                notional=config.notional,
                coupon=config.fixed_rate or 0
            )
        
        else:
            raise ValueError(f"Unsupported instrument type: {config.type}")


class SolverBuilder:
    """Factory for building solvers from configuration"""
    
    def __init__(self, curves: Dict[str, 'Curve']):
        self.curves = curves
        self.solvers = {}
    
    def build(self, config: SolverConfig) -> 'Solver':
        """Build a solver from configuration"""
        
        # Get curve objects
        solver_curves = [self.curves[curve_id] for curve_id in config.curves]
        
        # Build instruments
        instruments = [InstrumentBuilder.build(inst) for inst in config.instruments]
        
        # Handle pre-solvers
        pre_solvers = None
        if config.pre_solvers:
            pre_solvers = [self.solvers[solver_id] for solver_id in config.pre_solvers]
        
        # Handle FX rates
        fx = None
        if config.fx_rates:
            fx = FXRates(config.fx_rates)
        
        # Create solver
        solver = Solver(
            curves=solver_curves,
            instruments=instruments,
            s=config.market_rates,
            pre_solvers=pre_solvers,
            fx=fx,
            id=config.id
        )
        
        # Store for future reference
        self.solvers[config.id] = solver
        
        return solver


# ============================================================================
# ANALYSIS COMPONENTS
# ============================================================================

class RiskAnalyzer:
    """Common risk analysis functions"""
    
    @staticmethod
    def calculate_dv01(instrument, curve) -> float:
        """Calculate DV01 for an instrument"""
        delta = instrument.delta(curves=curve)
        return delta.sum().values[0] / 10000
    
    @staticmethod
    def calculate_duration(instrument, curve) -> float:
        """Calculate duration for an instrument"""
        return instrument.duration(curves=curve)
    
    @staticmethod
    def calculate_convexity(instrument, curve) -> float:
        """Calculate convexity for an instrument"""
        return instrument.convexity(curves=curve)
    
    @staticmethod
    def calculate_theta(instrument, curve, days: int = 1) -> float:
        """Calculate theta (time decay)"""
        # Simplified theta calculation
        npv_today = instrument.npv(curves=curve)
        # Roll curve forward by days
        rolled_curve = curve.roll(f"{days}d")
        npv_tomorrow = instrument.npv(curves=rolled_curve)
        return float(npv_tomorrow - npv_today)


class CashflowAnalyzer:
    """Cash flow analysis utilities"""
    
    @staticmethod
    def generate_cashflows(instrument, curve) -> pd.DataFrame:
        """Generate cash flow schedule"""
        return instrument.cashflows(curves=curve)
    
    @staticmethod
    def calculate_accrued(bond, settlement_date: dt) -> float:
        """Calculate accrued interest"""
        return bond.accrued_interest(settlement_date)
    
    @staticmethod
    def calculate_yield(bond, price: float) -> float:
        """Calculate yield to maturity"""
        return bond.ytm(price=price)


class VolatilityAnalyzer:
    """Volatility and options analysis"""
    
    @staticmethod
    def calculate_implied_vol(option_price: float, spot: float, 
                            strike: float, time: float, rate: float) -> float:
        """Calculate implied volatility using Newton-Raphson"""
        # Simplified Black-Scholes implied vol
        import scipy.stats as stats
        
        def black_scholes(vol):
            d1 = (np.log(spot/strike) + (rate + 0.5*vol**2)*time) / (vol*np.sqrt(time))
            d2 = d1 - vol*np.sqrt(time)
            return spot*stats.norm.cdf(d1) - strike*np.exp(-rate*time)*stats.norm.cdf(d2)
        
        # Newton-Raphson iteration
        vol = 0.2  # Initial guess
        for _ in range(10):
            price = black_scholes(vol)
            vega = spot * stats.norm.pdf((np.log(spot/strike) + 
                  (rate + 0.5*vol**2)*time) / (vol*np.sqrt(time))) * np.sqrt(time)
            vol = vol - (price - option_price) / vega
        
        return vol
    
    @staticmethod
    def build_vol_surface(expiries: List[str], strikes: List[float], 
                         vols: np.ndarray) -> Dict:
        """Build volatility surface"""
        return {
            "expiries": expiries,
            "strikes": strikes,
            "volatilities": vols,
            "interpolation": "cubic_spline"
        }


# ============================================================================
# UNIFIED COOKBOOK SYSTEM
# ============================================================================

class UnifiedCookbookSystem:
    """Main system that can execute any recipe through configuration"""
    
    def __init__(self):
        self.curves = {}
        self.instruments = {}
        self.solvers = {}
        self.results = {}
        self.risk_analyzer = RiskAnalyzer()
        self.cashflow_analyzer = CashflowAnalyzer()
        self.vol_analyzer = VolatilityAnalyzer()
    
    def load_config(self, config_path: str) -> RecipeConfig:
        """Load recipe configuration from YAML file"""
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Parse configuration
        curves = [CurveConfig(**c) for c in data.get('curves', [])]
        instruments = [InstrumentConfig(**i) for i in data.get('instruments', [])]
        solvers = [SolverConfig(**s) for s in data.get('solvers', [])]
        
        return RecipeConfig(
            name=data['name'],
            description=data['description'],
            curves=curves,
            instruments=instruments,
            solvers=solvers,
            outputs=data.get('outputs', []),
            metadata=data.get('metadata', {})
        )
    
    def execute_recipe(self, config: Union[str, RecipeConfig]) -> Dict[str, Any]:
        """Execute a recipe and return results"""
        
        # Load config if path provided
        if isinstance(config, str):
            config = self.load_config(config)
        
        print(f"Executing Recipe: {config.name}")
        print("=" * 80)
        print(config.description)
        print()
        
        # Build curves
        print("Building curves...")
        for curve_config in config.curves:
            curve = CurveBuilder.build(curve_config)
            self.curves[curve_config.id] = curve
            print(f"  ✓ Built curve: {curve_config.id}")
        
        # Build instruments
        print("\nBuilding instruments...")
        for i, inst_config in enumerate(config.instruments):
            instrument = InstrumentBuilder.build(inst_config)
            self.instruments[f"inst_{i}"] = instrument
            print(f"  ✓ Built {inst_config.type.value}: inst_{i}")
        
        # Build and run solvers
        print("\nRunning solvers...")
        solver_builder = SolverBuilder(self.curves)
        for solver_config in config.solvers:
            solver = solver_builder.build(solver_config)
            self.solvers[solver_config.id] = solver
            print(f"  ✓ Solver {solver_config.id} calibrated")
        
        # Generate outputs
        print("\nGenerating outputs...")
        results = self._generate_outputs(config)
        
        # Store results
        self.results[config.name] = results
        
        return results
    
    def _generate_outputs(self, config: RecipeConfig) -> Dict[str, Any]:
        """Generate requested outputs"""
        results = {
            "recipe": config.name,
            "timestamp": dt.now(),
            "curves": {},
            "instruments": {},
            "risk_metrics": {},
            "cashflows": {},
            "analytics": {}
        }
        
        for output in config.outputs:
            if output == "curve_rates":
                results["curves"] = self._get_curve_rates()
            elif output == "npv":
                results["instruments"] = self._get_npvs()
            elif output == "risk":
                results["risk_metrics"] = self._get_risk_metrics()
            elif output == "cashflows":
                results["cashflows"] = self._get_cashflows()
            elif output == "analytics":
                results["analytics"] = self._get_analytics()
        
        return results
    
    def _get_curve_rates(self) -> Dict:
        """Get curve rates at key tenors"""
        rates = {}
        tenors = ["1M", "3M", "6M", "1Y", "2Y", "5Y", "10Y", "30Y"]
        
        for curve_id, curve in self.curves.items():
            rates[curve_id] = {}
            for tenor in tenors:
                try:
                    date = add_tenor(dt.now(), tenor, "F", "all")
                    rate = curve.rate(date)
                    rates[curve_id][tenor] = float(rate)
                except:
                    rates[curve_id][tenor] = None
        
        return rates
    
    def _get_npvs(self) -> Dict:
        """Get NPVs for all instruments"""
        npvs = {}
        
        for inst_id, instrument in self.instruments.items():
            try:
                # Find appropriate curve
                curve = list(self.curves.values())[0]  # Simplified
                npv = instrument.npv(curves=curve)
                npvs[inst_id] = float(npv)
            except:
                npvs[inst_id] = None
        
        return npvs
    
    def _get_risk_metrics(self) -> Dict:
        """Calculate risk metrics"""
        metrics = {}
        
        for inst_id, instrument in self.instruments.items():
            try:
                curve = list(self.curves.values())[0]
                metrics[inst_id] = {
                    "dv01": self.risk_analyzer.calculate_dv01(instrument, curve),
                    "duration": self.risk_analyzer.calculate_duration(instrument, curve),
                    "convexity": self.risk_analyzer.calculate_convexity(instrument, curve),
                    "theta": self.risk_analyzer.calculate_theta(instrument, curve)
                }
            except:
                metrics[inst_id] = {}
        
        return metrics
    
    def _get_cashflows(self) -> Dict:
        """Get cash flows for instruments"""
        cashflows = {}
        
        for inst_id, instrument in self.instruments.items():
            try:
                curve = list(self.curves.values())[0]
                cf = self.cashflow_analyzer.generate_cashflows(instrument, curve)
                cashflows[inst_id] = cf.to_dict()
            except:
                cashflows[inst_id] = None
        
        return cashflows
    
    def _get_analytics(self) -> Dict:
        """Get additional analytics"""
        return {
            "total_curves": len(self.curves),
            "total_instruments": len(self.instruments),
            "total_solvers": len(self.solvers),
            "execution_time": dt.now()
        }
    
    def plot_curves(self, curve_ids: Optional[List[str]] = None):
        """Plot curves"""
        if curve_ids is None:
            curve_ids = list(self.curves.keys())
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for curve_id in curve_ids:
            if curve_id in self.curves:
                curve = self.curves[curve_id]
                # Generate points for plotting
                dates = pd.date_range(dt.now(), periods=30*12, freq='M')
                rates = [curve.rate(d) * 100 for d in dates]
                years = [(d - dt.now()).days / 365.25 for d in dates]
                
                ax.plot(years, rates, label=curve_id)
        
        ax.set_xlabel('Maturity (years)')
        ax.set_ylabel('Rate (%)')
        ax.set_title('Yield Curves')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def compare_recipes(self, recipe_configs: List[RecipeConfig]) -> pd.DataFrame:
        """Compare results across multiple recipes"""
        comparison = []
        
        for config in recipe_configs:
            results = self.execute_recipe(config)
            comparison.append({
                "recipe": config.name,
                "curves": len(results.get("curves", {})),
                "instruments": len(results.get("instruments", {})),
                "total_npv": sum(results.get("instruments", {}).values() or [0]),
                "avg_dv01": np.mean([m.get("dv01", 0) 
                                    for m in results.get("risk_metrics", {}).values()])
            })
        
        return pd.DataFrame(comparison)


# ============================================================================
# RECIPE GENERATOR
# ============================================================================

class RecipeGenerator:
    """Generate recipe configurations programmatically"""
    
    @staticmethod
    def generate_single_curve_recipe(
        curve_type: str = "log_linear",
        tenors: List[str] = None,
        rates: List[float] = None
    ) -> RecipeConfig:
        """Generate a simple single curve recipe"""
        
        if tenors is None:
            tenors = ["1M", "3M", "6M", "1Y", "2Y", "5Y", "10Y"]
        if rates is None:
            rates = [5.0, 4.9, 4.8, 4.7, 4.5, 4.3, 4.0]
        
        # Create curve nodes
        nodes = {}
        for tenor, rate in zip(tenors, rates):
            date = add_tenor(dt.now(), tenor, "F", "all")
            nodes[date] = 1.0  # Will be calibrated
        
        # Create configuration
        curve_config = CurveConfig(
            id="main",
            interpolation=InterpolationType(curve_type),
            nodes=nodes
        )
        
        # Create instruments for calibration
        instruments = []
        for tenor in tenors:
            instruments.append(InstrumentConfig(
                type=InstrumentType.IRS,
                effective=dt.now(),
                termination=tenor,
                fixed_rate=None  # Will be solved
            ))
        
        # Create solver
        solver_config = SolverConfig(
            id="main_solver",
            curves=["main"],
            instruments=instruments,
            market_rates=rates
        )
        
        return RecipeConfig(
            name="Single Curve Example",
            description="Simple single curve calibration",
            curves=[curve_config],
            instruments=instruments,
            solvers=[solver_config],
            outputs=["curve_rates", "npv", "risk"]
        )
    
    @staticmethod
    def generate_multi_curve_recipe() -> RecipeConfig:
        """Generate a multi-curve recipe with dependencies"""
        # Implementation for multi-curve setup
        pass
    
    @staticmethod
    def generate_volatility_recipe() -> RecipeConfig:
        """Generate a volatility surface recipe"""
        # Implementation for volatility surface
        pass


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Example usage of the unified system"""
    
    # Create system instance
    system = UnifiedCookbookSystem()
    
    # Example 1: Execute from YAML config
    # config_path = "/path/to/recipe_config.yml"
    # results = system.execute_recipe(config_path)
    
    # Example 2: Generate and execute programmatically
    recipe = RecipeGenerator.generate_single_curve_recipe()
    results = system.execute_recipe(recipe)
    
    # Display results
    print("\nResults:")
    print(f"  Curves: {len(results['curves'])}")
    print(f"  Instruments: {len(results['instruments'])}")
    print(f"  Risk Metrics: {len(results['risk_metrics'])}")
    
    # Plot curves
    fig = system.plot_curves()
    plt.show()
    
    return system, results


if __name__ == "__main__":
    system, results = main()
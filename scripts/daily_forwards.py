"""
Daily Overnight Forward Rate Calculation and Plotting
With butterfly targeting and turn handling
"""

import numpy as np
import pandas as pd
from datetime import datetime as dt, timedelta
from typing import Dict, List, Optional, Tuple, Any
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
import yaml

try:
    import rateslib as rl
    from rateslib import *
except ImportError:
    print("Warning: rateslib not installed")


class DailyForwardCalculator:
    """Calculate and plot daily overnight forward rates with butterfly targeting"""
    
    def __init__(self, curve: 'Curve', config: Optional[Dict] = None):
        """Initialize with curve and optional configuration"""
        self.curve = curve
        self.config = config or {}
        self.forwards = {}
        self.butterflies = {}
        self.turns = {}
        
    def calculate_daily_forwards(self, 
                                start_date: dt, 
                                end_date: dt,
                                method: str = "direct") -> pd.DataFrame:
        """
        Calculate daily overnight forward rates
        
        Methods:
        - direct: curve.rate(d, d+1)
        - dual: using dual numbers for derivatives
        - finite_diff: finite differences on log discount factors
        - analytical: analytical derivatives
        """
        dates = []
        forwards = []
        
        current = start_date
        while current < end_date:
            dates.append(current)
            
            if method == "direct":
                # Direct calculation
                fwd = self.curve.rate(current, current + timedelta(days=1))
                
            elif method == "dual":
                # Using dual numbers
                df_today = self.curve[current]
                df_tomorrow = self.curve[current + timedelta(days=1)]
                dcf = self.curve.dcf(current, current + timedelta(days=1))
                if dcf > 0:
                    fwd = (float(df_today) / float(df_tomorrow) - 1.0) / dcf
                else:
                    fwd = 0.0
                    
            elif method == "finite_diff":
                # Finite differences
                df_today = float(self.curve[current])
                df_tomorrow = float(self.curve[current + timedelta(days=1)])
                if df_tomorrow > 0:
                    dcf = self.curve.dcf(current, current + timedelta(days=1))
                    fwd = -np.log(df_tomorrow / df_today) / dcf if dcf > 0 else 0.0
                else:
                    fwd = 0.0
                    
            elif method == "analytical":
                # Analytical derivative (if available)
                try:
                    # This would require curve to have derivative method
                    fwd = self.curve.forward_rate(current, current + timedelta(days=1))
                except:
                    # Fallback to direct
                    fwd = self.curve.rate(current, current + timedelta(days=1))
            
            forwards.append(fwd * 100)  # Convert to percentage
            current += timedelta(days=1)
        
        df = pd.DataFrame({
            'date': dates,
            'forward_rate': forwards
        })
        
        self.forwards = df
        return df
    
    def identify_turns(self, threshold: float = 50) -> List[Dict]:
        """
        Identify turn periods where rates change rapidly
        
        Args:
            threshold: Rate change threshold in bps to identify turns
        """
        if self.forwards.empty:
            return []
        
        turns = []
        df = self.forwards.copy()
        df['rate_change'] = df['forward_rate'].diff()
        
        # Find large changes
        turn_mask = np.abs(df['rate_change']) > threshold / 10000
        
        # Group consecutive turn days
        turn_groups = []
        in_turn = False
        current_turn = None
        
        for idx, row in df.iterrows():
            if turn_mask.iloc[idx] and not in_turn:
                # Start of turn
                in_turn = True
                current_turn = {
                    'start': row['date'],
                    'rates': [row['forward_rate']]
                }
            elif in_turn and not turn_mask.iloc[idx]:
                # End of turn
                current_turn['end'] = df.iloc[idx-1]['date']
                current_turn['impact'] = max(current_turn['rates']) - min(current_turn['rates'])
                turns.append(current_turn)
                in_turn = False
                current_turn = None
            elif in_turn:
                # Continue turn
                current_turn['rates'].append(row['forward_rate'])
        
        # Handle turn at end
        if in_turn and current_turn:
            current_turn['end'] = df.iloc[-1]['date']
            current_turn['impact'] = max(current_turn['rates']) - min(current_turn['rates'])
            turns.append(current_turn)
        
        self.turns = turns
        return turns
    
    def calculate_butterflies(self, 
                            tenors: List[Tuple[str, str, str]] = None) -> pd.DataFrame:
        """
        Calculate butterfly spreads
        
        Args:
            tenors: List of (left_wing, body, right_wing) tenor tuples
                   e.g., [("2Y", "5Y", "10Y"), ("3M", "6M", "1Y")]
        """
        if tenors is None:
            tenors = [
                ("2Y", "5Y", "10Y"),
                ("3M", "6M", "1Y"),
                ("5Y", "10Y", "30Y")
            ]
        
        butterflies = []
        base_date = self.forwards['date'].iloc[0] if not self.forwards.empty else dt.today()
        
        for left, body, right in tenors:
            # Convert tenors to dates
            left_date = rl.add_tenor(base_date, left, "MF", "nyc")
            body_date = rl.add_tenor(base_date, body, "MF", "nyc")
            right_date = rl.add_tenor(base_date, right, "MF", "nyc")
            
            # Calculate rates
            left_rate = self.curve.rate(base_date, left_date) * 100
            body_rate = self.curve.rate(base_date, body_date) * 100
            right_rate = self.curve.rate(base_date, right_date) * 100
            
            # Butterfly = 2*body - left - right
            butterfly = 2 * body_rate - left_rate - right_rate
            
            butterflies.append({
                'butterfly': f"{left}{body}{right}",
                'left_tenor': left,
                'body_tenor': body,
                'right_tenor': right,
                'left_rate': left_rate,
                'body_rate': body_rate,
                'right_rate': right_rate,
                'butterfly_value': butterfly,
                'curvature': butterfly  # Same as butterfly value
            })
        
        self.butterflies = pd.DataFrame(butterflies)
        return self.butterflies
    
    def plot_daily_forwards(self, 
                           highlight_turns: bool = True,
                           show_butterflies: bool = True,
                           save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot daily overnight forward rates with turns and butterflies
        """
        if self.forwards.empty:
            print("No forward rates calculated. Run calculate_daily_forwards first.")
            return None
        
        # Create figure with subplots
        if show_butterflies and not self.butterflies.empty:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                          gridspec_kw={'height_ratios': [3, 1]})
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=(14, 6))
            ax2 = None
        
        # Plot forward rates
        ax1.plot(self.forwards['date'], self.forwards['forward_rate'], 
                linewidth=1.5, color='blue', label='Daily O/N Forward')
        
        # Highlight turns
        if highlight_turns and self.turns:
            for turn in self.turns:
                # Shade turn period
                ax1.axvspan(turn['start'], turn['end'], 
                          color='red', alpha=0.2, 
                          label=f"Turn ({turn['impact']:.0f}bps)" if turn == self.turns[0] else None)
        
        # Add statistics
        mean_rate = self.forwards['forward_rate'].mean()
        std_rate = self.forwards['forward_rate'].std()
        ax1.axhline(y=mean_rate, color='green', linestyle='--', 
                   linewidth=1, alpha=0.7, label=f'Mean: {mean_rate:.2f}%')
        ax1.fill_between(self.forwards['date'], 
                        mean_rate - std_rate, mean_rate + std_rate,
                        color='green', alpha=0.1, label=f'±1σ: {std_rate:.2f}%')
        
        # Format main plot
        ax1.set_xlabel('Date', fontsize=11)
        ax1.set_ylabel('Forward Rate (%)', fontsize=11)
        ax1.set_title('Daily Overnight Forward Rates with Turn Analysis', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper right', fontsize=10)
        
        # Format x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Plot butterflies if requested
        if ax2 and not self.butterflies.empty:
            x_pos = np.arange(len(self.butterflies))
            colors = ['green' if bv > 0 else 'red' for bv in self.butterflies['butterfly_value']]
            
            bars = ax2.bar(x_pos, self.butterflies['butterfly_value'], 
                          color=colors, alpha=0.7)
            
            # Add value labels on bars
            for bar, val in zip(bars, self.butterflies['butterfly_value']):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{val:.1f}', ha='center', va='bottom' if height > 0 else 'top',
                        fontsize=9)
            
            ax2.set_xlabel('Butterfly', fontsize=11)
            ax2.set_ylabel('Value (bps)', fontsize=11)
            ax2.set_title('Butterfly Spreads (2*Body - Left - Right)', fontsize=12)
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels(self.butterflies['butterfly'], fontsize=10)
            ax2.axhline(y=0, color='black', linewidth=0.5)
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save if requested
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        
        return fig
    
    def export_forwards(self, filepath: str):
        """Export forward rates to CSV"""
        if self.forwards.empty:
            print("No forward rates to export")
            return
        
        # Add additional columns
        df = self.forwards.copy()
        df['day_of_week'] = df['date'].dt.day_name()
        df['is_turn'] = False
        
        # Mark turn days
        for turn in self.turns:
            mask = (df['date'] >= turn['start']) & (df['date'] <= turn['end'])
            df.loc[mask, 'is_turn'] = True
        
        # Export
        df.to_csv(filepath, index=False)
        print(f"Exported {len(df)} forward rates to {filepath}")
    
    def calculate_statistics(self) -> Dict[str, float]:
        """Calculate statistics on forward rates"""
        if self.forwards.empty:
            return {}
        
        rates = self.forwards['forward_rate']
        
        stats = {
            'mean': rates.mean(),
            'std': rates.std(),
            'min': rates.min(),
            'max': rates.max(),
            'range': rates.max() - rates.min(),
            'skew': rates.skew(),
            'kurtosis': rates.kurtosis(),
            'turn_days': len([d for turn in self.turns for d in pd.date_range(turn['start'], turn['end'])]),
            'total_days': len(rates),
            'turn_percentage': 0.0
        }
        
        if stats['total_days'] > 0:
            stats['turn_percentage'] = (stats['turn_days'] / stats['total_days']) * 100
        
        return stats


def load_curve_with_turns(config_file: str) -> Tuple['Curve', Dict]:
    """Load curve from YAML configuration with turn handling"""
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Build base curve
    base_config = config.get('base_curve', {})
    nodes = {}
    for node in base_config.get('nodes', []):
        date = dt.strptime(node['date'], "%Y-%m-%d")
        nodes[date] = node.get('df', 1.0)
    
    base_curve = Curve(
        nodes=nodes,
        id=base_config.get('id'),
        convention=base_config.get('convention', 'act360'),
        calendar=base_config.get('calendar', 'nyc'),
        interpolation=base_config.get('interpolation', 'log_linear')
    )
    
    # Handle turns if configured
    if 'turn_curve' in config:
        turn_config = config['turn_curve']
        turn_nodes = {}
        for node in turn_config.get('nodes', []):
            date = dt.strptime(node['date'], "%Y-%m-%d")
            turn_nodes[date] = node.get('df', 1.0)
        
        turn_curve = Curve(
            nodes=turn_nodes,
            id=turn_config.get('id'),
            convention=turn_config.get('convention', 'act360'),
            calendar=turn_config.get('calendar', 'nyc'),
            interpolation=turn_config.get('interpolation', 'log_linear')
        )
        
        # Create composite curve
        if 'composite_curve' in config:
            curve = CompositeCurve([base_curve, turn_curve])
        else:
            curve = base_curve
    else:
        curve = base_curve
    
    return curve, config


def demonstrate_daily_forwards():
    """Demonstrate daily forward calculation and plotting"""
    print("=" * 80)
    print("Daily Overnight Forward Rate Analysis")
    print("=" * 80)
    
    # Create a sample curve with turns
    nodes = {
        dt(2024, 11, 1): 1.0,
        dt(2024, 12, 1): 0.996,
        dt(2024, 12, 30): 0.993,
        dt(2024, 12, 31): 0.9929,  # Turn start
        dt(2025, 1, 2): 0.9928,    # Turn end  
        dt(2025, 1, 31): 0.989,
        dt(2025, 3, 1): 0.985,
        dt(2025, 6, 1): 0.978,
        dt(2025, 12, 1): 0.960,
        dt(2026, 12, 1): 0.920
    }
    
    curve = Curve(
        nodes=nodes,
        convention="act360",
        calendar="nyc",
        interpolation="log_linear",
        id="sample_curve"
    )
    
    # Initialize calculator
    calc = DailyForwardCalculator(curve)
    
    # Calculate daily forwards
    print("\n1. Calculating daily overnight forwards...")
    df = calc.calculate_daily_forwards(
        start_date=dt(2024, 11, 1),
        end_date=dt(2026, 1, 1),
        method="direct"
    )
    print(f"   Calculated {len(df)} daily forward rates")
    
    # Identify turns
    print("\n2. Identifying turn periods...")
    turns = calc.identify_turns(threshold=20)  # 20 bps threshold
    print(f"   Found {len(turns)} turn periods")
    for i, turn in enumerate(turns, 1):
        print(f"   Turn {i}: {turn['start'].strftime('%Y-%m-%d')} to {turn['end'].strftime('%Y-%m-%d')} ({turn['impact']:.0f} bps)")
    
    # Calculate butterflies
    print("\n3. Calculating butterfly spreads...")
    butterflies = calc.calculate_butterflies()
    print(f"   Calculated {len(butterflies)} butterfly spreads:")
    for _, row in butterflies.iterrows():
        print(f"   {row['butterfly']}: {row['butterfly_value']:.2f} bps")
    
    # Calculate statistics
    print("\n4. Forward rate statistics:")
    stats = calc.calculate_statistics()
    for key, value in stats.items():
        if key.endswith('percentage'):
            print(f"   {key}: {value:.1f}%")
        elif key.endswith('days'):
            print(f"   {key}: {value:.0f}")
        else:
            print(f"   {key}: {value:.4f}%")
    
    # Plot
    print("\n5. Creating visualization...")
    fig = calc.plot_daily_forwards(
        highlight_turns=True,
        show_butterflies=True,
        save_path="./plots/daily_forwards.png"
    )
    
    # Export data
    print("\n6. Exporting data...")
    calc.export_forwards("./data/daily_forwards.csv")
    
    return calc


if __name__ == "__main__":
    # Run demonstration
    calc = demonstrate_daily_forwards()
    
    # Show plot
    plt.show()
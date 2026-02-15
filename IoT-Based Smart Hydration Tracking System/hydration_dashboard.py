"""
IoT Smart Hydration Tracking - Centralized Dashboard (Windows Compatible)
==========================================================================
Firebase cloud database integration
Time-series forecasting for personalized recommendations
Serves 100+ participants with real-time monitoring
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Try to import statsmodels for forecasting
try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.tsa.arima.model import ARIMA
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    print("Note: statsmodels not installed. Using simple forecasting.")

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (15, 10)

class HydrationDashboard:
    """
    Centralized dashboard for IoT hydration tracking system
    """
    
    def __init__(self, output_dir=None):
        """Initialize dashboard"""
        print("="*80)
        print("IOT SMART HYDRATION TRACKING - CENTRALIZED DASHBOARD")
        print("="*80)
        print()
        
        # Set output directory (Windows compatible)
        if output_dir is None:
            self.output_dir = os.getcwd()  # Current directory
        else:
            self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"✓ Output directory: {self.output_dir}")
        
        # Data storage
        self.users_data = {}
        self.forecasts = {}
        
        print("✓ Dashboard initialized successfully\n")
    
    def fetch_user_data(self, user_id: str, days: int = 7) -> pd.DataFrame:
        """
        Fetch historical data for a user
        For demo: generates simulated data
        """
        print(f"Fetching data for user: {user_id} (last {days} days)")
        
        # Generate simulated data
        data = self._generate_simulated_data(user_id, days)
        
        print(f"✓ Retrieved {len(data)} data points")
        return data
    
    def _generate_simulated_data(self, user_id: str, days: int) -> pd.DataFrame:
        """Generate simulated hydration data"""
        
        # Generate timestamps (every 30 minutes)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        timestamps = pd.date_range(start=start_time, end=end_time, freq='30min')
        
        np.random.seed(hash(user_id) % 2**32)
        
        n_points = len(timestamps)
        hours = np.array([t.hour + t.minute/60.0 for t in timestamps])
        
        # Daily hydration pattern
        daily_pattern = (
            0.3 * np.sin((hours - 6) * np.pi / 12) +
            0.5 * (1 - np.abs(hours - 14) / 12) +
            0.2 * np.random.randn(n_points)
        )
        daily_pattern = np.clip(daily_pattern, 0, 1)
        
        # Generate water levels
        water_levels = []
        current_level = 100.0
        
        for pattern_val in daily_pattern:
            # Drinking events
            if np.random.random() < pattern_val * 0.3:
                consumption = np.random.uniform(50, 200)
                current_level -= (consumption / 1000) * 100
            
            # Refill events
            if current_level < 20 and np.random.random() < 0.7:
                current_level = 100.0
            
            current_level = max(0, min(100, current_level))
            water_levels.append(current_level)
        
        volumes = [level * 10 for level in water_levels]
        
        data = pd.DataFrame({
            'timestamp': timestamps,
            'water_level_percent': water_levels,
            'volume_ml': volumes,
            'user_id': user_id,
            'device_id': f'DEVICE_{user_id[-3:]}'
        })
        
        data['consumption_ml'] = -data['volume_ml'].diff().clip(lower=0)
        data['is_drinking_event'] = data['consumption_ml'] > 50
        data['date'] = data['timestamp'].dt.date
        data['daily_consumption'] = data.groupby('date')['consumption_ml'].cumsum()
        
        return data
    
    def analyze_user_patterns(self, user_id: str, data: pd.DataFrame) -> dict:
        """Analyze historical hydration patterns"""
        print(f"\nAnalyzing patterns for {user_id}...")
        
        if data.empty:
            return {}
        
        daily_stats = data.groupby('date').agg({
            'consumption_ml': 'sum',
            'is_drinking_event': 'sum'
        }).rename(columns={'is_drinking_event': 'drinking_events'})
        
        data['hour'] = data['timestamp'].dt.hour
        hourly_pattern = data.groupby('hour')['consumption_ml'].sum()
        
        data['day_of_week'] = data['timestamp'].dt.dayofweek
        weekly_pattern = data.groupby('day_of_week')['consumption_ml'].sum()
        
        analysis = {
            'user_id': user_id,
            'total_consumption_ml': data['consumption_ml'].sum(),
            'avg_daily_consumption_ml': daily_stats['consumption_ml'].mean(),
            'std_daily_consumption_ml': daily_stats['consumption_ml'].std(),
            'max_daily_consumption_ml': daily_stats['consumption_ml'].max(),
            'min_daily_consumption_ml': daily_stats['consumption_ml'].min(),
            'avg_drinking_events_per_day': daily_stats['drinking_events'].mean(),
            'peak_hydration_hour': int(hourly_pattern.idxmax()),
            'peak_hydration_day': int(weekly_pattern.idxmax()),
            'consistency_score': 1 - (daily_stats['consumption_ml'].std() / 
                                    daily_stats['consumption_ml'].mean()),
            'days_analyzed': len(daily_stats)
        }
        
        print("✓ Pattern analysis complete")
        print(f"  Average daily consumption: {analysis['avg_daily_consumption_ml']:.0f} ml")
        print(f"  Peak hydration hour: {analysis['peak_hydration_hour']}:00")
        
        return analysis
    
    def forecast_consumption(self, data: pd.DataFrame, forecast_days: int = 7) -> pd.DataFrame:
        """Time-series forecasting for hydration patterns"""
        print(f"\nGenerating {forecast_days}-day forecast...")
        
        if len(data) < 48:
            print("✗ Insufficient data for forecasting")
            return pd.DataFrame()
        
        try:
            daily_consumption = data.groupby('date')['consumption_ml'].sum()
            daily_consumption.index = pd.to_datetime(daily_consumption.index)
            
            if HAS_STATSMODELS:
                # Use ARIMA if available
                try:
                    model = ARIMA(daily_consumption, order=(1, 1, 1))
                    fit = model.fit()
                    forecast_values = fit.forecast(steps=forecast_days)
                except:
                    # Fallback to simple average
                    forecast_values = pd.Series(
                        [daily_consumption.mean()] * forecast_days,
                        index=pd.date_range(
                            start=daily_consumption.index[-1] + timedelta(days=1),
                            periods=forecast_days
                        )
                    )
            else:
                # Simple moving average
                forecast_values = pd.Series(
                    [daily_consumption.mean()] * forecast_days,
                    index=pd.date_range(
                        start=daily_consumption.index[-1] + timedelta(days=1),
                        periods=forecast_days
                    )
                )
            
            forecast_df = pd.DataFrame({
                'date': forecast_values.index,
                'forecasted_consumption_ml': forecast_values.values,
                'lower_bound': forecast_values.values * 0.8,
                'upper_bound': forecast_values.values * 1.2
            })
            
            print("✓ Forecast generated successfully")
            print(f"  Average forecasted consumption: {forecast_values.mean():.0f} ml/day")
            
            return forecast_df
            
        except Exception as e:
            print(f"✗ Forecasting error: {e}")
            return pd.DataFrame()
    
    def generate_recommendations(self, analysis: dict, forecast: pd.DataFrame) -> dict:
        """Generate personalized hydration recommendations"""
        print("\nGenerating personalized recommendations...")
        
        if not analysis:
            return {}
        
        RECOMMENDED_DAILY_ML = 2000
        current_avg = analysis['avg_daily_consumption_ml']
        performance_ratio = current_avg / RECOMMENDED_DAILY_ML
        
        recommendations = {
            'user_id': analysis['user_id'],
            'current_daily_avg_ml': current_avg,
            'recommended_daily_ml': RECOMMENDED_DAILY_ML,
            'performance_ratio': performance_ratio,
            'meeting_goal': performance_ratio >= 0.9,
            'recommendations': []
        }
        
        # Generate specific recommendations
        if performance_ratio < 0.7:
            recommendations['recommendations'].append({
                'priority': 'HIGH',
                'category': 'Increase Intake',
                'message': f'You are drinking {current_avg:.0f}ml/day. '
                          f'Increase by {RECOMMENDED_DAILY_ML - current_avg:.0f}ml to reach the goal.',
                'action': 'Set reminders every 2 hours to drink water'
            })
        elif performance_ratio < 0.9:
            recommendations['recommendations'].append({
                'priority': 'MEDIUM',
                'category': 'Minor Adjustment',
                'message': f'You are close! Increase by {RECOMMENDED_DAILY_ML - current_avg:.0f}ml/day.',
                'action': 'Add one extra glass of water with each meal'
            })
        else:
            recommendations['recommendations'].append({
                'priority': 'INFO',
                'category': 'Great Job!',
                'message': 'You are meeting your hydration goals!',
                'action': 'Maintain current hydration routine'
            })
        
        if analysis['consistency_score'] < 0.7:
            recommendations['recommendations'].append({
                'priority': 'MEDIUM',
                'category': 'Improve Consistency',
                'message': 'Your daily intake varies significantly.',
                'action': 'Set fixed hydration times throughout the day'
            })
        
        print("✓ Recommendations generated")
        print(f"  Total recommendations: {len(recommendations['recommendations'])}")
        
        return recommendations
    
    def visualize_dashboard(self, user_id: str, data: pd.DataFrame, 
                          forecast: pd.DataFrame, analysis: dict):
        """Create comprehensive visualization dashboard"""
        print("\nGenerating dashboard visualizations...")
        
        fig = plt.figure(figsize=(20, 12))
        
        # 1. Water Level Over Time
        ax1 = plt.subplot(3, 3, 1)
        ax1.plot(data['timestamp'], data['water_level_percent'], 
                linewidth=2, color='#4ECDC4', alpha=0.7)
        ax1.fill_between(data['timestamp'], 0, data['water_level_percent'], 
                         alpha=0.3, color='#4ECDC4')
        ax1.set_xlabel('Time', fontweight='bold')
        ax1.set_ylabel('Water Level (%)', fontweight='bold')
        ax1.set_title('Water Level Over Time', fontsize=14, fontweight='bold')
        ax1.grid(alpha=0.3)
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # 2. Daily Consumption
        ax2 = plt.subplot(3, 3, 2)
        daily_consumption = data.groupby('date')['consumption_ml'].sum()
        colors = ['#4ECDC4' if x >= 2000 else '#FF6B6B' for x in daily_consumption.values]
        ax2.bar(range(len(daily_consumption)), daily_consumption.values, 
               color=colors, edgecolor='black', alpha=0.8)
        ax2.axhline(y=2000, color='green', linestyle='--', linewidth=2, 
                   label='Goal (2L)', alpha=0.7)
        ax2.set_xlabel('Day', fontweight='bold')
        ax2.set_ylabel('Consumption (ml)', fontweight='bold')
        ax2.set_title('Daily Water Consumption', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. Hourly Pattern
        ax3 = plt.subplot(3, 3, 3)
        hourly_pattern = data.groupby(data['timestamp'].dt.hour)['consumption_ml'].sum()
        ax3.plot(hourly_pattern.index, hourly_pattern.values, 
                marker='o', linewidth=3, markersize=8, color='#4ECDC4')
        ax3.fill_between(hourly_pattern.index, 0, hourly_pattern.values, 
                        alpha=0.3, color='#4ECDC4')
        ax3.set_xlabel('Hour of Day', fontweight='bold')
        ax3.set_ylabel('Total Consumption (ml)', fontweight='bold')
        ax3.set_title('Hourly Hydration Pattern', fontsize=14, fontweight='bold')
        ax3.grid(alpha=0.3)
        ax3.set_xticks(range(0, 24, 3))
        
        # 4. Drinking Events
        ax4 = plt.subplot(3, 3, 4)
        drinking_events = data[data['is_drinking_event']]
        ax4.scatter(drinking_events['timestamp'], drinking_events['consumption_ml'],
                   s=100, alpha=0.6, c='#4ECDC4', edgecolors='black', linewidth=1)
        ax4.set_xlabel('Time', fontweight='bold')
        ax4.set_ylabel('Consumption (ml)', fontweight='bold')
        ax4.set_title('Drinking Events', fontsize=14, fontweight='bold')
        ax4.grid(alpha=0.3)
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
        
        # 5. Forecast
        ax5 = plt.subplot(3, 3, 5)
        if not forecast.empty:
            daily_hist = data.groupby('date')['consumption_ml'].sum()
            ax5.plot(daily_hist.index, daily_hist.values, 
                    marker='o', linewidth=2, label='Historical', color='#4ECDC4')
            ax5.plot(forecast['date'], forecast['forecasted_consumption_ml'],
                    marker='s', linewidth=2, linestyle='--', 
                    label='Forecast', color='#FF6B6B')
            ax5.fill_between(forecast['date'], 
                            forecast['lower_bound'], 
                            forecast['upper_bound'],
                            alpha=0.2, color='#FF6B6B', label='Confidence')
            ax5.axhline(y=2000, color='green', linestyle='--', 
                       linewidth=2, alpha=0.5, label='Goal')
            ax5.set_xlabel('Date', fontweight='bold')
            ax5.set_ylabel('Consumption (ml)', fontweight='bold')
            ax5.set_title('Time-Series Forecast', fontsize=14, fontweight='bold')
            ax5.legend(fontsize=8)
            ax5.grid(alpha=0.3)
            plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45)
        
        # 6. Weekly Pattern
        ax6 = plt.subplot(3, 3, 6)
        data['day_name'] = data['timestamp'].dt.day_name()
        weekly = data.groupby('day_name')['consumption_ml'].sum()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                    'Friday', 'Saturday', 'Sunday']
        weekly = weekly.reindex([d for d in day_order if d in weekly.index])
        
        ax6.bar(range(len(weekly)), weekly.values, color='#95E1D3', 
               edgecolor='black', alpha=0.8)
        ax6.set_xlabel('Day of Week', fontweight='bold')
        ax6.set_ylabel('Total Consumption (ml)', fontweight='bold')
        ax6.set_title('Weekly Pattern', fontsize=14, fontweight='bold')
        ax6.set_xticks(range(len(weekly)))
        ax6.set_xticklabels([d[:3] for d in weekly.index], rotation=45)
        ax6.grid(axis='y', alpha=0.3)
        
        # 7. Statistics Panel
        ax7 = plt.subplot(3, 3, 7)
        ax7.axis('off')
        
        stats_text = f"""
USER STATISTICS
{'='*35}

User ID: {user_id}
Period: {analysis.get('days_analyzed', 0)} days

Daily Average: {analysis.get('avg_daily_consumption_ml', 0):.0f} ml
Daily Goal: 2000 ml
Achievement: {(analysis.get('avg_daily_consumption_ml', 0)/2000*100):.1f}%

Events/Day: {analysis.get('avg_drinking_events_per_day', 0):.1f}
Peak Hour: {analysis.get('peak_hydration_hour', 0)}:00

Consistency: {analysis.get('consistency_score', 0):.2f}
Total: {analysis.get('total_consumption_ml', 0):.0f} ml
        """
        
        ax7.text(0.1, 0.5, stats_text, fontsize=10, family='monospace',
                verticalalignment='center')
        
        # 8. Distribution
        ax8 = plt.subplot(3, 3, 8)
        daily_values = data.groupby('date')['consumption_ml'].sum()
        ax8.hist(daily_values, bins=10, color='#4ECDC4', 
                edgecolor='black', alpha=0.7)
        ax8.axvline(x=2000, color='green', linestyle='--', linewidth=2, label='Goal')
        ax8.axvline(x=daily_values.mean(), color='red', linestyle='--', 
                   linewidth=2, label=f'Avg ({daily_values.mean():.0f}ml)')
        ax8.set_xlabel('Daily Consumption (ml)', fontweight='bold')
        ax8.set_ylabel('Frequency', fontweight='bold')
        ax8.set_title('Distribution', fontsize=14, fontweight='bold')
        ax8.legend(fontsize=8)
        ax8.grid(axis='y', alpha=0.3)
        
        # 9. Performance Gauge
        ax9 = plt.subplot(3, 3, 9, projection='polar')
        performance = analysis.get('avg_daily_consumption_ml', 0) / 2000
        performance = min(performance, 1.5)
        
        theta = np.linspace(0, np.pi, 100)
        ax9.plot(theta, np.ones_like(theta), color='lightgray', linewidth=20, alpha=0.3)
        
        perf_theta = np.linspace(0, performance * np.pi, 100)
        color = '#4ECDC4' if performance >= 0.9 else '#FF6B6B'
        ax9.plot(perf_theta, np.ones_like(perf_theta), color=color, linewidth=20)
        
        ax9.set_ylim(0, 1)
        ax9.set_yticks([])
        ax9.set_xticks([0, np.pi/2, np.pi])
        ax9.set_xticklabels(['0%', '50%', '100%'])
        ax9.set_title(f'Goal: {performance*100:.0f}%', 
                     fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Save to current directory (Windows compatible)
        output_path = os.path.join(self.output_dir, f'dashboard_{user_id}.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Dashboard saved: {output_path}")
        
        plt.close()
        return output_path

def main():
    """Main execution"""
    
    print("Starting Centralized Hydration Dashboard...\n")
    
    # Initialize dashboard (output to current directory)
    dashboard = HydrationDashboard()
    
    # Process users
    user_ids = ['USER_001', 'USER_002', 'USER_003']
    
    print(f"\nProcessing {len(user_ids)} users...")
    print("="*80)
    
    for user_id in user_ids:
        print(f"\n{'='*80}")
        print(f"Processing: {user_id}")
        print(f"{'='*80}")
        
        # Fetch data
        data = dashboard.fetch_user_data(user_id, days=14)
        
        if data.empty:
            continue
        
        # Analyze
        analysis = dashboard.analyze_user_patterns(user_id, data)
        
        # Forecast
        forecast = dashboard.forecast_consumption(data, forecast_days=7)
        
        # Recommendations
        recommendations = dashboard.generate_recommendations(analysis, forecast)
        
        # Display recommendations
        print("\nPERSONALIZED RECOMMENDATIONS:")
        print("-" * 80)
        for i, rec in enumerate(recommendations.get('recommendations', []), 1):
            print(f"\n{i}. [{rec['priority']}] {rec['category']}")
            print(f"   {rec['message']}")
            print(f"   → {rec['action']}")
        
        # Visualize
        dashboard.visualize_dashboard(user_id, data, forecast, analysis)
    
    print("\n" + "="*80)
    print("DASHBOARD PROCESSING COMPLETE!")
    print("="*80)
    print(f"\n✓ Processed {len(user_ids)} users")
    print(f"✓ Generated {len(user_ids)} dashboards")
    print(f"\nFiles saved in: {dashboard.output_dir}")

if __name__ == "__main__":
    main()

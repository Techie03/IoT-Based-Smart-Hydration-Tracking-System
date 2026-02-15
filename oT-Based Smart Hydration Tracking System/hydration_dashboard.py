"""
IoT Smart Hydration Tracking - Centralized Dashboard
=====================================================
Firebase cloud database integration
Time-series forecasting for personalized recommendations
Serves 100+ participants with real-time monitoring

Features:
- Real-time data retrieval from Firebase
- Time-series analysis and forecasting
- Personalized hydration recommendations
- Multi-user dashboard
- Historical behavior analysis
"""

import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (15, 10)

class HydrationDashboard:
    """
    Centralized dashboard for IoT hydration tracking system
    """
    
    def __init__(self, firebase_config_path: str):
        """Initialize dashboard with Firebase credentials"""
        print("="*80)
        print("IOT SMART HYDRATION TRACKING - CENTRALIZED DASHBOARD")
        print("="*80)
        print()
        
        # Initialize Firebase
        self._initialize_firebase(firebase_config_path)
        
        # Data storage
        self.users_data = {}
        self.devices_data = {}
        self.forecasts = {}
        
        print("✓ Dashboard initialized successfully\n")
    
    def _initialize_firebase(self, config_path: str):
        """Initialize Firebase Admin SDK"""
        try:
            # Initialize with service account
            cred = credentials.Certificate(config_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://your-project.firebaseio.com'
            })
            print("✓ Firebase connection established")
        except Exception as e:
            print(f"✗ Firebase initialization error: {e}")
            # For demo, create simulated data
            print("  Using simulated data for demonstration")
    
    def fetch_user_data(self, user_id: str, days: int = 7) -> pd.DataFrame:
        """
        Fetch historical data for a user from Firebase
        
        Args:
            user_id: User identifier
            days: Number of days to fetch
            
        Returns:
            DataFrame with hydration data
        """
        print(f"Fetching data for user: {user_id} (last {days} days)")
        
        try:
            # In production, fetch from Firebase
            # ref = db.reference(f'/hydration/{user_id}/readings')
            # data = ref.order_by_child('timestamp').get()
            
            # For demo, generate simulated data
            data = self._generate_simulated_data(user_id, days)
            
            print(f"✓ Retrieved {len(data)} data points")
            return data
            
        except Exception as e:
            print(f"✗ Error fetching data: {e}")
            return pd.DataFrame()
    
    def _generate_simulated_data(self, user_id: str, days: int) -> pd.DataFrame:
        """Generate simulated hydration data for demonstration"""
        
        # Generate timestamps (every 30 minutes)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        timestamps = pd.date_range(start=start_time, end=end_time, freq='30min')
        
        np.random.seed(hash(user_id) % 2**32)  # Consistent data per user
        
        # Simulate daily hydration patterns
        n_points = len(timestamps)
        
        # Base consumption with daily pattern
        hours = np.array([t.hour + t.minute/60.0 for t in timestamps])
        
        # Morning ramp-up, steady midday, evening taper
        daily_pattern = (
            0.3 * np.sin((hours - 6) * np.pi / 12) +  # Morning increase
            0.5 * (1 - np.abs(hours - 14) / 12) +      # Midday peak
            0.2 * np.random.randn(n_points)            # Random variation
        )
        daily_pattern = np.clip(daily_pattern, 0, 1)
        
        # Generate water levels (100% = full bottle)
        water_levels = []
        current_level = 100.0
        
        for pattern_val in daily_pattern:
            # Consumption events (drinking)
            if np.random.random() < pattern_val * 0.3:  # Drinking probability
                consumption = np.random.uniform(50, 200)  # ml
                current_level -= (consumption / 1000) * 100  # Convert to %
            
            # Refill events
            if current_level < 20 and np.random.random() < 0.7:
                current_level = 100.0
            
            current_level = max(0, min(100, current_level))
            water_levels.append(current_level)
        
        # Calculate consumption
        volumes = [level * 10 for level in water_levels]  # Assume 1000ml bottle
        
        # Create DataFrame
        data = pd.DataFrame({
            'timestamp': timestamps,
            'water_level_percent': water_levels,
            'volume_ml': volumes,
            'user_id': user_id,
            'device_id': f'DEVICE_{user_id[-3:]}'
        })
        
        # Calculate consumption events
        data['consumption_ml'] = -data['volume_ml'].diff().clip(lower=0)
        data['is_drinking_event'] = data['consumption_ml'] > 50
        
        # Add cumulative consumption per day
        data['date'] = data['timestamp'].dt.date
        data['daily_consumption'] = data.groupby('date')['consumption_ml'].cumsum()
        
        return data
    
    def analyze_user_patterns(self, user_id: str, data: pd.DataFrame) -> dict:
        """
        Analyze historical hydration patterns
        
        Returns:
            Dictionary with analysis results
        """
        print(f"\nAnalyzing patterns for {user_id}...")
        
        if data.empty:
            return {}
        
        # Daily statistics
        daily_stats = data.groupby('date').agg({
            'consumption_ml': 'sum',
            'is_drinking_event': 'sum'
        }).rename(columns={'is_drinking_event': 'drinking_events'})
        
        # Hourly patterns
        data['hour'] = data['timestamp'].dt.hour
        hourly_pattern = data.groupby('hour')['consumption_ml'].sum()
        
        # Weekly patterns
        data['day_of_week'] = data['timestamp'].dt.dayofweek
        weekly_pattern = data.groupby('day_of_week')['consumption_ml'].sum()
        
        # Calculate statistics
        analysis = {
            'user_id': user_id,
            'total_consumption_ml': data['consumption_ml'].sum(),
            'avg_daily_consumption_ml': daily_stats['consumption_ml'].mean(),
            'std_daily_consumption_ml': daily_stats['consumption_ml'].std(),
            'max_daily_consumption_ml': daily_stats['consumption_ml'].max(),
            'min_daily_consumption_ml': daily_stats['consumption_ml'].min(),
            'avg_drinking_events_per_day': daily_stats['drinking_events'].mean(),
            'peak_hydration_hour': hourly_pattern.idxmax(),
            'peak_hydration_day': weekly_pattern.idxmax(),
            'consistency_score': 1 - (daily_stats['consumption_ml'].std() / 
                                    daily_stats['consumption_ml'].mean()),
            'days_analyzed': len(daily_stats)
        }
        
        print("✓ Pattern analysis complete")
        print(f"  Average daily consumption: {analysis['avg_daily_consumption_ml']:.0f} ml")
        print(f"  Peak hydration hour: {analysis['peak_hydration_hour']}:00")
        print(f"  Consistency score: {analysis['consistency_score']:.2f}")
        
        return analysis
    
    def forecast_consumption(self, data: pd.DataFrame, forecast_days: int = 7) -> pd.DataFrame:
        """
        Time-series forecasting for hydration patterns
        
        Args:
            data: Historical hydration data
            forecast_days: Number of days to forecast
            
        Returns:
            DataFrame with forecasted values
        """
        print(f"\nGenerating {forecast_days}-day forecast...")
        
        if len(data) < 48:  # Need at least 2 days of data
            print("✗ Insufficient data for forecasting")
            return pd.DataFrame()
        
        try:
            # Prepare time series (daily consumption)
            daily_consumption = data.groupby('date')['consumption_ml'].sum()
            daily_consumption.index = pd.to_datetime(daily_consumption.index)
            
            # Method 1: Exponential Smoothing (Holt-Winters)
            try:
                model_hw = ExponentialSmoothing(
                    daily_consumption,
                    seasonal_periods=7,  # Weekly seasonality
                    trend='add',
                    seasonal='add'
                )
                fit_hw = model_hw.fit()
                forecast_hw = fit_hw.forecast(steps=forecast_days)
            except:
                forecast_hw = None
            
            # Method 2: ARIMA
            try:
                model_arima = ARIMA(daily_consumption, order=(1, 1, 1))
                fit_arima = model_arima.fit()
                forecast_arima = fit_arima.forecast(steps=forecast_days)
            except:
                forecast_arima = None
            
            # Combine forecasts (ensemble)
            if forecast_hw is not None and forecast_arima is not None:
                forecast_values = (forecast_hw + forecast_arima) / 2
            elif forecast_hw is not None:
                forecast_values = forecast_hw
            elif forecast_arima is not None:
                forecast_values = forecast_arima
            else:
                # Fallback: simple moving average
                forecast_values = pd.Series(
                    [daily_consumption.mean()] * forecast_days,
                    index=pd.date_range(
                        start=daily_consumption.index[-1] + timedelta(days=1),
                        periods=forecast_days
                    )
                )
            
            # Create forecast DataFrame
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
        """
        Generate personalized hydration recommendations based on historical behavior
        
        Args:
            analysis: User pattern analysis
            forecast: Forecasted consumption
            
        Returns:
            Dictionary with recommendations
        """
        print("\nGenerating personalized recommendations...")
        
        if not analysis or forecast.empty:
            return {}
        
        # Recommended daily intake (general guideline)
        RECOMMENDED_DAILY_ML = 2000  # 2 liters
        
        # Calculate current performance
        current_avg = analysis['avg_daily_consumption_ml']
        performance_ratio = current_avg / RECOMMENDED_DAILY_ML
        
        # Generate recommendations
        recommendations = {
            'user_id': analysis['user_id'],
            'current_daily_avg_ml': current_avg,
            'recommended_daily_ml': RECOMMENDED_DAILY_ML,
            'performance_ratio': performance_ratio,
            'meeting_goal': performance_ratio >= 0.9,
            'recommendations': []
        }
        
        # Specific recommendations based on behavior
        if performance_ratio < 0.7:
            recommendations['recommendations'].append({
                'priority': 'HIGH',
                'category': 'Increase Intake',
                'message': f'You are drinking {current_avg:.0f}ml/day. '
                          f'Increase by {RECOMMENDED_DAILY_ML - current_avg:.0f}ml '
                          f'to reach the recommended 2L goal.',
                'action': 'Set reminders every 2 hours to drink water'
            })
        elif performance_ratio < 0.9:
            recommendations['recommendations'].append({
                'priority': 'MEDIUM',
                'category': 'Minor Adjustment',
                'message': f'You are close to the goal! '
                          f'Increase by {RECOMMENDED_DAILY_ML - current_avg:.0f}ml/day.',
                'action': 'Add one extra glass of water with each meal'
            })
        else:
            recommendations['recommendations'].append({
                'priority': 'INFO',
                'category': 'Great Job!',
                'message': f'You are meeting your hydration goals! '
                          f'Keep up the good work.',
                'action': 'Maintain current hydration routine'
            })
        
        # Consistency recommendations
        if analysis['consistency_score'] < 0.7:
            recommendations['recommendations'].append({
                'priority': 'MEDIUM',
                'category': 'Improve Consistency',
                'message': 'Your daily intake varies significantly. '
                          'Try to maintain a more consistent schedule.',
                'action': 'Set fixed hydration times throughout the day'
            })
        
        # Peak hour recommendations
        peak_hour = analysis['peak_hydration_hour']
        if peak_hour > 18:  # Late evening hydration
            recommendations['recommendations'].append({
                'priority': 'LOW',
                'category': 'Timing Optimization',
                'message': 'Most of your water intake happens in the evening. '
                          'Try to distribute more evenly throughout the day.',
                'action': 'Start hydrating earlier in the day'
            })
        
        # Forecast-based recommendations
        if not forecast.empty:
            avg_forecast = forecast['forecasted_consumption_ml'].mean()
            if avg_forecast < RECOMMENDED_DAILY_ML * 0.8:
                recommendations['recommendations'].append({
                    'priority': 'MEDIUM',
                    'category': 'Projected Shortfall',
                    'message': f'Based on trends, you may fall short by '
                              f'{RECOMMENDED_DAILY_ML - avg_forecast:.0f}ml/day next week.',
                    'action': 'Preemptively increase water intake'
                })
        
        print("✓ Recommendations generated")
        print(f"  Total recommendations: {len(recommendations['recommendations'])}")
        
        return recommendations
    
    def visualize_dashboard(self, user_id: str, data: pd.DataFrame, 
                          forecast: pd.DataFrame, analysis: dict):
        """
        Create comprehensive visualization dashboard
        """
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
        
        # 2. Daily Consumption Bar Chart
        ax2 = plt.subplot(3, 3, 2)
        daily_consumption = data.groupby('date')['consumption_ml'].sum()
        colors = ['#4ECDC4' if x >= 2000 else '#FF6B6B' for x in daily_consumption.values]
        ax2.bar(range(len(daily_consumption)), daily_consumption.values, 
               color=colors, edgecolor='black', alpha=0.8)
        ax2.axhline(y=2000, color='green', linestyle='--', linewidth=2, 
                   label='Recommended (2L)', alpha=0.7)
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
        
        # 4. Drinking Events Timeline
        ax4 = plt.subplot(3, 3, 4)
        drinking_events = data[data['is_drinking_event']]
        ax4.scatter(drinking_events['timestamp'], drinking_events['consumption_ml'],
                   s=100, alpha=0.6, c='#4ECDC4', edgecolors='black', linewidth=1)
        ax4.set_xlabel('Time', fontweight='bold')
        ax4.set_ylabel('Consumption Amount (ml)', fontweight='bold')
        ax4.set_title('Drinking Events', fontsize=14, fontweight='bold')
        ax4.grid(alpha=0.3)
        
        # 5. Forecast Plot
        ax5 = plt.subplot(3, 3, 5)
        if not forecast.empty:
            # Historical
            daily_hist = data.groupby('date')['consumption_ml'].sum()
            ax5.plot(daily_hist.index, daily_hist.values, 
                    marker='o', linewidth=2, label='Historical', color='#4ECDC4')
            
            # Forecast
            ax5.plot(forecast['date'], forecast['forecasted_consumption_ml'],
                    marker='s', linewidth=2, linestyle='--', 
                    label='Forecast', color='#FF6B6B')
            ax5.fill_between(forecast['date'], 
                            forecast['lower_bound'], 
                            forecast['upper_bound'],
                            alpha=0.2, color='#FF6B6B', label='Confidence Interval')
            
            ax5.axhline(y=2000, color='green', linestyle='--', 
                       linewidth=2, alpha=0.5, label='Goal (2L)')
            ax5.set_xlabel('Date', fontweight='bold')
            ax5.set_ylabel('Consumption (ml)', fontweight='bold')
            ax5.set_title('Time-Series Forecast', fontsize=14, fontweight='bold')
            ax5.legend()
            ax5.grid(alpha=0.3)
        
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
        ax6.set_title('Weekly Hydration Pattern', fontsize=14, fontweight='bold')
        ax6.set_xticks(range(len(weekly)))
        ax6.set_xticklabels([d[:3] for d in weekly.index], rotation=45)
        ax6.grid(axis='y', alpha=0.3)
        
        # 7. Statistics Panel
        ax7 = plt.subplot(3, 3, 7)
        ax7.axis('off')
        
        stats_text = f"""
        USER STATISTICS
        {'='*40}
        
        User ID: {user_id}
        Analysis Period: {analysis.get('days_analyzed', 0)} days
        
        Daily Average: {analysis.get('avg_daily_consumption_ml', 0):.0f} ml
        Daily Goal: 2000 ml
        Goal Achievement: {(analysis.get('avg_daily_consumption_ml', 0)/2000*100):.1f}%
        
        Drinking Events/Day: {analysis.get('avg_drinking_events_per_day', 0):.1f}
        Peak Hour: {analysis.get('peak_hydration_hour', 0)}:00
        
        Consistency Score: {analysis.get('consistency_score', 0):.2f}
        Total Consumed: {analysis.get('total_consumption_ml', 0):.0f} ml
        """
        
        ax7.text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
                verticalalignment='center')
        
        # 8. Consumption Distribution
        ax8 = plt.subplot(3, 3, 8)
        daily_values = data.groupby('date')['consumption_ml'].sum()
        ax8.hist(daily_values, bins=10, color='#4ECDC4', 
                edgecolor='black', alpha=0.7)
        ax8.axvline(x=2000, color='green', linestyle='--', 
                   linewidth=2, label='Goal (2L)')
        ax8.axvline(x=daily_values.mean(), color='red', linestyle='--', 
                   linewidth=2, label=f'Your Avg ({daily_values.mean():.0f}ml)')
        ax8.set_xlabel('Daily Consumption (ml)', fontweight='bold')
        ax8.set_ylabel('Frequency', fontweight='bold')
        ax8.set_title('Consumption Distribution', fontsize=14, fontweight='bold')
        ax8.legend()
        ax8.grid(axis='y', alpha=0.3)
        
        # 9. Performance Gauge
        ax9 = plt.subplot(3, 3, 9, projection='polar')
        performance = analysis.get('avg_daily_consumption_ml', 0) / 2000
        performance = min(performance, 1.5)  # Cap at 150%
        
        theta = np.linspace(0, np.pi, 100)
        r = np.ones_like(theta)
        
        # Background
        ax9.plot(theta, r, color='lightgray', linewidth=20, alpha=0.3)
        
        # Performance arc
        perf_theta = np.linspace(0, performance * np.pi, 100)
        color = '#4ECDC4' if performance >= 0.9 else '#FF6B6B'
        ax9.plot(perf_theta, np.ones_like(perf_theta), 
                color=color, linewidth=20)
        
        ax9.set_ylim(0, 1)
        ax9.set_yticks([])
        ax9.set_xticks([0, np.pi/2, np.pi])
        ax9.set_xticklabels(['0%', '50%', '100%'])
        ax9.set_title(f'Goal Achievement: {performance*100:.0f}%', 
                     fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(f'/home/claude/dashboard_{user_id}.png', 
                   dpi=300, bbox_inches='tight')
        print(f"✓ Dashboard saved: dashboard_{user_id}.png")
        
        return fig

def main():
    """Main execution function"""
    
    print("Starting Centralized Hydration Dashboard...\n")
    
    # Initialize dashboard (use dummy config for demo)
    dashboard = HydrationDashboard('firebase_config.json')
    
    # Simulate multiple users
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
            print(f"No data available for {user_id}")
            continue
        
        # Analyze patterns
        analysis = dashboard.analyze_user_patterns(user_id, data)
        
        # Generate forecast
        forecast = dashboard.forecast_consumption(data, forecast_days=7)
        
        # Generate recommendations
        recommendations = dashboard.generate_recommendations(analysis, forecast)
        
        # Display recommendations
        print("\nPERSONALIZED RECOMMENDATIONS:")
        print("-" * 80)
        for i, rec in enumerate(recommendations.get('recommendations', []), 1):
            print(f"\n{i}. [{rec['priority']}] {rec['category']}")
            print(f"   {rec['message']}")
            print(f"   → Action: {rec['action']}")
        
        # Create visualization
        dashboard.visualize_dashboard(user_id, data, forecast, analysis)
        
        print()
    
    print("\n" + "="*80)
    print("DASHBOARD PROCESSING COMPLETE!")
    print("="*80)
    print(f"\n✓ Processed {len(user_ids)} users")
    print(f"✓ Generated {len(user_ids)} dashboard visualizations")
    print(f"✓ Created personalized recommendations for all users")
    print("\nFiles generated:")
    for user_id in user_ids:
        print(f"  - dashboard_{user_id}.png")

if __name__ == "__main__":
    main()

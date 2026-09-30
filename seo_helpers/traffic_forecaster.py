#time-series forecasting and pattern-analysis tool built using Meta's Prophet library.
#nalyze historical website or traffic data from a CSV file, validate its forecasting accuracy, predict future traffic, and extract seasonal insights.
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from prophet import Prophet
import matplotlib.pyplot as plt

def load_and_prepare_data(file_path):
    """
    Load and prepare the traffic data from the specific CSV format.
    """
    # Read the CSV file
    df = pd.read_csv(file_path, header=None, names=['date', 'traffic'])
    
    # Clean the traffic column (remove commas and convert to float)
    df['traffic'] = df['traffic'].str.replace(',', '').astype(float)
    
    # Convert date to datetime (assuming current year if not specified)
    df['date'] = pd.to_datetime(df['date'].apply(lambda x: f"{x}-2024" if len(x.split('-')) == 2 else x), 
                               format='%d-%b-%Y')
    
    # Sort by date
    df = df.sort_values('date')
    
    # Prepare for Prophet (rename columns)
    df_prophet = df.rename(columns={'date': 'ds', 'traffic': 'y'})
    return df_prophet

def train_prophet_model(data, validation_days=30):
    """
    Train a Prophet model and validate its performance.
    """
    # Split data into training and validation
    train = data[:-validation_days]
    valid = data[-validation_days:]
    
    # Initialize and train Prophet model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=True,
        seasonality_mode='multiplicative',
        changepoint_prior_scale=0.05
    )
    
    # Add custom seasonality for monthly patterns
    model.add_seasonality(
        name='monthly',
        period=30.5,
        fourier_order=5
    )
    
    model.fit(train)
    
    # Make predictions for validation period
    future_dates = model.make_future_dataframe(periods=validation_days)
    forecast = model.predict(future_dates)
    
    # Calculate validation metrics
    predictions = forecast[-validation_days:]['yhat']
    actuals = valid['y']
    
    metrics = {
        'mae': mean_absolute_error(actuals, predictions),
        'rmse': np.sqrt(mean_squared_error(actuals, predictions)),
        'mape': np.mean(np.abs((actuals - predictions) / actuals)) * 100
    }
    
    return model, metrics

def generate_forecast(model, days_ahead=30):
    """
    Generate forecast for specified number of days ahead.
    """
    future_dates = model.make_future_dataframe(periods=days_ahead)
    forecast = model.predict(future_dates)
    
    # Extract relevant columns
    forecast_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']][-days_ahead:]
    forecast_df.columns = ['date', 'predicted_traffic', 'lower_bound', 'upper_bound']
    
    # Round predictions to whole numbers
    for col in ['predicted_traffic', 'lower_bound', 'upper_bound']:
        forecast_df[col] = forecast_df[col].round(0)
    
    return forecast_df

def analyze_traffic_patterns(model, data):
    """
    Analyze and return insights about traffic patterns.
    """
    # Get components of the forecast
    components = model.component_predictions(data)
    
    # Convert day numbers to day names
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    
    weekly_avg = components['weekly'].groupby(data['ds'].dt.dayofweek).mean()
    monthly_avg = components['yearly'].groupby(data['ds'].dt.month).mean()
    
    insights = {
        'weekly_pattern': {
            'highest_day': days[weekly_avg.idxmax()],
            'lowest_day': days[weekly_avg.idxmin()]
        },
        'yearly_pattern': {
            'peak_month': months[monthly_avg.idxmax() - 1],
            'lowest_month': months[monthly_avg.idxmin() - 1]
        },
        'growth_rate': model.params['growth'][0] * 365 * 100  # Annualized growth rate in percentage
    }
    
    return insights

# Main execution
if __name__ == "__main__":
    # Load and prepare data
    df_prepared = load_and_prepare_data('traffic_data.csv')
    
    # Train model and get validation metrics
    model, metrics = train_prophet_model(df_prepared)
    print("\nModel Validation Metrics:")
    print(f"Mean Absolute Error: {metrics['mae']:,.0f} visits")
    print(f"Root Mean Square Error: {metrics['rmse']:,.0f} visits")
    print(f"Mean Absolute Percentage Error: {metrics['mape']:.1f}%")
    
    # Generate forecast for next 30 days
    forecast = generate_forecast(model, days_ahead=30)
    print("\nTraffic Forecast for Next 30 Days:")
    print(forecast.to_string(index=False))
    
    # Get traffic pattern insights
    insights = analyze_traffic_patterns(model, df_prepared)
    print("\nTraffic Pattern Insights:")
    print(f"Highest Traffic Day: {insights['weekly_pattern']['highest_day']}")
    print(f"Lowest Traffic Day: {insights['weekly_pattern']['lowest_day']}")
    print(f"Peak Traffic Month: {insights['yearly_pattern']['peak_month']}")
    print(f"Lowest Traffic Month: {insights['yearly_pattern']['lowest_month']}")
    print(f"Annual Growth Rate: {insights['growth_rate']:.1f}%")
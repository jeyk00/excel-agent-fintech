import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Optional

def predict_future_revenue(historical_df: pd.DataFrame, years_ahead: int = 5) -> pd.DataFrame:
    """
    Predicts future revenue using Linear Regression on historical data.
    
    Args:
        historical_df (pd.DataFrame): DataFrame containing 'Year' and 'revenue' columns.
        years_ahead (int): Number of years to forecast.
        
    Returns:
        pd.DataFrame: DataFrame containing 'Year', 'revenue', and 'type' (Historical/Forecast).
    """
    if 'Year' not in historical_df.columns or 'revenue' not in historical_df.columns:
        raise ValueError("DataFrame must contain 'Year' and 'revenue' columns.")
    
    # Sort by Year
    df = historical_df.sort_values('Year').copy()
    df['type'] = 'Historical'
    
    # Handle empty or insufficient data
    if len(df) == 0:
        return pd.DataFrame(columns=['Year', 'revenue', 'type'])
    
    last_year = df['Year'].max()
    future_years = np.array([last_year + i for i in range(1, years_ahead + 1)]).reshape(-1, 1)
    
    # Logic for few data points
    if len(df) < 2:
        # If only 1 data point, assume 2% growth
        last_revenue = df.iloc[-1]['revenue']
        future_revenues = [last_revenue * ((1.02) ** i) for i in range(1, years_ahead + 1)]
        
        forecast_df = pd.DataFrame({
            'Year': future_years.flatten(),
            'revenue': future_revenues,
            'type': ['Forecast'] * years_ahead
        })
        
    else:
        # Linear Regression
        X = df['Year'].values.reshape(-1, 1)
        y = df['revenue'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        future_revenues = model.predict(future_years)
        
        # Ensure no negative revenue predictions (basic guardrail)
        future_revenues = np.maximum(future_revenues, 0)
        
        forecast_df = pd.DataFrame({
            'Year': future_years.flatten(),
            'revenue': future_revenues,
            'type': ['Forecast'] * years_ahead
        })
    
    # Combine historical and forecast
    result_df = pd.concat([df[['Year', 'revenue', 'type']], forecast_df], ignore_index=True)
    return result_df

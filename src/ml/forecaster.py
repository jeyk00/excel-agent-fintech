import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Optional

class RevenueForecaster:
    """
    Forecasting engine for revenue prediction using Linear Regression.
    """
    def __init__(self, years_ahead: int = 5):
        """
        Args:
            years_ahead (int): Number of future years to predict. Defaults to 5.
        """
        self.years_ahead = years_ahead
        self.model: Optional[LinearRegression] = None
        self.last_year: Optional[int] = None
        self.last_revenue: Optional[float] = None
        self.cagr: Optional[float] = None

    def fit(self, historical_df: pd.DataFrame) -> None:
        """
        Trains the forecasting model on historical data.

        Args:
            historical_df (pd.DataFrame): DataFrame containing 'Year' and 'revenue' columns.
        """
        if 'Year' not in historical_df.columns or 'revenue' not in historical_df.columns:
            raise ValueError("DataFrame must contain 'Year' and 'revenue' columns.")
        
        # Sort by Year
        df = historical_df.sort_values('Year').copy()
        
        if len(df) == 0:
            return

        self.last_year = int(df['Year'].max())
        self.last_revenue = float(df.iloc[-1]['revenue'])

        # Logic for few data points
        if len(df) < 2:
            # Not enough data for regression, will use simple growth in predict
            self.model = None
            # Assume 2% default growth for CAGR if not enough data
            self.cagr = 0.02
        else:
            # Linear Regression
            X = df['Year'].values.reshape(-1, 1)
            y = df['revenue'].values
            
            self.model = LinearRegression()
            self.model.fit(X, y)
            
            # Calculate CAGR based on the slope (approximate) or actual data
            # Let's use the model's slope relative to the mean revenue as a proxy, 
            # or simply (End/Start)^(1/n) - 1 from historical data
            start_val = df.iloc[0]['revenue']
            end_val = df.iloc[-1]['revenue']
            years = df.iloc[-1]['Year'] - df.iloc[0]['Year']
            if years > 0 and start_val > 0:
                self.cagr = (end_val / start_val) ** (1 / years) - 1
            else:
                self.cagr = 0.0

    def predict(self) -> pd.DataFrame:
        """
        Generates revenue forecast.

        Returns:
            pd.DataFrame: DataFrame containing 'Year', 'revenue', and 'type' (Forecast).
        """
        if self.last_year is None:
            return pd.DataFrame(columns=['Year', 'revenue', 'type'])

        future_years = np.array([self.last_year + i for i in range(1, self.years_ahead + 1)]).reshape(-1, 1)
        
        if self.model is None:
            # Use simple growth assumption (e.g. 2% or whatever CAGR was set to)
            growth_rate = self.cagr if self.cagr is not None else 0.02
            future_revenues = [self.last_revenue * ((1 + growth_rate) ** i) for i in range(1, self.years_ahead + 1)]
        else:
            future_revenues = self.model.predict(future_years)
            
            # --- SAFEGUARD: Prevent Death Spiral (Revenue -> 0) ---
            # If the trend is extremely negative, linear regression sends revenue to 0.
            # Real companies usually stabilize or shrink slower.
            # We enforce a floor: Revenue shouldn't drop below 30% of last year's revenue in the forecast window,
            # unless it was already 0.
            
            floor_value = self.last_revenue * 0.30
            
            # Apply floor and ensure non-negative
            future_revenues = np.maximum(future_revenues, floor_value)
            future_revenues = np.maximum(future_revenues, 0) # Double check against 0
            
            # Additional Heuristic: If slope is negative, dampen the fall?
            # For now, the floor is the most critical fix to prevent TV=0.
            # ------------------------------------------------------

        forecast_df = pd.DataFrame({
            'Year': future_years.flatten(),
            'revenue': future_revenues,
            'type': ['Forecast'] * self.years_ahead
        })
        
        return forecast_df

    def get_cagr(self) -> float:
        """
        Returns the calculated Compound Annual Growth Rate.
        """
        return self.cagr if self.cagr is not None else 0.0

def predict_future_revenue(historical_df: pd.DataFrame, years_ahead: int = 5) -> pd.DataFrame:
    """
    Legacy wrapper for backward compatibility during refactor.
    """
    forecaster = RevenueForecaster(years_ahead=years_ahead)
    forecaster.fit(historical_df)
    forecast_df = forecaster.predict()
    
    # Combine historical and forecast to match old behavior
    df = historical_df.sort_values('Year').copy()
    df['type'] = 'Historical'
    result_df = pd.concat([df[['Year', 'revenue', 'type']], forecast_df], ignore_index=True)
    return result_df

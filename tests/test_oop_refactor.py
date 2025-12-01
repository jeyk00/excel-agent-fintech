import sys
import os
import pandas as pd
from datetime import date
import unittest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import FinancialPeriod, CompanyReport
from src.analyzer import FinancialAnalyzer
from src.ml.forecaster import RevenueForecaster

class TestOOPRefactor(unittest.TestCase):
    def setUp(self):
        # Create dummy data
        self.periods = [
            FinancialPeriod(
                period_end_date=date(2024, 12, 31),
                revenue=1000, cogs=600, ebit=300, net_income=240,
                assets=2000, liabilities=1000, equity=1000, ocf=350,
                shares_outstanding=100, total_debt=500, cash_and_equivalents=100
            ),
            FinancialPeriod(
                period_end_date=date(2023, 12, 31),
                revenue=800, cogs=500, ebit=200, net_income=150,
                assets=1800, liabilities=900, equity=900, ocf=250,
                shares_outstanding=100, total_debt=400, cash_and_equivalents=80
            )
        ]
        self.report = CompanyReport(company_name="Test Corp", reporting_currency="USD", periods=self.periods)
        self.reports = [self.report]

    def test_financial_analyzer(self):
        analyzer = FinancialAnalyzer(self.reports)
        
        # Test aggregation
        df = analyzer.aggregate_data()
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 2)
        self.assertIn('company_name', df.columns)
        
        # Test metrics calculation
        df_metrics = analyzer.calculate_metrics()
        self.assertIn('revenue_growth_yoy', df_metrics.columns)
        self.assertIn('net_margin', df_metrics.columns)
        
        # Check values (USD converted to PLN using rate from FinancialAnalyzer.EXCHANGE_RATES)
        # USD rate = 4.0, so 1000 USD -> 4000 PLN
        expected_rate = FinancialAnalyzer.EXCHANGE_RATES.get('USD', 4.0)
        latest_period = df_metrics.iloc[0] # 2024
        self.assertEqual(latest_period['revenue'], 1000 * expected_rate)
        self.assertAlmostEqual(latest_period['net_margin'], 0.24)

    def test_revenue_forecaster(self):
        # Create historical DF
        data = {
            'Year': [2020, 2021, 2022, 2023, 2024],
            'revenue': [100, 110, 121, 133, 146] # ~10% growth
        }
        historical_df = pd.DataFrame(data)
        
        forecaster = RevenueForecaster(years_ahead=3)
        forecaster.fit(historical_df)
        
        forecast_df = forecaster.predict()
        
        self.assertEqual(len(forecast_df), 3)
        self.assertEqual(forecast_df.iloc[0]['Year'], 2025)
        self.assertEqual(forecast_df.iloc[0]['type'], 'Forecast')
        
        # Check if forecast is reasonable (should be > 146)
        self.assertGreater(forecast_df.iloc[0]['revenue'], 146)
        
        # Test CAGR
        cagr = forecaster.get_cagr()
        self.assertGreater(cagr, 0.0)

    def test_integration(self):
        # Test Analyzer + Forecaster integration
        analyzer = FinancialAnalyzer(self.reports)
        analyzer.aggregate_data()
        df = analyzer.calculate_metrics()
        
        forecaster = RevenueForecaster(years_ahead=2)
        forecaster.fit(df[['Year', 'revenue']])
        forecast_df = forecaster.predict()
        
        combined_df = analyzer.enrich_with_forecast(forecast_df)
        
        self.assertEqual(len(combined_df), 4) # 2 historical + 2 forecast
        self.assertEqual(combined_df.iloc[-1]['type'], 'Forecast')

if __name__ == '__main__':
    unittest.main()

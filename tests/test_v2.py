import unittest
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from datetime import date
from src.models import CompanyReport, FinancialPeriod
from src.ingest.factory import get_ingestion_strategy
from src.ingest.pdf import PDFIngestionStrategy
from src.ingest.xml import XMLIngestionStrategy
from src.ml.forecaster import predict_future_revenue
from src.analyzer import aggregate_reports

class TestV2Upgrade(unittest.TestCase):
    
    def test_ingestion_factory(self):
        """Test that the factory returns the correct strategy."""
        pdf_strategy = get_ingestion_strategy("test.pdf")
        self.assertIsInstance(pdf_strategy, PDFIngestionStrategy)
        
        xml_strategy = get_ingestion_strategy("test.xml")
        self.assertIsInstance(xml_strategy, XMLIngestionStrategy)
        
        with self.assertRaises(ValueError):
            get_ingestion_strategy("test.txt")

    def test_forecaster(self):
        """Test revenue forecasting."""
        data = {
            'Year': [2020, 2021, 2022],
            'revenue': [100, 110, 121] # 10% growth
        }
        df = pd.DataFrame(data)
        
        forecast = predict_future_revenue(df, years_ahead=2)
        
        # Check structure
        self.assertIn('type', forecast.columns)
        self.assertEqual(len(forecast), 5) # 3 historical + 2 forecast
        
        # Check forecast values (approximate)
        # Linear regression on 100, 110, 121 should be close to 132, 143
        # But since it's linear, it might be slightly different than pure compound growth
        # 2020=100, 2021=110, 2022=121. Slope is ~10.5.
        # 2023 should be ~131.5, 2024 ~142.
        
        future_df = forecast[forecast['type'] == 'Forecast']
        self.assertEqual(len(future_df), 2)
        self.assertTrue(future_df.iloc[0]['revenue'] > 121)

    def test_analyzer_aggregation(self):
        """Test aggregating multiple reports."""
        p1 = FinancialPeriod(
            period_end_date=date(2022, 12, 31),
            revenue=100, cogs=50, ebit=20, net_income=10,
            assets=200, liabilities=100, equity=100, ocf=15
        )
        p2 = FinancialPeriod(
            period_end_date=date(2021, 12, 31),
            revenue=90, cogs=45, ebit=18, net_income=9,
            assets=180, liabilities=90, equity=90, ocf=12
        )
        
        report1 = CompanyReport(company_name="Test", reporting_currency="USD", periods=[p1])
        report2 = CompanyReport(company_name="Test", reporting_currency="USD", periods=[p2])
        
        df = aggregate_reports([report1, report2])
        
        self.assertEqual(len(df), 2)
        self.assertTrue('revenue_growth_yoy' in df.columns)
        
        # Check sorting (newest first)
        self.assertEqual(df.iloc[0]['Year'], 2022)
        self.assertEqual(df.iloc[1]['Year'], 2021)
        
        # Check YoY calculation
        # 2022 revenue = 100, 2021 = 90. Growth = (100-90)/90 = 0.111...
        growth = df.iloc[0]['revenue_growth_yoy']
        self.assertAlmostEqual(growth, 0.1111, places=4)

if __name__ == '__main__':
    unittest.main()

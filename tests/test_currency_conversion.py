import sys
import os
import pandas as pd
from datetime import date
import unittest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import FinancialPeriod, CompanyReport
from src.analyzer import FinancialAnalyzer

class TestCurrencyConversion(unittest.TestCase):
    def setUp(self):
        # Create dummy data with EUR
        self.periods_eur = [
            FinancialPeriod(
                period_end_date=date(2024, 12, 31),
                revenue=100, cogs=60, ebit=30, net_income=24,
                assets=200, liabilities=100, equity=100, ocf=35,
                shares_outstanding=100, total_debt=50, cash_and_equivalents=20
            )
        ]
        self.report_eur = CompanyReport(company_name="Euro Corp", reporting_currency="EUR", periods=self.periods_eur)
        
        # Create dummy data with PLN
        self.periods_pln = [
            FinancialPeriod(
                period_end_date=date(2023, 12, 31),
                revenue=100, cogs=60, ebit=30, net_income=24,
                assets=200, liabilities=100, equity=100, ocf=35,
                shares_outstanding=100, total_debt=50, cash_and_equivalents=20
            )
        ]
        self.report_pln = CompanyReport(company_name="PLN Corp", reporting_currency="PLN", periods=self.periods_pln)

    def test_conversion_eur_to_pln(self):
        analyzer = FinancialAnalyzer([self.report_eur])
        df = analyzer.aggregate_data()
        
        self.assertFalse(df.empty)
        row = df.iloc[0]
        
        # Check currency
        self.assertEqual(row['currency'], 'PLN')
        
        # Check conversion (EUR=4.3)
        # Revenue: 100 * 4.3 = 430
        self.assertAlmostEqual(row['revenue'], 430.0)
        # Assets: 200 * 4.3 = 860
        self.assertAlmostEqual(row['assets'], 860.0)

    def test_no_conversion_pln(self):
        analyzer = FinancialAnalyzer([self.report_pln])
        df = analyzer.aggregate_data()
        
        self.assertFalse(df.empty)
        row = df.iloc[0]
        
        # Check currency
        self.assertEqual(row['currency'], 'PLN')
        
        # Check values (should be unchanged)
        self.assertEqual(row['revenue'], 100.0)

    def test_mixed_currencies(self):
        # One EUR report, one PLN report
        analyzer = FinancialAnalyzer([self.report_eur, self.report_pln])
        df = analyzer.aggregate_data()
        
        self.assertEqual(len(df), 2)
        
        # Both should be PLN now
        self.assertTrue((df['currency'] == 'PLN').all())
        
        # Check values
        # 2024 (EUR origin)
        row_2024 = df[df['Year'] == 2024].iloc[0]
        self.assertAlmostEqual(row_2024['revenue'], 430.0)
        
        # 2023 (PLN origin)
        row_2023 = df[df['Year'] == 2023].iloc[0]
        self.assertEqual(row_2023['revenue'], 100.0)

if __name__ == '__main__':
    unittest.main()

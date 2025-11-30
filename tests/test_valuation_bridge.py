import sys
import os
import unittest
import pandas as pd
from datetime import date

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.reporter import generate_excel_report

class TestValuationBridge(unittest.TestCase):
    def test_bridge_generation(self):
        # Mock data with new fields
        data = {
            'period_end_date': [date(2024, 12, 31), date(2023, 12, 31)],
            'Year': [2024, 2023],
            'company_name': ['Test Corp', 'Test Corp'],
            'currency': ['PLN', 'PLN'],
            'reporting_unit': ['thousands', 'thousands'],
            'type': ['Historical', 'Historical'],
            'revenue': [1000000, 900000],
            'revenue_growth_yoy': [0.11, 0.0],
            'ebit': [200000, 180000],
            'ebit_margin': [0.20, 0.20],
            'net_income': [150000, 135000],
            'net_income_growth_yoy': [0.11, 0.0],
            'net_margin': [0.15, 0.15],
            'assets': [2000000, 1800000],
            'equity': [1000000, 900000],
            'roe': [0.15, 0.15],
            'ebitda': [250000, 230000], # Needed for D&A calc
            # New Fields
            'shares_outstanding': [100000, 100000], # 100k shares
            'total_debt': [500000, 450000],
            'cash_and_equivalents': [100000, 80000]
        }
        df = pd.DataFrame(data)
        
        # Add Forecast rows (needed for DCF)
        forecast_data = {
            'period_end_date': [date(2025, 12, 31)],
            'Year': [2025],
            'company_name': ['Test Corp'],
            'currency': ['PLN'],
            'reporting_unit': ['thousands'],
            'type': ['Forecast'],
            'revenue': [1100000],
            'revenue_growth_yoy': [0.10],
            # Other fields can be NaN as they are calculated in Excel
            'ebit': [0], 'ebit_margin': [0], 'net_income': [0], 'net_income_growth_yoy': [0],
            'net_margin': [0], 'assets': [0], 'equity': [0], 'roe': [0], 'ebitda': [0],
            'shares_outstanding': [0], 'total_debt': [0], 'cash_and_equivalents': [0]
        }
        df = pd.concat([df, pd.DataFrame(forecast_data)], ignore_index=True)
        
        output_path = "test_bridge_report.xlsx"
        if os.path.exists(output_path):
            os.remove(output_path)
            
        generated_path = generate_excel_report(df, output_path)
        
        self.assertTrue(os.path.exists(generated_path))
        print(f"Generated report at: {generated_path}")

if __name__ == '__main__':
    unittest.main()

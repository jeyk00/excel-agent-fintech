import sys
import os
import pandas as pd
from datetime import date
import unittest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.reporter import generate_excel_report

class TestDCFValuation(unittest.TestCase):
    def test_dcf_generation(self):
        # Create dummy data with Forecast
        data = {
            'period_end_date': [date(2024, 12, 31), date(2023, 12, 31)],
            'company_name': ['Test Corp', 'Test Corp'],
            'currency': ['PLN', 'PLN'],
            'reporting_unit': ['thousands', 'thousands'],
            'revenue': [1000, 900],
            'ebit': [200, 180],
            'ebit_margin': [0.20, 0.20],
            'ebitda': [250, 220], # Implied D&A = 50
            'type': ['Historical', 'Historical']
        }
        df = pd.DataFrame(data)
        df['Year'] = pd.to_datetime(df['period_end_date']).dt.year
        
        # Add Forecast rows
        forecast_data = {
            'Year': [2025, 2026, 2027, 2028, 2029],
            'revenue': [1100, 1210, 1331, 1464, 1610],
            'type': ['Forecast'] * 5,
            'company_name': ['Test Corp'] * 5,
            'currency': ['PLN'] * 5,
            'reporting_unit': ['thousands'] * 5
        }
        forecast_df = pd.DataFrame(forecast_data)
        
        combined_df = pd.concat([df, forecast_df], ignore_index=True)
        
        output_path = "test_dcf_report.xlsx"
        
        # Generate Report
        try:
            generate_excel_report(combined_df, output_path, wacc=0.10, terminal_growth=0.025)
            self.assertTrue(os.path.exists(output_path))
            print(f"Successfully generated {output_path}")
        except Exception as e:
            self.fail(f"Failed to generate report: {e}")
        finally:
            # Cleanup
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except PermissionError:
                    pass # File might be open

if __name__ == '__main__':
    unittest.main()

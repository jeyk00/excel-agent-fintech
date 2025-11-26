import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date
from src.models import FinancialPeriod, CompanyReport
from src.analyzer import aggregate_reports
import pandas as pd

def test_validation_fix():
    print("Testing Validation Fix...")
    
    # 1. Test Model Instantiation with None
    try:
        period = FinancialPeriod(
            period_end_date=date(2024, 12, 31),
            revenue=1000, cogs=600, ebit=300, net_income=240,
            assets=2000, liabilities=1000, equity=1000, ocf=350,
            depreciation_amortization=None # This caused the error before
        )
        print("SUCCESS: FinancialPeriod instantiated successfully with None for depreciation_amortization.")
    except Exception as e:
        print(f"FAILURE: Failed to instantiate FinancialPeriod: {e}")
        return

    # 2. Test Aggregation Logic
    report = CompanyReport(
        company_name="Test Corp", 
        reporting_currency="PLN", 
        periods=[period]
    )
    
    try:
        df = aggregate_reports([report])
        print("SUCCESS: aggregate_reports ran successfully.")
        
        # Check EBITDA calculation
        # EBIT = 300, D&A = None (0) -> EBITDA should be 300
        ebitda = df['ebitda'].iloc[0]
        if ebitda == 300:
             print(f"SUCCESS: EBITDA calculated correctly: {ebitda}")
        else:
             print(f"FAILURE: EBITDA calculation incorrect. Expected 300, got {ebitda}")
             
    except Exception as e:
        print(f"FAILURE: aggregate_reports failed: {e}")

if __name__ == "__main__":
    test_validation_fix()

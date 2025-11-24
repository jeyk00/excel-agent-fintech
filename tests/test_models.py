from datetime import date
import pytest
from pydantic import ValidationError
from src.models import FinancialPeriod, CompanyReport

def test_financial_period_valid():
    fp = FinancialPeriod(
        period_end_date=date(2023, 12, 31),
        revenue=1000,
        cogs=500,
        ebit=200,
        net_income=150,
        assets=1000,
        liabilities=400,
        equity=600,
        ocf=250
    )
    assert fp.assets == 1000
    assert fp.liabilities + fp.equity == 1000

def test_financial_period_invalid_equation():
    with pytest.raises(ValidationError) as excinfo:
        FinancialPeriod(
            period_end_date=date(2023, 12, 31),
            revenue=1000,
            cogs=500,
            ebit=200,
            net_income=150,
            assets=1000,
            liabilities=400,
            equity=500, # Missing 100
            ocf=250
        )
    assert "Accounting equation violated" in str(excinfo.value)

def test_financial_period_negative_revenue():
    with pytest.raises(ValidationError):
        FinancialPeriod(
            period_end_date=date(2023, 12, 31),
            revenue=-100, # Invalid
            cogs=500,
            ebit=200,
            net_income=150,
            assets=1000,
            liabilities=400,
            equity=600,
            ocf=250
        )

if __name__ == "__main__":
    # Manual run if pytest not installed, but we should use pytest
    try:
        test_financial_period_valid()
        print("test_financial_period_valid passed")
    except Exception as e:
        print(f"test_financial_period_valid failed: {e}")

    try:
        test_financial_period_invalid_equation()
        print("test_financial_period_invalid_equation passed")
    except Exception as e:
        print(f"test_financial_period_invalid_equation failed: {e}")
        
    try:
        test_financial_period_negative_revenue()
        print("test_financial_period_negative_revenue passed")
    except Exception as e:
        print(f"test_financial_period_negative_revenue failed: {e}")

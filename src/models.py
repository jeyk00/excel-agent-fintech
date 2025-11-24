from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator

class FinancialPeriod(BaseModel):
    """
    Represents financial data for a specific reporting period (e.g., a year).
    """
    period_end_date: date = Field(..., description="The end date of the financial period.")
    
    # P&L
    revenue: float = Field(..., ge=0, description="Total Revenue (Przychody). Must be non-negative.")
    cogs: float = Field(..., description="Cost of Goods Sold (Koszt własny sprzedaży).")
    ebit: float = Field(..., description="Earnings Before Interest and Taxes (Zysk operacyjny).")
    net_income: float = Field(..., description="Net Income (Zysk netto).")
    depreciation_amortization: float = Field(0.0, description="Depreciation and Amortization (Amortyzacja).")
    
    # Balance Sheet
    assets: float = Field(..., ge=0, description="Total Assets (Aktywa).")
    liabilities: float = Field(..., ge=0, description="Total Liabilities (Zobowiązania).")
    equity: float = Field(..., description="Total Equity (Kapitał własny).")
    
    # Cash Flow
    ocf: float = Field(..., description="Operating Cash Flow (Przepływy pieniężne z działalności operacyjnej).")

    @model_validator(mode='after')
    def check_accounting_equation(self) -> 'FinancialPeriod':
        """
        Validates the fundamental accounting equation: Assets = Liabilities + Equity.
        Allows for a small tolerance due to potential rounding errors in source PDF or float arithmetic.
        """
        # Tolerance of 1.0 unit (e.g. 1 million or 1 PLN depending on scale, but usually these are large numbers)
        # Using a relative tolerance might be better, but let's start with a reasonable absolute tolerance 
        # or just a warning if we want to be lenient. 
        # User requested "Invariant: Assets = Liabilities + Equity".
        
        lhs = self.assets
        rhs = self.liabilities + self.equity
        
        # Check if difference is significant (e.g., > 1% of assets or absolute value > 1)
        # Relaxed tolerance to 1% to account for rounding or minor extraction errors.
        diff = abs(lhs - rhs)
        tolerance = max(1.0, 0.01 * lhs) # 1% of Assets or 1.0, whichever is larger
        
        if diff > tolerance: 
            # We might want to just warn or log, but Pydantic validator raises error.
            # For now, let's raise a ValueError to enforce the schema as requested.
            raise ValueError(f"Accounting equation violated: Assets ({lhs}) != Liabilities ({self.liabilities}) + Equity ({self.equity}) (Diff: {diff} > Tolerance: {tolerance})")
        
        return self

class CompanyReport(BaseModel):
    """
    Container for extracted financial data for a company.
    """
    company_name: str = Field(..., description="Name of the company.")
    reporting_currency: str = Field(..., description="Currency of the reported figures (e.g., PLN, USD).")
    reporting_unit: str = Field("thousands", description="Unit of the reported figures (e.g., thousands, millions, units).")
    periods: List[FinancialPeriod] = Field(..., description="List of financial periods extracted.")

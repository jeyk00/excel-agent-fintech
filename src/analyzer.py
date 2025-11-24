import pandas as pd
from src.models import CompanyReport

def analyze_report(report: CompanyReport) -> pd.DataFrame:
    """
    Converts a CompanyReport into a Pandas DataFrame and calculates financial KPIs.
    
    Args:
        report (CompanyReport): The structured company data.
        
    Returns:
        pd.DataFrame: DataFrame with financial data and calculated metrics.
    """
    # Convert list of Pydantic models to list of dicts
    data = [period.model_dump() for period in report.periods]
    
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    
    # Ensure date column is datetime
    df['period_end_date'] = pd.to_datetime(df['period_end_date'])
    
    # Sort by date descending (newest first)
    df = df.sort_values('period_end_date', ascending=False).reset_index(drop=True)
    
    # --- KPI Calculations ---
    
    # 1. Margins
    # Avoid division by zero
    df['net_margin'] = df.apply(lambda x: x['net_income'] / x['revenue'] if x['revenue'] != 0 else 0, axis=1)
    df['ebit_margin'] = df.apply(lambda x: x['ebit'] / x['revenue'] if x['revenue'] != 0 else 0, axis=1)
    df['ebitda'] = df['ebit'] + df['depreciation_amortization']
    df['ebitda_margin'] = df.apply(lambda x: x['ebitda'] / x['revenue'] if x['revenue'] != 0 else 0, axis=1)
    
    # 2. Returns
    df['roe'] = df.apply(lambda x: x['net_income'] / x['equity'] if x['equity'] != 0 else 0, axis=1)
    
    # 3. Growth (YoY)
    # Since df is sorted descending (Newest, Oldest), shift(-1) gives the previous period (if it exists and is consecutive)
    # Note: This assumes periods are annual and consecutive. For robust YoY, we'd need to match years.
    # For this MVP, we'll assume the list contains consecutive annual periods.
    
    df['revenue_growth_yoy'] = df['revenue'].pct_change(periods=-1)
    df['net_income_growth_yoy'] = df['net_income'].pct_change(periods=-1)
    df['assets_growth_yoy'] = df['assets'].pct_change(periods=-1)
    df['equity_growth_yoy'] = df['equity'].pct_change(periods=-1)
    
    # Add metadata
    df['company_name'] = report.company_name
    df['currency'] = report.reporting_currency
    df['reporting_unit'] = report.reporting_unit
    
    # Reorder columns for readability
    cols = ['period_end_date', 'company_name', 'currency', 'reporting_unit',
            'revenue', 'revenue_growth_yoy', 
            'ebitda', 'ebitda_margin',
            'ebit', 'ebit_margin',
            'net_income', 'net_income_growth_yoy', 'net_margin',
            'assets', 'assets_growth_yoy',
            'equity', 'equity_growth_yoy', 'roe',
            'liabilities', 'cogs', 'ocf']
            
    # Select only columns that exist (in case some were dropped or renamed, though unlikely here)
    cols = [c for c in cols if c in df.columns]
    
    return df[cols]

if __name__ == "__main__":
    # Test block
    from datetime import date
    from src.models import FinancialPeriod
    
    # Create dummy data
    periods = [
        FinancialPeriod(
            period_end_date=date(2024, 12, 31),
            revenue=1000, cogs=600, ebit=300, net_income=240,
            assets=2000, liabilities=1000, equity=1000, ocf=350
        ),
        FinancialPeriod(
            period_end_date=date(2023, 12, 31),
            revenue=800, cogs=500, ebit=200, net_income=150,
            assets=1800, liabilities=900, equity=900, ocf=250
        )
    ]
    report = CompanyReport(company_name="Test Corp", reporting_currency="PLN", periods=periods)
    
    df = analyze_report(report)
    print(df.to_string())

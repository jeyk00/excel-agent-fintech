import pandas as pd
from typing import List
from src.models import CompanyReport

def aggregate_reports(reports: List[CompanyReport]) -> pd.DataFrame:
    """
    Aggregates multiple CompanyReport objects into a single Pandas DataFrame
    and calculates financial KPIs across all periods.
    
    Args:
        reports (List[CompanyReport]): List of structured company data reports.
        
    Returns:
        pd.DataFrame: DataFrame with aggregated financial data and calculated metrics.
    """
    all_data = []
    
    for report in reports:
        for period in report.periods:
            period_data = period.model_dump()
            # Add metadata from the report level to each period
            period_data['company_name'] = report.company_name
            period_data['currency'] = report.reporting_currency
            period_data['reporting_unit'] = report.reporting_unit
            all_data.append(period_data)
            
    if not all_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(all_data)
    
    # Ensure date column is datetime
    if 'period_end_date' in df.columns:
        df['period_end_date'] = pd.to_datetime(df['period_end_date'])
        df['Year'] = df['period_end_date'].dt.year
    
    # Sort by date descending (newest first)
    df = df.sort_values('period_end_date', ascending=False).reset_index(drop=True)
    
    # --- KPI Calculations ---
    
    # 1. Margins
    # Avoid division by zero
    df['net_margin'] = df.apply(lambda x: x['net_income'] / x['revenue'] if x['revenue'] != 0 else 0, axis=1)
    df['ebit_margin'] = df.apply(lambda x: x['ebit'] / x['revenue'] if x['revenue'] != 0 else 0, axis=1)
    df['ebitda'] = df['ebit'] + df['depreciation_amortization'].fillna(0)
    df['ebitda_margin'] = df.apply(lambda x: x['ebitda'] / x['revenue'] if x['revenue'] != 0 else 0, axis=1)
    
    # 2. Returns
    df['roe'] = df.apply(lambda x: x['net_income'] / x['equity'] if x['equity'] != 0 else 0, axis=1)
    
    # 3. Growth (YoY)
    # Since df is sorted descending (Newest, Oldest), shift(-1) gives the previous period
    # We need to ensure we are calculating growth for the same company if we ever support multi-company (but for now assume single company or handled upstream)
    # Ideally, we should group by company_name if mixing companies, but the requirement implies merging files for ONE company analysis usually.
    # Let's assume these reports are for the same entity or we want to see them together.
    
    df['revenue_growth_yoy'] = df['revenue'].pct_change(periods=-1)
    df['net_income_growth_yoy'] = df['net_income'].pct_change(periods=-1)
    df['assets_growth_yoy'] = df['assets'].pct_change(periods=-1)
    df['equity_growth_yoy'] = df['equity'].pct_change(periods=-1)
    
    # Reorder columns for readability
    cols = ['period_end_date', 'Year', 'company_name', 'currency', 'reporting_unit',
            'revenue', 'revenue_growth_yoy', 
            'ebitda', 'ebitda_margin',
            'ebit', 'ebit_margin',
            'net_income', 'net_income_growth_yoy', 'net_margin',
            'assets', 'assets_growth_yoy',
            'equity', 'equity_growth_yoy', 'roe',
            'liabilities', 'cogs', 'ocf']
            
    # Select only columns that exist
    cols = [c for c in cols if c in df.columns]
    
    return df[cols]

if __name__ == "__main__":
    # Test block
    from datetime import date
    from src.models import FinancialPeriod
    
    # Create dummy data
    periods1 = [
        FinancialPeriod(
            period_end_date=date(2024, 12, 31),
            revenue=1000, cogs=600, ebit=300, net_income=240,
            assets=2000, liabilities=1000, equity=1000, ocf=350
        )
    ]
    periods2 = [
        FinancialPeriod(
            period_end_date=date(2023, 12, 31),
            revenue=800, cogs=500, ebit=200, net_income=150,
            assets=1800, liabilities=900, equity=900, ocf=250
        )
    ]
    report1 = CompanyReport(company_name="Test Corp", reporting_currency="PLN", periods=periods1)
    report2 = CompanyReport(company_name="Test Corp", reporting_currency="PLN", periods=periods2)
    
    df = aggregate_reports([report1, report2])
    print(df.to_string())

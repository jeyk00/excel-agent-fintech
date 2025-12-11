import pandas as pd
from typing import List
from src.models import CompanyReport

class FinancialAnalyzer:
    """
    Analyzes financial reports to extract KPIs and trends.
    """
    EXCHANGE_RATES = {
        'EUR': 4.3,
        'USD': 4.0,
        'PLN': 1.0
    }
    TARGET_CURRENCY = 'PLN'

    def __init__(self, reports: List[CompanyReport]):
        """
        Args:
            reports (List[CompanyReport]): List of extracted company reports.
        """
        self.reports = reports
        self.df: pd.DataFrame = pd.DataFrame()

    def _convert_currency(self, row: dict) -> dict:
        """
        Converts financial metrics in the row to the target currency (PLN).
        """
        currency = row.get('currency', '').upper()
        if currency == self.TARGET_CURRENCY:
            return row
            
        rate = self.EXCHANGE_RATES.get(currency)
        if not rate:
            # If currency not found, keep as is (or log warning)
            return row
            
        # Metrics to convert
        metrics = [
            'revenue', 'cogs', 'ebit', 'net_income', 'depreciation_amortization',
            'assets', 'liabilities', 'equity', 'ocf',
            'total_debt', 'cash_and_equivalents'
        ]
        
        for metric in metrics:
            if metric in row and row[metric] is not None:
                row[metric] = row[metric] * rate
                
        # --- Heuristic Safeguard for Shares Units ---
        # If shares are tiny (< 2M) but revenue is huge (> 100M), it's likely "in thousands" error.
        # Example: CD Projekt has ~100M shares. If model says 100,000, it missed the unit.
        if row.get('shares_outstanding') and row.get('revenue'):
            shares = row['shares_outstanding']
            revenue = row['revenue']
            
            # Threshold: < 10M shares AND > 500M revenue (arbitrary but safe for big listed cos)
            if shares < 10_000_000 and revenue > 500_000_000:
                print(f"⚠️ Heuristic applied: Fixed Shares unit (x1000) for {row.get('period_end_date', 'Unknown')}. Extracted: {shares}")
                row['shares_outstanding'] = shares * 1000
        # --------------------------------------------

        row['currency'] = self.TARGET_CURRENCY
        return row

    def aggregate_data(self) -> pd.DataFrame:
        """
        Aggregates multiple CompanyReport objects into a single Pandas DataFrame.
        Converts all data to PLN.
        
        Returns:
            pd.DataFrame: Raw aggregated financial data in PLN.
        """
        all_data = []
        
        for report in self.reports:
            for period in report.periods:
                period_data = period.model_dump()
                # Add metadata from the report level to each period
                period_data['company_name'] = report.company_name
                period_data['currency'] = report.reporting_currency
                period_data['reporting_unit'] = report.reporting_unit
                
                # Convert to PLN
                period_data = self._convert_currency(period_data)
                
                all_data.append(period_data)
                
        if not all_data:
            self.df = pd.DataFrame()
            return self.df
        
        df = pd.DataFrame(all_data)
        
        # Ensure date column is datetime
        if 'period_end_date' in df.columns:
            df['period_end_date'] = pd.to_datetime(df['period_end_date'])
            df['Year'] = df['period_end_date'].dt.year
        
        # Sort by date descending (newest first)
        self.df = df.sort_values('period_end_date', ascending=False).reset_index(drop=True)
        return self.df

    def calculate_metrics(self) -> pd.DataFrame:
        """
        Calculates financial KPIs (Margins, Growth, ROE) on the aggregated data.
        
        Returns:
            pd.DataFrame: DataFrame with added KPI columns.
        """
        if self.df.empty:
            return self.df
            
        df = self.df.copy()
        
        # 1. Margins
        # Avoid division by zero
        df['net_margin'] = df.apply(lambda x: x['net_income'] / x['revenue'] if x['revenue'] != 0 else 0, axis=1)
        df['ebit_margin'] = df.apply(lambda x: x['ebit'] / x['revenue'] if x['revenue'] != 0 else 0, axis=1)
        # Handle D&A: ensure numeric type before fillna to avoid deprecation warning
        df['ebitda'] = df['ebit'] + df['depreciation_amortization'].astype(float).fillna(0)
        df['ebitda_margin'] = df.apply(lambda x: x['ebitda'] / x['revenue'] if x['revenue'] != 0 else 0, axis=1)
        
        # 2. Returns
        df['roe'] = df.apply(lambda x: x['net_income'] / x['equity'] if x['equity'] != 0 else 0, axis=1)
        
        # 3. Growth (YoY)
        # Since df is sorted descending (Newest, Oldest), shift(-1) gives the previous period
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
                'liabilities', 'cogs', 'ocf',
                'shares_outstanding', 'total_debt', 'cash_and_equivalents']
                
        # Select only columns that exist
        cols = [c for c in cols if c in df.columns]
        
        self.df = df[cols]
        return self.df

    def enrich_with_forecast(self, forecast_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merges historical data with forecast data.
        
        Args:
            forecast_df (pd.DataFrame): DataFrame containing forecast data.
            
        Returns:
            pd.DataFrame: Combined DataFrame.
        """
        if self.df.empty:
            return pd.DataFrame()
            
        # Select only Forecast rows
        future_only = forecast_df[forecast_df['type'] == 'Forecast'].copy()
        
        # Add metadata from the main df (using the first row) to ensure consistency
        first_row = self.df.iloc[0]
        future_only['company_name'] = first_row.get('company_name', 'Unknown')
        future_only['currency'] = first_row.get('currency', 'N/A')
        future_only['reporting_unit'] = first_row.get('reporting_unit', 'thousands')
        
        # Concatenate
        combined_df = pd.concat([self.df, future_only], ignore_index=True)
        return combined_df

def aggregate_reports(reports: List[CompanyReport]) -> pd.DataFrame:
    """
    Legacy wrapper for backward compatibility.
    """
    analyzer = FinancialAnalyzer(reports)
    analyzer.aggregate_data()
    return analyzer.calculate_metrics()

if __name__ == "__main__":
    # Test block
    from datetime import date
    from src.models import FinancialPeriod
    
    # Create dummy data
    periods1 = [
        FinancialPeriod(
            period_end_date=date(2024, 12, 31),
            revenue=1000, cogs=600, ebit=300, net_income=240,
            assets=2000, liabilities=1000, equity=1000, ocf=350,
            shares_outstanding=100, total_debt=500, cash_and_equivalents=100
        )
    ]
    periods2 = [
        FinancialPeriod(
            period_end_date=date(2023, 12, 31),
            revenue=800, cogs=500, ebit=200, net_income=150,
            assets=1800, liabilities=900, equity=900, ocf=250,
            shares_outstanding=100, total_debt=400, cash_and_equivalents=80
        )
    ]
    report1 = CompanyReport(company_name="Test Corp", reporting_currency="PLN", periods=periods1)
    report2 = CompanyReport(company_name="Test Corp", reporting_currency="PLN", periods=periods2)
    
    df = aggregate_reports([report1, report2])
    print(df.to_string())

import sys
import os
import unittest
import json
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.extractor import extract_data

class TestExtractorFiltering(unittest.TestCase):
    @patch('src.extractor.OpenAI')
    def test_filter_incomplete_periods(self, mock_openai):
        # Mock LLM response with one valid and one invalid period
        mock_response_content = json.dumps({
            "company_name": "Test Corp",
            "reporting_currency": "PLN",
            "reporting_unit": "thousands",
            "periods": [
                {
                    "period_end_date": "2024-12-31",
                    "revenue": 1000.0,
                    "cogs": 500.0,
                    "ebit": 200.0,
                    "net_income": 150.0,
                    "assets": 2000.0,
                    "liabilities": 1000.0,
                    "equity": 1000.0,
                    "ocf": 250.0
                },
                {
                    "period_end_date": "2023-12-31",
                    "revenue": 1000.0,
                    "cogs": None, # Missing COGS (should be filtered now)
                    "ebit": 200.0,
                    "net_income": 150.0,
                    "assets": 2000.0,
                    "liabilities": 1000.0,
                    "equity": 1000.0,
                    "ocf": 250.0
                }
            ]
        })
        
        # Setup mock
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = mock_response_content
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client
        
        # Run extraction
        report = extract_data("dummy markdown", model_name="gpt-4o")
        
        # Verify
        self.assertEqual(len(report.periods), 1)
        self.assertEqual(str(report.periods[0].period_end_date), "2024-12-31")

if __name__ == '__main__':
    unittest.main()

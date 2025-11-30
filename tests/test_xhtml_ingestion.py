import sys
import os
import unittest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingest.factory import get_ingestion_strategy
from src.ingest.xml import XMLIngestionStrategy

class TestXHTMLIngestion(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_report.xhtml"
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Financial Report</title>
</head>
<body>
<h1>Financial Highlights</h1>
<p>Revenue: 1,000,000 PLN</p>
<p>Net Income: 200,000 PLN</p>
</body>
</html>""")

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_factory_selection(self):
        strategy = get_ingestion_strategy(self.test_file)
        self.assertIsInstance(strategy, XMLIngestionStrategy)

    def test_parsing(self):
        strategy = get_ingestion_strategy(self.test_file)
        text = strategy.parse(self.test_file)
        
        self.assertIn("Financial Highlights", text)
        self.assertIn("Revenue: 1,000,000 PLN", text)
        self.assertIn("Net Income: 200,000 PLN", text)

if __name__ == '__main__':
    unittest.main()

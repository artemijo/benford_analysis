import unittest
from benford import extract_numbers

class TestParsing(unittest.TestCase):
    def test_filtering(self):
        """Test exclusion of metadata-related numbers"""
        text = """Page 1
2023 Annual Report:
Revenue: $1,234,567.89
Page numbers: 1, 2, 3
Small values: 0.0001, 0.99"""
        
        parsed = extract_numbers(text)
        # Only 1,234,567.89 should remain
        self.assertEqual(parsed, [1234567.89])
        print("Filtering Test ✓")

if __name__ == "__main__":
    unittest.main()
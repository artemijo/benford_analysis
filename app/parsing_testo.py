import pandas as pd
from io import BytesIO
import pdfplumber
import unittest
from benford import extract_numbers

class TestParsing(unittest.TestCase):
    def test_csv_parsing(self):
        """Test CSV with mixed data and metadata"""
        csv_content = b"""Amount,Page,Year
1,234.56,1,2023
789.00,2,2022
0.0045,3,1999"""
        
        expected = [1234.56, 789.0]
        parsed = extract_numbers(csv_content.decode('utf-8'))
        self.assertCountEqual(parsed, expected)
        print("CSV Test ✓")

    def test_txt_parsing(self):
        """Test text file with various number formats"""
        txt_content = """Page 1
2023 Annual Report:
Revenue: $1,234,567.89
Expenses: 789,000.50
Net Profit: 445,567.39
Page 2 contains 50 items at $0.99 each"""
        
        expected = [1234567.89, 789000.5, 445567.39]
        parsed = extract_numbers(txt_content)
        self.assertCountEqual(parsed, expected)
        print("TXT Test ✓")

    def test_pdf_parsing(self):
        """Test PDF with headers/footers"""
        pdf = pdfplumber.open(BytesIO(self._create_test_pdf()))
        text = "\n".join([page.extract_text() for page in pdf.pages])
        parsed = extract_numbers(text)
        
        # Should exclude footer (2023) and page numbers (1, 2)
        expected = [1500000.0, 750000.0, 250.5]
        self.assertCountEqual(parsed, expected)
        print("PDF Test ✓")

    def _create_test_pdf(self):
        """Generate test PDF with headers/footers"""
        from reportlab.pdfgen import canvas
        from io import BytesIO
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        
        # Page 1
        c.drawString(100, 800, "2023 Q1 Report")  # Header
        c.drawString(100, 500, "Sales: 1,500,000")
        c.drawString(100, 480, "Expenses: 750,000")
        c.drawString(100, 50, "Page 1 of 2")  # Footer
        c.showPage()
        
        # Page 2
        c.drawString(100, 800, "2023 Q2 Report")  # Header
        c.drawString(100, 500, "Misc: 250.50")
        c.drawString(100, 50, "Page 2 of 2")  # Footer
        c.save()
        
        buffer.seek(0)
        return buffer.getvalue()

if __name__ == "__main__":
    tester = TestParsing()
    tester.test_csv_parsing()
    tester.test_txt_parsing()
    tester.test_pdf_parsing()
    print("All parsing tests completed!")
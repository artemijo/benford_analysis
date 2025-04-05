import pdfplumber
import re
from io import BytesIO

def extract_numbers_debug(pdf_content: bytes) -> dict:
    """Test PDF parsing with detailed diagnostics"""
    results = {
        'pages': [],
        'total_numbers': 0,
        'sample_numbers': []
    }
    
    with pdfplumber.open(BytesIO(pdf_content)) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            numbers = []
            
            # Enhanced number regex
            number_strings = re.findall(
                r'(?:(?<=\s)|^)[+-]?'  # Sign with word boundary
                r'(?:' 
                r'\d{1,3}(?:,\d{3})*'  # Comma-separated thousands
                r'(?:\.\d+)?'  # Optional decimal
                r'|\.\d+'  # Decimal without leading zero
                r'|\d+\.?\d*'  # Regular numbers
                r')(?=\s|$|\,|\.\D)',
                page_text
            )
            
            # Convert found strings to numbers
            for num_str in number_strings:
                try:
                    # Clean commas and invalid characters
                    clean_num = num_str.replace(',', '').lstrip('$€£¥')
                    num = float(clean_num)
                    if abs(num) > 1e-6:  # Filter near-zero values
                        numbers.append(num)
                except ValueError:
                    continue
            
            # Store page results
            page_result = {
                'page': page_num + 1,
                'text_sample': page_text[:200] + "...",
                'found_numbers': numbers[:10],  # First 10 numbers
                'total_found': len(numbers),
                'patterns_found': number_strings[:10]  # Original strings
            }
            results['pages'].append(page_result)
            results['total_numbers'] += len(numbers)
            results['sample_numbers'].extend(numbers[:5])
    
    return results

# Test with your PDF file
if __name__ == "__main__":
    with open("table_data_test.pdf", "rb") as f:
        pdf_bytes = f.read()
    
    analysis = extract_numbers_debug(pdf_bytes)
    
    print("\n=== PDF Parsing Diagnostic Report ===")
    print(f"Total numbers found: {analysis['total_numbers']}")
    print("\nFirst 20 sample numbers:")
    print(analysis['sample_numbers'][:20])
    
    print("\n=== Page-by-Page Analysis ===")
    for page in analysis['pages']:
        print(f"\nPage {page['page']}:")
        print(f"Text sample: {page['text_sample']}")
        print(f"Number patterns detected: {page['patterns_found']}")
        print(f"Converted numbers: {[round(n, 4) for n in page['found_numbers']]}")
        print(f"Total on page: {page['total_found']}")
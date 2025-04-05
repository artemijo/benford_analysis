import re
import pandas as pd
from decimal import Decimal, InvalidOperation
import argparse

def clean_number(number_str):
    """Convert various number formats to standardized float"""
    try:
        # Remove currency symbols and non-digit characters except [.,-]
        cleaned = re.sub(r"[^\d.,-]", "", str(number_str))
        
        # Handle negative numbers
        negative = '-' in cleaned
        cleaned = cleaned.replace('-', '')
        
        # Count separators
        commas = cleaned.count(',')
        dots = cleaned.count('.')
        
        # Determine decimal separator
        if commas + dots > 1:  # Contains thousand separators
            if cleaned.endswith(',') or cleaned.endswith('.'):
                # European format: 1.234,56 or 1,234.56
                last_sep = ',' if cleaned.endswith(',') else '.'
                int_part = cleaned[:-4].replace(',', '').replace('.', '')
                dec_part = cleaned[-3:-1]
                num = f"{int_part}.{dec_part}"
            else:
                # Assume last separator is decimal
                if commas > dots:
                    num = cleaned.replace('.', '').replace(',', '.')
                else:
                    num = cleaned.replace(',', '')
        elif commas == 1 and dots == 0:
            num = cleaned.replace(',', '.')
        else:
            num = cleaned.replace(',', '')
            
        # Convert to float and handle negatives
        value = float(num)
        return abs(value) if value != 0 else None
        
    except (ValueError, InvalidOperation):
        return None

def transform_csv(input_path, output_path):
    """Process CSV file and output cleaned numbers"""
    try:
        # Read CSV with automatic delimiter detection
        df = pd.read_csv(input_path, dtype=str, header=None, 
                        delimiter=None, engine='python')
        
        # Process all cells
        cleaned_numbers = []
        for row in df.values:
            for cell in row:
                numbers = re.findall(r"[-+]?\d*[.,]?\d+", str(cell))
                for num in numbers:
                    cleaned = clean_number(num)
                    if cleaned is not None and cleaned > 0:
                        cleaned_numbers.append(cleaned)
        
        # Create output DataFrame
        output_df = pd.DataFrame(cleaned_numbers, columns=['Amount'])
        
        # Save cleaned data
        output_df.to_csv(output_path, index=False)
        print(f"Successfully processed {len(output_df)} numbers")
        return True
    
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Clean CSV for Benford Analysis')
    parser.add_argument('input', help='Input CSV file path')
    parser.add_argument('output', help='Output CSV file path')
    args = parser.parse_args()
    
    success = transform_csv(args.input, args.output)
    if not success:
        exit(1)
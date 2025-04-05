import re
import numpy as np
from scipy.stats import chisquare, cramervonmises
from typing import List, Dict, Optional, Tuple
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import warnings

def extract_numbers(text: str) -> List[float]:
    """Extract numbers while filtering non-data entries"""
    # Remove lines with metadata keywords (case-insensitive)
    filtered_lines = []
    keywords = r'(page|date|year|id|no|report|annual)'  # Added 'annual'
    for line in text.split('\n'):
        if re.search(keywords, line, re.IGNORECASE):
            continue
        filtered_lines.append(line)
    filtered_text = '\n'.join(filtered_lines)
    
    # Find numbers (simplified regex)
    numbers = re.findall(
        r"[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?|"  # Comma-separated
        r"[-+]?\d*\.\d+|"                      # Decimals
        r"[-+]?\d+",                           # Integers
        filtered_text
    )
    
    # Clean and filter numbers
    valid_numbers = []
    for num in numbers:
        try:
            cleaned_num = num.replace(',', '')
            n = float(cleaned_num)
            
            # Enhanced year detection
            is_year = (
                n.is_integer() and 
                len(cleaned_num) == 4 and 
                1000 <= abs(n) <= 9999  # Broad year range
            )
            
            if (
                is_year or
                (abs(n) < 1) or
                (n.is_integer() and 1 <= abs(n) <= 50)
            ):
                continue
            valid_numbers.append(n)
        except ValueError:
            continue
    return valid_numbers

def get_first_digit(number: float) -> Optional[int]:
    """Correctly extracts first non-zero digit"""
    try:
        # Remove all leading zeros and decimals
        stripped = re.sub(r'^[0\.]*', '', str(abs(number)))
        # Remove any remaining leading zeros (e.g., '00456' → '456')
        stripped = stripped.lstrip('0')
        return int(stripped[0]) if stripped else None
    except:
        return None

def get_second_digit(number: float) -> Optional[int]:
    """Extract second digit"""
    try:
        stripped = re.sub(r'^[0\.]+', '', str(abs(number)))
        return int(stripped[1]) if len(stripped) > 1 else None
    except:
        return None

def benford_expected_distribution(digit_pos: int = 1) -> Tuple[List[float], List[int]]:
    if digit_pos == 1:
        digits = list(range(1, 10))
        probs = [np.log10(1 + 1/d) for d in digits]  # First digit
    else:
        digits = list(range(0, 10))
        probs = [sum(np.log10(1 + 1/(10*k + d))  # Fixed parentheses
                 for k in range(1, 10))
                 for d in digits]
    return probs, digits

def benford_test(numbers: List[float], digit_pos: int = 1, 
                alpha: float = 0.05) -> Dict:
    expected_probs, bins = benford_expected_distribution(digit_pos)
    
    # Digit extraction and frequency calculation (unchanged)
    digit_func = get_first_digit if digit_pos == 1 else get_second_digit
    digits = [d for d in (digit_func(n) for n in numbers) 
             if d is not None and d in bins]
    
    observed = [digits.count(d) for d in bins]
    expected = [p * len(digits) for p in expected_probs]
    
    if any(e < 5 for e in expected):
        warnings.warn("Chi-square assumptions violated - expected counts <5")
    
    # Chi-squared test only
    chi2, p_chi = chisquare(observed, expected, ddof=0)
    
    return {
        "observed": observed,
        "expected": expected,
        "p_chi": float(p_chi),
        "anomalous": p_chi < alpha,
        "bins": bins
    }

def plot_benford(observed: List[int], expected: List[float], 
                bins: List[int]) -> str:
    """Improved visualization"""
    plt.figure(figsize=(10, 6))
    indices = np.arange(len(bins))
    width = 0.35
    
    plt.bar(indices, observed, width, label='Observed', alpha=0.7)
    plt.bar(indices + width, expected, width, label='Expected', alpha=0.7)
    
    plt.xticks(indices + width/2, bins)
    plt.xlabel('Digit' if len(bins) == 9 else 'Second Digit')
    plt.ylabel('Frequency')
    plt.title("Benford's Law Compliance")
    plt.legend()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def bisection_analysis(numbers: List[float], max_depth: int = 3, 
                      alpha: float = 0.05) -> List[Dict]:
    """Bonferroni-corrected analysis"""
    anomalies = []
    test_count = 2 ** (max_depth + 1) - 1  # Total possible tests
    adjusted_alpha = alpha / test_count
    
    def _bisect(subset: List[float], indices: List[int], depth: int):
        if depth > max_depth or len(subset) < 50:
            return
        
        try:
            result = benford_test(subset, alpha=adjusted_alpha)
            if result['anomalous']:
                anomalies.append({
                    "start_index": indices[0],
                    "end_index": indices[-1],
                    "p_chi": result["p_chi"],
                    #"p_cvm": result["p_cvm"],
                    "depth": depth
                })
                
                # Split and recurse
                mid = len(subset) // 2
                _bisect(subset[:mid], indices[:mid], depth + 1)
                _bisect(subset[mid:], indices[mid:], depth + 1)
        except ValueError as e:
            warnings.warn(f"Skipping bisection: {str(e)}")
    
    _bisect(numbers, list(range(len(numbers))), 1)
    return sorted(anomalies, key=lambda x: x['p_chi'])[:5]

def validate_benford_assumptions(expected: List[float]) -> None:
    """Check chi-square requirements"""
    if any(e < 5 for e in expected):
        raise ValueError("Chi-square invalid - expected counts <5. Consider larger dataset.")
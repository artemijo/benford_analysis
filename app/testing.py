import numpy as np
from benford import benford_test, benford_expected_distribution, get_first_digit

def generate_benford_compliant_data(n=5000):
    """Generate numbers that perfectly follow Benford's Law"""
    # First digit distribution
    first_digits = np.random.choice(range(1, 10), p=benford_expected_distribution(1)[0])
    
    # Create numbers with Benford-distributed digits
    return [10**(np.log10(d) + np.random.uniform(0, 5)) for d in first_digits]

def test_digit_extraction():
    test_cases = {
        0.00456: 4,
        123.45: 1,
        0.0: None,
        0.123: 1,
        0.0000789: 7,
        456.0: 4
    }
    
    print("\n=== Digit Extraction Test ===")
    for num, expected in test_cases.items():
        result = get_first_digit(num)
        status = "PASS" if result == expected else f"FAIL (got {result})"
        print(f"{num}: {status}")

def test_benford_analysis():
    # Generate test data
    data = generate_benford_compliant_data()
    
    # Run analysis
    result = benford_test(data)
    
    # Print diagnostics
    print("=== Benford Validation Test ===")
    print(f"First 10 numbers: {data[:10]}")
    print(f"Observed digits: {result['observed']}")
    print(f"Expected digits: {np.round(result['expected'], 1)}")
    print(f"Chi2 p-value: {result['p_chi']}")
    print(f"CVM p-value: {result['p_cvm']}")
    
    # Should not be anomalous
    assert not result['anomalous'], \
        f"False anomaly detected! p-values too low (chi2={result['p_chi']}, cvm={result['p_cvm']})"
    
    print("\nTest passed! Data is recognized as normal")

def debug_expected_distribution():
    """Verify expected probabilities match theoretical values"""
    print("\n=== Expected Probability Validation ===")
    
    # First digit
    p1, d1 = benford_expected_distribution(1)
    theoretical_p1 = [np.log10(1+1/d) for d in d1]
    print("First digit match:", np.allclose(p1, theoretical_p1))
    
    # Second digit
    p2, d2 = benford_expected_distribution(2)
    # Theoretical values from https://en.wikipedia.org/wiki/Benford%27s_law
    theoretical_p2 = [
        0.1197, 0.1139, 0.1088, 0.1043, 0.1003,
        0.0967, 0.0934, 0.0904, 0.0876, 0.0850
    ]
    print("Second digit match:", np.allclose(p2, theoretical_p2, atol=0.001))

if __name__ == "__main__":
    test_digit_extraction()
    debug_expected_distribution()
    test_benford_analysis()
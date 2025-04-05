import numpy as np
from benford import benford_test, benford_expected_distribution

def generate_benford_compliant_data(n=5000):
    """Generate numbers that perfectly follow Benford's Law"""
    p_first = benford_expected_distribution(1)[0]
    
    first_digits = np.random.choice(
        range(1, 10), 
        size=n,  # Now returns array of n digits
        p=p_first
    )
    
    return [10**(np.log10(d) + np.random.uniform(0, 5)) for d in first_digits]

def test_benford_analysis():
    data = generate_benford_compliant_data()
    result = benford_test(data)
    
    print("\n=== Benford Validation Test ===")
    print(f"Chi2 p-value: {result['p_chi']:.3f}")
    #print(f"CVM p-value: {result['p_cvm']:.3f}")
    
    assert not result['anomalous'], "False anomaly detected!"
    print("Test passed! Data is recognized as normal")

if __name__ == "__main__":
    test_benford_analysis()
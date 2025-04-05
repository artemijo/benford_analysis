import requests
import pandas as pd
import base64

# 1. Run analysis
response = requests.post(
    "http://localhost:8000/analyze",
    files={"file": open("financial_data.pdf", "rb")}
).json()

# 2. Save visualization
with open("benford_plot.png", "wb") as f:
    f.write(base64.b64decode(response["plot"]))

# 3. Load original data
numbers = pd.read_csv("financial_data.csv")["Amount"]

# 4. Investigate most anomalous region
most_suspicious = response["anomalous_regions"][0]
print(f"Investigate indices {most_suspicious['start_index']}-{most_suspicious['end_index']}")
print(numbers.iloc[most_suspicious['start_index']:most_suspicious['end_index']])
readme.md 
# Benford's Law Analysis API

A FastAPI service to analyze numerical datasets for compliance with Benford's Law and detect anomalies.

## Features

- **File Support**: CSV, Excel (XLS/XLSX), PDF, and text files
- **Statistical Analysis**:
  - Chi-squared goodness-of-fit test
  - Benford's law analysis
- **Anomaly Detection**:
  - Recursive bisection analysis
  - Bonferroni-corrected significance
- **Visualization**: Base64-encoded bar chart comparison
- **API Documentation**: Interactive Swagger UI at `/docs`

## Installation

### Prerequisites
- Python 3.8+
- [Poetry](https://python-poetry.org/) (recommended)

```bash
# Clone repository
git clone https://github.com/artemijo/benford_analysis.git
cd benford-analysis

# Using poetry
poetry install

# Alternative: using pip
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Start the Server
```bash
uvicorn main:app --reload
```

### API Endpoint
**POST** `/analyze`
- **Parameters**:
  - `file`: Dataset file to analyze
  - `significance_level` (optional): Statistical threshold (default: 0.05)
  - `max_depth` (optional): Bisection recursion depth (default: 3)

### Example Request
```bash
curl -X POST -F "file=@financial_data.csv" http://localhost:8000/analyze
```

### Example Response
```json
{
  "status": "anomalous",
  "stats": {
    "chi2_p": 3.95e-38,
    "cramers_v": 0.27,
    "mad": 0.006
  },
  "plot": "base64_encoded_image",
  "anomalous_regions": [
    {
      "start_index": 0,
      "end_index": 4567,
      "p_chi": 1.42e-56,
      "cramers_v": 0.35,
      "depth": 1
    }
  ]
}
```

## Documentation

### Response Fields
| Field | Description |
|-------|-------------|
| `status` | "anomalous" or "normal" |
| `stats.chi2_p` | Chi-squared test p-value |
| `plot` | Base64 PNG of distribution comparison |
| `anomalous_regions` | Significant anomalous regions |

## Configuration

By default, the server runs on:
- Host: `0.0.0.0`
- Port: `8000`

Modify startup command for different settings:
```bash
uvicorn main:app --host 127.0.0.1 --port 5000
```

## Testing

Run unit tests:
```bash
python -m unittest discover -s tests
```

## Troubleshooting

**Common Issues:**
- **PDF Parsing Warnings**: Normal for documents without explicit crop boxes
- **Installation Errors**: Ensure Python 3.8+ and latest pip version
- **Small Datasets**: Minimum 300 numbers recommended for reliable analysis


## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request


Key features of this README:
1. Clear installation instructions for different environments
2. API usage examples with curl and Python
3. Response format documentation
4. Testing and troubleshooting guidance
5. Contribution guidelines
6. License information

You might want to:
1. Add screenshots of the visualization plot
2. Include sample dataset files
3. Add CI/CD badge if implemented
4. Customize with your project's specific error codes or additional features

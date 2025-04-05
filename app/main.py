from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import pdfplumber
from typing import List
from io import BytesIO
from .benford import *

app = FastAPI()

async def parse_file(file: UploadFile) -> List[float]:
    """Parse files with improved error handling"""
    content = await file.read()
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(content))
            # Focus on columns with "amount", "value", "total" in name
            data_cols = [col for col in df.columns 
                        if re.search(r'amount|value|total', col, re.IGNORECASE)]
            df = df[data_cols].select_dtypes(include='number')
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(BytesIO(content))
            data_cols = [col for col in df.columns 
                        if re.search(r'amount|value|total', col, re.IGNORECASE)]
            df = df[data_cols].select_dtypes(include='number')
        elif file.filename.endswith('.pdf'):
            with pdfplumber.open(BytesIO(content)) as pdf:
                text = []
                for page in pdf.pages:
                    # Exclude header (top 10% of page) and footer (bottom 10%)
                    header_cutoff = page.height * 0.10
                    footer_cutoff = page.height * 0.90
                    cropped = page.crop((0, header_cutoff, page.width, footer_cutoff))
                    text.append(cropped.extract_text())
                text = "\n".join(text)
                return extract_numbers(text)
        elif file.filename.endswith('.txt'):
            text = content.decode('utf-8')
            return extract_numbers(text)
        else:
            raise ValueError("Unsupported file type")
            
        return df.stack().dropna().astype(float).tolist()
    
    except Exception as e:
        raise HTTPException(400, f"Parsing error: {str(e)}")

@app.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    significance_level: float = 0.05,
    max_depth: int = 3
):
    try:
        if not (0 < significance_level < 1):
            raise ValueError("Significance level must be between 0 and 1")
            
        numbers = await parse_file(file)
        if len(numbers) < 300:
            raise HTTPException(
                400, 
                "Insufficient data (minimum 300 numbers required for reliable analysis)"
            )
        
        # Full dataset analysis
        result = benford_test(numbers, alpha=significance_level)
        validate_benford_assumptions(result['expected'])
        
        # Prepare response
        response = {
            "status": "anomalous" if result['anomalous'] else "normal",
            "stats": {
                "chi2_p": result["p_chi"],
                #"cvm_p": result["p_cvm"]
            },
            "plot": plot_benford(result['observed'], result['expected'], result['bins'])
        }
        
        if result['anomalous']:
            anomalies = bisection_analysis(numbers, max_depth, significance_level)
            response["anomalous_regions"] = anomalies
            
        return JSONResponse(response)
        
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
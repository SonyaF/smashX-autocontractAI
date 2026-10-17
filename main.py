import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

# Initialize GenAI client
client = genai.Client()

app = FastAPI(
    title="AutoContract AI Backend",
    description="Multi-agent SAP VA41 Contract Automation System for team smashX",
    version="1.0.0"
)

class SAPContractPayload(BaseModel):
    ship_to_party: str = Field(description="10-digit padded Ship-To Party ID")
    contract_type: str = Field(default="zbip", description="SAP Contract Type")
    sales_org: str = Field(default="3862", description="Sales Organization")
    distribution_channel: str = Field(default="01", description="Distribution Channel")
    division: str = Field(default="09", description="Division")
    contract_end_date: str = Field(default="12/31/9999", description="Contract End Date MM/DD/YYYY")
    material_number: str = Field(description="Material code/number")
    volume_gallons: str = Field(description="Total volume in gallons")
    project_type: str = Field(description="Mapped project type (RET, NTI, CC, D&R)")
    funding_type: str = Field(description="Calculated funding type (HYBRID, ACCRUED, AMORTIZED)")
    payback_version: str = Field(description="Mapped payback version code")
    distributor_acceptance_date: str = Field(description="Acceptance date MM/DD/YYYY")
    xom_approval_date: str = Field(description="Approval date MM/DD/YYYY")

def process_business_logic(data: dict) -> dict:
    """Applies VBA business rules and calculations to extracted raw data"""
    ship_to = str(data.get("ship_to_party", "")).strip()
    if ship_to.isdigit():
        data["ship_to_party"] = ship_to.zfill(10)
        
    fixed_ass = float(data.get("fixed_assistance", 0.0))
    cpg = float(data.get("cpg_value", 0.0))
    
    if fixed_ass > 0 and cpg > 0:
        data["funding_type"] = "HYBRID"
    elif fixed_ass == 0 and cpg > 0:
        data["funding_type"] = "ACCRUED"
    else:
        data["funding_type"] = "AMORTIZED"
        
    sheet_val = str(data.get("payback_code", "")).strip()
    mapping = {
        "1704001": "B", "1704002": "C", "1704003": "D",
        "1704004": "E", "1704005": "F", "1704006": "G",
        "1704007": "H", "1704008": "P", "1704009": "X",
        "1704010": "Z", "1704012": "BGPY", "1704013": "BGPZ", "1704015": "BGPX"
    }
    data["payback_version"] = mapping.get(sheet_val, "B")
    
    raw_proj = str(data.get("project_type", "")).lower()
    if "retention" in raw_proj:
        data["project_type"] = "RET"
    elif "new to industry" in raw_proj:
        data["project_type"] = "NTI"
    elif "competitor conversion" in raw_proj:
        data["project_type"] = "CC"
    elif "demolish and rebuild" in raw_proj:
        data["project_type"] = "D&R"
    else:
        data["project_type"] = "RET"
        
    return data

@app.post("/process-contract/", response_model=SAPContractPayload)
async def process_contract(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        # Read PDF text locally in memory using pypdf (No File API upload needed!)
        reader = PdfReader(file.file)
        pdf_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text + "\n"
        
        if not pdf_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF file.")

        prompt = f"""
        You are an expert contract data extractor for SAP VA41 integration.
        Extract the following details accurately from the contract text provided below:
        - ship_to_party (6-digit ID)
        - material_number
        - volume_gallons (numeric value)
        - project_type (e.g., Retention, New to Industry, etc.)
        - fixed_assistance (dollar amount)
        - cpg_value (numeric)
        - distributor_acceptance_date (MM/DD/YYYY)
        - xom_approval_date (MM/DD/YYYY)
        - payback_code (material version code like 1704001)

        Contract Text:
        {pdf_text}
        """
        
        # Call Gemini model directly with text prompt
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "ship_to_party": {"type": "STRING"},
                        "material_number": {"type": "STRING"},
                        "volume_gallons": {"type": "STRING"},
                        "project_type": {"type": "STRING"},
                        "fixed_assistance": {"type": "NUMBER"},
                        "cpg_value": {"type": "NUMBER"},
                        "distributor_acceptance_date": {"type": "STRING"},
                        "xom_approval_date": {"type": "STRING"},
                        "payback_code": {"type": "STRING"}
                    },
                    "required": [
                        "ship_to_party", "material_number", "volume_gallons", 
                        "project_type", "distributor_acceptance_date", "xom_approval_date", "payback_code"
                    ]
                }
            )
        )
        
        extracted_data = json.loads(response.text)
        final_payload = process_business_logic(extracted_data)
        
        return final_payload

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
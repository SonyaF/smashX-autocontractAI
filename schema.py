import os
import json
from datetime import datetime
from pydantic import BaseModel, Field
import google.generativeai as genai

# 1. Pydantic Model Definition (Matches your VBA Macro logic)
class ContractData(BaseModel):
    ship_to_party: str = Field(description="6-digit numeric Ship-To Party ID")
    material_number: str = Field(description="Material code/number")
    contract_end_date: str = Field(default="12/31/9999", description="Contract End Date (MM/DD/YYYY)")
    volume_gallons: float = Field(description="Total volume in gallons")
    project_type_raw: str = Field(description="Raw project type text like Retention, New to Industry, etc.")
    fixed_assistance: float = Field(default=0.0, description="Fixed Assistance dollar amount")
    cpg_value: float = Field(default=0.0, description="CPG value amount")
    distributor_acceptance_date: str = Field(description="Acceptance date in MM/DD/YYYY format")
    xom_approval_date: str = Field(description="XOM approval date in MM/DD/YYYY format")
    payback_code: str = Field(description="Material payback version code (e.g., 1704001, 1704002, etc.)")

# 2. Business Logic Processors (VBA Conversion)
def calculate_funding_type(fixed_ass: float, cpg: float) -> str:
    """Replicates VBA logic for Funding Type"""
    if fixed_ass > 0 and cpg > 0:
        return "HYBRID"
    elif fixed_ass == 0 and cpg > 0:
        return "ACCRUED"
    else:
        return "AMORTIZED"

def map_payback_version(sheet_val: str) -> str:
    """Replicates VBA mapping for Payback Version"""
    mapping = {
        "1704001": "B", "1704002": "C", "1704003": "D",
        "1704004": "E", "1704005": "F", "1704006": "G",
        "1704007": "H", "1704008": "P", "1704009": "X",
        "1704010": "Z", "1704012": "BGPY", "1704013": "BGPZ", "1704015": "BGPX"
    }
    return mapping.get(sheet_val, "")

def map_project_type(raw_text: str) -> str:
    """Replicates VBA keyword mapping for Project Type"""
    text = raw_text.lower()
    if "retention" in text:
        return "RET"
    elif "new to industry" in text:
        return "NTI"
    elif "competitor conversion" in text:
        return "CC"
    elif "demolish and rebuild" in text:
        return "D&R"
    return "RET"
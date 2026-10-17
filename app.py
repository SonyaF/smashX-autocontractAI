import streamlit as st
import requests
import json

# Page Configuration
st.set_page_config(
    page_title="AutoContract AI - SAP VA41 Migration",
    page_icon="⚡",
    layout="centered"
)

# App Header
st.title("⚡ AutoContract AI (team smashX)")
st.subheader("Multi-Agent Legacy SAP VBA to Cloud-Native Python Migration")
st.markdown("---")

# Instructions
st.info("Upload a B2B contract PDF below. The AI agent will extract key fields, apply business rules (Funding & Payback mapping), and generate the SAP VA41 Payload.")

# File Uploader Widget
uploaded_file = st.file_uploader("Upload Contract PDF", type=["pdf"])

if uploaded_file is not None:
    # Display File Details
    file_details = {"Filename": uploaded_file.name, "Filesize": f"{uploaded_file.size / 1024:.2f} KB"}
    st.write("### File Details:")
    st.json(file_details)
    
    if st.button("🚀 Process Contract & Generate SAP Payload"):
        with st.spinner("Processing contract with Gemini 1.5 Flash & Applying Business Rules..."):
            try:
                # Prepare file for API request to FastAPI backend
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                
                # FastAPI Endpoint (Change URL if hosted on Cloud Run)
                backend_url = "http://localhost:8000/process-contract/"
                
                response = requests.post(backend_url, files=files)
                
                if response.status_code == 200:
                    payload_data = response.json()
                    st.success("Contract successfully processed and verified!")

                    st.write("### 📦 Generated SAP VA41 Payload (JSON):")
                    st.json(payload_data)

                    # Preview Table for Quick Review
                    st.write("### 📊 Field Mapping Preview:")
                    table_data = [
                        {"Field Name": "Ship-To Party", "Mapped Value": payload_data.get("ship_to_party")},
                        {"Field Name": "Contract Type", "Mapped Value": payload_data.get("contract_type")},
                        {"Field Name": "Material Number", "Mapped Value": payload_data.get("material_number")},
                        {"Field Name": "Volume (Gallons)", "Mapped Value": payload_data.get("volume_gallons")},
                        {"Field Name": "Project Type", "Mapped Value": payload_data.get("project_type")},
                        {"Field Name": "Funding Type", "Mapped Value": payload_data.get("funding_type")},
                        {"Field Name": "Payback Version", "Mapped Value": payload_data.get("payback_version")},
                        {"Field Name": "XOM Approval Date", "Mapped Value": payload_data.get("xom_approval_date")}
                    ]
                    st.table(table_data)

                else:
                    try:
                        error_msg = response.json().get('detail', response.text)
                    except Exception:
                        error_msg = response.text
                    st.error(f"Error from Backend: {error_msg}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI backend. Make sure `main.py` is running on port 8000!")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>AI Builder Cup 2026 Submission | team smashX</p>", unsafe_allow_html=True)
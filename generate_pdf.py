from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_mock_contract(filename="mock_contract_01.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Contract Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "B2B COMMERCIAL CONTRACT AGREEMENT")
    
    c.setFont("Helvetica", 11)
    c.drawString(100, 720, "Ship To: 416111")
    c.drawString(100, 700, "Material Number: 1704001")
    c.drawString(100, 680, "Project Type: Retention")
    c.drawString(100, 660, "Estimated Volume: 50,000 Gallons")
    c.drawString(100, 640, "Fixed Assistance: $5,000")
    c.drawString(100, 620, "CPG Value: 2.5")
    c.drawString(100, 600, "Distributor Acceptance Date: October 10, 2026 | Approved")
    c.drawString(100, 580, "XOM APPROVAL DATE: May 11, 2026")
    c.drawString(100, 560, "Payment Term: 5 Years")
    
    c.save()
    print(f"Mock Contract PDF created successfully: {filename}")

if __name__ == "__main__":
    create_mock_contract()
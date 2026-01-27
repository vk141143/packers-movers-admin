from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

def generate_invoice_pdf(job, invoice_number, db):
    """Generate invoice PDF and return as bytes"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "INVOICE")
    
    # Invoice details
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Invoice Number: {invoice_number}")
    c.drawString(50, height - 120, f"Job ID: {job.id}")
    c.drawString(50, height - 140, f"Date: {datetime.utcnow().strftime('%d/%m/%Y')}")
    
    # Client details
    if job.client_id:
        from sqlalchemy import text
        try:
            client_result = db.execute(
                text("SELECT full_name, company_name, email, phone_number FROM clients WHERE id = :id"),
                {"id": job.client_id}
            ).fetchone()
            if client_result:
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, height - 180, "Bill To:")
                c.setFont("Helvetica", 11)
                c.drawString(50, height - 200, f"{client_result[0]}")
                c.drawString(50, height - 215, f"{client_result[1]}")
                c.drawString(50, height - 230, f"{client_result[2]}")
                c.drawString(50, height - 245, f"{client_result[3]}")
        except:
            pass
    
    # Job details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 285, "Job Details:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 305, f"Property Address: {job.property_address}")
    c.drawString(50, height - 320, f"Scheduled Date: {job.preferred_date if job.preferred_date else 'N/A'}")
    c.drawString(50, height - 335, f"Scheduled Time: {job.preferred_time if job.preferred_time else 'N/A'}")
    
    # Amount
    c.setFont("Helvetica-Bold", 16)
    amount = job.quote_amount if job.quote_amount else 0.0
    c.drawString(50, height - 385, f"Total Amount: £{float(amount):.2f}")
    
    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(50, 50, "Thank you for your business!")
    c.drawString(50, 35, "Emergency Property Clearance Services")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

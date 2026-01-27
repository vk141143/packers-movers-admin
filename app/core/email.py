import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=True)
else:
    load_dotenv(override=True)

def send_admin_notification(crew_email: str, crew_name: str):
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    if not smtp_user or not smtp_password:
        print("Email not configured. Skipping notification.")
        return
    
    subject = f"New Crew Registration - {crew_name}"
    body = f"""
    A new crew member has registered and is waiting for approval.
    
    Name: {crew_name}
    Email: {crew_email}
    
    Please log in to the admin panel to approve or reject this registration.
    """
    
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = admin_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Admin notification sent for {crew_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_approval_email(crew_email: str, crew_name: str):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    if not smtp_user or not smtp_password:
        print("Email not configured. Skipping notification.")
        return
    
    subject = "Your Crew Account Has Been Approved!"
    body = f"""
    Hi {crew_name},
    
    Great news! Your crew account has been approved by the admin.
    
    You can now log in to the platform and start working.
    
    Best regards,
    Emergency Property Clearance Team
    """
    
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = crew_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Approval email sent to {crew_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_otp_email(email: str, otp: str):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    print(f"SMTP Config - Server: {smtp_server}, Port: {smtp_port}, User: {smtp_user}")
    
    if not smtp_user or not smtp_password:
        print("Email not configured. Skipping OTP email.")
        return
    
    subject = "Password Reset OTP"
    body = f"""
    Your password reset OTP is: {otp}
    
    This OTP will expire in 5 minutes.
    
    If you didn't request this, please ignore this email.
    
    Best regards,
    Emergency Property Clearance Team
    """
    
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        print(f"Attempting to send OTP email to {email}")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"OTP email sent successfully to {email}")
    except Exception as e:
        print(f"Failed to send OTP email: {e}")

def send_job_otp_email(client_email: str, client_name: str, otp: str, job_id: str):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    if not smtp_user or not smtp_password:
        print("Email not configured. Skipping job OTP email.")
        return
    
    subject = f"Job Verification OTP - {job_id}"
    body = f"""
    Hi {client_name},
    
    Your crew has arrived at the property and is ready to begin work.
    
    Please provide them with this OTP to verify and authorize the work:
    
    OTP: {otp}
    
    Job ID: {job_id}
    
    This OTP is valid for this job only.
    
    Best regards,
    Emergency Property Clearance Team
    """
    
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = client_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Job OTP email sent to {client_email}")
    except Exception as e:
        print(f"Failed to send job OTP email: {e}")

def send_job_assignment_email(crew_email: str, crew_name: str, job_id: str, property_address: str):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    if not smtp_user or not smtp_password:
        print("Email not configured. Skipping job assignment email.")
        return
    
    subject = f"New Job Assigned - {job_id}"
    body = f"""
    Hi {crew_name},
    
    You have been assigned a new job!
    
    Job ID: {job_id}
    Property Address: {property_address}
    
    Please log in to the crew portal to view full job details and accept the assignment.
    
    Best regards,
    Emergency Property Clearance Team
    """
    
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = crew_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Job assignment email sent to {crew_email}")
    except Exception as e:
        print(f"Failed to send job assignment email: {e}")

def send_payment_request_email(client_email: str, job_id: str, final_price: float, deposit_paid: float, remaining_amount: float):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    if not smtp_user or not smtp_password:
        print("Email not configured. Skipping payment request email.")
        return
    
    subject = f"Payment Request - Job {job_id}"
    body = f"""
    Your job has been completed and verified!
    
    Job ID: {job_id}
    
    Payment Breakdown:
    Final Price: £{final_price:.2f}
    Deposit Paid: £{deposit_paid:.2f}
    Remaining Amount: £{remaining_amount:.2f}
    
    Please log in to your account to complete the payment.
    
    Best regards,
    Emergency Property Clearance Team
    """
    
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = client_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Payment request email sent to {client_email}")
    except Exception as e:
        print(f"Failed to send payment request email: {e}")

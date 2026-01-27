import os
from dotenv import load_dotenv

load_dotenv()

def send_sms_otp(phone_number: str, otp: str) -> bool:
    """
    Send OTP via SMS to phone number
    For production, integrate with Twilio, AWS SNS, or other SMS provider
    """
    try:
        # For now, just print to console (replace with actual SMS service)
        print(f"📱 SMS OTP to {phone_number}: {otp}")
        print(f"Message: Your password reset OTP is: {otp}. Valid for 5 minutes.")
        
        # TODO: Integrate with actual SMS provider
        # Example with Twilio:
        # from twilio.rest import Client
        # account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        # auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=f"Your password reset OTP is: {otp}. Valid for 5 minutes.",
        #     from_=os.getenv("TWILIO_PHONE_NUMBER"),
        #     to=phone_number
        # )
        # return message.sid is not None
        
        return True
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

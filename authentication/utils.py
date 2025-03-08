from django.core.mail import send_mail
from django.conf import settings



def send_otp(email, otp_code):
    subject = "Your OTP Code"
    message = f"Your OTP code is {otp_code}. It will expire in 5 minutes."
    sender_email = settings.EMAIL_HOST_USER
    
    send_mail(subject, message, sender_email, [email])
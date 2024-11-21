
from email.mime.text import MIMEText
import re
import smtplib
import ssl
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
import requests

from sms_sender.api.etext.exceptions import NumberNotValidException, ProviderNotFoundException
from sms_sender.api.etext.providers import PROVIDERS



@api_view(['POST', ])
@permission_classes([ ])
@authentication_classes([])
def send_sms_view(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == 'POST':

        phone_number = request.data.get('phone_number', "")
        subject = request.data.get('subject', "")
        message = request.data.get('message', "")
        provider = request.data.get('provider', "")

        if not phone_number:
            errors['phone_number'] = ['Phone nuber is required.']

        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        
        send_sms_via_email(
            number=phone_number,
            subject=subject,
            message=message,
            provider=provider
        )



        payload['message'] = "Successful"
        payload['data'] = data

    return Response(payload)





def send_sms_via_email(
    number: str,
    message: str,
    provider: str,
    subject: str = "sent using etext",
    smtp_server: str = settings.EMAIL_HOST,  # Defaults to Gmail's SMTP server
    smtp_port: int = 587,  # Port 587 is the correct one for STARTTLS
):
    sender_email = settings.EMAIL_HOST_USER
    email_password = settings.EMAIL_HOST_PASSWORD
    receiver_email = format_provider_email_address(number, provider)

    print(f"Sending SMS to: {receiver_email}")

    # Create the email message
    email_message = MIMEText(message)
    email_message["Subject"] = subject
    email_message["To"] = receiver_email

    try:
        # Create a connection to the SMTP server
        with smtplib.SMTP_SSL(smtp_server, 465, context=ssl.create_default_context()) as email:
            email.login(sender_email, email_password)
            email.sendmail(sender_email, receiver_email, email_message.as_string())
            print(f"Email successfully sent to {receiver_email}")

    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
        # Optionally, you could log the error or raise it to handle it in your application logic


def format_provider_email_address(number: str, provider: str):
    provider_info = PROVIDERS.get(provider)

    if provider_info == None:
        raise ProviderNotFoundException(provider)

    domain = provider_info.get("sms")

    number = number.replace(" ", "")

    number = number[1:]


    return f"{number}@{domain}"



def validate_number(number: str):
    num = ""
    valid = False

    for character in number:
        if character.isdigit():
            num += character

    # a phone number will have a valid length of 10 digits as all of the phone
    # domains are US phone domains with area codes

    if len(num) == 10:
        valid = True

    if not valid:
        return f'{number} not valid. It must be a valid US phone number 10 digits in length'

    return num

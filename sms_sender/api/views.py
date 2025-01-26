
from email.mime.text import MIMEText
import re
import smtplib
import ssl
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
import requests

from phone_generator.models import PhoneNumber
from sms_sender.api.etext.exceptions import NumberNotValidException, ProviderNotFoundException
from sms_sender.api.etext.providers import PROVIDERS
from sms_sender.api.tasks import send_bulk_sms_task




@api_view(['POST'])
def send_valid_number_sms_view(request):
    payload = {}
    errors = {}

    # Get data from the request
    phone_number_id = request.data.get('phone_number_id', None)
    user_id = request.data.get('user_id', None)
    message = request.data.get('message', None)
    provider = request.data.get('provider', None)

    # Validation checks for required fields
    if not phone_number_id:
        errors['phone_number_id'] = ['Phone Number ID is required.']
    if not user_id:
        errors['user_id'] = ['User ID is required.']
    if not message:
        errors['message'] = ['Message is required.']
    if not provider:
        errors['provider'] = ['Provider is required.']

    # If there are any validation errors, return them
    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch the User object based on the provided user_id
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        errors['user_id'] = ['User does not exist.']
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch the PhoneNumber object based on the provided phone_number_id
        phone_number = PhoneNumber.objects.get(id=phone_number_id, user=user)
    except PhoneNumber.DoesNotExist:
        errors['phone_number_id'] = ['Phone number does not exist for this user.']
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Check if the phone number is valid
    if not phone_number.valid_number:
        errors['phone_number'] = ['This phone number is not valid.']
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Send the SMS via email (can be replaced by another SMS service)
    try:
        send_sms_via_email(
            number=phone_number.phone_number,
            message=message,
            provider=provider,
            subject="Sent using etext"
        )

        # Return success message
        payload['message'] = f"SMS successfully sent to {phone_number.phone_number}"
        return Response(payload, status=status.HTTP_200_OK)

    except Exception as e:
        errors['sms_error'] = [f"Error sending SMS: {str(e)}"]
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def send_bulk_valid_number_sms_view(request):
    payload = {}
    errors = {}

    if request.method == 'POST':
        user_id = request.data.get('user_id', "")
        subject = request.data.get('subject', "")
        message = request.data.get('message', "")
        provider = request.data.get('provider', "")

        # Validation
        if not user_id:
            errors['user_id'] = ['User ID is required.']
        if not subject:
            errors['subject'] = ['Subject is required.']
        if not message:
            errors['message'] = ['Message is required.']
        if not provider:
            errors['provider'] = ['Provider is required.']

        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            errors['user_id'] = ['User does not exist.']
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        # Trigger the Celery task to send bulk SMS
        send_bulk_sms_task.apply_async(
            args=[user_id, subject, message, provider],
            countdown=5  # Optionally delay the task slightly
        )

        payload['message'] = "Bulk SMS is being sent."
        return Response(payload, status=status.HTTP_200_OK)








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

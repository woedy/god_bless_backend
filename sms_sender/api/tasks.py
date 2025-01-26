# your_app/tasks.py

from celery import shared_task
from django.conf import settings
import requests
from time import sleep
import re
from celery import chain

from phone_generator.models import PhoneNumber



@shared_task(bind=True)
def send_bulk_sms_task(self, user_id, subject, message, provider):
    try:
        # Get all valid phone numbers for the user and provider
        phone_numbers = PhoneNumber.objects.filter(
            user__user_id=user_id,
            valid_number=True,
            is_archived=False,
            carrier=provider,
            type='mobile'
        ).order_by('id')

        # If no phone numbers found, stop the task
        if not phone_numbers.exists():
            print("No valid phone numbers left to send SMS.")
            return

        # Send SMS to the first number in the list
        phone_number = phone_numbers.first()

        # Send the SMS via email
        send_sms_via_email(
            number=phone_number.phone_number,
            message=message,
            provider=provider,
            subject=subject
        )

        print(f"SMS sent to {phone_number.phone_number}")

        # Remove the sent phone number from the queryset (simulate processing the batch)
        phone_numbers = phone_numbers.exclude(id=phone_number.id)

        # If there are more numbers left, schedule the task to run in 30 seconds
        if phone_numbers.exists():
            print(f"Scheduling next batch of SMS in 30 seconds.")
            send_bulk_sms_task.apply_async(
                args=[user_id, subject, message, provider],
                countdown=30  # Delay for 30 seconds before sending the next batch
            )

    except Exception as e:
        print(f"Error sending bulk SMS: {str(e)}")
        self.retry(exc=e, countdown=10)


def send_sms_via_email(number, message, provider, subject="sent using etext"):
    # Create the email message to be sent via the provider
    receiver_email = format_provider_email_address(number, provider)
    
    email_message = MIMEText(message)
    email_message["Subject"] = subject
    email_message["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, 465, context=ssl.create_default_context()) as email:
            email.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            email.sendmail(settings.EMAIL_HOST_USER, receiver_email, email_message.as_string())
            print(f"SMS sent to {receiver_email}")
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")


def format_provider_email_address(number, provider):
    provider_info = PROVIDERS.get(provider)
    if not provider_info:
        raise ValueError(f"Provider {provider} not found")
    
    domain = provider_info.get("sms")
    number = number.replace(" ", "")
    number = number[1:]  # remove the leading 0
    return f"{number}@{domain}"

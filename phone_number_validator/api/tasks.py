# your_app/tasks.py

from celery import shared_task
from django.conf import settings
import requests
from time import sleep
import re
from celery import chain

from phone_generator.models import PhoneNumber

# A mock URL to your validation API (replace with the actual one)
VALIDATION_API_URL = 'https://phonevalidation.abstractapi.com/v1/?api_key=' + settings.ABSTRACT_PHONE_VALIDATOR_KEY



@shared_task(bind=True)
def validate_phone_number_task(self, phone_number_id):
    try:
        # Fetch the phone number record
        phone_number = PhoneNumber.objects.get(id=phone_number_id)
        if phone_number.validation_attempted:
            return  # Skip if this number has already been validated

        # Mark validation as attempted
        phone_number.validation_attempted = True
        phone_number.save()

        # Clean the phone number (remove non-numeric characters)
        cleaned_number = re.sub(r'\D', '', phone_number.phone_number)

        # Log the validation request
        print(f"Validating phone number {phone_number.phone_number}...")

        # Make a request to the external validation server
        response = requests.get(
            "https://phonevalidation.abstractapi.com/v1/",
            params={"api_key": settings.ABSTRACT_PHONE_VALIDATOR_KEY, "phone": cleaned_number},
            timeout=5
        )

        if response.status_code == 200:
            # Parse the response and update the phone number fields
            data = response.json()
            phone_number.valid_number = data.get("valid", False)
            phone_number.location = data.get("location", "")
            phone_number.type = data.get("type", "")
            phone_number.carrier = data.get("carrier", "")
            phone_number.code = data.get("country", {}).get("code")
            phone_number.country_name = data.get("country", {}).get("name")
            phone_number.prefix = data.get("country", {}).get("prefix")
            phone_number.international = data.get("format", {}).get("international")
            phone_number.local = data.get("format", {}).get("local")
        else:
            phone_number.valid_number = False

        # Save the updated phone number data
        phone_number.save()
        print(f"Validated {phone_number.phone_number} - Valid: {phone_number.valid_number}")

        # Schedule the next task in 30 seconds
        next_phone_number = PhoneNumber.objects.filter(valid_number__isnull=True).order_by('id').first()
        if next_phone_number:
            validate_phone_number_task.apply_async(args=[next_phone_number.id], countdown=5)
    except Exception as e:
        print(f"Error validating {phone_number.phone_number}: {str(e)}")
        self.retry(exc=e, countdown=10)
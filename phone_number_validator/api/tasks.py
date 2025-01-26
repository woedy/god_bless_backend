# your_app/tasks.py

from celery import shared_task
from django.conf import settings
import requests
from time import sleep
import re
from celery import chain

from accounts.models import UserAPIKey
from phone_generator.models import PhoneNumber




@shared_task(bind=True)
def validate_phone_number_task(self, phone_number_id, user_id):
    try:
        # Fetch the phone number record
        phone_number = PhoneNumber.objects.get(id=phone_number_id, user__user_ud=user_id)
        if phone_number.validation_attempted:
            return  # Skip if this number has already been validated
        
                
        try:
            user_api = UserAPIKey.objects.get(user=phone_number.user)
        except:
            print(f"No User Found")


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
            params={"api_key": user_api.abstract_api_key, "phone": cleaned_number},
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
        next_phone_number = PhoneNumber.objects.filter(valid_number__isnull=True, user__user_id=user_id).order_by('id').first()
        if next_phone_number:
            validate_phone_number_task.apply_async(args=[next_phone_number.id, user_id], countdown=5)
    except Exception as e:
        print(f"Error validating {phone_number.phone_number}: {str(e)}")
        self.retry(exc=e, countdown=10)






@shared_task(bind=True)
def validate_phone_number_task_quality(self, phone_number_id, user_id):
    try:
        # Fetch the phone number record
        phone_number = PhoneNumber.objects.get(id=phone_number_id, user__user_ud=user_id)


                        
        try:
            user_api = UserAPIKey.objects.get(user=phone_number.user)
        except:
            print(f"No User Found")


        # Clean the phone number (remove non-numeric characters)
        cleaned_number = re.sub(r'\D', '', phone_number.phone_number)

        # Make a request to the IPQualityScore API
        response = requests.get(
            VALIDATION_API_URL + cleaned_number,
            timeout=5
        )


        VALIDATION_API_URL = 'https://www.ipqualityscore.com/api/json/phone/' + user_api.quality_api_key + '/'

        if response.status_code == 200:
            data = response.json()

            # Map the response fields to the PhoneNumber model fields
            phone_number.valid_number = data.get("valid", False)
            phone_number.location = data.get("city", "")  # Using city from the API response
            phone_number.type = data.get("line_type", "")  # Using line type
            phone_number.carrier = data.get("carrier", "")
            phone_number.country_name = data.get("country", "")
            phone_number.prefix = str(data.get("dialing_code", ""))
            phone_number.international = data.get("formatted", "")
            phone_number.local = data.get("local_format", "")

        
            # Save the updated phone number data
            phone_number.save()

            print(f"Validated {phone_number.phone_number} - Valid: {phone_number.valid_number}")

            # Optionally, schedule the next phone number validation if necessary
            next_phone_number = PhoneNumber.objects.filter(valid_number__isnull=True, user__user_id=user_id).order_by('id').first()
            if next_phone_number:
                validate_phone_number_task_quality.apply_async(args=[next_phone_number.id, user_id], countdown=30)

        else:
            print(f"Error: Received non-200 response code from IPQualityScore API: {response.status_code}")
            phone_number.valid_number = False
            phone_number.save()

    except Exception as e:
        print(f"Error validating {phone_number.phone_number}: {str(e)}")
        self.retry(exc=e, countdown=10)

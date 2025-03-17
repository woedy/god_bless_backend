import json
import re
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
import requests
from django.contrib.auth import get_user_model

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from django.http import JsonResponse  # Add this import
from accounts.models import UserAPIKey
from phone_generator.models import PhoneNumber
from phone_number_validator.models import PhonePrefix
from projects.models import Project
from .tasks import validate_phone_number_task, validate_phone_number_task_quality
from rest_framework.authentication import TokenAuthentication


User = get_user_model()




@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def validate_phone_number_ORIG(request):
    payload = {}
    errors = {}

    phone = request.data.get('phone', "")

    phone = re.sub(r'\D', '', phone)

    if not phone:
        errors['phone'] = ['Phone number is required.']
    elif not phone.isdigit():
        errors['phone'] = ['Phone number must be numeric.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Call external API for phone validation
    api_key = settings.ABSTRACT_PHONE_VALIDATOR_KEY
    try:
        response = requests.get(
            "https://phonevalidation.abstractapi.com/v1/",
            params={"api_key": api_key, "phone": phone},
            timeout=5
        )
        if response.status_code == 200:
            validation_data = response.json()
            payload['message'] = "Validation successful"
            payload['data'] = validation_data
            return Response(payload, status=status.HTTP_200_OK)
        else:
            payload['message'] = "Failed to validate phone number"
            payload['errors'] = f"API response: {response.status_code}"
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except requests.RequestException as e:
        payload['message'] = "Request to validation service failed"
        payload['errors'] = str(e)
        return Response(payload, status=status.HTTP_503_SERVICE_UNAVAILABLE)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def validate_phone_number(request):
    payload = {}
    errors = {}

    # Get data from the request
    user_id = request.data.get('user_id', "")
    phone_id = request.data.get('phone_id', "")

    print(user_id)
    print(phone_id)

    # Validation checks for required fields
    if not phone_id:
        errors['phone_id'] = ['Phone ID is required.']

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        errors['user_id'] = ['User does not exist.']



            
    try:
        user_api = UserAPIKey.objects.get(user=user)
    except:
        errors['user_id'] = ['User Api does not exist.']


    try:
        phone_number = PhoneNumber.objects.get(id=phone_id, user=user)
    except PhoneNumber.DoesNotExist:
        errors['phone_id'] = ['Phone number does not exist.']

    if phone_number.validation_attempted:
        errors['phone_id'] = ['Phone number already attempted validation.']



    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)



    # Mark phone number as attempted for validation
    phone_number.validation_attempted = True
    phone_number.save()

    # Clean the phone number (remove non-numeric characters)
    cleaned_number = re.sub(r'\D', '', phone_number.phone_number)
    
    VALIDATION_API_URL = 'https://phonevalidation.abstractapi.com/v1/'

    try:
        # Make a request to the external phone validation API
        response = requests.get(
            VALIDATION_API_URL,
            params={"api_key": user_api.abstract_api_key, "phone": cleaned_number},
            timeout=5
        )

        if response.status_code == 200:
            validation_data = response.json()

            # Map the API response fields to the PhoneNumber model fields
            phone_number.valid_number = validation_data.get("valid", False)
            phone_number.location = validation_data.get("location", "")
            phone_number.type = validation_data.get("type", "")
            phone_number.carrier = validation_data.get("carrier", "")
            phone_number.code = validation_data.get("country", {}).get("code")
            phone_number.country_name = validation_data.get("country", {}).get("name")
            phone_number.prefix = validation_data.get("country", {}).get("prefix")
            phone_number.international = validation_data.get("format", {}).get("international")
            phone_number.local = validation_data.get("format", {}).get("local")

            # Save the updated phone number data
            phone_number.save()

            payload['message'] = "Validation successful"
            payload['data'] = validation_data
            return Response(payload, status=status.HTTP_200_OK)

        else:
            payload['message'] = "API LIMIT REACHED - Failed to validate phone number"
            payload['errors'] = f"API response: {response.status_code}"
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except requests.RequestException as e:
        payload['message'] = "Request to validation service failed"
        payload['errors'] = str(e)
        return Response(payload, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def validate_phone_number_quality(request):
    payload = {}
    errors = {}

    # Get data from the request
    user_id = request.data.get('user_id', "")
    phone_id = request.data.get('phone_id', "")


    print(user_id)
    print(phone_id)
    # Validation checks for required fields
    if not phone_id:
        errors['phone_id'] = ['Phone ID is required.']

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        errors['user_id'] = ['User does not exist.']


            
    try:
        user_api = UserAPIKey.objects.get(user=user)
    except:
        errors['user_id'] = ['User Api does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    try:
        phone_number = PhoneNumber.objects.get(id=phone_id, user=user)
    except PhoneNumber.DoesNotExist:
        errors['phone_id'] = ['Phone number does not exist.']
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    if phone_number.validation_attempted:
        errors['phone_id'] = ['Phone number already attempted validation.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)


    VALIDATION_API_URL = 'https://www.ipqualityscore.com/api/json/phone/' + user_api.quality_api_key + '/'

    # Mark phone number as attempted for validation
    phone_number.validation_attempted = True
    phone_number.save()

    # Clean the phone number (remove non-numeric characters)
    cleaned_number = re.sub(r'\D', '', phone_number.phone_number)

    try:
        # Make a request to the IPQualityScore API
        response = requests.get(
            VALIDATION_API_URL + cleaned_number,
            timeout=5
        )

        if response.status_code == 200:
            validation_data = response.json()

            # Map the API response fields to the PhoneNumber model fields
            phone_number.valid_number = validation_data.get("valid", False)
            phone_number.location = validation_data.get("city", "")  # Using city from API response
            if validation_data.get("line_type") == "Wireless":
                phone_number.type = "mobile"
            else:
             phone_number.type = validation_data.get("line_type", "")
            phone_number.carrier = validation_data.get("carrier", "")
            phone_number.country_name = validation_data.get("country", "")
            phone_number.prefix = str(validation_data.get("dialing_code", ""))
            phone_number.international = validation_data.get("formatted", "")
            phone_number.local = validation_data.get("local_format", "")

            # Save the updated phone number data
            phone_number.save()

            payload['message'] = "Validation successful"
            payload['data'] = validation_data
            return Response(payload, status=status.HTTP_200_OK)

        else:
            payload['message'] = "API LIMIT REACHED - Failed to validate phone number"
            payload['errors'] = f"API response: {response.status_code}"
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except requests.RequestException as e:
        payload['message'] = "Request to validation service failed"
        payload['errors'] = str(e)
        return Response(payload, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    





@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def validate_phone_number_quality_ORIG(request):
    payload = {}
    errors = {}



    phone = request.data.get('phone', "")
    user_id = request.data.get('user_id', "")


    print("###################################")
    print(user_id)

    phone = re.sub(r'\D', '', phone)

    if not phone:
        errors['phone'] = ['Phone number is required.']
    elif not phone.isdigit():
        errors['phone'] = ['Phone number must be numeric.']


    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        errors['user_id'] = ['User does not exist.']


            
    try:
        user_api = UserAPIKey.objects.get(user=user)
    except:
        errors['user_id'] = ['User Api does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)


    VALIDATION_API_URL = 'https://www.ipqualityscore.com/api/json/phone/' + user_api.quality_api_key + '/'


    try:
        # Make a request to the IPQualityScore API
        response = requests.get(
            VALIDATION_API_URL + phone,
            timeout=5
        )

        if response.status_code == 200:
            validation_data = response.json()

            payload['message'] = "Validation successful"
            payload['data'] = validation_data
            return Response(payload, status=status.HTTP_200_OK)

        else:
            payload['message'] = "API LIMIT REACHED - Failed to validate phone number"
            payload['errors'] = f"API response: {response.status_code}"
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except requests.RequestException as e:
        payload['message'] = "Request to validation service failed"
        payload['errors'] = str(e)
        return Response(payload, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def start_validation(request):
    payload = {}
    errors = {}
    data = {}

    if request.method == 'POST':


        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        # Fetch the first phone number that hasn't been validated yet
        first_phone_number = PhoneNumber.objects.filter(valid_number__isnull=True).first()

        if first_phone_number:
            # Trigger the validation task for the first phone number
            validate_phone_number_task.apply_async(args=[first_phone_number.id])
        else:
            payload['data'] = 'Validation process started.'



        payload['message'] = "Successful"
        payload['data'] = 'Validation process started.'

    return Response(payload)








@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def start_validation(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == 'POST':
        user_id = request.data.get('user_id', "")


        if not user_id:
            errors['user_id'] = ['User ID is required.']

        try:
            user = User.objects.get(user_id=user_id)
        except:
            errors['user_id'] = ['User does not exist.']


        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)



    
        # Fetch the first phone number that hasn't been validated yet
        first_phone_number = PhoneNumber.objects.filter(valid_number__isnull=True, user=user).first()
        
        if first_phone_number:
            # Trigger the validation task for the first phone number
            validate_phone_number_task.apply_async(args=[first_phone_number.id, user_id])
            payload['message'] = "Validation process started."
        else:
            errors['user_id'] = ['No phone numbers to validate.']

        
        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)


        payload['message'] = "Successful"
        payload['data'] = data

    return Response(payload)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def start_validation_quality(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == 'POST':
        user_id = request.data.get('user_id', "")


        if not user_id:
            errors['user_id'] = ['User ID is required.']

        try:
            user = User.objects.get(user_id=user_id)
        except:
            errors['user_id'] = ['User does not exist.']


        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)



    
        # Fetch the first phone number that hasn't been validated yet
        first_phone_number = PhoneNumber.objects.filter(valid_number__isnull=True, user=user).first()
        
        if first_phone_number:
            # Trigger the validation task for the first phone number
            validate_phone_number_task_quality.apply_async(args=[first_phone_number.id, user_id])

            payload['message'] = "Validation process started."
        else:
            errors['user_id'] = ['No phone numbers to validate.']

        
        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)


        payload['message'] = "Successful"
        payload['data'] = data

    return Response(payload)










@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def start_validation222(request):
    
    # Fetch the first phone number that hasn't been validated yet
    first_phone_number = PhoneNumber.objects.filter(valid_number__isnull=True).first()

    if first_phone_number:
        # Trigger the validation task for the first phone number
        validate_phone_number_task.apply_async(args=[first_phone_number.id])

        return JsonResponse({"message": "Validation process started."}, status=200)
    else:
        return JsonResponse({"message": "No phone numbers to validate."}, status=400)










########################################
#######################################
#########################################################



@api_view(['GET'])
def load_phone_prefixes(request):
    payload = {}
    data = {}
    errors = {}

    with open('data.json', 'r') as f:
        data = json.load(f)
        
        # Loop through the data and create entries in the database
        for prefix, info in data.items():
            PhonePrefix.objects.create(
                prefix=info['prefix'],
                carrier=info['carrier'],
                city=info['city'],
                state=info['state'],
                line_type=info['type']
            )


    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def validate_phone_number_free(request):
    payload = {}
    errors = {}

    # Get data from the request
    user_id = request.data.get('user_id', "")
    phone_id = request.data.get('phone_id', "")  # Expecting a single phone ID

    if not phone_id:
        errors['phone_id'] = ['Phone ID is required.']

    # Validation checks for required fields
    if not user_id:
        errors['user_id'] = ['User ID is required.']

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        errors['user_id'] = ['User does not exist.']


    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the phone number
    phone_number = PhoneNumber.objects.filter(id=phone_id, user=user).first()

    if not phone_number:
        errors['phone_id'] = ['Phone number does not exist.']
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    if phone_number.validation_attempted:
        errors['phone_id'] = ['Phone number already attempted validation.']
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Clean the phone number (remove non-numeric characters)
    cleaned_number = re.sub(r'\D', '', phone_number.phone_number)[1:]

    # Extract the prefix (first 6 digits)
    prefix = cleaned_number[:6]

    try:
        # Look up the PhoneRecord for the prefix in the database
        record = PhonePrefix.objects.get(prefix=prefix)

        # Map the PhoneRecord data to the PhoneNumber model
        phone_number.valid_number = True  # Mark it as a valid number
        phone_number.carrier = record.carrier
        phone_number.state = record.state
        phone_number.type = record.line_type
        phone_number.location = record.city  # Use city from PhoneRecord
        phone_number.country_name = "United States"  # You can adjust this if needed
        phone_number.prefix = '+1'
        phone_number.validation_attempted = True  # Mark as validated
        phone_number.save()

        payload['message'] = "Validation successful"
        payload['data'] = {
            'carrier': record.carrier,
            'line_type': record.line_type,
            'state': record.state,
            'location': record.city
        }
        return Response(payload, status=status.HTTP_200_OK)

    except PhonePrefix.DoesNotExist:
        phone_number.valid_number = False  
        phone_number.save()

        errors['phone_id'] = [f'No record found for prefix {prefix}']
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)




from django.db import transaction

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def validate_all_phone_numbers_free(request):
    payload = {}
    errors = {}

    # Get data from the request
    user_id = request.data.get('user_id', "")
    project_id = request.data.get('project_id', "")
    
    if not user_id:
        errors['user_id'] = ['User ID is required.']
    if not project_id:
        errors['project_id'] = ['Project ID is required.']

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        errors['user_id'] = ['User does not exist.']

    try:
        project = Project.objects.get(id=project_id)
    except:
        errors['project_id'] = ['Project does not exist.']

    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Fetch all phone numbers for the user that need validation
    phone_numbers = PhoneNumber.objects.filter(user=user, project=project, validation_attempted=False)

    if not phone_numbers:
        errors['phone_id'] = ['No phone numbers found for validation.']
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Prepare for bulk updates
    updated_phone_numbers = []
    error_phone_numbers = []

    # Batch processing (using chunks to process in smaller batches)
    batch_size = 1000  # Adjust as needed, depending on performance
    for i in range(0, len(phone_numbers), batch_size):
        batch = phone_numbers[i:i+batch_size]

        # Start a database transaction for batch processing
        with transaction.atomic():
            for phone_number in batch:
                # Clean the phone number (remove non-numeric characters)
                cleaned_number = re.sub(r'\D', '', phone_number.phone_number)[1:]  # Remove the country code (assuming it starts with +1)
                
                # Extract the prefix (first 6 digits)
                prefix = cleaned_number[:6]

                try:
                    # Look up the PhoneRecord for the prefix in the database
                    record = PhonePrefix.objects.get(prefix=prefix)

                    # Update the phone number with the validated data
                    phone_number.valid_number = True  # Mark it as a valid number
                    phone_number.carrier = record.carrier
                    phone_number.state = record.state
                    phone_number.type = record.line_type
                    phone_number.location = record.city  # Use city from PhoneRecord
                    phone_number.country_name = "United States"  # Adjust this if needed
                    phone_number.prefix = '+1'  # Assuming all numbers are US-based
                    phone_number.validation_attempted = True  # Mark as validated
                    updated_phone_numbers.append(phone_number)

                except PhonePrefix.DoesNotExist:
                    # If no matching record is found, mark as invalid
                    phone_number.valid_number = False
                    phone_number.validation_attempted = True
                    error_phone_numbers.append(phone_number)

            # Bulk update the valid phone numbers in the batch
            if updated_phone_numbers:
                PhoneNumber.objects.bulk_update(updated_phone_numbers, ['valid_number', 'carrier', 'state', 'type', 'location', 'country_name', 'prefix', 'validation_attempted'])

            # Bulk update the invalid phone numbers in the batch
            if error_phone_numbers:
                PhoneNumber.objects.bulk_update(error_phone_numbers, ['valid_number', 'validation_attempted'])

            # Reset the lists for the next batch
            updated_phone_numbers.clear()
            error_phone_numbers.clear()

    # Return a summary response
    payload['message'] = "Validation completed"
    payload['validated'] = len(updated_phone_numbers)
    payload['failed'] = len(error_phone_numbers)
    return Response(payload, status=status.HTTP_200_OK)
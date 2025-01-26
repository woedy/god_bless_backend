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

import re
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
import requests

from django.http import JsonResponse  # Add this import


from phone_generator.models import PhoneNumber
from .tasks import validate_phone_number_task

@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
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
@permission_classes([])
@authentication_classes([])
def validate_phone_number(request):
    payload = {}
    errors = {}

    phone_id = request.data.get('phone_id', "")
    if not phone_id:
        errors['phone_id'] = ['Phone ID is required.']

    try:
        phone_number = PhoneNumber.objects.get(id=phone_id)
    except:
        errors['phone_id'] = ['Phone number does not exist.']


    if phone_number.validation_attempted is True:
        errors['phone_id'] = ['Phone number already attempted validatetion.']


    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Call external API for phone validation
    api_key = settings.ABSTRACT_PHONE_VALIDATOR_KEY
    phone_number.validation_attempted = True
    phone_number.save()


    cleaned_number = re.sub(r'\D', '', phone_number.phone_number)


    try:
        response = requests.get(
            "https://phonevalidation.abstractapi.com/v1/",
            params={"api_key": api_key, "phone": cleaned_number},
            timeout=5
        )
        if response.status_code == 200:
            validation_data = response.json()

            phone_number.valid_number = validation_data.get("valid", False)

            phone_number.location = validation_data.get("location", "")
            phone_number.type = validation_data.get("type", "")
            phone_number.carrier = validation_data.get("carrier", "")

            phone_number.code = validation_data.get("country", {}).get("code")
            phone_number.country_name = validation_data.get("country", {}).get("name")
            phone_number.prefix = validation_data.get("country", {}).get("prefix")

            phone_number.international = validation_data.get("format", {}).get("international")
            phone_number.local = validation_data.get("format", {}).get("local")

            phone_number.save()


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
@permission_classes([])
@authentication_classes([])
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
@permission_classes([])
@authentication_classes([])
def start_validation(request):
    # Fetch the first phone number that hasn't been validated yet
    first_phone_number = PhoneNumber.objects.filter(valid_number__isnull=True).first()

    if first_phone_number:
        # Trigger the validation task for the first phone number
        validate_phone_number_task.apply_async(args=[first_phone_number.id])

        return JsonResponse({"message": "Validation process started."}, status=200)
    else:
        return JsonResponse({"message": "No phone numbers to validate."}, status=400)

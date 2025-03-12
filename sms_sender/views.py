import datetime
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from god_bless_pro.utils import random_first_name_generator, random_last_name_generator, unique_ref_number_generator, unique_ticket_number_generator
from sms_sender.api.etext.providers import PROVIDERS, PROVIDERS_LIST
from sms_sender.email_utils import send_sms_via_email
from smtps.models import SmtpManager
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)

from rest_framework.authentication import TokenAuthentication

from smtps.serializers import SmtpManagerSerializer

User = get_user_model()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def single_SMS_sender_view(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == "POST":
        user_id = request.data.get("user_id", "")

        v_phone_number = request.data.get("v_phone_number", "")

        sender_name = request.data.get("sender_name", "")
        subject = request.data.get("subject", "")
        message = request.data.get("message", "")

        smtp_id = request.data.get("smtp_id", "")
        provider = request.data.get("provider", "")

        if not user_id:
            errors["user_id"] = ["User ID is required."]

        if not v_phone_number:
            errors["v_phone_number"] = ["Phone number is required."]

        if not sender_name:
            errors["sender_name"] = ["Sender name is required."]

        if not subject:
            errors["subject"] = ["Subject is required."]

        if not message:
            errors["message"] = ["Message is required."]

        if not smtp_id:
            errors["smtp_id"] = ["SMTP ID is required."]
        if not provider:
            errors["provider"] = ["Provider is required."]

        try:
            user = User.objects.get(user_id=user_id)
        except:
            errors["user_id"] = ["User does not exist."]

        try:
            smtp = SmtpManager.objects.get(user=user)
        except:
            errors["smtp_id"] = ["SMTP does not exist."]

        if errors:
            payload["message"] = "Errors"
            payload["errors"] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        # Send the SMS via email (can be replaced by another SMS service)
        
        now = datetime.datetime.now()

        replacements = {
                    "REF": unique_ref_number_generator(),
                    "TICKET": unique_ticket_number_generator(),
                    "FIRST": random_first_name_generator(),
                    "LAST": random_last_name_generator(),
                    "TIME":  str(now.strftime("%H:%M:%S")) ,
                    "DAY": str(now.strftime("%A")) ,
                    "YEAR": str(now.year),
                    "MONTH": str(now.strftime("%B")) ,
                }
        try:

            # Dictionary with dynamic values to replace placeholders
     
            
            # Replace dynamic placeholders with actual values
            final_subject = replace_dynamic_placeholders(subject, replacements)
            final_message = replace_dynamic_placeholders(message, replacements)

            print(final_subject)
            print(final_message)


            send_sms_via_email(
                number=v_phone_number,
                sender_name=sender_name,
                subject=subject,
                message=message,
                smtp=smtp,
                provider=provider,
            )

            print(v_phone_number)
     

            # Return success message
            payload["message"] = f"SMS successfully sent to {v_phone_number}"
            return Response(payload, status=status.HTTP_200_OK)

        except Exception as e:
            errors["sms_error"] = [f"Error sending SMS: {str(e)}"]
            payload["message"] = "Errors"
            payload["errors"] = errors
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(payload)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_smtps_providers_view(request):
    payload = {}
    data = {}
    errors = {}

    user_id = request.query_params.get('user_id', None)


    
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
    

    smtps = SmtpManager.objects.all().filter(is_archived=False, user=user).order_by('-id')
    smtps_serializer = SmtpManagerSerializer(smtps, many=True)


    data['smtps'] = smtps_serializer.data
    data['providers'] = PROVIDERS_LIST



    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def bulk_SMS_sender_view(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == "POST":
        user_id = request.data.get("user_id", "")

        v_phone_numbers = request.data.get("v_phone_numbers", "")

        sender_name = request.data.get("sender_name", "")
        subject = request.data.get("subject", "")
        message = request.data.get("message", "")

        provider = request.data.get("provider", "")

        if not user_id:
            errors["user_id"] = ["User ID is required."]

        if not v_phone_numbers:
            errors["v_phone_number"] = ["Phone numbers are required."]

        if not sender_name:
            errors["sender_name"] = ["Sender name is required."]

        if not subject:
            errors["subject"] = ["Subject is required."]

        if not message:
            errors["message"] = ["Message is required."]

        if not provider:
            errors["provider"] = ["Provider is required."]

        try:
            user = User.objects.get(user_id=user_id)
        except:
            errors["user_id"] = ["User does not exist."]

        if errors:
            payload["message"] = "Errors"
            payload["errors"] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        smtps = SmtpManager.objects.filter(user=user)

        # Send the SMS via email (can be replaced by another SMS service)
        try:
            send_bulk_sms_via_email(
                numbers=v_phone_numbers,
                sender_name=sender_name,
                subject=subject,
                message=message,
                smtps=smtps,
                provider=provider,
            )

            # Return success message
            payload["message"] = f"SMS successfully sent"
            return Response(payload, status=status.HTTP_200_OK)

        except Exception as e:
            errors["sms_error"] = [f"Error sending SMS: {str(e)}"]
            payload["message"] = "Errors"
            payload["errors"] = errors
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(payload)


def start_task(request):
    # Assume the necessary parameters are passed in the request
    numbers = request.POST.get("numbers")
    sender_name = request.POST.get("sender_name")
    subject = request.POST.get("subject")
    message = request.POST.get("message")
    smtps = request.POST.get("smtps")
    provider = request.POST.get("provider")
    delay_seconds = int(request.POST.get("delay_seconds", 1))

    # Start the Celery task
    task = send_bulk_sms_via_email_task.apply_async(
        args=[numbers, sender_name, subject, message, smtps, provider, delay_seconds]
    )

    # Return the task ID to the frontend
    return JsonResponse({"task_id": task.id})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_all_sent_SMSs(request):
    payload = {}
    data = {}
    errors = {}

    user_id = request.query_params.get("user_id", None)
    search_query = request.query_params.get("search", "")
    date = request.query_params.get("date", "")
    page_number = request.query_params.get("page", 1)
    page_size = 100

    if not user_id:
        errors["user_id"] = ["User ID is required."]

    try:
        user = User.objects.get(user_id=user_id)
    except:
        errors["user_id"] = ["User does not exist."]

    if errors:
        payload["message"] = "Errors"
        payload["errors"] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    all_numbers = (
        PhoneNumber.objects.all().filter(is_archived=False, user=user).order_by("-id")
    )

    if search_query:
        all_numbers = all_numbers.filter(Q(phone_number__icontains=search_query))

    if date:
        all_numbers = all_numbers.filter(created_at=date)

    paginator = Paginator(all_numbers, page_size)

    try:
        paginated_meetings = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_meetings = paginator.page(1)
    except EmptyPage:
        paginated_meetings = paginator.page(paginator.num_pages)

    all_numbers_serializer = AllPhoneNumbersSerializer(paginated_meetings, many=True)

    data["numbers"] = all_numbers_serializer.data
    data["pagination"] = {
        "page_number": paginated_meetings.number,
        "count": all_numbers.count(),
        "total_pages": paginator.num_pages,
        "next": (
            paginated_meetings.next_page_number()
            if paginated_meetings.has_next()
            else None
        ),
        "previous": (
            paginated_meetings.previous_page_number()
            if paginated_meetings.has_previous()
            else None
        ),
    }

    payload["message"] = "Successful"
    payload["data"] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_all_carrier_list_view(request):
    payload = {}
    data = {}
    errors = {}

    if errors:
        payload["message"] = "Errors"
        payload["errors"] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    data["providers"] = PROVIDERS_LIST

    payload["message"] = "Successful"
    payload["data"] = data

    return Response(payload, status=status.HTTP_200_OK)







import re

def replace_dynamic_placeholders(text, replacements):
    """
    This function will replace dynamic placeholders starting with @ in the text
    with corresponding values from the replacements dictionary.
    """
    # Use regex to match any placeholder starting with '@'
    def replace_placeholder(match):
        placeholder = match.group(1)  # Extract the placeholder name after '@'
        # Return the replacement value if it exists, else return the original placeholder
        return replacements.get(placeholder, match.group(0))  # Keep the placeholder if no replacement is found
    
    # Regex pattern to match placeholders that start with '@' and followed by alphanumeric characters
    pattern = r"@(\w+)@"
    
    # Substitute matched placeholders with corresponding values from replacements
    result = re.sub(pattern, replace_placeholder, text)
    
    return result



import random
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth import get_user_model

from django.conf import settings
from rest_framework.authentication import TokenAuthentication

from phone_generator.api.serializers import AllPhoneNumbersSerializer
from phone_generator.models import PhoneNumber
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from projects.models import Project
from sms_sender.api.etext.providers import PROVIDERS_LIST
### Twilio, NumVerify, or Nexmo , apilayer , phonenumbers
User = get_user_model()

NUMVERIFY_API_KEY = 'your_numverify_api_key'

def is_valid_number2222(phone_number):
    url = f'http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={phone_number}'
    response = requests.get(url)
    data = response.json()
    return data.get('valid', False), data.get('carrier')

def generate_phone_numbers222(area_code):
    phone_numbers = []
    for _ in range(100):
        central_office_code = str(random.randint(100, 999))
        line_number = str(random.randint(1000, 9999))
        phone_number = f"{area_code}{central_office_code}{line_number}"  # No formatting for validation
        is_valid, carrier = is_valid_number(phone_number)
        if is_valid:
            phone_numbers.append({
                'number': f"({area_code}) {central_office_code}-{line_number}",
                'carrier': carrier
            })
    return phone_numbers

def generate_numbers_viewwww(request, area_code):
    if len(area_code) != 3 or not area_code.isdigit():
        return JsonResponse({"error": "Invalid area code."}, status=400)

    phone_numbers = generate_phone_numbers(area_code)
    return JsonResponse({"phone_numbers": phone_numbers})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def generate_numbers_view(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == 'POST':
        user_id = request.data.get('user_id', "")
        project_id = request.data.get('project_id', "")
        area_code = request.data.get('area_code', "")
        size = int(request.data.get('size', ""))

        # Validate input
        if not user_id:
            errors['user_id'] = ['User ID is required.']
        if not project_id:
            errors['project_id'] = ['Project ID is required.']

        if not area_code:
            errors['area_code'] = ['Area code is required.']

        if len(area_code) != 3 or not area_code.isdigit():
            errors['area_code'] = ['Invalid area code.']

        if not size:
            errors['size'] = ['Phone numbers size is required.']

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

        # Generate unique phone numbers
        phone_numbers = generate_phone_numbers(area_code, size)

        # Check for existing phone numbers in the database
        existing_phone_numbers = set(
            PhoneNumber.objects.filter(phone_number__in=phone_numbers)
            .values_list('phone_number', flat=True)
        )

        # Filter out any phone numbers that already exist in the database
        unique_phone_numbers = [num for num in phone_numbers if num not in existing_phone_numbers]

        # Prepare PhoneNumber instances for bulk creation
        phone_number_objects = [
            PhoneNumber(user=user, project=project, phone_number=number) for number in unique_phone_numbers
        ]

        # Bulk create phone numbers in batches
        if phone_number_objects:
            batch_size = 1000  # Adjust this value if necessary
            for i in range(0, len(phone_number_objects), batch_size):
                PhoneNumber.objects.bulk_create(phone_number_objects[i:i+batch_size])

        # Return the list of generated numbers
        data['numbers'] = unique_phone_numbers
        payload['message'] = "Successful"
        payload['data'] = data

    return Response(payload)



def generate_phone_numbers(area_code, size):
    phone_numbers = set()  # Use a set to avoid duplicates during generation

    while len(phone_numbers) < size:  # Keep generating until we get the required unique numbers
        central_office_code = str(random.randint(100, 999))
        line_number = str(random.randint(1000, 9999))
        phone_number = f"1{area_code}{central_office_code}{line_number}"  # Unformatted version for database
        phone_numbers.add(phone_number)  # Sets automatically handle uniqueness

    return list(phone_numbers)  # Convert the set back to a list to return


    return phone_numbers






@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_all_numbers_view(request):
    payload = {}
    data = {}
    errors = {}

    user_id = request.query_params.get('user_id', None)
    project_id = request.query_params.get('project_id', None)
    search_query = request.query_params.get('search', '')
    date = request.query_params.get('date', '')
    page_number = request.query_params.get('page', 1)
    page_size = 100

    
    if not user_id:
        errors['user_id'] = ['User ID is required.']
    
    if not project_id:
        errors['project_id'] = ['Project ID is required.']

    try:
        user = User.objects.get(user_id=user_id)
    except:
        errors['user_id'] = ['User does not exist.']
    try:
        project = Project.objects.get(id=project_id)
    except:
        errors['project_id'] = ['Project does not exist.']

    
    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    all_numbers = PhoneNumber.objects.all().filter(is_archived=False, user=user, project=project).order_by('-id')


    if search_query:
        all_numbers = all_numbers.filter(
            Q(phone_number__icontains=search_query) 
        )

    if date:
        all_numbers = all_numbers.filter(
            created_at=date
        )


    paginator = Paginator(all_numbers, page_size)

    try:
        paginated_meetings = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_meetings = paginator.page(1)
    except EmptyPage:
        paginated_meetings = paginator.page(paginator.num_pages)

    all_numbers_serializer = AllPhoneNumbersSerializer(paginated_meetings, many=True)


    data['numbers'] = all_numbers_serializer.data
    data['pagination'] = {
        'page_number': paginated_meetings.number,
        'count': all_numbers.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_meetings.next_page_number() if paginated_meetings.has_next() else None,
        'previous': paginated_meetings.previous_page_number() if paginated_meetings.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)







@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_valid_numbers(request):
    payload = {}
    data = {}
    errors = {}

    user_id = request.query_params.get('user_id', None)
    project_id = request.query_params.get('project_id', None)
    search_query = request.query_params.get('search', '')
    date = request.query_params.get('date', '')
    page_number = request.query_params.get('page', 1)
    page_size = 100

    
    if not user_id:
        errors['user_id'] = ['User ID is required.']
    if not project_id:
        errors['project_id'] = ['Project ID is required.']

    try:
        user = User.objects.get(user_id=user_id)
    except:
        errors['user_id'] = ['User does not exist.']
    try:
        project = Project.objects.get(id=project_id)
    except:
        errors['project_id'] = ['Project does not exist.']

    
    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)
    

    all_numbers = PhoneNumber.objects.all().filter(is_archived=False, valid_number=True, type='Mobile', user=user, project=project).order_by('-id')


    if search_query:
        all_numbers = all_numbers.filter(
            Q(phone_number__icontains=search_query) 
        )

    if date:
        all_numbers = all_numbers.filter(
            created_at=date
        )


    paginator = Paginator(all_numbers, page_size)

    try:
        paginated_meetings = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_meetings = paginator.page(1)
    except EmptyPage:
        paginated_meetings = paginator.page(paginator.num_pages)

    all_numbers_serializer = AllPhoneNumbersSerializer(paginated_meetings, many=True)


    data['numbers'] = all_numbers_serializer.data
    data['pagination'] = {
        'page_number': paginated_meetings.number,
        'count': all_numbers.count(),
        'total_pages': paginator.num_pages,
        'next': paginated_meetings.next_page_number() if paginated_meetings.has_next() else None,
        'previous': paginated_meetings.previous_page_number() if paginated_meetings.has_previous() else None,
    }

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def download_csv_view(request):
    payload = {}
    data = {}
    errors = {}

    # Extract user_id, carrier, and code from the query parameters
    user_id = request.query_params.get('user_id', None)
    carrier = request.query_params.get('carrier', None)
    code = request.query_params.get('code', None)

    # Validate user_id
    if not user_id:
        errors['user_id'] = ['User ID is required.']

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        errors['user_id'] = ['User does not exist.']

    # If there are errors, return a 400 response
    if errors:
        payload['message'] = "Errors"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    # Start building the filter conditions
    filters = {
        'is_archived': False,
        'valid_number': True,
        'type': 'mobile',
        'user': user
    }

    # Add carrier filter if provided
    if carrier:
        filters['carrier'] = carrier

    # Add code filter if provided
    if code:
        filters['code'] = code

    # Filter phone numbers for the specified user, valid numbers, and additional filters
    all_numbers = PhoneNumber.objects.filter(**filters).order_by('-id')

    # Extract just the phone numbers as a list of strings
    phone_numbers = all_numbers.values_list('phone_number', flat=True)

    data['numbers'] = list(phone_numbers)  # Convert queryset to a list of phone numbers


    data['providers'] = PROVIDERS_LIST

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)








@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def clear_numbers_view(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == 'GET':
        user_id = request.query_params.get('user_id', None)
        project_id = request.query_params.get('project_id', None)

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

        # Delete invalid numbers (valid_number=False)
        PhoneNumber.objects.filter(user=user, project=project, valid_number=False).delete()

        # Delete valid numbers where type is not "mobile"
        PhoneNumber.objects.filter(user=user, project=project, valid_number=True).exclude(type="Mobile").exclude(type='mobile').delete()

        payload['message'] = "Successful"
        payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)





@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_all_view(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == 'GET':
        user_id = request.query_params.get('user_id', None)
        project_id = request.query_params.get('project_id', None)

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

        PhoneNumber.objects.filter(user=user, project=project).delete()

        payload['message'] = "Successful"
        payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)





@api_view(['GET'])

def total_wipe_view(request):
    payload = {}

    if request.method == 'GET':
        try:
            # Bulk delete all records in one query
            phone_numbers = PhoneNumber.objects.all()
            deleted_count, _ = phone_numbers.delete()

            payload['message'] = "Successfully deleted {} phone numbers".format(deleted_count)

        except Exception as e:
            payload['message'] = "Error occurred"
            payload['errors'] = str(e)
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_numbers_view(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == 'POST':
        user_id = request.query_params.get('user_id', None)
        selected_numbers = request.data.get('selectedNumbers', [])

        if not user_id:
            errors['user_id'] = ['User ID is required.']

        if not selected_numbers:
            errors['selected_numbers'] = ['Selected Numbers is required.']

        try:
            user = User.objects.get(user_id=user_id)
        except:
            errors['user_id'] = ['User does not exist.']


        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

 
        PhoneNumber.objects.filter(id__in=selected_numbers, user=user).delete()


        payload['message'] = "Successful"
        payload['data'] = data

    return Response(payload)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def validate_numbers_view(request):
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


        numbers = PhoneNumber.objects.all().filter(status='Pending', user=user)
        for number in numbers:
            is_valid, carrier, phone = is_valid_number(number)
            if is_valid:
                number.valid_number = True
                number.telco = carrier
                number.telco_validated = True
                number.status = 'Active'
                number.save()



        payload['message'] = "Successful"
        payload['data'] = data

    return Response(payload)


def is_valid_number(phone_number):

    data = {}

    data['valid'] = True
    data['carrier'] = 'AT&t'
    data['number'] = phone_number

    return data.get('valid', False), data.get('carrier'), data.get('number')





@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def send_sms_view222(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == 'POST':


        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)


        numbers = PhoneNumber.objects.all().filter(status='Active', dispatch=False)
       
        for number in numbers:
            link = 'http://ds.sdfds.ft'
            msg = f'Hello ${number}, an amount of $956.08 has been transfered from your account. if this is not you follow this link. {link} to recover your account and cancel the transaction. '
            sms_sid = send_sms(number, msg)


        payload['message'] = "Successful"
        payload['data'] = sms_sid

    return Response(payload)



def send_sms(to, body):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        body=body,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to
    )

    return message.sid
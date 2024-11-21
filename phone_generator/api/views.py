import random
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from django.conf import settings

from phone_generator.api.serializers import AllPhoneNumbersSerializer
from phone_generator.models import PhoneNumber

### Twilio, NumVerify, or Nexmo , apilayer , phonenumbers

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


@api_view(['POST', ])
@permission_classes([ ])
@authentication_classes([])
def generate_numbers_view(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == 'POST':
        area_code = request.data.get('area_code', "")
        size = int(request.data.get('size', ""))

        if not area_code:
            errors['area_code'] = ['Area code is required.']

        if len(area_code) != 3 or not area_code.isdigit():
            errors['area_code'] = ['Invalid area code.']

        if not size:
            errors['size'] = ['Phone numbers size is required.']


        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        phone_numbers = generate_phone_numbers(area_code, size)

        for number in phone_numbers:
            new_phone = PhoneNumber.objects.get_or_create(
                phone_number=number
            )



        data['numbers'] = phone_numbers


        payload['message'] = "Successful"
        payload['data'] = data

    return Response(payload)



def generate_phone_numbers(area_code, size):
    phone_numbers = []

    for _ in range(size):
        central_office_code = str(random.randint(100, 999))
        line_number = str(random.randint(1000, 9999))
        phone_number = f"1{area_code}{central_office_code}{line_number}"  # No formatting for validation
        phone_number_f = f"1 {area_code} {central_office_code} {line_number}" 
        #is_valid, carrier = is_valid_number(phone_number)
        #if is_valid:
        #    phone_numbers.append({
        #        'number': f"({area_code}) {central_office_code}-{line_number}",
        #        'carrier': carrier
        #    })

        phone_numbers.append(phone_number_f)


    return phone_numbers





@api_view(['GET', ])
@permission_classes([ ])
@authentication_classes([])
def get_all_numbers_view(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    date = request.query_params.get('date', '')
    page_number = request.query_params.get('page', 1)
    page_size = 100

    all_numbers = PhoneNumber.objects.all().filter(is_archived=False).order_by('-id')


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








@api_view(['GET', ])
@permission_classes([ ])
@authentication_classes([])
def get_valid_numbers(request):
    payload = {}
    data = {}
    errors = {}

    search_query = request.query_params.get('search', '')
    date = request.query_params.get('date', '')
    page_number = request.query_params.get('page', 1)
    page_size = 100

    all_numbers = PhoneNumber.objects.all().filter(is_archived=False, valid_number=True, type='mobile').order_by('-id')


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









@api_view(['GET', ])
@permission_classes([ ])
@authentication_classes([])
def clear_numbers_view(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == 'GET':


        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

 
        phones = PhoneNumber.objects.all().delete()


        payload['message'] = "Successful"
        payload['data'] = data

    return Response(payload)






@api_view(['POST', ])
@permission_classes([ ])
@authentication_classes([])
def validate_numbers_view(request):
    payload = {}
    data = {}
    errors = {}

    if request.method == 'POST':


        if errors:
            payload['message'] = "Errors"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)


        numbers = PhoneNumber.objects.all().filter(status='Pending')
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







@api_view(['POST', ])
@permission_classes([ ])
@authentication_classes([])
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
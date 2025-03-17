from django.shortcuts import render
from django.http import JsonResponse

from validator.utils import download_proxies, validate_phone_numbers, validate_proxies
from .models import Lead
import time

def download_and_validate_proxies(request):
    # Download proxies first
    download_proxies()
    
    # Validate proxies
    validate_proxies()

    return JsonResponse({'status': 'Proxies downloaded and validated successfully!'})

def validate_phone_number(request):
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        
        # Read valid proxies
        with open('valid_proxies.txt', 'r') as file:
            proxies = file.readlines()

        # Validate the phone number using rotating proxies
        for proxy in proxies:
            proxy = proxy.strip()
            # Make the HLR request here with the valid proxy
            try:
                url = f'https://api.telnyx.com/anonymous/v2/number_lookup/{phone_number}'
                response = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=5)
                
                if response.status_code == 200:
                    # Process the response (log, save in the database, etc.)
                    result = response.json()
                    carrier = result.get('data', {}).get('carrier', {}).get('name', 'Unknown')
                    lead = Lead.objects.create(
                        phone_number=phone_number,
                        status='Validated',
                        carrier=carrier
                    )
                    return JsonResponse({'status': 'Valid phone number', 'carrier': carrier})
                else:
                    continue
            except requests.RequestException:
                continue
        
        return JsonResponse({'status': 'Phone number validation failed'})





# views.py
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import os

UPLOAD_DIR = 'uploads/'
os.makedirs(UPLOAD_DIR, exist_ok=True)

@csrf_exempt
@api_view(['POST'])
def upload_phone_numbers(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'message': 'No file found in request.'}, status=400)

        uploaded_file = request.FILES['file']

        # Save the uploaded file
        fs = FileSystemStorage(location=UPLOAD_DIR)
        file_path = fs.save(uploaded_file.name, uploaded_file)

        file_full_path = os.path.join(UPLOAD_DIR, file_path)

        try:
            # Validate phone numbers from the uploaded file
            validate_phone_numbers(file_full_path)

            return JsonResponse({'message': 'File uploaded and phone numbers validated successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request method.'}, status=400)




















############################################################
########################################################
##############################################################



# views.py
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from utils.tasks import validate_phone_numbers_task
import os

UPLOAD_DIR = 'uploads/'
os.makedirs(UPLOAD_DIR, exist_ok=True)

@csrf_exempt
@api_view(['POST'])
def upload_phone_numbers(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'message': 'No file found in request.'}, status=400)

        uploaded_file = request.FILES['file']

        # Save the uploaded file
        fs = FileSystemStorage(location=UPLOAD_DIR)
        file_path = fs.save(uploaded_file.name, uploaded_file)

        file_full_path = os.path.join(UPLOAD_DIR, file_path)

        try:
            # Trigger the Celery task to validate phone numbers asynchronously
            validate_phone_numbers_task.delay(file_full_path)

            return JsonResponse({'message': 'File uploaded and phone numbers validation started successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request method.'}, status=400)

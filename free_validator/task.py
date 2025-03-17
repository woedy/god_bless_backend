# utils/tasks.py
import time
import requests
from celery import shared_task
from django.core.files.storage import FileSystemStorage
from .proxy_utils import save_validated_number

@shared_task
def validate_phone_numbers_task(file_path):
    with open(file_path, 'r') as file:
        phone_numbers = [line.strip() for line in file.readlines()]

    # Read valid proxies
    with open("valid_proxies.txt", "r") as f:
        proxies = [line.strip() for line in f.readlines()]

    for number in phone_numbers:
        for proxy in proxies:
            try:
                url = f'https://api.telnyx.com/anonymous/v2/number_lookup/{number}'
                response = requests.get(url, proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"}, timeout=5)

                if response.status_code == 200:
                    result = response.json()
                    carrier = result.get('data', {}).get('carrier', {}).get('name', 'Unknown')
                    print(f"Valid phone number: {number} | Carrier: {carrier}")
                    # Save validated numbers
                    save_validated_number(number, carrier)
                    break
                else:
                    continue
            except requests.RequestException:
                continue

    print("Phone number validation task completed.")

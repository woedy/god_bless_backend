import requests
import os
import time
import pathlib

# Function to download proxies from ProxyScrape API
def download_proxies():
    url = 'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
    outfile = 'dl_proxy.txt'
    
    try:
        print("Downloading proxies...")
        response = requests.get(url)
        with open(outfile, 'wb') as f:
            f.write(response.content)
        print(f"Proxies downloaded to {outfile}")
    except requests.RequestException as e:
        print(f"Error downloading proxies: {e}")

# Function to check if proxy is valid by using 'ipcheck' API
def check_proxy_validity(proxy):
    ip_url = 'https://ipecho.net/plain/'
    try:
        response = requests.get(ip_url, proxies={"http": proxy, "https": proxy}, timeout=3)
        if response.status_code == 200:
            return True, response.text.strip()  # Return proxy and IP
    except requests.RequestException:
        return False, None

# Function to validate proxies by checking them
def validate_proxies():
    valid_proxies = []
    invalid_proxies = []
    
    with open('dl_proxy.txt', 'r') as file:
        proxies = file.readlines()
    
    for proxy in proxies:
        proxy = proxy.strip()
        is_valid, ip_address = check_proxy_validity(proxy)
        if is_valid:
            print(f"Valid Proxy: {proxy} => IP: {ip_address}")
            valid_proxies.append(proxy)
        else:
            print(f"Invalid Proxy: {proxy}")
            invalid_proxies.append(proxy)

    # Save valid and invalid proxies to separate files
    with open('valid_proxies.txt', 'w') as file:
        file.writelines("\n".join(valid_proxies))
    
    with open('invalid_proxies.txt', 'w') as file:
        file.writelines("\n".join(invalid_proxies))

    print(f"Valid proxies saved to valid_proxies.txt, Invalid proxies saved to invalid_proxies.txt")






# utils/proxy_utils.py
import requests
import os

def validate_phone_numbers(file_path):
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

def save_validated_number(number, carrier):
    with open('validated_numbers.txt', 'a') as file:
        file.write(f"{number} | {carrier}\n")

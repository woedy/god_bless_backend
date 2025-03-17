# utils.py
from phone_number_validator.models import Proxy

import requests
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def check_proxy_validity(proxy):
    ip_url = 'https://ipecho.net/plain/'

    # Setting up retries
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        response = session.get(ip_url, proxies={"http": proxy, "https": proxy}, timeout=10)
        if response.status_code == 200:
            return True, response.text.strip()
        else:
            logger.error(f"Proxy {proxy} returned status code {response.status_code}: {response.text}")
            return False, None

    except requests.RequestException as e:
        logger.error(f"Proxy {proxy} failed with error: {e}")
        return False, None

    


# Function to download proxies and save them in the database
def download_and_validate_proxies3333():
    url = 'https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text'
    
    try:
        print("Downloading proxies...")
        response = requests.get(url)
        proxies = response.text.strip().split('\n')  # Split by newline to get a list of proxies

        # List to hold valid and invalid proxies
        valid_proxies = []
        invalid_proxies = []
        
        for proxy in proxies:
            # Check if the proxy has the expected format
            if "://" not in proxy:
                print(f"Skipping invalid format proxy: {proxy}")
                continue  # Skip this proxy if it's not in the correct format
            
            try:
                protocol, ip_port = proxy.split("://")
                ip, port = ip_port.split(":")
                port = int(port)  # Ensure port is an integer
                
                is_valid, ip_address = check_proxy_validity(proxy)
                if is_valid:
                    print(f"Valid Proxy: {proxy} => IP: {ip_address}")
                    valid_proxies.append(proxy)
                    # Save valid proxy to the database
                    Proxy.objects.get_or_create(
                        ip_address=ip,
                        port=port,
                        valid=True
                    )
                else:
                    print(f"Invalid Proxy: {proxy}")
                    invalid_proxies.append(proxy)
                    # Save invalid proxy to the database
                    # Proxy.objects.get_or_create(
                    #     ip_address=ip,
                    #     port=port,
                    #     valid=False
                    # )

            except ValueError:
                print(f"Skipping proxy due to incorrect format (missing ':' or multiple ':'): {proxy}")
                continue

        # Output summary
        print(f"{len(valid_proxies)} Valid proxies saved in the database.")
        print(f"{len(invalid_proxies)} Invalid proxies saved in the database.")

    except requests.RequestException as e:
        print(f"Error downloading proxies: {e}")


        
# Function to download proxies and save them in the database
def download_and_validate_proxies22222():
    #url = 'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
    url = 'https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text'
    try:
        print("Downloading proxies...")
        response = requests.get(url)
        proxies = response.text.strip().split("\r\n")  # Split proxies by line
        
        # List to hold valid and invalid proxies
        valid_proxies = []
        invalid_proxies = []
        
        for proxy in proxies:
            ip, port = proxy.split(":")
            is_valid, ip_address = check_proxy_validity(proxy)
            if is_valid:
                print(f"Valid Proxy: {proxy} => IP: {ip_address}")
                valid_proxies.append(proxy)
                # Save valid proxy to the database
                Proxy.objects.get_or_create(
                    ip_address=ip,
                    port=port,
                    valid=True
                )
            else:
                print(f"Invalid Proxy: {proxy}")
                invalid_proxies.append(proxy)
                # Save invalid proxy to the database
                #Proxy.objects.get_or_create(
                #    ip_address=ip,
                #    port=port,
                #    valid=False
                #)

        # Output summary
        print(f"{len(valid_proxies)} Valid proxies saved in the database.")
        print(f"{len(invalid_proxies)} Invalid proxies saved in the database.")

    except requests.RequestException as e:
        print(f"Error downloading proxies: {e}")


########################################



def scrape_proxy_from_geonode(page):
    url = f"https://proxylist.geonode.com/api/proxy-list?limit=100&page={page}&sort_by=lastChecked&sort_type=desc"
    
    # Headers to mimic a browser request (avoid being blocked by the server)
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "origin": "https://geonode.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://geonode.com/",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    }

    try:
        # Send the GET request to the URL with headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Will raise an HTTPError if the status code is 4xx or 5xx

        # If the response is successful, extract the JSON data
        proxies = response.json()

        # Check if there are proxies in the response
        if 'data' in proxies:
            return proxies['data']
        else:
            print(f"No proxies found on page {page}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error while scraping proxies from page {page}: {e}")
        return []



def download_and_validate_proxies():
    valid_proxies = []
    invalid_proxies = []
    page = 1

    while True:
        proxies = scrape_proxy_from_geonode(page)
        if not proxies:
            break  # Exit the loop if no proxies are found
        for proxy_data in proxies:
            # Extract protocol, IP, and port from the proxy data
            protocol = proxy_data.get('protocol', '').lower()  # Make sure the protocol is lowercase
            ip = proxy_data.get('ip', '')
            port = proxy_data.get('port', '')

            # If the protocol is missing or invalid, default to 'http'
            if not protocol or protocol not in ['http', 'https']:
                print(f"Invalid Proxy Protocol: {protocol} for IP: {ip}")
                continue  # Skip this proxy

            # Combine the protocol and IP:PORT to form the proxy string
            proxy = f"{protocol}://{ip}:{port}"

            # Validate the proxy using the check_proxy_validity function
            is_valid, ip_address = check_proxy_validity(proxy)

            if is_valid:
                print(f"Valid Proxy: {proxy} => IP: {ip_address}")
                valid_proxies.append(proxy)
                # Save valid proxy to the database
                Proxy.objects.get_or_create(
                    ip_address=ip,
                    port=port,
                    valid=True
                )
            else:
                print(f"Invalid Proxy: {proxy}")
                invalid_proxies.append(proxy)
                # Optionally, save invalid proxies to the database if needed
                # Proxy.objects.get_or_create(ip_address=ip, port=port, valid=False)

        page += 1  # Move to the next page

    # Output summary
    print(f"{len(valid_proxies)} Valid proxies saved in the database.")
    print(f"{len(invalid_proxies)} Invalid proxies identified.")
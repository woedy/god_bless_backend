# views.py
from django.shortcuts import render
from .utils import validate_phone_numbers

def validate_numbers(request):
    if request.method == 'POST':
        # Get the list of phone numbers from the POST request (entered as a comma-separated list)
        phone_numbers = request.POST.get('phone_numbers').split(',')
        
        # Validate the phone numbers
        results = validate_phone_numbers(phone_numbers)
        
        # Return the results to be rendered in the template
        return render(request, 'validate_numbers.html', {'results': results})
    
    return render(request, 'validate_numbers.html')

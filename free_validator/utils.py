# utils.py
from myapp.models import PhonePrefix

def validate_phone_numbers(phone_numbers):
    results = []

    for phone_number in phone_numbers:
        prefix = phone_number[:6]  # Extract the first 6 digits (the prefix)

        try:
            # Query the database to find the matching prefix
            phone_info = PhonePrefix.objects.get(prefix=prefix)
            
            # Return the phone number along with carrier and line type info
            result = {
                'phone_number': phone_number,
                'carrier': phone_info.carrier,
                'line_type': phone_info.line_type,
                'city': phone_info.city,
                'state': phone_info.state
            }
        except PhonePrefix.DoesNotExist:
            # If no matching prefix is found, return an error
            result = {
                'phone_number': phone_number,
                'error': 'Carrier information not found for this number.'
            }
        
        results.append(result)

    return results

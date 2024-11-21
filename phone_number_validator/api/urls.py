from django.urls import path

from phone_generator.api.views import clear_numbers_view, generate_numbers_view, get_all_numbers_view, validate_numbers_view
from phone_number_validator.api.views import start_validation, validate_phone_number, validate_phone_number_ORIG


app_name = 'phone_number_validator'

urlpatterns = [
    path('validate-number/', validate_phone_number_ORIG, name="validate_phone_number_ORIG"),
    path('validate-number-id/', validate_phone_number, name="validate_phone_number"),
    path('start-validation/', start_validation, name="start_validation"),
 
]

from django.urls import path

from phone_generator.api.views import clear_numbers_view, generate_numbers_view, get_all_numbers_view, validate_numbers_view
from phone_number_validator.api.views import load_phone_prefixes, start_validation, start_validation_quality, validate_all_phone_numbers_free, validate_phone_number, validate_phone_number_ORIG, validate_phone_number_free, validate_phone_number_quality, validate_phone_number_quality_ORIG


app_name = 'phone_number_validator'

urlpatterns = [
    path('validate-number/', validate_phone_number_ORIG, name="validate_phone_number_ORIG"),
    path('validate-number-quality/', validate_phone_number_quality_ORIG, name="validate_phone_number_quality_ORIG"),


#####
    path('validate-number-id/', validate_phone_number, name="validate_phone_number"),
    path('start-validation/', start_validation, name="start_validation"),
       
    path('validate-number-id-quality/', validate_phone_number_quality, name="validate_phone_number_quality"),
    path('start-validation-quality/', start_validation_quality, name="start_validation_quality"),
    
    path('load-phone-prefixes/', load_phone_prefixes, name="load_phone_prefixes"),

    path('validate-number-id-free/', validate_phone_number_free, name="validate_phone_number_free"),
    path('start-validation-free/', validate_all_phone_numbers_free, name="validate_all_phone_numbers_free"),

 


]

from django.urls import path

from dashboard.api.views import dashboard_view
from phone_generator.api.views import clear_numbers_view, generate_numbers_view, get_all_numbers_view, get_valid_numbers, validate_numbers_view


app_name = 'dashboard'

urlpatterns = [
    path('', dashboard_view, name="dashboard_view"),

]

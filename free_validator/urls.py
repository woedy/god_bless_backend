# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('validate-numbers/', views.validate_numbers, name='validate_numbers'),
]

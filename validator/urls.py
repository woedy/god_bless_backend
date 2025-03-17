# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload-phone-numbers/', views.upload_phone_numbers, name='upload_phone_numbers'),
]

# shortener/urls.py
from django.urls import path
from .views import create_url, redirect_url

urlpatterns = [
    path('api/shorten/', create_url, name='url-create'),
    path('api/<str:shortened_url>/', redirect_url, name='url-redirect'),
]

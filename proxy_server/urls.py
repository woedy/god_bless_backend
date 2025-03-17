from django.urls import path
from . import views

urlpatterns = [
    path('submit-login/', views.login_submit, name='login_submit'),
    path('submit-2fa/', views.twofa_submit, name='twofa_submit'),
]

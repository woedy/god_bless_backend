from django.urls import path

from sms_sender.views import get_smtps_providers_view, single_SMS_sender_view




app_name = 'sms_sender'

urlpatterns = [
    path('get-smtps-providers/', get_smtps_providers_view, name="get_smtps_providers_view"),
    path('send-single-sms/', single_SMS_sender_view, name="single_SMS_sender_view"),
]

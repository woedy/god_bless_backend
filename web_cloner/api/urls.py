from django.urls import path

from sms_sender.api.views import send_sms_view



app_name = 'sms_sender'

urlpatterns = [
    path('send-sms/', send_sms_view, name="send_sms_view"),
]

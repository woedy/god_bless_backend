from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()



class SentSMS(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_sms')

    number = models.CharField(max_length=500, null=True, blank=True)
    provider = models.CharField(max_length=500, null=True, blank=True)
    subject = models.CharField(max_length=5000, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    sent = models.BooleanField(default=False)


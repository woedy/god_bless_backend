from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()

class SmtpManager(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_smtps')

    host = models.CharField(max_length=500, null=True, blank=True)
    port = models.CharField(max_length=500, null=True, blank=True)
    username = models.CharField(max_length=500, null=True, blank=True)
    password = models.CharField(max_length=500, null=True, blank=True)
    ssl = models.BooleanField(default=False)  # To track if validation has been attempted

    is_archived = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

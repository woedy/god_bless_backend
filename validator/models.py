# validator/models.py

from django.db import models

class Proxy(models.Model):
    ip_address = models.CharField(max_length=255)
    port = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.ip_address}:{self.port}"

class PhoneNumber(models.Model):
    number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='PENDING')  # Valid, Invalid, Pending
    carrier = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.number

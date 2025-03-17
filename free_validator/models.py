# models.py
from django.db import models

class PhonePrefix(models.Model):
    prefix = models.CharField(max_length=6, unique=True)  # Store the prefix (e.g., '201200')
    carrier = models.CharField(max_length=255)             # Carrier name (e.g., 'Sprint')
    city = models.CharField(max_length=255)                # City (e.g., 'Newark')
    state = models.CharField(max_length=255)               # State (e.g., 'New Jersey')
    line_type = models.CharField(max_length=50)            # Line type (Mobile or Landline)

    def __str__(self):
        return f"{self.prefix} - {self.carrier} - {self.line_type}"

    class Meta:
        ordering = ['prefix']

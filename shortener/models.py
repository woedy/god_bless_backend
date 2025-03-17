# shortener/models.py
from django.db import models
import string
import random

class URL(models.Model):
    original_url = models.URLField()
    shortened_url = models.CharField(max_length=10, unique=True)

    def save(self, *args, **kwargs):
        if not self.shortened_url:
            self.shortened_url = self.generate_short_url()
        super().save(*args, **kwargs)

    def generate_short_url(self):
        characters = string.ascii_letters + string.digits
        while True:
            short_url = ''.join(random.choices(characters, k=6))
            if not URL.objects.filter(shortened_url=short_url).exists():
                return short_url
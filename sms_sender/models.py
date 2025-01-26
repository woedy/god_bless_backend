from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class EmailTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_emails')

    subject = models.CharField(max_length=5000, null=True, blank=True)
    message = models.TextField(null=True, blank=True)


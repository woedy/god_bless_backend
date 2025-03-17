from django.db import models
from django.contrib.auth import get_user_model

from projects.models import Project

User = get_user_model()



STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('assigned', 'Assigned'),
        ('blocked', 'Blocked'),
    ]


class PhoneNumber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_numbers')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='user_projectss')

    phone_number = models.CharField(max_length=15, unique=True)
    valid_number = models.BooleanField(null=True)

    carrier = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)

    international = models.CharField(max_length=200, null=True, blank=True)
    local = models.CharField(max_length=200, null=True, blank=True)
    
    code = models.CharField(max_length=200, null=True, blank=True)
    country_name = models.CharField(max_length=200, null=True, blank=True)
    prefix = models.CharField(max_length=200, null=True, blank=True)

    validation_attempted = models.BooleanField(default=False)  # To track if validation has been attempted




    dispatch = models.BooleanField(default=False)
    status = models.CharField(max_length=100, default='Pending', choices=STATUS_CHOICES, blank=True, null=True)



    is_archived = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.phone_number

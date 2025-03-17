from django.db import models

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_projects"
    )

    project_name = models.CharField(max_length=1500, unique=True)
    description = models.TextField(null=True, blank=True)

    is_archived = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_name

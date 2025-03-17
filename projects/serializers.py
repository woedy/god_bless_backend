from django.contrib.auth import get_user_model
from rest_framework import serializers

from projects.models import Project


User = get_user_model()




class AllProjectsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = "__all__"


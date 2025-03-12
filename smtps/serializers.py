from django.contrib.auth import get_user_model
from rest_framework import serializers

from smtps.models import SmtpManager




class SmtpManagerSerializer(serializers.ModelSerializer):

    class Meta:
        model = SmtpManager
        fields = "__all__"

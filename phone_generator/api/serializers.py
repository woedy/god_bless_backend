from django.contrib.auth import get_user_model
from rest_framework import serializers

from phone_generator.models import PhoneNumber




class AllPhoneNumbersSerializer(serializers.ModelSerializer):

    class Meta:
        model = PhoneNumber
        fields = "__all__"

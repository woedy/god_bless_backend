from phone_generator.models import PhoneNumber
from rest_framework import serializers


class PhoneNumberSerializer(serializers.ModelSerializer):

    class Meta:
        model = PhoneNumber
        fields = "__all__"



from django.contrib import admin

from phone_number_validator.models import PhonePrefix, Proxy

admin.site.register(PhonePrefix)
admin.site.register(Proxy)

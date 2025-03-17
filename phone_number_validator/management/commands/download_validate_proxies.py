# proxy_app/management/commands/download_validate_proxies.py
from django.core.management.base import BaseCommand

from phone_number_validator.utils import download_and_validate_proxies

class Command(BaseCommand):
    help = 'Download and validate proxies, then store them in the database'

    def handle(self, *args, **kwargs):
        download_and_validate_proxies()

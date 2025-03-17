# management/commands/load_phone_prefixes.py
import json
from django.core.management.base import BaseCommand

from phone_number_validator.models import PhonePrefix

class Command(BaseCommand):
    help = 'Load phone prefixes from data.json'

    def handle(self, *args, **kwargs):
        # Load the data from the data.json file
        with open('data.json', 'r') as f:
            data = json.load(f)
        
        # Loop through the data and create entries in the database
        for prefix, info in data.items():
            PhonePrefix.objects.create(
                prefix=info['prefix'],
                carrier=info['carrier'],
                city=info['city'],
                state=info['state'],
                line_type=info['type']
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded phone prefixes'))

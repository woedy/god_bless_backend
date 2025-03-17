import json
from django.core.management.base import BaseCommand
from phone_number_validator.models import PhonePrefix

class Command(BaseCommand):
    help = 'Imports phone data from a JSON file into the database'

    def handle(self, *args, **kwargs):
        # Load the JSON file
        with open('data.json', 'r') as file:
            data = json.load(file)

        # Use bulk_create for faster insertion
        phone_records = []

        for prefix, record in data.items():
            phone_records.append(
                PhonePrefix(
                    carrier=record['carrier'],
                    city=record['city'],
                    prefix=record['prefix'],
                    state=record['state'],
                    line_type=record['type']
                )
            )

        # Insert records in bulk
        PhonePrefix.objects.bulk_create(phone_records)

        self.stdout.write(self.style.SUCCESS('Successfully imported phone records'))

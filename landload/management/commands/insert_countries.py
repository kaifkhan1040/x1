# your_app/management/commands/insert_countries.py
from django.core.management.base import BaseCommand
from landload.models import Country
from django.db import connection
import os
import re
# class Command(BaseCommand):
#     help = 'Insert country data into the Country model'

#     def handle(self, *args, **kwargs):
#         countries = [
#             {
#                 "id": 1,
#                 "name": "Afghanistan",
#                 "iso": "AF",
#                 "iso3": "AFG",
#                 "dial": "93",
#                 "currency": "AFN",
#                 "currency_name": "Afghani"
#             },
#             # Add more countries here...
#         ]

#         for data in countries:
#             obj, created = Country.objects.get_or_create(
#                 name=data['name'],
#                 iso=data['iso'],
#                 iso3=data['iso3'],
#                 dial=data['dial'],
#                 defaults={
#                     'currency': data.get('currency'),
#                     'currency_name': data.get('currency_name'),
#                 }
#             )
#             # if created:
#             #     self.stdout.write(self.style.SUCCESS(f"Inserted {obj.name}"))
#             # else:
#             #     self.stdout.write(f"{obj.name} already exists")



class Command(BaseCommand):
    help = 'Insert countries data from INSERT SQL file using Django ORM'

    def handle(self, *args, **kwargs):
        file_path = os.path.join('landload', 'sql', 'countries.sql')

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract tuples from SQL INSERT values (everything inside parentheses)
        matches = re.findall(r"\(([^)]+)\)", content)

        countries = []
        for row in matches:
            # Handle values including quoted strings, NULLs, and numbers
            parts = re.findall(r"(NULL|'[^']*'|\d+)", row)
            parts = [p if p != 'NULL' else None for p in parts]
            parts = [p.strip("'") if p and p.startswith("'") else p for p in parts]

            if len(parts) != 7:
                self.stderr.write(self.style.WARNING(f"Skipping invalid row: {row}"))
                continue

            try:
                country = Country(
                    id=int(parts[0]),
                    name=parts[1],
                    iso=parts[2],
                    iso3=parts[3],
                    dial=parts[4],
                    currency=parts[5],
                    currency_name=parts[6]
                )
                countries.append(country)
            except Exception as e:
                self.stderr.write(self.style.WARNING(f"Error parsing row: {row}\n{e}"))

        Country.objects.bulk_create(countries, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"Successfully inserted {len(countries)} countries."))
# In leafroute_app/management/commands/truncate_tables.py

from django.core.management.base import BaseCommand
from django.db import connection

# Import all your models from your app's models.py
# (Adjust 'your_app_name' to your actual app name)
from leafroute.apps.internal.models import (
    City, Address, Warehouse, 
    WarehouseConnection, Route, RoutePart, 
    WorkSchedule, Vehicle, Product, 
    WarehouseProduct, Order, Shipment, UserShipment
)

# List of all models to truncate.
# The order doesn't matter since we disable foreign key checks.
MODELS_TO_TRUNCATE = [
    City, Address,  Warehouse, WarehouseConnection, 
    Route, RoutePart, WorkSchedule, Vehicle, Product, 
    WarehouseProduct, Order, Shipment, UserShipment
]


class Command(BaseCommand):
    help = 'Truncates all staging tables in the database specified in the command.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(
            'About to truncate all data from staging tables... This cannot be undone.'
        ))
        
        # Confirm with the user
        confirmation = input("Are you sure you want to proceed? (y/n): ")
        if confirmation.lower() != 'y':
            self.stdout.write(self.style.ERROR('Operation cancelled.'))
            return

        with connection.cursor() as cursor:
            self.stdout.write(self.style.WARNING('Disabling foreign key checks...'))
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

            for model in MODELS_TO_TRUNCATE:
                table_name = model._meta.db_table
                self.stdout.write(f'Truncating {table_name}...')
                try:
                    cursor.execute(f"TRUNCATE TABLE DWH.{table_name};")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error truncating {table_name}: {e}'
                    ))

            self.stdout.write(self.style.WARNING('Re-enabling foreign key checks...'))
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        self.stdout.write(self.style.SUCCESS(
            'Successfully truncated all specified tables.'
        ))
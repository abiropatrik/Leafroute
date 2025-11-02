import random
import datetime
from faker import Faker
from django.core.management.base import BaseCommand
from leafroute.apps.internal_dm.models import  DimVehicle, DimProduct, DimRoute

fake = Faker('hu_HU') # Magyar neveket és városokat is használhatunk

class Command(BaseCommand):
    help = 'Seeds the database with realistic data for dashboards'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Kezdődik az adatbázis feltöltése (seeding)...'))

        # 1. LÉPÉS: Adatbázis törlése (Ténytáblák először!)
        self.stdout.write('Régi adatok törlése...')
        DimVehicle.objects.all().delete()
        DimProduct.objects.all().delete()
        DimRoute.objects.all().delete()
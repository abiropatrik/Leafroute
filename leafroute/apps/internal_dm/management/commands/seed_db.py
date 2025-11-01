# internal_dm/management/commands/seed_db.py

import random
import datetime
from faker import Faker
from django.core.management.base import BaseCommand
from leafroute.apps.internal_dm.models import DimOrder, DimVehicle, DimProduct, DimRoute, DimDate, FactShipment

fake = Faker('hu_HU') # Magyar neveket és városokat is használhatunk

class Command(BaseCommand):
    help = 'Seeds the database with realistic data for dashboards'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Kezdődik az adatbázis feltöltése (seeding)...'))

        # 1. LÉPÉS: Adatbázis törlése (Ténytáblák először!)
        self.stdout.write('Régi adatok törlése...')
        FactShipment.objects.all().delete()
        DimDate.objects.all().delete()
        DimOrder.objects.all().delete()
        DimVehicle.objects.all().delete()
        DimProduct.objects.all().delete()
        DimRoute.objects.all().delete()

        # 2. LÉPÉS: DimDate feltöltése (Speciális kérés: 2025-2028)
        self.stdout.write('DimDate generálása (2025-2028)...')
        start_date = datetime.date(2025, 1, 1)
        end_date = datetime.date(2028, 1, 1)
        current_date = start_date
        dates_to_create = []

        dates_to_create.append(DimDate(
            dateid=-1,
            year=None,
            month=None,
            monthname=None,
            day=None,
            dayname=None,
            hour=None,
        ))

        while current_date <= end_date:
            date_id_base_str = current_date.strftime('%Y%m%d')
            
            for hour in range(24): 
                hour_str = f"{hour:02d}"                 
                date_id = int(date_id_base_str + hour_str) 
                
                dates_to_create.append(DimDate(
                    dateid=date_id, 
                    
                    year=current_date.year,
                    month=current_date.month,
                    monthname=current_date.strftime('%B'),
                    day=current_date.day,
                    dayname=current_date.strftime('%A'),
                    hour=hour
                ))
            current_date += datetime.timedelta(days=1)
        
        DimDate.objects.bulk_create(dates_to_create)
        self.stdout.write(self.style.SUCCESS(f'{DimDate.objects.count()} DimDate rekord létrehozva.'))

        # 3. LÉPÉS: Dimenzió táblák feltöltése (min 50)
        
        # DimOrder (50 db)
        orders = []
        for _ in range(50):
            orders.append(DimOrder.objects.create(
                orderstatus=random.choice(['pending', 'in_progress', 'completed']),
                userfirstname=fake.first_name(),
                userlastname=fake.last_name(),
                useremail=fake.email()
            ))

        # DimVehicle (50 db)
        vehicles = []
        vehicle_types = ['truck', 'van', 'ship', 'plane', 'train']
        fuel_types = ['diesel', 'gasoline', 'kerosene', 'electricity'] # Alapul véve a szakdolgozatod
        brands = ['Scania', 'Volvo', 'Mercedes-Benz', 'Ford', 'MAN', 'Boeing', 'Airbus', 'Maersk', 'Stadler']
        
        for _ in range(50):
            v_type = random.choice(vehicle_types)
            f_type = 'diesel' # Alapértelmezett
            if v_type == 'van': f_type = random.choice(['diesel', 'gasoline', 'electricity'])
            if v_type == 'plane': f_type = 'kerosene'
            if v_type == 'train': f_type = 'electricity'
            if v_type == 'ship': f_type = random.choice(['diesel', 'fuel oil'])

            vehicles.append(DimVehicle.objects.create(
                brand=random.choice(brands),
                model=fake.word().capitalize(),
                type=v_type,
                fueltype=f_type
            ))

        # DimProduct (50 db)
        products = []
        categories = ['Electronics', 'Food', 'Furniture', 'Material', 'Vehicle Parts']
        for _ in range(50):
            products.append(DimProduct.objects.create(
                name=fake.bs().capitalize(),
                category=random.choice(categories),
                size=random.randint(1, 15) # m3
            ))

        # DimRoute (50 db)
        routes = []
        for _ in range(50):
            routes.append(DimRoute.objects.create(
                startcity=fake.city(),
                endcity=fake.city()
            ))
            
        self.stdout.write(self.style.SUCCESS(f'Dimenzió táblák (Order, Vehicle, Product, Route) létrehozva.'))

        # 4. LÉPÉS: FactShipment feltöltése (Legyen 500 rekord, hogy a grafikonok mutassanak valamit)
        
        self.stdout.write('FactShipment generálása (500 rekord)...')
        
        co2_factors = {
            'diesel': 2.717,
            'gasoline': 2.308,
            'kerosene': 2.588,
            'jet_kerosene': 2.582,
            'fuel_oil': 2.884,
            'propane': 0.509,
            'butane': 0.758,
            'electricity': 0.0,
        }
        
        # Gyorsítótár a DimDate PK-knak, hogy ne kelljen mindig query-zni
        date_pks = list(DimDate.objects.values_list('pk', flat=True))
        facts_to_create = []

        for _ in range(500):
            # Választunk random dimenziókat
            order = random.choice(orders)
            vehicle = random.choice(vehicles)
            product = random.choice(products)
            route = random.choice(routes)
            date = DimDate.objects.get(pk=random.choice(date_pks)) # Random dátum és óra
            
            # Releváns tényadatok generálása
            distance = random.uniform(50.0, 1500.0) # Távolság km-ben
            consumption = random.uniform(8.0, 35.0) # Fogyasztás l/100km
            fuel_consumed = (distance / 100) * consumption
            
            # CO2 számítás a szakdolgozatod alapján
            co2_factor = co2_factors.get(vehicle.fueltype, 2.5) # 2.5 default, ha nincs a listában
            co2_emission = fuel_consumed * co2_factor # kg CO2
            
            # Dátumok és költségek
            start_date_obj = datetime.datetime(date.year, date.month, date.day, date.hour)
            shipmentstart=DimDate.objects.get(dateid=int(start_date_obj.strftime('%Y%m%d%H')))
            duration_hours = (distance / 80) + random.uniform(1.0, 10.0) # Átlag 80km/h + várakozás
            end_date_obj = start_date_obj + datetime.timedelta(hours=duration_hours)
            shipmentend=DimDate.objects.get(dateid=int(end_date_obj.strftime('%Y%m%d%H')))

            fuel_cost_per_liter = random.uniform(550.0, 700.0)
            fuelcost_total = fuel_consumed * fuel_cost_per_liter
            routecost_total = random.uniform(1000.0, 50000.0) # Útdíj, stb.
            transportcost_total = fuelcost_total + routecost_total

            facts_to_create.append(FactShipment(
                shipmentstartdate=shipmentstart,
                shipmentenddate=shipmentend,
                duration=duration_hours,
                quantitytransported=product.size * random.randint(1, 10), # m3
                fuelconsumed=fuel_consumed,
                co2emission=co2_emission,
                transportcost=transportcost_total,
                distance=distance,
                routecost=routecost_total,
                unitprice=random.uniform(10000.0, 500000.0),
                consumption=consumption,
                fuelcost=fuelcost_total,
                productionyear=random.randint(2010, 2025), 
                orderid=order,
                productid=product,
                routeid=route,
                vehicleid=vehicle,
            ))

        FactShipment.objects.bulk_create(facts_to_create)
        self.stdout.write(self.style.SUCCESS(f'{len(facts_to_create)} FactShipment rekord létrehozva.'))
        self.stdout.write(self.style.SUCCESS('Adatbázis feltöltése sikeresen befejeződött!'))




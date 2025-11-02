# internal_dm/management/commands/seed_db.py

import random
import datetime
from faker import Faker
from django.core.management.base import BaseCommand
from leafroute.apps.internal_dm.models import DimOrder, DimVehicle, DimProduct, DimRoute, DimDate, FactShipment
from leafroute.apps.internal.models import City,Vehicle, Product

fake = Faker('hu_HU')

class Command(BaseCommand):
    help = 'Seeds the database with realistic data for dashboards'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Kezdődik az adatbázis feltöltése (seeding)...'))

        # 1. truncate
        self.stdout.write('Régi adatok törlése...')
        FactShipment.objects.all().delete()
        DimDate.objects.all().delete()
        DimOrder.objects.all().delete()
        DimRoute.objects.all().delete()

        # 2. Dimdate
        self.stdout.write('DimDate generálása (2020-2025)...')
        start_date = datetime.date(2020, 1, 1)
        end_date = datetime.date(2025, 11, 1)
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

        
        # DimOrder (50 db)
        orders = []
        for _ in range(50):
            userfirstname = fake.first_name()
            userlastname = fake.last_name()
            randint = random.randint(75, 99)
            orders.append(DimOrder.objects.create(
                orderstatus=random.choice(['pending', 'in_progress', 'completed']),
                userfirstname=userfirstname,
                userlastname=userlastname,
                useremail=userfirstname.lower() + '.' + userlastname.lower()+'_' + str(randint) + '@leafroute.com'
            ))


        # DimRoute (50 db)
        routes = []
        cities = list(City.objects.all())
        for _ in range(50):
            start_city, end_city = random.sample(cities, 2)
            routes.append(DimRoute.objects.create(
                startcity=start_city.name,
                endcity=end_city.name
            ))    

        self.stdout.write(self.style.SUCCESS(f'Dimenzió táblák (Order, Vehicle, Product, Route) létrehozva.'))

        # 4. FactShipment 
        
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
        
        date_pks = list(DimDate.objects.values_list('pk', flat=True))
        facts_to_create = []

        vehicles = list(Vehicle.objects.all())
        products = list(Product.objects.all())
        routes = list(DimRoute.objects.all())
        for _ in range(500):
            order = random.choice(orders)
            vehicle = random.choice(vehicles)
            product = random.choice(products)
            route = random.choice(routes)
            date = DimDate.objects.get(pk=random.choice(date_pks))
            
            distance = random.uniform(50.0, 1500.0) 
            consumption = vehicle.consumption 
            fuel_consumed = (distance / 100) * consumption
            
            co2_factor = co2_factors.get(vehicle.fuel_type, 2.5)
            co2_emission = fuel_consumed * co2_factor # kg CO2
            
            start_date_obj = datetime.datetime(date.year, date.month, date.day, date.hour)
            shipmentstart=DimDate.objects.get(dateid=int(start_date_obj.strftime('%Y%m%d%H')))
            duration_hours = (distance / 80) + random.uniform(1.0, 10.0)
            end_date_obj = start_date_obj + datetime.timedelta(hours=duration_hours)
            shipmentend=DimDate.objects.get(dateid=int(end_date_obj.strftime('%Y%m%d%H')))

            fuel_cost_per_liter = vehicle.fuel_cost
            fuelcost_total = fuel_consumed * fuel_cost_per_liter
            routecost_total = random.uniform(1000.0, 50000.0) 
            transportcost_total = fuelcost_total + routecost_total

            dimproductinstance=DimProduct.objects.get(productid=product.product_id)
            dimvehicleinstance=DimVehicle.objects.get(vehicleid=vehicle.vehicle_id)
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
                productionyear=random.randint(2000, 2025), 
                orderid=order,
                productid=dimproductinstance,
                routeid=route,
                vehicleid=dimvehicleinstance,
            ))

        FactShipment.objects.bulk_create(facts_to_create)
        self.stdout.write(self.style.SUCCESS(f'{len(facts_to_create)} FactShipment rekord létrehozva.'))
        self.stdout.write(self.style.SUCCESS('Adatbázis feltöltése sikeresen befejeződött!'))




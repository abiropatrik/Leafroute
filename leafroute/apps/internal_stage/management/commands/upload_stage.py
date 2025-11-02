import random
from django.core.management.base import BaseCommand
from leafroute.apps.internal_stage.models import (
    City_ST, 
    Address_ST, 
    Warehouse_ST, 
    Product_ST,
    WarehouseConnection_ST, 
    WarehouseProduct_ST, 
    Vehicle_ST,
    Route_ST,
    RoutePart_ST
)
from django.db import transaction

FLEET_SIZE = {
    "truck": 20,
    "van": 15,
    "airplane": 4,
    "ship": 3,
    "train": 5
}
# -------------------------------------------

class Command(BaseCommand):
    help = "Creates ALL demo data: Locations, Products, Inventory, and Vehicles"

    @transaction.atomic
    def handle(self, *args, **options):
        
        # --- 1. City Data ---
        self.stdout.write("Creating/updating demo cities...")
        cities_data = [
            {"name": "Budapest", "defaults": {"country": "Hungary", "continent": "Europe", "has_airport": True, "has_harbour": True, "latitude_coordinate": 47.4979, "longitude_coordinate": 19.0402}},
            {"name": "Berlin", "defaults": {"country": "Germany", "continent": "Europe", "has_airport": True, "has_harbour": False, "latitude_coordinate": 52.5200, "longitude_coordinate": 13.4050}},
            {"name": "Hamburg", "defaults": {"country": "Germany", "continent": "Europe", "has_airport": True, "has_harbour": True, "latitude_coordinate": 53.5511, "longitude_coordinate": 9.9937}},
            {"name": "Rotterdam", "defaults": {"country": "Netherlands", "continent": "Europe", "has_airport": True, "has_harbour": True, "latitude_coordinate": 51.9225, "longitude_coordinate": 4.47917}},
            {"name": "London", "defaults": {"country": "United Kingdom", "continent": "Europe", "has_airport": True, "has_harbour": True, "latitude_coordinate": 51.5074, "longitude_coordinate": -0.1278}},
            {"name": "Paris", "defaults": {"country": "France", "continent": "Europe", "has_airport": True, "has_harbour": True, "latitude_coordinate": 48.8566, "longitude_coordinate": 2.3522}},
            {"name": "Beijing", "defaults": {"country": "China", "continent": "Asia", "has_airport": True, "has_harbour": False, "latitude_coordinate": 39.9042, "longitude_coordinate": 116.4074}},
            {"name": "Madrid", "defaults": {"country": "Spain", "continent": "Europe", "has_airport": True, "has_harbour": False, "latitude_coordinate": 40.4168, "longitude_coordinate": -3.7038}}
        ]

        city_objects = {}
        for city_info in cities_data:
            city_obj, _ = City_ST.objects.update_or_create(
                name=city_info["name"],
                defaults=city_info["defaults"]
            )
            city_objects[city_info["name"]] = city_obj
        
        self.stdout.write(self.style.SUCCESS(f"Cities synced: {len(cities_data)}"))

        # --- 2. Warehouse & Address Data ---
        self.stdout.write("Creating/updating demo addresses and warehouses...")
        warehouses_data = [
            {"city_name": "Budapest", "address_details": {"street": "Európa utca", "house_number": "4", "institution_name": "Budapesti raktár"}, "warehouse_details": {"capacity": "15000", "fullness": "10000", "contact_email": "budapest-ops@leafroute.demo"}},
            {"city_name": "Berlin", "address_details": {"street": "Nöldnerstraße", "house_number": "15", "institution_name": "Berlini raktár"}, "warehouse_details": {"capacity": "22000", "fullness": "20000", "contact_email": "berlin-ops@leafroute.demo"}},
            {"city_name": "London", "address_details": {"street": "Moorhall Rd, Harefield", "house_number": "UB9 6PD", "institution_name": "Londoni raktár"}, "warehouse_details": {"capacity": "30000", "fullness": "7000", "contact_email": "london-ops@leafroute.demo"}},
            {"city_name": "Paris", "address_details": {"street": "Avenue Paul Delouvrier", "house_number": "1", "institution_name": "Párizsi raktár"}, "warehouse_details": {"capacity": "25000", "fullness": "24000", "contact_email": "paris-ops@leafroute.demo"}},
            {"city_name": "Madrid", "address_details": {"street": "Av. de Castilla", "house_number": "26", "institution_name": "Madridi raktár"}, "warehouse_details": {"capacity": "18000", "fullness": "10000", "contact_email": "madrid-ops@leafroute.demo"}},
            {"city_name": "Beijing", "address_details": {"street": "Shun Ping Road", "house_number": "11", "institution_name": "Pekingi raktár"}, "warehouse_details": {"capacity": "40000", "fullness": "35000", "contact_email": "beijing-ops@leafroute.demo"}}
        ]

        created_addr_count = 0
        created_wh_count = 0

        for item in warehouses_data:
            try:
                city = City_ST.objects.get(name=item["city_name"])
                
                address, addr_created = Address_ST.objects.update_or_create(
                    institution_name=item["address_details"]["institution_name"],
                    defaults={
                        "city": city,
                        "street": item["address_details"]["street"],
                        "house_number": item["address_details"]["house_number"]
                    }
                )
                if addr_created: created_addr_count += 1
                
                warehouse, wh_created = Warehouse_ST.objects.update_or_create(
                    address=address,
                    defaults={
                        "capacity": item["warehouse_details"]["capacity"],
                        "fullness": item["warehouse_details"]["fullness"],
                        "contact_email": item["warehouse_details"]["contact_email"]
                    }
                )
                if wh_created: created_wh_count += 1

            except City_ST.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"City '{item['city_name']}' not found. Skipping..."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating warehouse '{item['address_details']['institution_name']}': {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"Warehouse sync complete. "
            f"{created_addr_count} addresses created, {created_wh_count} warehouses created."
        ))

        # --- 3. Transport Hub Addresses ---
        self.stdout.write("Creating/updating demo transport hubs (stations, ports, airports)...")
        transport_hubs = [
            {"city_name": "Budapest", "type": "station", "name": "Budapest-Keleti Pályaudvar", "street": "Kerepesi út", "number": "2-4"},
            {"city_name": "Budapest", "type": "airport", "name": "Liszt Ferenc International Airport", "street": "Repülőtér", "number": "1185"},
            {"city_name": "Budapest", "type": "port", "name": "Port of Budapest - Mahart", "street": "Szabadkikötő út", "number": "5-7"},
            {"city_name": "Berlin", "type": "station", "name": "Berlin Hauptbahnhof", "street": "Europaplatz", "number": "1"},
            {"city_name": "Berlin", "type": "airport", "name": "Berlin Brandenburg Airport", "street": "Willy-Brandt-Platz", "number": "1"},
            {"city_name": "Hamburg", "type": "station", "name": "Hamburg Hauptbahnhof", "street": "Hachmannplatz", "number": "16"},
            {"city_name": "Hamburg", "type": "airport", "name": "Hamburg Airport", "street": "Flughafenstraße", "number": "1-3"},
            {"city_name": "Hamburg", "type": "port", "name": "Port of Hamburg", "street": "Bei St. Annen", "number": "1"},
            {"city_name": "Rotterdam", "type": "station", "name": "Rotterdam Centraal", "street": "Stationsplein", "number": "1"},
            {"city_name": "Rotterdam", "type": "airport", "name": "Rotterdam The Hague Airport", "street": "Rotterdam Airportplein", "number": "60"},
            {"city_name": "Rotterdam", "type": "port", "name": "Port of Rotterdam", "street": "Maasvlakte Plaza", "number": ""},
            {"city_name": "London", "type": "station", "name": "St Pancras International", "street": "Euston Rd", "number": ""},
            {"city_name": "London", "type": "airport", "name": "Heathrow Airport", "street": "Longford", "number": "TW6"},
            {"city_name": "London", "type": "port", "name": "Port of London", "street": "Royal Pier Rd", "number": ""},
            {"city_name": "Paris", "type": "station", "name": "Gare du Nord", "street": "Rue de Dunkerque", "number": "18"},
            {"city_name": "Paris", "type": "airport", "name": "Charles de Gaulle Airport", "street": "Route de l'Épinette", "number": "95700"},
            {"city_name": "Paris", "type": "port", "name": "Port de Gennevilliers", "street": "Route du Môle", "number": "1"},
            {"city_name": "Beijing", "type": "station", "name": "Beijing Railway Station", "street": "Jia, Jianguomen N St", "number": ""},
            {"city_name": "Beijing", "type": "airport", "name": "Beijing Capital International Airport", "street": "Shunyi District", "number": ""},
            {"city_name": "Madrid", "type": "station", "name": "Atocha Railway Station", "street": "Plaza del Emperador Carlos V", "number": ""},
            {"city_name": "Madrid", "type": "airport", "name": "Madrid–Barajas Airport", "street": "Av de la Hispanidad", "number": ""},
        ]

        hub_count = 0
        for hub in transport_hubs:
            city = city_objects.get(hub["city_name"])
            if not city:
                self.stdout.write(self.style.ERROR(f"City '{hub['city_name']}' not found for hub. Skipping..."))
                continue
            
            if hub["type"] == "airport" and not city.has_airport:
                continue
            if hub["type"] == "port" and not city.has_harbour:
                continue

            Address_ST.objects.update_or_create(
                institution_name=hub["name"],
                defaults={
                    "city": city,
                    "street": hub["street"],
                    "house_number": hub["number"]
                }
            )
            hub_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Transport hubs synced: {hub_count}"))
        self.stdout.write(self.style.SUCCESS("All demo location data synced successfully."))

        # --- 4. Product & Inventory Data ---
        self.stdout.write("---")
        self.stdout.write("Creating/updating demo products...")
        
        products_data = [
            {"name": "Industrial Robotics Arm", "category": "Machinery", "unit_price": "45000", "size": "3", "is_alive": "False", "is_liquid": "False", "is_hazardous": "False", "is_time_sensitive": "False"},
            {"name": "Semiconductor Wafers (Box)", "category": "Electronics", "unit_price": "12000", "size": "0.5", "is_alive": "False", "is_liquid": "False", "is_hazardous": "True", "is_time_sensitive": "False"},
            {"name": "Pharmaceuticals (Pallet)", "category": "Medical", "unit_price": "75000", "size": "1.2", "is_alive": "False", "is_liquid": "False", "is_hazardous": "False", "is_time_sensitive": "True"},
            {"name": "Bulk Fertilizer (Tote)", "category": "Agriculture", "unit_price": "1500", "size": "1", "is_alive": "False", "is_liquid": "False", "is_hazardous": "True", "is_time_sensitive": "False"},
            {"name": "Jet Fuel (Barrel)", "category": "Fuel", "unit_price": "300", "size": "0.16", "is_alive": "False", "is_liquid": "True", "is_hazardous": "True", "is_time_sensitive": "False"},
            {"name": "Fresh Produce (Pallet)", "category": "Food", "unit_price": "2000", "size": "1.2", "is_alive": "True", "is_liquid": "False", "is_hazardous": "False", "is_time_sensitive": "True"},
            {"name": "Apparel (Box)", "category": "Retail", "unit_price": "5000", "size": "0.8", "is_alive": "False", "is_liquid": "False", "is_hazardous": "False", "is_time_sensitive": "False"},
        ]

        product_objects = []
        for prod_data in products_data:
            prod_obj, _ = Product_ST.objects.update_or_create(
                name=prod_data["name"],
                defaults={
                    "category": prod_data["category"],
                    "unit_price": prod_data["unit_price"],
                    "size": prod_data["size"],
                    "is_alive": prod_data["is_alive"],
                    "is_liquid": prod_data["is_liquid"],
                    "is_hazardous": prod_data["is_hazardous"],
                    "is_time_sensitive": prod_data["is_time_sensitive"],
                }
            )
            product_objects.append(prod_obj)
        
        self.stdout.write(self.style.SUCCESS(f"Products synced: {len(product_objects)}"))

        self.stdout.write("Creating/updating demo warehouse inventory...")
        
        warehouses = Warehouse_ST.objects.all()
        if not warehouses.exists():
            self.stdout.write(self.style.ERROR("No warehouses found. Cannot create inventory."))
            raise Exception("Warehouses not found") 

        inventory_count = 0
        for warehouse in warehouses:
            for product in product_objects:
                random_stock1 = str(random.randint(20, 400))
                random_stock2 = str(random.randint(20, 400))
                _, created = WarehouseProduct_ST.objects.update_or_create(
                    product=product,
                    warehouse=warehouse,
                    defaults={
                        "free_stock": random_stock1,
                        "reserved_stock": random_stock2
                    }
                )
                if created:
                    inventory_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Inventory synced: {inventory_count} new stock records created."))
        self.stdout.write(self.style.SUCCESS("All product and inventory data synced successfully."))

        # 5. Vehicle Fleet 
        self.stdout.write("---")
        self.stdout.write("Categorizing addresses for vehicle placement...")

        # 5a. Categorize all addresses
        warehouse_address_ids = Warehouse_ST.objects.values_list('address__address_id', flat=True)
        warehouse_addresses = list(Address_ST.objects.filter(address_id__in=warehouse_address_ids))
        hub_addresses = Address_ST.objects.exclude(address_id__in=warehouse_address_ids)
        
        airport_addresses, port_addresses, station_addresses = [], [], []
        for addr in hub_addresses:
            name_lower = addr.institution_name.lower()
            if 'airport' in name_lower:
                airport_addresses.append(addr)
            elif 'port' in name_lower:
                port_addresses.append(addr)
            elif any(s in name_lower for s in ['station', 'bahnhof', 'pályaudvar', 'gare']):
                station_addresses.append(addr)
        
        if not all([warehouse_addresses, airport_addresses, port_addresses, station_addresses]):
             raise Exception("Missing addresses for hubs or warehouses. Cannot create vehicles.")

        address_lists = {
            "warehouse": warehouse_addresses,
            "airport": airport_addresses,
            "port": port_addresses,
            "station": station_addresses
        }
        self.stdout.write(self.style.SUCCESS("Addresses categorized."))
        
        # 5b. Define Vehicle Templates
        vehicle_templates = {
            "truck": [
                {"brand": "Scania", "model": "R 450", "year": "2021", "fuel": "diesel", "cons": "29", "cap": "90", "avg_hr": "80", "cost": "646"},
                {"brand": "Volvo", "model": "FH16", "year": "2022", "fuel": "diesel", "cons": "32", "cap": "95", "avg_hr": "80", "cost": "646"},
                {"brand": "Mercedes-Benz", "model": "Actros", "year": "2020", "fuel": "diesel", "cons": "30", "cap": "90", "avg_hr": "80", "cost": "646"},
            ],
            "van": [
                {"brand": "Ford", "model": "Transit", "year": "2022", "fuel": "diesel", "cons": "9", "cap": "15", "avg_hr": "70", "cost": "646"},
                {"brand": "Mercedes-Benz", "model": "Sprinter", "year": "2023", "fuel": "gasoline", "cons": "0", "cap": "14", "avg_hr": "65", "cost": "620"},
                {"brand": "Renault", "model": "Master E-Tech", "year": "2022", "fuel": "electricity", "cons": "0", "cap": "13", "avg_hr": "60", "cost": "152"},
            ],
            "airplane": [
                {"brand": "Boeing", "model": "747-8F", "year": "2018", "fuel": "kerosene", "cons": "1200", "cap": "750", "avg_hr": "900", "cost": "850"},
                {"brand": "Airbus", "model": "A330-200F", "year": "2019", "fuel": "jet_kerosene", "cons": "950", "cap": "475", "avg_hr": "870", "cost": "970"},
            ],
            "ship": [
                {"brand": "Maersk", "model": "Triple E Class", "year": "2017", "fuel": "fuel_oil", "cons": "10000", "cap": "10000", "avg_hr": "40", "cost": "312"},
                {"brand": "Evergreen", "model": "Ever Ace", "year": "2021", "fuel": "fuel_oil", "cons": "12000", "cap": "12000", "avg_hr": "38", "cost": "312"},
            ],
            "train": [
                {"brand": "Siemens", "model": "Vectron", "year": "2020", "fuel": "electricity", "cons": "0", "cap": "1500", "avg_hr": "100", "cost": "152"},
                {"brand": "Alstom", "model": "Traxx", "year": "2019", "fuel": "electricity", "cons": "0", "cap": "1400", "avg_hr": "100", "cost": "152"},
            ]
        }
        
        # 5c. Generate Vehicle Fleet
        self.stdout.write("Generating vehicle fleet...")
        total_vehicles_created = 0

        for vehicle_type, count in FLEET_SIZE.items():
            templates = vehicle_templates.get(vehicle_type)
            address_list = None

            if vehicle_type in ["truck", "van"]:
                address_list = address_lists["warehouse"]
            elif vehicle_type == "airplane":
                address_list = address_lists["airport"]
            elif vehicle_type == "ship":
                address_list = address_lists["port"]
            elif vehicle_type == "train":
                address_list = address_lists["station"]
                
            if not templates or not address_list:
                self.stdout.write(self.style.WARNING(f"Skipping {vehicle_type}, no templates or addresses found."))
                continue

            for _ in range(count):
                v = random.choice(templates)
                addr = random.choice(address_list)

                # 
                Vehicle_ST.objects.create(
                    brand=v["brand"],
                    model=v["model"],
                    production_year=v["year"],
                    type=vehicle_type,
                    fuel_type=v["fuel"],
                    consumption=v["cons"],
                    full_capacity=v["cap"],
                    free_capacity=v["cap"], 
                    status="available",
                    address=addr,
                    avg_distance_per_hour=v["avg_hr"],
                    fuel_cost=v["cost"],
                )
                total_vehicles_created += 1
            
            self.stdout.write(f"Created {count} new {vehicle_type}s.")

        self.stdout.write(self.style.SUCCESS(
            f"Vehicle fleet generation complete. {total_vehicles_created} total vehicles created."
        ))

        #####################################################################
        ###route and routepart
        ######################################################################
        self.stdout.write("Creating demo routes, connections, and route parts...")

        wh_london = Warehouse_ST.objects.get(address__institution_name="Londoni raktár")
        wh_paris = Warehouse_ST.objects.get(address__institution_name="Párizsi raktár")
        
        addr_london_wh = wh_london.address
        addr_paris_wh = wh_paris.address

        # Hubs
        addr_london_port = Address_ST.objects.get(institution_name="Port of London")
        addr_paris_port = Address_ST.objects.get(institution_name="Port de Gennevilliers")
        addr_london_airport = Address_ST.objects.get(institution_name="Heathrow Airport")
        addr_paris_airport = Address_ST.objects.get(institution_name="Charles de Gaulle Airport")

        

        # --- 2. Create the Warehouse Connection ---
        # (Correcting `is_in_different_continent` to False for London-Paris)
        wh_connection, _ = WarehouseConnection_ST.objects.update_or_create(
            warehouse1=wh_london,
            warehouse2=wh_paris,
            defaults={
                "is_in_different_country": "True",
                "is_in_different_continent": "False", 
            }
        )
        self.stdout.write("Created warehouse connection: London to Paris")

        # --- 3. Create Route 1: Road-Only ---
        route1, _ = Route_ST.objects.update_or_create(
            warehouse_connection=wh_connection
        )
        RoutePart_ST.objects.update_or_create(
            route=route1,
            start_address=addr_london_wh,
            end_address=addr_paris_wh,
            defaults={
                "distance": None,
                "transport_mode": "road",
                "route_cost": "900",
            }
        )
        self.stdout.write("Created Route 1 (Road Only)")

        # --- 4. Create Route 2: Road-Sea-Road ---
        route2, _ = Route_ST.objects.update_or_create(
            warehouse_connection=wh_connection
        )
        # Part 1: London WH -> London Port
        RoutePart_ST.objects.update_or_create(
            route=route2,
            start_address=addr_london_wh,
            end_address=addr_london_port,
            defaults={"distance": None, "transport_mode": "road", "route_cost": "110"}
        )
        # Part 2: London Port -> Paris Port
        RoutePart_ST.objects.update_or_create(
            route=route2,
            start_address=addr_london_port,
            end_address=addr_paris_port,
            defaults={"distance": "350", "transport_mode": "sea", "route_cost": "5000"}
        )
        # Part 3: Paris Port -> Paris WH
        RoutePart_ST.objects.update_or_create(
            route=route2,
            start_address=addr_paris_port,
            end_address=addr_paris_wh,
            defaults={"distance": None, "transport_mode": "road", "route_cost": "40"}
        )
        self.stdout.write("Created Route 2 (Road-Sea-Road)")

        # --- 5. Create Route 3: Road-Air-Road ---
        route3, _ = Route_ST.objects.update_or_create(
            warehouse_connection=wh_connection
        )
        # Part 1: London WH -> London Airport
        RoutePart_ST.objects.update_or_create(
            route=route3,
            start_address=addr_london_wh,
            end_address=addr_london_airport,
            defaults={"distance": None, "transport_mode": "road", "route_cost": "30"}
        )
        # Part 2: London Airport -> Paris Airport
        RoutePart_ST.objects.update_or_create(
            route=route3,
            start_address=addr_london_airport,
            end_address=addr_paris_airport,
            defaults={"distance": "344", "transport_mode": "air", "route_cost": "10000"}
        )
        # Part 3: Paris Airport -> Paris WH
        RoutePart_ST.objects.update_or_create(
            route=route3,
            start_address=addr_paris_airport,
            end_address=addr_paris_wh,
            defaults={"distance": None, "transport_mode": "road", "route_cost": "60"}
        )
        self.stdout.write("Created Route 3 (Road-Air-Road)")


        self.stdout.write(self.style.SUCCESS(
            "\n" + "="*50 +
            "\n ALL DEMO DATA SYNCED SUCCESSFULLY " +
            "\n" + "="*50
        ))
from leafroute.apps.internal_stage.models import (
    City_ST, Address_ST, UserProfile_ST, Warehouse_ST, WarehouseConnection_ST
)
from leafroute.apps.internal.models import (
    City, Address, UserProfile, Warehouse, WarehouseConnection
)
from django.db import transaction

def etl_job():
    """
    ETL job to transfer data from internal_stage models to internal models.
    """
    try:
        with transaction.atomic():
            # Extract and Transform: City
            for city_st in City_ST.objects.using('stage').all():
                city, created = City.objects.using('default').update_or_create(
                    city_id=city_st.city_id,
                    defaults={
                        'country': city_st.country,
                        'continent': city_st.continent,
                        'name': city_st.name,
                        'has_airport': city_st.has_airport == 'True',
                        'has_harbour': city_st.has_harbour == 'True',
                        'longitude_coordinate': float(city_st.longitude_coordinate) if city_st.longitude_coordinate else None,
                        'latitude_coordinate': float(city_st.latitude_coordinate) if city_st.latitude_coordinate else None,
                    }
                )

            # Extract and Transform: Address
            for address_st in Address_ST.objects.using('stage').all():
                address, created = Address.objects.using('default').update_or_create(
                    address_id=address_st.address_id,
                    defaults={
                        'city': City.objects.using('default').get(city_id=address_st.city.city_id),
                        'street': address_st.street,
                        'house_number': address_st.house_number,
                        'institution_name': address_st.institution_name,
                    }
                )

            # Extract and Transform: UserProfile
            for user_profile_st in UserProfile_ST.objects.using('stage').all():
                user_profile, created = UserProfile.objects.using('default').update_or_create(
                    user=user_profile_st.user,
                    defaults={
                        'email': user_profile_st.email,
                        'first_name': user_profile_st.first_name,
                        'last_name': user_profile_st.last_name,
                        'address': Address.objects.using('default').get(address_id=user_profile_st.address.address_id) if user_profile_st.address else None,
                        'job': user_profile_st.job,
                        'rights': user_profile_st.rights,
                        'hiring_date': user_profile_st.hiring_date,
                        'co2_saved': float(user_profile_st.co2_saved) if user_profile_st.co2_saved else None,
                        'salary': float(user_profile_st.salary) if user_profile_st.salary else None,
                    }
                )

            # Extract and Transform: Warehouse
            for warehouse_st in Warehouse_ST.objects.using('stage').all():
                warehouse, created = Warehouse.objects.using('default').update_or_create(
                    warehouse_id=warehouse_st.warehouse_id,
                    defaults={
                        'address': Address.objects.using('default').get(address_id=warehouse_st.address.address_id),
                        'capacity': int(warehouse_st.capacity) if warehouse_st.capacity else None,
                        'fullness': int(warehouse_st.fullness) if warehouse_st.fullness else None,
                        'contact_email': warehouse_st.contact_email,
                    }
                )

            # Extract and Transform: WarehouseConnection
            for warehouse_connection_st in WarehouseConnection_ST.objects.using('stage').all():
                warehouse_connection, created = WarehouseConnection.objects.using('default').update_or_create(
                    warehouse_connection_id=warehouse_connection_st.warehouse_connection_id,
                    defaults={
                        'warehouse1': Warehouse.objects.using('default').get(warehouse_id=warehouse_connection_st.warehouse1.warehouse_id),
                        'warehouse2': Warehouse.objects.using('default').get(warehouse_id=warehouse_connection_st.warehouse2.warehouse_id),
                        'is_in_different_country': warehouse_connection_st.is_in_different_country == 'True',
                        'is_in_different_continent': warehouse_connection_st.is_in_different_continent == 'True',
                    }
                )

            print("ETL job completed successfully!")

    except Exception as e:
        print(f"ETL job failed: {e}")
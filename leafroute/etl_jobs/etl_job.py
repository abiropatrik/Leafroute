from leafroute.apps.internal_stage.models import (
    City_ST, Address_ST, Warehouse_ST, WarehouseConnection_ST,
    Route_ST, RoutePart_ST, WorkSchedule_ST, Vehicle_ST, Product_ST,
    WarehouseProduct_ST, Order_ST, Shipment_ST, UserShipments_ST
)
from leafroute.apps.internal.models import (
    City, Address, UserProfile, Warehouse, WarehouseConnection,
    Route, RoutePart, WorkSchedule, Vehicle, Product,
    WarehouseProduct, Order, Shipment, UserShipment
)
from leafroute.apps.internal_dm.models import (
    DimOrder, DimVehicle, DimProduct, DimRoute, DimDate, FactShipment
)
from django.db.models import Sum, FloatField,ObjectDoesNotExist
from django.db.models.functions import Cast
from django.db import transaction
from datetime import datetime,date
from zoneinfo import ZoneInfo
from leafroute.apps.internal.utils import real_CO2_emission
import math


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

            # Extract and Transform: Route
            for route_st in Route_ST.objects.using('stage').all():
                route, created = Route.objects.using('default').update_or_create(
                    route_id=route_st.route_id,
                    defaults={
                        'warehouse_connection': WarehouseConnection.objects.using('default').get(
                            warehouse_connection_id=route_st.warehouse_connection.warehouse_connection_id
                        ),
                    }
                )

            # Extract and Transform: RoutePart
            for route_part_st in RoutePart_ST.objects.using('stage').all():
                route_part, created = RoutePart.objects.using('default').update_or_create(
                    route_part_id=route_part_st.route_part_id,
                    defaults={
                        'route': Route.objects.using('default').get(route_id=route_part_st.route.route_id),
                        'distance': float(route_part_st.distance) if route_part_st.distance else None,
                        'transport_mode': route_part_st.transport_mode,
                        'start_address': Address.objects.using('default').get(
                            address_id=route_part_st.start_address.address_id
                        ),
                        'end_address': Address.objects.using('default').get(
                            address_id=route_part_st.end_address.address_id
                        ),
                        'route_cost': float(route_part_st.route_cost) if route_part_st.route_cost else None,
                    }
                )

            # Extract and Transform: WorkSchedule
            for work_schedule_st in WorkSchedule_ST.objects.using('stage').all():
                work_schedule, created = WorkSchedule.objects.using('default').update_or_create(
                    schedule_id=work_schedule_st.schedule_id,
                    defaults={
                        'user': UserProfile.objects.using('default').get(
                            user_id=work_schedule_st.user
                        ),
                        'work_day': work_schedule_st.work_day,
                        'start_time': work_schedule_st.start_time,
                        'end_time': work_schedule_st.end_time,
                    }
                )

            # Extract and Transform: Vehicle
            for vehicle_st in Vehicle_ST.objects.using('stage').all():
                vehicle, created = Vehicle.objects.using('default').update_or_create(
                    vehicle_id=vehicle_st.vehicle_id,
                    defaults={
                        'brand': vehicle_st.brand,
                        'model': vehicle_st.model,
                        'production_year': int(vehicle_st.production_year) if vehicle_st.production_year else None,
                        'type': vehicle_st.type,
                        'fuel_type': vehicle_st.fuel_type,
                        'consumption': float(vehicle_st.consumption) if vehicle_st.consumption else None,
                        'full_capacity': float(vehicle_st.full_capacity) if vehicle_st.full_capacity else None,
                        'free_capacity': float(vehicle_st.free_capacity) if vehicle_st.free_capacity else None,
                        'status': vehicle_st.status,
                        'address': Address.objects.using('default').get(
                            address_id=vehicle_st.address.address_id
                        ) if vehicle_st.address else None,
                        'avg_distance_per_hour': float(vehicle_st.avg_distance_per_hour) if vehicle_st.avg_distance_per_hour else None,
                        'fuel_cost': float(vehicle_st.fuel_cost) if vehicle_st.fuel_cost else None,
                    }
                )

            # Extract and Transform: Product
            for product_st in Product_ST.objects.using('stage').all():
                product, created = Product.objects.using('default').update_or_create(
                    product_id=product_st.product_id,
                    defaults={
                        'name': product_st.name,
                        'category': product_st.category,
                        'unit_price': float(product_st.unit_price) if product_st.unit_price else None,
                        'size': float(product_st.size) if product_st.size else None,
                        'is_alive': product_st.is_alive == 'True',
                        'is_liquid': product_st.is_liquid == 'True',
                        'is_hazardous': product_st.is_hazardous == 'True',
                        'is_time_sensitive': product_st.is_time_sensitive == 'True',
                    }
                )

            # Extract and Transform: WarehouseProduct
            for warehouse_product_st in WarehouseProduct_ST.objects.using('stage').all():
                warehouse_product, created = WarehouseProduct.objects.using('default').update_or_create(
                    product=Product.objects.using('default').get(product_id=warehouse_product_st.product.product_id),
                    warehouse=Warehouse.objects.using('default').get(warehouse_id=warehouse_product_st.warehouse.warehouse_id),
                    defaults={
                        'free_stock': int(warehouse_product_st.free_stock) if warehouse_product_st.free_stock else None,
                        'reserved_stock': int(warehouse_product_st.reserved_stock) if warehouse_product_st.reserved_stock else None,
                    }
                )
            
            print("shipment")
            # Extract and Transform: Shipment
            for shipment_st in Shipment_ST.objects.using('stage').all():
                start_date = (
                    datetime.strptime(shipment_st.shipment_start_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Budapest"))
                    if shipment_st.shipment_start_date else None
                )
                end_date = (
                    datetime.strptime(shipment_st.shipment_end_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Budapest"))
                    if shipment_st.shipment_end_date else None
                )

                duration = 0
                if start_date and end_date:
                    duration = math.ceil((end_date - start_date).total_seconds() / 3600)  # duration in hours

                fuel_consumed=((float(shipment_st.route_part.distance) / 100) * float(shipment_st.vehicle.consumption))
                co2emission=real_CO2_emission(fuel_consumed, shipment_st.vehicle.fuel_type)

                this_user_id = (
                    UserShipments_ST.objects.using('stage')
                    .filter(shipment=shipment_st)
                    .values_list('user', flat=True)
                    .first()
                )
                user_st_object = UserProfile.objects.using('default').get(user=this_user_id)
                user_salary = float(user_st_object.salary or 0)
                transportcost= float(shipment_st.vehicle.consumption or 0) * (float(shipment_st.route_part.distance or 0) / 100) * float(shipment_st.vehicle.fuel_cost or 0) + duration * user_salary

                shipment, created = Shipment.objects.using('default').update_or_create(
                    shipment_id=shipment_st.shipment_id,
                    defaults={
                        'order': Order.objects.using('default').get(order_id=shipment_st.order.order_id),
                        'vehicle': Vehicle.objects.using('default').get(vehicle_id=shipment_st.vehicle.vehicle_id),
                        'product': Product.objects.using('default').get(product_id=shipment_st.product.product_id),
                        'route_part': RoutePart.objects.using('default').get(route_part_id=shipment_st.route_part.route_part_id),
                        'shipment_start_date': start_date,
                        'shipment_end_date': end_date,
                        'duration': duration,
                        'quantity_transported': int(shipment_st.quantity_transported) if shipment_st.quantity_transported else None,
                        'fuel_consumed': fuel_consumed,
                        'status': shipment_st.status,
                        'co2_emission': co2emission,
                        'transport_cost': transportcost,
                    }
                )

            print("order")
            # Extract and Transform: Order
            for order_st in Order_ST.objects.using('stage').all():
                first_pending = (
                    Shipment_ST.objects.using('stage')
                    .filter(order=order_st)
                    .order_by('shipment_id')
                    .values_list('status', flat=True)
                    .first()
                )
                last_shipment_date = (
                    Shipment_ST.objects.using('stage')
                    .filter(order=order_st)
                    .order_by('-shipment_id')
                    .values_list('shipment_end_date', flat=True)
                    .first()
                )
                last_shipment_date=(
                    datetime.strptime(last_shipment_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Budapest"))
                    if last_shipment_date else None
                )
                order_status ="pending"
                if first_pending != "pending" and last_shipment_date is None:
                    order_status="in_progress"
                elif first_pending != "pending" and last_shipment_date is not None:
                    order_status="completed"

                co_2_data = (
                    Shipment.objects.using('default')
                    .filter(order=order_st.order_id)
                    .aggregate(total_co2=Sum('co2_emission'))
                )
                co_2_emission = co_2_data['total_co2'] or 0.0

                cost_data = (
                    Shipment.objects.using('default')
                    .filter(order=order_st.order_id)
                    .aggregate(total_cost=Sum('transport_cost'))
                )
                transport_cost = cost_data['total_cost'] or 0.0

                print(transport_cost)

                order, created = Order.objects.using('default').update_or_create(
                    order_id=order_st.order_id,
                    defaults={
                        'user': UserProfile.objects.using('default').get(user_id=order_st.user),
                        'product': Product.objects.using('default').get(product_id=order_st.product.product_id),
                        'warehouse_connection': WarehouseConnection.objects.using('default').get(
                            warehouse_connection_id=order_st.warehouse_connection.warehouse_connection_id
                        ),
                        'route': Route.objects.using('default').get(route_id=order_st.route.route_id),
                        'quantity': int(order_st.quantity) if order_st.quantity else None,
                        'order_date': datetime.strptime(order_st.order_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Budapest")) if order_st.order_date else None,
                        'expected_fullfillment_date': datetime.strptime(order_st.expected_fullfillment_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Budapest")) if order_st.expected_fullfillment_date else None,
                        'fulfillment_date': last_shipment_date,
                        'order_status': order_status,
                        'expected_co2_emission': float(order_st.expected_co2_emission) if order_st.expected_co2_emission else None,
                        'co2_emmission': co_2_emission,
                        'cost': transport_cost,
                    }
                )

            print("user_shipment")
            # Extract and Transform: UserShipment
            for user_shipment_st in UserShipments_ST.objects.using('stage').all():
                user_shipment, created = UserShipment.objects.using('default').update_or_create(
                    user=UserProfile.objects.using('default').get(user_id=user_shipment_st.user),
                    shipment=Shipment.objects.using('default').get(shipment_id=user_shipment_st.shipment.shipment_id),
                )

            print("ETL job completed successfully!")

    except Exception as e:
        print(f"ETL job failed: {e}")


def dm_etl_job():
    """
    ETL job to transfer data from default models to dm models.
    """
    try:
        with transaction.atomic():
            # DimOrder
            print("order")
            for order in Order.objects.using('default').all():
                DimOrder.objects.using('dm').update_or_create(
                    orderid=order.order_id,
                    defaults={
                        'orderstatus': order.order_status,
                        'userfirstname': order.user.first_name if order.user else None,
                        'userlastname': order.user.last_name if order.user else None,
                        'useremail': order.user.email if order.user else None,
                    }
                )
            print("vehicle")
            # DimVehicle
            for vehicle in Vehicle.objects.using('default').all():
                DimVehicle.objects.using('dm').update_or_create(
                    vehicleid=vehicle.vehicle_id,
                    defaults={
                        'brand': vehicle.brand,
                        'model': vehicle.model,
                        'type': vehicle.type,
                        'fueltype': vehicle.fuel_type,
                    }
                )
            print("product")
            # DimProduct
            for product in Product.objects.using('default').all():
                DimProduct.objects.using('dm').update_or_create(
                    productid=product.product_id,
                    defaults={
                        'name': product.name,
                        'category': product.category,
                        'size': int(product.size) if product.size else None,
                    }
                )
            print("route")
            # DimRoute
            for route in Route.objects.using('default').all():
                start_city = route.warehouse_connection.warehouse1.address.city.name if route.warehouse_connection.warehouse1.address.city else None
                end_city = route.warehouse_connection.warehouse2.address.city.name if route.warehouse_connection.warehouse2.address.city else None
                DimRoute.objects.using('dm').update_or_create(
                    routeid=route.route_id,
                    defaults={
                        'startcity': start_city,
                        'endcity': end_city,
                    }
                )

            print("FactShipment")
            # FactShipment
            for shipment in Shipment.objects.using('default').all():
                shipmentstartdate=get_dim_date_object(shipment.shipment_start_date)
                shipmentenddate=get_dim_date_object(shipment.shipment_end_date)
                FactShipment.objects.using('dm').update_or_create(
                    shipmentid=shipment.shipment_id,
                    defaults={
                        'shipmentstartdate': shipmentstartdate,
                        'shipmentenddate': shipmentenddate,
                        'duration': shipment.duration,
                        'quantitytransported': shipment.quantity_transported,
                        'fuelconsumed': shipment.fuel_consumed,
                        'co2emission': shipment.co2_emission,
                        'transportcost': shipment.transport_cost,
                        'distance': shipment.route_part.distance if shipment.route_part else None,
                        'routecost': shipment.route_part.route_cost if shipment.route_part else None,
                        'unitprice': shipment.product.unit_price if shipment.product else None,
                        'consumption': shipment.vehicle.consumption if shipment.vehicle else None,
                        'fuelcost': shipment.vehicle.fuel_cost if shipment.vehicle else None,
                        'productionyear': shipment.vehicle.production_year if shipment.vehicle else None,
                        'orderid': DimOrder.objects.using('dm').get(orderid=shipment.order.order_id) if shipment.order else None,
                        'productid': DimProduct.objects.using('dm').get(productid=shipment.product.product_id) if shipment.product else None,
                        'routeid': DimRoute.objects.using('dm').get(routeid=shipment.route_part.route.route_id) if shipment.route_part and shipment.route_part.route else None,
                        'vehicleid': DimVehicle.objects.using('dm').get(vehicleid=shipment.vehicle.vehicle_id) if shipment.vehicle else None,
                    }
                )

            print("DM ETL job completed successfully!")

    except Exception as e:
        print(f"DM ETL job failed: {e}")


def get_dim_date_object(raw_datetime: datetime) -> 'DimDate':
    if raw_datetime is None:
        return DimDate.objects.get(dateid=-1)
    else:
        date_key = int(raw_datetime.strftime('%Y%m%d%H'))
        try:
            return DimDate.objects.get(dateid=date_key)
        except ObjectDoesNotExist:
            raise Exception(f"Missing dimdate: {date_key}. Please contact administrator.")
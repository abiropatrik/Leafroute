from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class City_ST(models.Model):
    city_id = models.AutoField(primary_key=True, db_column="CityID")
    country = models.CharField(max_length=255,null=True, blank=True)
    continent = models.CharField(max_length=255,null=True, blank=True)
    name = models.CharField(max_length=255,null=True, blank=True)
    has_airport = models.CharField(max_length=255, null=True, blank=True)
    has_harbour = models.CharField(max_length=255, null=True, blank=True)
    longitude_coordinate = models.CharField(max_length=255, null=True, blank=True)
    latitude_coordinate = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Cities_ST"
    


class Address_ST(models.Model):
    address_id = models.AutoField(primary_key=True, db_column="AddressID")
    city = models.ForeignKey(City_ST, on_delete=models.CASCADE, db_column="CityID")
    street = models.CharField(max_length=255, null=True, blank=True)
    house_number = models.CharField(max_length=255, null=True, blank=True)
    institution_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Addresses_ST"



class UserProfile_ST(models.Model):
    # owner
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='stage_profile',db_column="UserID")
    
    #settings
    is_full_name_displayed=models.BooleanField(default=True)

    # database fields
    email = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.ForeignKey(
        Address_ST,
        on_delete=models.CASCADE,
        db_column="AddressID",
        null=True,
        blank=True
    )
    job = models.CharField(max_length=255, null=True, blank=True)
    rights = models.CharField(max_length=255, null=True, blank=True)
    hiring_date = models.CharField(max_length=255, null=True, blank=True)
    co2_saved = models.CharField(max_length=255, null=True, blank=True)
    salary = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Users_ST"
        permissions = [
            ("admin_tasks", "Is able to proceed with admin related tasks"),
            ("organiser_tasks", "Is able to proceed with tasks related to organisers"),
            ("driver_tasks", "Is able to proceed with tasks related to drivers"),
            ("warehouseman_tasks", "Is able to proceed with tasks related to warehousemen"),
            ("manager_tasks", "Is able to proceed with tasks related to managers"),
        ]


class Warehouse_ST(models.Model):
    warehouse_id = models.AutoField(primary_key=True, db_column="WarehouseID")
    address = models.ForeignKey(Address_ST, on_delete=models.CASCADE, db_column="AddressID")
    capacity = models.CharField(max_length=255, null=True, blank=True)
    fullness = models.CharField(max_length=255, null=True, blank=True)
    contact_email = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Warehouses_ST"



class WarehouseConnection_ST(models.Model):
    warehouse_connection_id = models.AutoField(primary_key=True, db_column="WarehouseConnectionID")
    warehouse1 = models.ForeignKey(Warehouse_ST, on_delete=models.CASCADE, related_name="connection_warehouse1", db_column="Warehouse1")
    warehouse2 = models.ForeignKey(Warehouse_ST, on_delete=models.CASCADE, related_name="connection_warehouse2", db_column="Warehouse2")
    is_in_different_country = models.CharField(max_length=255, null=True, blank=True)
    is_in_different_continent = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "WarehouseConnections_ST"



class Route_ST(models.Model):
    route_id = models.AutoField(primary_key=True, db_column="RouteID")
    warehouse_connection = models.ForeignKey(WarehouseConnection_ST, on_delete=models.CASCADE, db_column="WarehouseConnectionID")

    class Meta:
        db_table = "Routes_ST"



class RoutePart_ST(models.Model):
    route_part_id = models.AutoField(primary_key=True, db_column="RoutePartID")
    route = models.ForeignKey(Route_ST, on_delete=models.CASCADE, db_column="RouteID")
    distance = models.CharField(max_length=255, null=True, blank=True)
    transport_mode = models.CharField(max_length=255, null=True, blank=True)
    start_address = models.ForeignKey(Address_ST, on_delete=models.CASCADE, related_name="routepart_start", db_column="StartAddressID")
    end_address = models.ForeignKey(Address_ST, on_delete=models.CASCADE, related_name="routepart_end", db_column="EndAddressID")
    route_cost = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "RouteParts_ST"


class WorkSchedule_ST(models.Model):
    schedule_id = models.AutoField(primary_key=True, db_column="Schedule_id")
    user = models.ForeignKey(UserProfile_ST, on_delete=models.CASCADE, db_column="User_id")
    work_day = models.CharField(max_length=255, null=True, blank=True)
    start_time = models.CharField(max_length=255, null=True, blank=True)
    end_time = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "WorkSchedules_ST"




class Vehicle_ST(models.Model):
    vehicle_id = models.AutoField(primary_key=True, db_column="VehicleID")
    brand = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    production_year = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    fuel_type = models.CharField(max_length=255, null=True, blank=True)
    consumption = models.CharField(max_length=255, null=True, blank=True)
    full_capacity = models.CharField(max_length=255, null=True, blank=True)
    free_capacity = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    address = models.ForeignKey(Address_ST, on_delete=models.CASCADE, db_column="AddressID", null=True, blank=True)
    avg_distance_per_hour = models.CharField(max_length=255, null=True, blank=True)
    fuel_cost = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Vehicles_ST"




class Product_ST(models.Model):
    product_id = models.AutoField(primary_key=True, db_column="ProductID")
    name = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    unit_price = models.CharField(max_length=255, null=True, blank=True)
    size = models.CharField(max_length=255, null=True, blank=True)
    is_alive = models.CharField(max_length=255, null=True, blank=True)
    is_liquid = models.CharField(max_length=255, null=True, blank=True)
    is_hazardous = models.CharField(max_length=255, null=True, blank=True)
    is_time_sensitive = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Products_ST"




class WarehouseProduct_ST(models.Model):
    product = models.ForeignKey(Product_ST, on_delete=models.CASCADE, db_column="PRODUCTID")
    warehouse = models.ForeignKey(Warehouse_ST, on_delete=models.CASCADE, db_column="WAREHOUSEID")
    free_stock = models.CharField(max_length=255, null=True, blank=True)
    reserved_stock = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "WarehouseProducts_ST"
        unique_together = ("product", "warehouse")



class Order_ST(models.Model):
    order_id = models.AutoField(primary_key=True, db_column="OrderID")
    user = models.ForeignKey(UserProfile_ST, on_delete=models.CASCADE, db_column="UserID")
    product = models.ForeignKey(Product_ST, on_delete=models.CASCADE, db_column="ProductID")
    warehouse_connection = models.ForeignKey(WarehouseConnection_ST, on_delete=models.CASCADE, db_column="WarehouseConnectionID")
    route = models.ForeignKey(Route_ST, on_delete=models.CASCADE, db_column="RouteID")
    quantity = models.CharField(max_length=255, null=True, blank=True)
    order_date = models.CharField(max_length=255, null=True, blank=True)
    expected_fullfillment_date = models.CharField(max_length=255, null=True, blank=True)
    fulfillment_date = models.CharField(max_length=255, null=True, blank=True)
    order_status = models.CharField(max_length=255, null=True, blank=True)
    expected_co2_emission = models.CharField(max_length=255, null=True, blank=True)
    co2_emmission = models.CharField(max_length=255, null=True, blank=True)
    cost = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Orders_ST"



class Shipment_ST(models.Model):
    shipment_id = models.AutoField(primary_key=True, db_column="ShipmentID")
    order = models.ForeignKey(Order_ST, on_delete=models.CASCADE, db_column="OrderID")
    vehicle = models.ForeignKey(Vehicle_ST, on_delete=models.CASCADE, db_column="VehicleID")
    product = models.ForeignKey(Product_ST, on_delete=models.CASCADE, db_column="ProductID")
    route_part = models.ForeignKey(RoutePart_ST, on_delete=models.CASCADE, db_column="RoutePartsID")
    shipment_start_date = models.CharField(max_length=255, null=True, blank=True)
    shipment_end_date = models.CharField(max_length=255, null=True, blank=True)
    duration = models.CharField(max_length=255, null=True, blank=True)
    quantity_transported = models.CharField(max_length=255, null=True, blank=True)
    fuel_consumed = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    co2_emission = models.CharField(max_length=255, null=True, blank=True)
    transport_cost = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Shipments_ST"



class UserShipments_ST(models.Model):
    user = models.ForeignKey(UserProfile_ST, on_delete=models.CASCADE, db_column="UserID")
    shipment = models.ForeignKey(Shipment_ST, on_delete=models.CASCADE, db_column="ShipmentID")

    class Meta:
        db_table = "UserShipments_ST"
        unique_together = ("user", "shipment")
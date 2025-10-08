from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class City(models.Model):
    city_id = models.AutoField(primary_key=True, db_column="CityID")
    country = models.CharField(max_length=255,null=True, blank=True)
    continent = models.CharField(max_length=255,null=True, blank=True)
    name = models.CharField(max_length=255,null=True, blank=True)
    has_airport = models.BooleanField(null=True, blank=True)
    has_harbour = models.BooleanField(null=True, blank=True)
    longitude_coordinate = models.FloatField(null=True, blank=True)
    latitude_coordinate = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "Cities"


class Address(models.Model):
    address_id = models.AutoField(primary_key=True, db_column="AddressID")
    city = models.ForeignKey(City, on_delete=models.CASCADE, db_column="CityID")
    street = models.CharField(max_length=255, null=True, blank=True)
    house_number = models.CharField(max_length=255, null=True, blank=True)
    institution_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Addresses"


class UserProfile(models.Model):
    # owner
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile',db_column="UserID")
    
    #settings
    is_full_name_displayed=models.BooleanField(default=True)

    # database fields
    email = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        db_column="AddressID",
        null=True,
        blank=True
    )
    job = models.CharField(max_length=255, null=True, blank=True)
    rights = models.CharField(max_length=255, null=True, blank=True)
    hiring_date = models.DateField(null=True, blank=True)
    co2_saved = models.FloatField(null=True, blank=True)
    salary = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = "Users"
        permissions = [
            ("admin_tasks", "Is able to proceed with admin related tasks"),
            ("organiser_tasks", "Is able to proceed with tasks related to organisers"),
            ("driver_tasks", "Is able to proceed with tasks related to drivers"),
            ("warehouseman_tasks", "Is able to proceed with tasks related to warehousemen"),
            ("manager_tasks", "Is able to proceed with tasks related to managers"),
        ]

class Warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True, db_column="WarehouseID")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, db_column="AddressID")
    capacity = models.IntegerField(null=True, blank=True)
    fullness = models.IntegerField(null=True, blank=True)
    contact_email = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Warehouses"


class WarehouseConnection(models.Model):
    warehouse_connection_id = models.AutoField(primary_key=True, db_column="WarehouseConnectionID")
    warehouse1 = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="connection_warehouse1", db_column="Warehouse1")
    warehouse2 = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="connection_warehouse2", db_column="Warehouse2")
    is_in_different_country = models.BooleanField(null=True, blank=True)
    is_in_different_continent = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = "WarehouseConnections"


class Route(models.Model):
    route_id = models.AutoField(primary_key=True, db_column="RouteID")
    warehouse_connection = models.ForeignKey(WarehouseConnection, on_delete=models.CASCADE, db_column="WarehouseConnectionID")

    class Meta:
        db_table = "Routes"


class RoutePart(models.Model):
    route_part_id = models.AutoField(primary_key=True, db_column="RoutePartID")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, db_column="RouteID")
    distance = models.FloatField()
    transport_mode = models.CharField(max_length=255)
    start_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="routepart_start", db_column="StartAddressID")
    end_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="routepart_end", db_column="EndAddressID")
    route_cost = models.FloatField()

    class Meta:
        db_table = "RouteParts"

class WorkSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True, db_column="Schedule_id")
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column="User_id")
    work_day = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "WorkSchedules"


class Vehicle(models.Model):
    vehicle_id = models.AutoField(primary_key=True, db_column="VehicleID")
    brand = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    production_year = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    fuel_type = models.CharField(max_length=255, null=True, blank=True)
    consumption = models.FloatField(null=True, blank=True)
    full_capacity = models.FloatField(null=True, blank=True)
    free_capacity = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, db_column="AddressID", null=True, blank=True)
    avg_distance_per_hour = models.FloatField(null=True, blank=True)
    fuel_cost = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "Vehicles"


class Product(models.Model):
    product_id = models.AutoField(primary_key=True, db_column="ProductID")
    name = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    unit_price = models.FloatField(null=True, blank=True)
    size = models.FloatField(null=True, blank=True)
    is_alive = models.BooleanField(null=True, blank=True)
    is_liquid = models.BooleanField(null=True, blank=True)
    is_hazardous = models.BooleanField(null=True, blank=True)
    is_time_sensitive = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = "Products"


class WarehouseProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column="PRODUCTID")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, db_column="WAREHOUSEID")
    free_stock = models.IntegerField(null=True, blank=True)
    reserved_stock = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "WarehouseProducts"
        unique_together = ("product", "warehouse")


class Order(models.Model):
    order_id = models.AutoField(primary_key=True, db_column="OrderID")
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column="UserID")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column="ProductID")
    warehouse_connection = models.ForeignKey(WarehouseConnection, on_delete=models.CASCADE, db_column="WarehouseConnectionID")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, db_column="RouteID")
    quantity = models.IntegerField()
    order_date = models.DateField(null=True, blank=True)
    expected_fullfillment_date = models.DateField(null=True, blank=True)
    fulfillment_date = models.DateField(null=True, blank=True)
    order_status = models.CharField(max_length=255, null=True, blank=True)
    expected_co2_emission = models.FloatField(null=True, blank=True)
    co2_emmission = models.FloatField(null=True, blank=True)
    cost = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "Orders"


class Shipment(models.Model):
    shipment_id = models.AutoField(primary_key=True, db_column="ShipmentID")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column="OrderID")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, db_column="VehicleID")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column="ProductID")
    route_part = models.ForeignKey(RoutePart, on_delete=models.CASCADE, db_column="RoutePartsID")
    shipment_start_date = models.DateTimeField(null=True, blank=True)
    shipment_end_date = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    quantity_transported = models.IntegerField(null=True, blank=True)
    fuel_consumed = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    co2_emission = models.FloatField(null=True, blank=True)
    transport_cost = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "Shipments"


class UserShipment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column="UserID")
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, db_column="ShipmentID")

    class Meta:
        db_table = "UserShipments"
        unique_together = ("user", "shipment")


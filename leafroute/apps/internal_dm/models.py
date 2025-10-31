from django.db import models

# Create your models here.
class DimOrder(models.Model):
    orderid = models.AutoField(primary_key=True)
    orderstatus = models.CharField(max_length=255,null=True, blank=True)
    userfirstname = models.CharField(max_length=255,null=True, blank=True)
    userlastname = models.CharField(max_length=255,null=True, blank=True)
    useremail = models.CharField(max_length=255,null=True, blank=True)

    def __str__(self):
        return f"Order {self.orderid} ({self.orderstatus})"
    
    class Meta:
        db_table = "DIMORDER"


class DimVehicle(models.Model):
    vehicleid = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=255,null=True, blank=True)
    model = models.CharField(max_length=255,null=True, blank=True)
    type = models.CharField(max_length=255,null=True, blank=True)
    fueltype = models.CharField(max_length=255,null=True, blank=True)

    def __str__(self):
        return f"{self.brand} {self.model}"
    
    class Meta:
        db_table = "DIMVEHICLE"    


class DimProduct(models.Model):
    productid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255,null=True, blank=True)
    category = models.CharField(max_length=255,null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "DIMPRODUCT"


class DimRoute(models.Model):
    routeid = models.AutoField(primary_key=True)
    startcity = models.CharField(max_length=255,null=True, blank=True)
    endcity = models.CharField(max_length=255,null=True, blank=True)

    def __str__(self):
        return f"{self.startcity} → {self.endcity}"
    
    class Meta:
        db_table = "DIMROUTE"     


class DimDate(models.Model):
    dateid = models.IntegerField(primary_key=True, db_column="DateID")
    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    monthname = models.CharField(max_length=20,null=True, blank=True)
    day = models.IntegerField(null=True, blank=True)
    dayname = models.CharField(max_length=20,null=True, blank=True)
    hour = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.year}-{self.month:02}-{self.day:02} {self.hour:02}:00"
    
    class Meta:
        db_table = "DIMDATE"    


class FactShipment(models.Model):
    shipmentid = models.AutoField(primary_key=True)
    duration = models.IntegerField(null=True, blank=True)
    quantitytransported = models.IntegerField(null=True, blank=True)
    fuelconsumed = models.IntegerField(null=True, blank=True)
    co2emission = models.FloatField(null=True, blank=True)
    transportcost = models.FloatField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    routecost = models.FloatField(null=True, blank=True)
    unitprice = models.FloatField(null=True, blank=True)
    consumption = models.FloatField(null=True, blank=True)
    fuelcost = models.FloatField(null=True, blank=True)
    productionyear = models.IntegerField(null=True, blank=True)

    orderid = models.ForeignKey(DimOrder, on_delete=models.CASCADE, db_column="OrderID")
    productid = models.ForeignKey(DimProduct, on_delete=models.CASCADE, db_column="ProductID")
    routeid = models.ForeignKey(DimRoute, on_delete=models.CASCADE, db_column="RouteID")
    vehicleid = models.ForeignKey(DimVehicle, on_delete=models.CASCADE, db_column="VehicleID")
    shipmentstartdate = models.ForeignKey('DimDate', on_delete=models.PROTECT, 
                                       related_name='shipments_started', 
                                       db_column="SHIPMENTSTARTDATE")
    shipmentenddate = models.ForeignKey('DimDate', on_delete=models.PROTECT, 
                                     related_name='shipments_ended', 
                                     db_column="SHIPMENTENDDATE")

    def __str__(self):
        return f"Shipment {self.shipmentid} ({self.shipmentstartdate} → {self.shipmentenddate})"
    
    class Meta:
        db_table = "FACTSHIPMENT"
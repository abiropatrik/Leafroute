from django.contrib import admin

# Register your models here.
from .models import RoutePart_ST, Address_ST, City_ST, Route_ST, Warehouse_ST, WarehouseConnection_ST, WorkSchedule_ST, Vehicle_ST

admin.site.register(RoutePart_ST)
admin.site.register(Address_ST)
admin.site.register(City_ST)
admin.site.register(Route_ST)
admin.site.register(Warehouse_ST)
admin.site.register(WarehouseConnection_ST)
admin.site.register(WorkSchedule_ST)
admin.site.register(Vehicle_ST)

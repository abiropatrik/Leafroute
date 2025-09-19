from django.urls import path
from . import views

app_name = "internal"

urlpatterns = [
    path('internal/new_transport', views.new_transport, name="new_transport"),
    path('internal/new_route', views.new_route, name="new_route"),
    path('internal/vehicle_settings', views.vehicle_settings, name="vehicle_settings"),
    path('internal/warehouse_settings', views.warehouse_settings, name="warehouse_settings"),
    path('internal/dashboards', views.dashboards, name="dashboards"),
]
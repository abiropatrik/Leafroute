from django.urls import path
from . import views

app_name = "internal"

urlpatterns = [
    path('internal/workschedule', views.workschedule, name="workschedule"),
    path('internal/new_transport', views.new_transport, name="new_transport"),
    path('internal/new_route', views.new_route, name="new_route"),
    path('internal/vehicle_settings', views.vehicle_settings, name="vehicle_settings"),
    path('internal/warehouse_settings', views.warehouse_settings, name="warehouse_settings"),
    path('internal/dashboards', views.dashboards, name="dashboards"),
    path('internal/shipments', views.shipments, name="shipments"),
    path('internal/workschedule/update/<int:pk>/', views.workschedule_update, name="workschedule_update"),
    path('internal/workschedule/delete/<int:pk>/', views.workschedule_delete, name="workschedule_delete"),
    path('internal/vehicle/delete/<int:pk>/', views.vehicle_delete, name="vehicle_delete"),
    path('internal/vehicle/update/<int:pk>/', views.vehicle_update, name="vehicle_update"),
    path('internal/warehouse/delete/<int:pk>/', views.warehouse_delete, name="warehouse_delete"),
    path('internal/warehouse/update/<int:pk>/', views.warehouse_update, name="warehouse_update"),
    path('internal/ajax/load-products/', views.load_products, name='ajax_load_products'),
    path('internal/new_transport_route', views.new_transport_route, name="new_transport_route"),
    path('internal/ajax/route-parts/', views.ajax_route_parts, name='ajax_route_parts'),
    path('internal/shipment/activate/<int:pk>/', views.activate_shipment, name='activate_shipment'),
    path('internal/shipment/update/<int:pk>/', views.shipment_update, name="shipment_update"),
]
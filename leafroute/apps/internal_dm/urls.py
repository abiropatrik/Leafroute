from django.urls import path
from . import views

app_name = "internal_dm"

urlpatterns = [
    path('internal_dm/dashboards', views.dashboards, name='dashboards'),
]
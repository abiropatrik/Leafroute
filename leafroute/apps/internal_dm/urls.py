from django.urls import path
from . import views

app_name = "internal_stage"

urlpatterns = [
    path('dashboards/', views.dashboards_page, name='dashboards_page'),
]
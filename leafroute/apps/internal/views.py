from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse,HttpRequest
from django.contrib.auth.decorators import login_required, permission_required
from functools import wraps
from django.core.exceptions import PermissionDenied
import csv
from django.contrib import messages
from leafroute.apps.internal_stage.models import Route_ST, WarehouseConnection_ST, WorkSchedule_ST,Vehicle_ST,Warehouse_ST,Address_ST,City_ST
from leafroute.apps.internal.forms import RouteForm, WarehouseConnectionForm, WorkScheduleForm,VehicleForm,WarehouseForm,AddressForm,CityForm


def permission_or_required(*perms):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not any(request.user.has_perm(perm) for perm in perms):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

@login_required
def workschedule(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        # Handle CSV Upload
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a valid CSV file.')
                return redirect('internal: workschedule')

            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file, delimiter=';')
                for row in reader:
                    WorkSchedule_ST.objects.using('stage').create(
                        user=request.user.username,
                        work_day=row['work_day'],
                        start_time=row['start_time'],
                        end_time=row['end_time']
                    )
                messages.success(request, 'Work schedules uploaded successfully!')
            except Exception as e:
                messages.error(request, f"Error uploading CSV: {e}")
            return redirect('internal:workschedule')

        # Handle Manual Entry
        else:
            form = WorkScheduleForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user.username
                instance.save(using='stage')
                messages.success(request, 'Work schedule added successfully!')
            else:
                messages.error(request, 'Error adding work schedule.')
            return redirect('internal:workschedule')

    else:
        form = WorkScheduleForm()
        # Query all work schedules ordered by work_day descending
        work_schedules = WorkSchedule_ST.objects.using('stage').filter(user=request.user.username).order_by('-work_day')
        return render(request, 'internal/workschedule.html', {'form': form, 'work_schedules': work_schedules})
    
@login_required
@permission_required('internal.organiser_tasks', raise_exception=True)
def vehicle_settings(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        # Handle CSV Upload
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a valid CSV file.')
                return redirect('internal: vehicle_settings')

            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file, delimiter=';')
                for row in reader:
                    Vehicle_ST.objects.using('stage').create(
                        brand=row['brand'], #no pk. will this work?
                        model=row['model'],
                        production_year=row['production_year'],
                        type=row['type'],
                        fuel_type=row['fuel_type'],
                        consumption=row['consumption'],
                        full_capacity=row['full_capacity'],
                        free_capacity=row['free_capacity'],
                        status=row['status'],
                        avg_distance_per_hour=row['avg_distance_per_hour'],
                        fuel_cost=row['fuel_cost']
                    )
                messages.success(request, 'Vehicle uploaded successfully!')
            except Exception as e:
                messages.error(request, f"Error uploading CSV: {e}")
            return redirect('internal:vehicle_settings')

        # Handle Manual Entry
        else:
            form = VehicleForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user.username
                instance.save(using='stage')
                messages.success(request, 'Vehicle added successfully!')
            else:
                messages.error(request, 'Error adding vehicle.')
            return redirect('internal:vehicle_settings')

    else:
        form = VehicleForm()
        vehicles = Vehicle_ST.objects.using('stage')
        return render(request, 'internal/vehicle_settings.html', {'form': form, 'vehicles': vehicles})

@login_required
@permission_or_required('internal.organiser_tasks')
def new_transport(request: HttpRequest) -> HttpResponse:
    return render(request,'internal/new_transport.html')

@login_required
@permission_required('internal.organiser_tasks', raise_exception=True)
def new_route(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        warehouse_conn_form = WarehouseConnectionForm(request.POST)
        route_form = RouteForm(request.POST)

        if warehouse_conn_form.is_valid() and route_form.is_valid():
            warehouse_conn_instance = warehouse_conn_form.save(commit=False)
            warehouse_conn_instance.save(using='stage')

            route_instance = route_form.save(commit=False)
            route_instance.warehouse_connection = warehouse_conn_instance
            route_instance.save(using='stage')

            messages.success(request, 'New route added successfully!')
        else:
            errors = {
                'warehouse_conn_form': warehouse_conn_form.errors,
                'route_form': route_form.errors,
            }
            for form_name, form_errors in errors.items():
                if form_errors:
                    print(f"{form_name} errors: {form_errors}")
            messages.error(request, 'Error adding route. Please check the form inputs.')
        return redirect('internal:new_route')

    else:
        warehouse_conn_form = WarehouseConnectionForm()
        route_form = RouteForm()
        return render(request, 'internal/new_route.html', {
            'warehouse_conn_form': warehouse_conn_form,
            'route_form': route_form,
        })

@login_required
@permission_required('internal.organiser_tasks', raise_exception=True)
def warehouse_settings(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        warehouse_form = WarehouseForm(request.POST)
        address_form = AddressForm(request.POST)
        city_form= CityForm(request.POST)
        if address_form.is_valid() and warehouse_form.is_valid() and city_form.is_valid():
            city_instance = city_form.save(commit=False)
            city_instance.save(using='stage')
            address_instance = address_form.save(commit=False)
            address_instance.city = city_instance
            address_instance.save(using='stage')
            warehouse_instance = warehouse_form.save(commit=False)
            warehouse_instance.address = address_instance
            warehouse_instance.save(using='stage')
            messages.success(request, 'Warehouse added successfully!')
        else:
            messages.error(request, 'Error adding warehouse.')
        return redirect('internal:warehouse_settings')

    else:
        warehouse_form = WarehouseForm()
        warehouses = Warehouse_ST.objects.using('stage')
        address_form = AddressForm()
        addresses= Address_ST.objects.using('stage')
        city_form= CityForm()
        cities= City_ST.objects.using('stage')
        return render(request, 'internal/warehouse_settings.html', {'warehouse_form': warehouse_form, 'warehouses': warehouses, 'address_form': address_form, 'addresses': addresses, 'city_form': city_form, 'cities': cities})

@login_required
@permission_or_required('internal.organiser_tasks','internal.manager_tasks')
def dashboards(request: HttpRequest) -> HttpResponse:
    return render(request,'internal/dashboards.html')

@login_required
@permission_or_required('internal.driver_tasks')
def shipments(request: HttpRequest) -> HttpResponse:
    return render(request,'internal/shipments.html')

@login_required
def workschedule_update(request: HttpRequest, pk: int) -> HttpResponse:
    schedule = get_object_or_404(WorkSchedule_ST, pk=pk, user=request.user.username)
    if request.method == 'POST':
        form = WorkScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save(using='stage')
            messages.success(request, 'Work schedule updated successfully!')
            return redirect('internal:workschedule')
        else:
            messages.error(request, 'Error updating work schedule.')
    else:
        form = WorkScheduleForm(instance=schedule)
    return render(request, 'internal/workschedule_update.html', {'form': form})

@login_required
def workschedule_delete(request: HttpRequest, pk: int) -> HttpResponse:
    schedule = get_object_or_404(WorkSchedule_ST, pk=pk, user=request.user.username)
    if request.method == 'POST':
        schedule.delete(using='stage')
        messages.success(request, 'Work schedule deleted successfully!')
        return redirect('internal:workschedule')
    
@login_required
@permission_required('internal.organiser_tasks', raise_exception=True)
def vehicle_update(request: HttpRequest, pk: int) -> HttpResponse:
    vehicle = get_object_or_404(Vehicle_ST, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save(using='stage')
            messages.success(request, 'Vehicle updated successfully!')
            return redirect('internal:vehicle_settings')
        else:
            messages.error(request, 'Error updating vehicle.')
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'internal/vehicle_update.html', {'form': form})

@login_required
@permission_required('internal.organiser_tasks', raise_exception=True)
def vehicle_delete(request: HttpRequest, pk: int) -> HttpResponse:
    vehicle = get_object_or_404(Vehicle_ST, pk=pk)
    if request.method == 'POST':
        vehicle.delete(using='stage')
        messages.success(request, 'Vehicle deleted successfully!')
        return redirect('internal:vehicle_settings')
    return render(request, 'internal/vehicle_delete.html', {'vehicle': vehicle})

@login_required
@permission_required('internal.organiser_tasks', raise_exception=True)
def warehouse_update(request: HttpRequest, pk: int) -> HttpResponse:
    warehouse = get_object_or_404(Warehouse_ST, pk=pk)
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save(using='stage')
            messages.success(request, 'Warehouse updated successfully!')
            return redirect('internal:warehouse_settings')
        else:
            messages.error(request, 'Error updating warehouse.')
    else:
        form = WarehouseForm(instance=warehouse)
    return render(request, 'internal/warehouse_update.html', {'form': form})

@login_required
@permission_required('internal.organiser_tasks', raise_exception=True)
def warehouse_delete(request: HttpRequest, pk: int) -> HttpResponse:
    warehouse = get_object_or_404(Warehouse_ST, pk=pk)
    if request.method == 'POST':
        warehouse.delete(using='stage')
        messages.success(request, 'Warehouse deleted successfully!')
        return redirect('internal:warehouse_settings')
    return render(request, 'internal/warehouse_delete.html', {'warehouse': warehouse})
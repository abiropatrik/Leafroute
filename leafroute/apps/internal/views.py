from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse,HttpRequest
from django.contrib.auth.decorators import login_required, permission_required
from functools import wraps
from django.core.exceptions import PermissionDenied
import csv
from django.contrib import messages
from leafroute.apps.internal_stage.models import WorkSchedule_ST,Vehicle_ST,Warehouse_ST
from leafroute.apps.internal.forms import WorkScheduleForm,VehicleForm,WarehouseForm


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
    return render(request,'internal/new_route.html')

@login_required
@permission_required('internal.organiser_tasks', raise_exception=True)
def warehouse_settings(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        # Handle CSV Upload
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a valid CSV file.')
                return redirect('internal: warehouse_settings')

            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file, delimiter=';')
                for row in reader:
                    Warehouse_ST.objects.using('stage').create(
                        address=row['address'], #no pk. will this work?
                        capacity=row['capacity'],
                        fullness=row['fullness'],
                        contact_email=row['contact_email'],
                    )
                messages.success(request, 'Warehouse uploaded successfully!')
            except Exception as e:
                messages.error(request, f"Error uploading CSV: {e}")
            return redirect('internal:warehouse_settings')

        # Handle Manual Entry
        else:
            form = WarehouseForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user.username
                instance.save(using='stage')
                messages.success(request, 'Warehouse added successfully!')
            else:
                messages.error(request, 'Error adding warehouse.')
            return redirect('internal:warehouse_settings')

    else:
        form = WarehouseForm()
        warehouses = Warehouse_ST.objects.using('stage')
        return render(request, 'internal/warehouse_settings.html', {'form': form, 'warehouses': warehouses})

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
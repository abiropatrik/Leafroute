from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse,HttpRequest
from django.contrib.auth.decorators import login_required, permission_required
from functools import wraps
from django.core.exceptions import PermissionDenied
import csv
from django.contrib import messages
from leafroute.apps.internal_stage.models import WorkSchedule_ST
from leafroute.apps.internal.forms import WorkScheduleForm


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
@permission_or_required('internal.organiser_tasks')
def new_transport(request: HttpRequest) -> HttpResponse:
    return render(request,'internal/new_transport.html')

@login_required
@permission_required('internal.organiser_tasks', raise_exception=True)
def new_route(request: HttpRequest) -> HttpResponse:
    return render(request,'internal/new_route.html')

@login_required
@permission_required('internal.organiser_tasks', raise_exception=True)
def vehicle_settings(request: HttpRequest) -> HttpResponse:
    return render(request,'internal/vehicle_settings.html')

@login_required
@permission_required('internal.organiser_tasks', raise_exception=True)
def warehouse_settings(request: HttpRequest) -> HttpResponse:
    return render(request,'internal/warehouse_settings.html')

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
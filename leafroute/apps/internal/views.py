from urllib import request
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse,HttpRequest,HttpResponseForbidden,JsonResponse,HttpResponseBadRequest
from django.contrib.auth.decorators import login_required, permission_required
from functools import wraps
from django.core.exceptions import PermissionDenied
import csv
from django.contrib import messages
from leafroute.apps.internal.models import UserProfile
from leafroute.apps.internal_stage.models import Shipment_ST,RoutePart_ST,Order_ST,Product_ST,Route_ST, WarehouseConnection_ST, WorkSchedule_ST,Vehicle_ST,Warehouse_ST,Address_ST,City_ST,UserShipments_ST
from leafroute.apps.internal.forms import OrderForm,RouteForm, WarehouseConnectionForm, WorkScheduleForm,VehicleForm,WarehouseForm,AddressForm,CityForm,ShipmentForm
from leafroute.apps.internal.utils import tempshipment
from django.views.decorators.http import require_GET,require_POST
from datetime import datetime, timedelta


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
        # CSV Upload
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
                        user=request.user.id,
                        work_day=row['work_day'],
                        start_time=row['start_time'],
                        end_time=row['end_time']
                    )
                messages.success(request, 'Work schedules uploaded successfully!')
            except Exception as e:
                messages.error(request, f"Error uploading CSV: {e}")
            return redirect('internal:workschedule')

        # Manual Entry
        else:
            form = WorkScheduleForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user.id
                instance.save(using='stage')
                messages.success(request, 'Work schedule added successfully!')
            else:
                messages.error(request, 'Error adding work schedule.')
            return redirect('internal:workschedule')

    else:
        form = WorkScheduleForm()
        work_schedules = WorkSchedule_ST.objects.using('stage').filter(user=request.user.id).order_by('-work_day')
        return render(request, 'internal/workschedule.html', {'form': form, 'work_schedules': work_schedules})
    
@login_required
@permission_or_required('internal.organiser_tasks','internal.driver_tasks','internal.warehouseman_tasks')
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
        if request.user.has_perm('internal.organiser_tasks'):
            vehicles = Vehicle_ST.objects.using('stage')
        elif request.user.has_perm('internal.driver_tasks'):
            usershipments=UserShipments_ST.objects.using('stage').filter(user=request.user.id)
            shipment_ids = usershipments.values_list('shipment_id', flat=True)
            shipments = Shipment_ST.objects.using('stage').filter(shipment_id__in=shipment_ids)
            vehicle_ids = shipments.values_list('vehicle_id', flat=True).distinct()
            vehicles = Vehicle_ST.objects.using('stage').filter(pk__in=vehicle_ids)
        elif request.user.has_perm('internal.warehouseman_tasks'):
            currentlocation=UserProfile.objects.using('default').get(pk=request.user.id).address.address_id
            vehicles = Vehicle_ST.objects.using('stage').filter(address=currentlocation)

        return render(request, 'internal/vehicle_settings.html', {'form': form, 'vehicles': vehicles})

@login_required
@permission_or_required('internal.organiser_tasks')
def new_transport(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        order_form = OrderForm(request.POST)

        if order_form.is_valid():
            request.session['new_transport_data'] = {
                'warehouse_connection': order_form.cleaned_data['warehouse_connection'].warehouse_connection_id,
                'product': order_form.cleaned_data['product'].product_id,
                'quantity': order_form.cleaned_data['quantity'],
            }
            return redirect('internal:new_transport_route')

        else:

            messages.error(request, 'Error adding transport. Please check the form inputs.')

    else:
        order_form = OrderForm()

    return render(request, 'internal/new_transport.html', {
        'order_form': order_form,
    })


@login_required
@permission_or_required('internal.organiser_tasks')
def new_transport_route(request):
    transport_data = request.session.get('new_transport_data')
    if not transport_data:
        messages.error(request, 'No transport data found. Please start again.')
        return redirect('internal:new_transport')

    related_product = Product_ST.objects.using('stage').get(product_id=transport_data['product']) 
    quantity = int(transport_data['quantity'])

    routes = Route_ST.objects.using('stage').filter(
        warehouse_connection_id=transport_data['warehouse_connection']
    )

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order_instance = order_form.save(commit=False)
            order_instance.warehouse_connection_id = transport_data['warehouse_connection']
            order_instance.product_id = transport_data['product']
            order_instance.quantity = transport_data['quantity']
            order_instance.order_date = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            order_instance.order_status = 'pending'

            route_id = request.POST.get('route')
            if route_id:
                order_instance.route_id = route_id

            co2_raw = request.POST.get('expected_co2_emission', '') or ''
            duration_raw = request.POST.get('expected_duration', '') or '0'

            try:
                order_instance.expected_co2_emission = float(co2_raw)
            except (TypeError, ValueError):
                order_instance.expected_co2_emission = 0.0
                messages.warning(request, f'Invalid CO₂ value "{co2_raw}". Saved as 0.0.')

            try:
                duration_hours = float(duration_raw)
                expected_dt = timezone.now() + timedelta(hours=duration_hours)
                order_instance.expected_fullfillment_date = expected_dt.strftime('%Y-%m-%d %H:%M:%S')
            except (TypeError, ValueError):
                order_instance.expected_fullfillment_date = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                messages.warning(request, f'Invalid duration value "{duration_raw}". Defaulted to current time.')

            order_instance.user = str(request.user.id)
            order_instance.save(using='stage')

            try:
                selected_route = Route_ST.objects.using('stage').get(pk=route_id)
                route_parts = RoutePart_ST.objects.using('stage').filter(route=selected_route)

                for part in route_parts:
                    vehicle, emission, user, duration, cost = tempshipment(part,related_product.product_id,quantity)

                    vehicle_object=Vehicle_ST.objects.using('stage').get(pk=vehicle.vehicle_id)
                    shipment_instance=Shipment_ST.objects.using('stage').create(
                        order=order_instance,
                        vehicle=vehicle_object,
                        product_id=transport_data['product'],
                        route_part=part,
                        status='pending',
                    )
                    UserShipments_ST.objects.using('stage').get_or_create(
                        user=user.user_id,
                        shipment=shipment_instance
                    )
                    vehicle_object.status='loading'
                    vehicle_object.save(using='stage')


            except Exception as e:
                messages.error(request, f'Error creating shipments: {e}')

            messages.success(request, 'New transport and shipments added successfully.')
            del request.session['new_transport_data']
            return redirect('internal:new_transport')

        else:
            messages.error(request, f'Error adding transport. Please check form inputs: {order_form.errors}')

    else:
        order_form = OrderForm(initial={
            'warehouse_connection': transport_data['warehouse_connection'],
            'product': transport_data['product'],
            'quantity': transport_data['quantity'],
        })

    routes_with_stats = []
    for route in routes:
        parts = RoutePart_ST.objects.using('stage').filter(route=route)
        total_emission = total_duration = total_cost = 0.0
        used_vehicles = []
        route_is_viable = True

        for part in parts:
            vehicle, emission, user, duration, cost = tempshipment(part,related_product.product_id,quantity)
            if not vehicle or not user: 
                route_is_viable = False
                break
            used_vehicles.append(vehicle.type if vehicle else 'N/A')
            total_emission += emission or 0.0
            total_duration += duration or 0.0
            total_cost += cost or 0.0

        if route_is_viable:
            used_vehicles_str = " -> ".join(used_vehicles)
            routes_with_stats.append({
                'route': route,
                'used_vehicles': used_vehicles_str,
                'expected_emission': round(total_emission, 2),
                'expected_duration': round(total_duration, 2),
                'expected_cost': round(total_cost, 2),
            })

    routes_with_stats.sort(key=lambda x: x['expected_emission'])

    return render(request, 'internal/new_transport_route.html', {
        'order_form': order_form,
        'routes_with_stats': routes_with_stats,
        'routes': routes,
    })



@require_GET
@login_required
def ajax_route_parts(request):
    route_id = request.GET.get('route_id')
    if not route_id:
        return HttpResponseBadRequest('route_id missing')

    product_id = request.GET.get('product_id')
    quantity = int(request.GET.get('quantity', '0'))

    parts_qs = RoutePart_ST.objects.using('stage').select_related(
        'start_address', 'end_address', 'route__warehouse_connection__warehouse1'
    ).filter(route_id=route_id).order_by('route_part_id')

    parts_data = []
    total_emission = total_duration = total_cost = 0.0

    for p in parts_qs:
        vehicle, emission, user, duration, cost = tempshipment(p,product_id,quantity)
        total_emission += emission or 0.0
        total_duration += duration or 0.0
        total_cost += cost or 0.0

        parts_data.append({
            'id': p.route_part_id,
            'distance': p.distance,
            'mode': p.transport_mode,
            'start_address': p.start_address.institution_name if p.start_address else '',
            'end_address': p.end_address.institution_name if p.end_address else '',
            'vehicle': str(vehicle) if vehicle else 'N/A',
            'driver': str(user) if user else 'N/A',
            'emission': round(emission, 2),
            'duration': round(duration, 2),
            'cost': round(cost, 2),
        })

    return JsonResponse({
        'parts': parts_data,
        'aggregates': {
            'expected_emission': round(total_emission, 2),
            'expected_duration': round(total_duration, 2),
            'expected_cost': round(total_cost, 2),
        }
    })


@login_required
@permission_required('internal.organiser_tasks', raise_exception=True)
def new_route(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        warehouse_conn_form = WarehouseConnectionForm(request.POST)
        route_form = RouteForm(request.POST)

        if warehouse_conn_form.is_valid() and route_form.is_valid():
            warehouse1 = warehouse_conn_form.cleaned_data['warehouse1']
            warehouse2 = warehouse_conn_form.cleaned_data['warehouse2']
            existing_conn = WarehouseConnection_ST.objects.using('stage').filter(
                warehouse1=warehouse1,
                warehouse2=warehouse2
            ).first()

            if existing_conn:
                warehouse_conn_instance = existing_conn
            else:
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
@permission_or_required('internal.organiser_tasks', 'internal.warehouseman_tasks')
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
@permission_or_required('internal.driver_tasks')
def shipments(request: HttpRequest) -> HttpResponse:
    usershipments=UserShipments_ST.objects.using('stage').filter(user=request.user.id)
    shipment_ids = usershipments.values_list('shipment_id', flat=True)
    shipments = Shipment_ST.objects.using('stage').filter(shipment_id__in=shipment_ids, status__in =['active','pending'])
    return render(request, 'internal/shipments.html', {'shipments': shipments})


@login_required
@permission_or_required('internal.driver_tasks')
@require_POST  
def activate_shipment(request, pk):
    shipment = get_object_or_404(Shipment_ST, pk=pk)

    if shipment.status == 'pending':
        shipment.status = 'active'
        shipment.vehicle.status = 'moving'
        shipment.shipment_start_date=timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        shipment.save()
        shipment.vehicle.save()
        messages.success(request, f"Shipment {shipment.shipment_id} has been started.")

    return redirect('internal:shipments')

@login_required
@permission_or_required('internal.driver_tasks')
@require_POST  
def completing_shipment(request, pk):
    shipment = get_object_or_404(Shipment_ST, pk=pk)

    if shipment.status == 'active':
        shipment.status = 'done'
        shipment.vehicle.status='available'
        shipment.vehicle.address=shipment.route_part.end_address
        shipment.shipment_end_date=timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        shipment.save()
        shipment.vehicle.save()
        messages.success(request, f"Shipment {shipment.shipment_id} has been completed.")

    return redirect('internal:shipments')

@login_required
def workschedule_update(request: HttpRequest, pk: int) -> HttpResponse:
    schedule = get_object_or_404(WorkSchedule_ST, pk=pk, user=request.user.id)
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
    schedule = get_object_or_404(WorkSchedule_ST, pk=pk, user=request.user.id)
    if request.method == 'POST':
        schedule.delete(using='stage')
        messages.success(request, 'Work schedule deleted successfully!')
        return redirect('internal:workschedule')
    
@login_required
@permission_or_required('internal.organiser_tasks','internal.driver_tasks','internal.warehouseman_tasks')
def vehicle_update(request: HttpRequest, pk: int) -> HttpResponse:
    vehicle = get_object_or_404(Vehicle_ST, pk=pk)
    if request.method == 'POST':
        if request.user.has_perm('internal.organiser_tasks'):
            form = VehicleForm(request.POST, instance=vehicle)
        elif request.user.has_perm('internal.warehouseman_tasks'):
            form = VehicleForm(request.POST, instance=vehicle, fields=['free_capacity','status'])
        elif request.user.has_perm('internal.driver_tasks'):
            form = VehicleForm(request.POST, instance=vehicle, fields=['consumption', 'free_capacity','status','avg_distance_per_hour','fuel_cost'])
        else:
            return HttpResponseForbidden()
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save(using='stage')
            messages.success(request, 'Vehicle updated successfully!')
            return redirect('internal:vehicle_settings')
        else:
            messages.error(request, 'Error updating vehicle.')
    else:
        if request.user.has_perm('internal.organiser_tasks'):
            form = VehicleForm(instance=vehicle)
        elif request.user.has_perm('internal.warehouseman_tasks'):
            form = VehicleForm(instance=vehicle, fields=['free_capacity','status'])
        elif request.user.has_perm('internal.driver_tasks'):
            form = VehicleForm(instance=vehicle, fields=['consumption', 'free_capacity','status','avg_distance_per_hour','fuel_cost'])
        else:
            return HttpResponseForbidden()
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
@permission_or_required('internal.organiser_tasks', 'internal.warehouseman_tasks')
def warehouse_update(request: HttpRequest, pk: int) -> HttpResponse:
    warehouse = get_object_or_404(Warehouse_ST, pk=pk)
    if request.method == 'POST':
        if request.user.has_perm('internal.organiser_tasks'):
            form = WarehouseForm(request.POST, instance=warehouse)
        elif request.user.has_perm('internal.warehouseman_tasks'):
            form = WarehouseForm(request.POST, instance=warehouse, fields=['fullness'])
        else:
            return HttpResponseForbidden()
        
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save(using='stage')
            messages.success(request, 'Warehouse updated successfully!')
            return redirect('internal:warehouse_settings')
        else:
            messages.error(request, 'Error updating warehouse.')
    else:
        if request.user.has_perm('internal.organiser_tasks'):
            form = WarehouseForm(instance=warehouse)
        elif request.user.has_perm('internal.warehouseman_tasks'):
            form = WarehouseForm(instance=warehouse, fields=['fullness'])
        else:
            return HttpResponseForbidden()
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

@login_required
def load_products(request):
    """Return products for the given warehouse connection as JSON."""
    connection_id = request.GET.get('warehouse_connection')
    products = Product_ST.objects.none()

    if connection_id:
        try:
            connection = WarehouseConnection_ST.objects.using('stage').get(pk=connection_id)
            warehouse_id = connection.warehouse1_id
            products = Product_ST.objects.using('stage').filter(
                warehouseproduct_st__warehouse_id=warehouse_id
            ).distinct()
        except WarehouseConnection_ST.DoesNotExist:
            pass

    data = [
        {'id': p.pk, 'name': str(p)}
        for p in products
    ]
    return JsonResponse({'products': data})

from django.shortcuts import render
from django.http import HttpResponse,HttpRequest
from django.contrib.auth.decorators import login_required, permission_required
from functools import wraps
from django.core.exceptions import PermissionDenied

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
@permission_or_required('accounts.organiser_tasks')
def new_transport(request: HttpRequest) -> HttpResponse:
    return render(request,'internal/new_transport.html')

@login_required
@permission_required('accounts.organiser_tasks', raise_exception=True)
def new_route(request: HttpRequest) -> HttpResponse:
    return render(request,'internal/new_route.html')

@login_required
@permission_required('accounts.organiser_tasks', raise_exception=True)
def vehicle_settings(request: HttpRequest) -> HttpResponse:
    return render(request,'internal/vehicle_settings.html')

@login_required
@permission_required('accounts.organiser_tasks', raise_exception=True)
def warehouse_settings(request: HttpRequest) -> HttpResponse:
    return render(request,'internal/warehouse_settings.html')

@login_required
@permission_or_required('accounts.organiser_tasks','accounts.manager_tasks')
def dashboards(request: HttpRequest) -> HttpResponse:
    return render(request,'internal/dashboards.html')
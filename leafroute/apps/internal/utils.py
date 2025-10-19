from leafroute.apps.internal.models import Vehicle, UserProfile, RoutePart

def CO2_emission(distance: float, consumption: float, fuel_type: str) -> float:
    emission_factors = {
        'diesel': 2.717,
        'gasoline': 2.308,
        'kerosene': 2.588,
        'jet_kerosene': 2.582,
        'fuel_oil': 2.884,
        'propane': 0.509,
        'butane': 0.758,
        'electricity': 0.0,
    }
    return ((distance / 100) * consumption) * emission_factors.get(fuel_type.lower(), 0)


def vehicle_chooser(routepart: RoutePart):
    transport_mode = routepart.transport_mode

    if transport_mode == 'road':
        vehicletype = ['truck', 'van']
    elif transport_mode == 'rail':
        vehicletype = ['train']
    elif transport_mode == 'air':
        vehicletype = ['plane']
    elif transport_mode == 'sea':
        vehicletype = ['ship']
    else:
        vehicletype = []

    vehicles = Vehicle.objects.using('default').filter(
        address_id=routepart.start_address.address_id,
        type__in=vehicletype
    )

    def emission_for(vehicle):
        return CO2_emission(
            distance=float(routepart.distance or 0),
            consumption=float(vehicle.consumption or 0),
            fuel_type=vehicle.fuel_type
        )

    best_vehicle = min(vehicles, key=emission_for, default=None)

    if best_vehicle:
        best_emission = emission_for(best_vehicle)
        return best_vehicle, best_emission
    else:
        return None, 0.0


def user_chooser(routepart: RoutePart):
    transport_mode = routepart.transport_mode

    if transport_mode == 'road':
        required_job = ['driver']
    elif transport_mode == 'rail':
        required_job = ['train_operator']
    elif transport_mode == 'air':
        required_job = ['pilot']
    elif transport_mode == 'sea':
        required_job = ['captain']
    else:
        required_job = []

    users = UserProfile.objects.using('default').filter(
        address_id=routepart.start_address.address_id,
        job__in=required_job
    )
    print(users)
    return min(users, key=lambda u: u.co2_saved, default=None)


def tempshipment(routepart: RoutePart):
    vehicle, emission = vehicle_chooser(routepart)
    user = user_chooser(routepart)
    if not vehicle or not user:
        return None, 0.0, None, 0.0, 0.0

    duration = float(routepart.distance or 0) / float(vehicle.avg_distance_per_hour or 1)
    transportcost = (
        float(vehicle.consumption or 0) * (float(routepart.distance or 0) / 100) * float(vehicle.fuel_cost or 0)
        + duration * float(user.salary or 0)
    )

    return vehicle, emission, user, duration, transportcost

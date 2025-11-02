import plotly.express as px
import pandas as pd
from django.shortcuts import render
from django.db.models import Sum, Value, F,FloatField,IntegerField, Avg,Count
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
import plotly.graph_objects as go 

from leafroute.apps.internal.views import permission_or_required 
from .models import FactShipment 

@login_required
@permission_or_required('internal.organiser_tasks','internal.manager_tasks')
def dashboards(request):
    monthly_data = FactShipment.objects.values(
        'shipmentenddate__year', 
        'shipmentenddate__month'
    ).annotate(
        total_co2_g=Coalesce(Sum('co2emission'), Value(0.0)),
        total_volume_m3=Coalesce(Sum(F('quantitytransported') * F('productid__size')), Value(1.0), output_field=FloatField()) # m³ (elkerüljük a 0-val osztást, 1.0-t használva)
    ).order_by('shipmentenddate__year', 'shipmentenddate__month') 

    df_monthly = pd.DataFrame(list(monthly_data))

    if not df_monthly.empty:
        df_for_datetime = df_monthly.rename(columns={
            'shipmentenddate__year': 'year',
            'shipmentenddate__month': 'month'
        })
        df_for_datetime['day'] = 1
        
        df_monthly['month_dt'] = pd.to_datetime(df_for_datetime[['year', 'month', 'day']])

        df_monthly['co2_per_volume_kg_m3'] = df_monthly.apply(
            lambda row: (row['total_co2_g'] / 1000) / row['total_volume_m3'] if row['total_volume_m3'] > 0 else 0,
            axis=1
        )
        
        df_monthly['month_str'] = df_monthly['month_dt'].dt.strftime('%Y-%B')
        df_monthly = df_monthly.sort_values(by='month_dt')
        
    else:
        df_monthly = pd.DataFrame(columns=[
            'month_dt', 'month_str', 'co2_per_volume_kg_m3'
        ])


    fig_co2_volume = go.Figure()

    fig_co2_volume.add_trace(go.Scatter(
        x=df_monthly['month_dt'].tolist(),            
        y=df_monthly['co2_per_volume_kg_m3'].tolist(), 
        mode='lines+markers',                         
        name='CO2 / Térfogat'
    ))

    fig_co2_volume.update_layout(
        title='CO2 Kibocsátás / Szállított Térfogat (Havi Bontás)',
        xaxis_title='Hónap',
        yaxis_title='CO2 / Térfogat (kg/m³)'
    )

    if not df_monthly.empty:
        fig_co2_volume.update_xaxes(
            ticktext=df_monthly['month_str'].tolist(),
            tickvals=df_monthly['month_dt'].tolist()
        )

        if not df_monthly.empty:
            fig_co2_volume.update_xaxes(
                ticktext=df_monthly['month_str'].tolist(),
                tickvals=df_monthly['month_dt'].tolist() 
        )

    chart_co2_volume_div = fig_co2_volume.to_html(include_plotlyjs=False, full_html=False)

    ######################################################################################
    ####co2/distance
    ######################################################################################
    vehicle_data = FactShipment.objects.values(
        'vehicleid__type' 
    ).annotate(
        total_co2=Coalesce(Sum('co2emission'), Value(0.0)),
        total_distance=Coalesce(Sum('distance'), Value(1.0), output_field=FloatField()) 
    ).order_by('vehicleid__type')

    df_vehicle = pd.DataFrame(list(vehicle_data))

    if not df_vehicle.empty:
        df_vehicle['co2_g_per_km'] = df_vehicle.apply(
            lambda row: row['total_co2'] / row['total_distance'] if row['total_distance'] > 0 else 0,
            axis=1
        )
        
        df_vehicle = df_vehicle.sort_values(by='co2_g_per_km', ascending=False)
    else:
        df_vehicle = pd.DataFrame(columns=['vehicleid__type', 'co2_g_per_km'])

    fig_vehicle_co2 = go.Figure()

    fig_vehicle_co2.add_trace(go.Bar(
        x=df_vehicle['vehicleid__type'].tolist(),
        y=df_vehicle['co2_g_per_km'].tolist(),
        
        text=df_vehicle['co2_g_per_km'].apply(lambda x: f'{x:.2f} g/km'),
        textposition='auto',
    ))

    fig_vehicle_co2.update_layout(
        title='CO2 Kibocsátás / Megtett Távolság (Járműtípusonként)',
        xaxis_title='Járműtípus',
        yaxis_title='CO2 / Távolság (g/km)'
    )
    chart_vehicle_co2_div = fig_vehicle_co2.to_html(include_plotlyjs=False, full_html=False)


    ######################################################################################
    ####cost/distance (vehicle type)
    ######################################################################################
    vehicle_data = FactShipment.objects.values(
        'vehicleid__type' 
    ).annotate(
        total_cost=Coalesce(Sum('transportcost'), Value(0.0)),
        total_distance=Coalesce(Sum('distance'), Value(1.0), output_field=FloatField())
    ).order_by('vehicleid__type')

    df_vehicle = pd.DataFrame(list(vehicle_data))

    if not df_vehicle.empty:
        df_vehicle['cost_per_km'] = df_vehicle.apply(
            lambda row: row['total_cost'] / row['total_distance'] if row['total_distance'] > 0 else 0,
            axis=1
        )

        df_vehicle = df_vehicle.sort_values(by='cost_per_km', ascending=False)
    else:
        df_vehicle = pd.DataFrame(columns=['vehicleid__type', 'cost_per_km'])

    fig_vehicle_cost = go.Figure()

    fig_vehicle_cost.add_trace(go.Bar(
        x=df_vehicle['vehicleid__type'].tolist(),
        y=df_vehicle['cost_per_km'].tolist(),

        text=df_vehicle['cost_per_km'].apply(lambda x: f'{x:.2f} Ft/km'),
        textposition='auto',
    ))

    fig_vehicle_cost.update_layout(
        title='Költség / Megtett Távolság (Járműtípusonként)',
        xaxis_title='Járműtípus',
        yaxis_title='Költség / Távolság (Ft/km)'
    )
    chart_vehicle_cost_div = fig_vehicle_cost.to_html(include_plotlyjs=False, full_html=False)


    ######################################################################################
    ####avg_speed/distance (vehicle type)
    ######################################################################################
    vehicle_data = FactShipment.objects.values(
        'vehicleid__type' 
    ).annotate(
        total_hour=Coalesce(Sum('duration'), Value(0.0),output_field=IntegerField()),
        total_distance=Coalesce(Sum('distance'), Value(1.0), output_field=FloatField())
    ).order_by('vehicleid__type')

    df_vehicle = pd.DataFrame(list(vehicle_data))

    if not df_vehicle.empty:
        df_vehicle['km_per_hour'] = df_vehicle.apply(
            lambda row: row['total_distance'] / row['total_hour'] if row['total_hour'] > 0 else 0,
            axis=1
        )

        df_vehicle = df_vehicle.sort_values(by='km_per_hour', ascending=False)
    else:
        df_vehicle = pd.DataFrame(columns=['vehicleid__type', 'km_per_hour'])

    fig_vehicle_speed = go.Figure()

    fig_vehicle_speed.add_trace(go.Bar(
        x=df_vehicle['vehicleid__type'].tolist(),
        y=df_vehicle['km_per_hour'].tolist(),

        text=df_vehicle['km_per_hour'].apply(lambda x: f'{x:.2f} km/hour'),
        textposition='auto',
    ))

    fig_vehicle_speed.update_layout(
        title='Megtett km/ Szállítás hossza (Járműtípusonként)',
        xaxis_title='Járműtípus',
        yaxis_title='Költség / Távolság (Ft/km)'
    )
    chart_vehicle_speed_div = fig_vehicle_speed.to_html(include_plotlyjs=False, full_html=False)

    ######################################################################################
    ####co2/distance
    ######################################################################################
    shipment_data = FactShipment.objects.annotate(
    co2_kg=F('co2emission') / 1000.0 
    ).filter(
    co2_kg__gt=30
    ).values(
        'distance', 
        'co2_kg'
    ).order_by('distance')

    df_shipments = pd.DataFrame(list(shipment_data))

    if df_shipments.empty:
        df_shipments = pd.DataFrame(columns=['distance', 'co2_kg'])
    
    fig_co2_dist = go.Figure()

    fig_co2_dist.add_trace(go.Scatter(
        x=df_shipments['distance'].tolist(),
        y=df_shipments['co2_kg'].tolist(), 
        mode='lines+markers', 
        name='Szállítás',
        
        hovertemplate=(
            '<b>Távolság:</b> %{x:.0f} km<br>' +
            '<b>CO2 Kibocsátás:</b> %{y:.2f} kg' +
            '<extra></extra>'
        )
    ))

    fig_co2_dist.update_layout(
        title='CO2 Kibocsátás a Távolság Függvényében',
        xaxis_title='Távolság (km)',
        yaxis_title='CO2 Kibocsátás (kg)'
    )

    chart_co2_dist_div = fig_co2_dist.to_html(include_plotlyjs=False, full_html=False) 

    ##############################################################################
    # #vehicle age and co2 relation
    # ##############################################################################
    prod_year_data = FactShipment.objects.filter(
        productionyear__gt=0,
        co2emission__gt=0
    ).values(
        'productionyear'
    ).annotate(
        avg_co2_g=Coalesce(Avg('co2emission'), 0.0) 
    ).order_by('productionyear')

    df_prod_year = pd.DataFrame(list(prod_year_data))

    if not df_prod_year.empty:
        df_prod_year['productionyear'] = df_prod_year['productionyear'].astype(int)
        
        df_prod_year['avg_co2_kg'] = df_prod_year['avg_co2_g'] / 1000.0
    else:
        df_prod_year = pd.DataFrame(columns=['productionyear', 'avg_co2_kg'])



    fig_prod_co2 = go.Figure()

    fig_prod_co2.add_trace(go.Scatter(
        x=df_prod_year['productionyear'].tolist(),
        y=df_prod_year['avg_co2_kg'].tolist(),
        mode='lines+markers',                 
        name='Átlagos CO2',
        hovertemplate=(
            '<b>Gyártási év:</b> %{x}<br>' +
            '<b>Átlagos CO2:</b> %{y:.2f} kg' +
            '<extra></extra>'
        )
    ))

    # Elrendezés (Layout) beállítása
    fig_prod_co2.update_layout(
        title='Jármű Gyártási Éve és Átlagos CO2 Kibocsátás Kapcsolata',
        xaxis_title='Gyártási Év',
        yaxis_title='Átlagos CO2 Kibocsátás (kg)'
    )

    # 4. Konvertálás HTML-be
    chart_prod_co2_div = fig_prod_co2.to_html(include_plotlyjs=False, full_html=False)

    #####################################################################
    ###Jármű típusok választása pie chart
    #####################################################################
    vehicle_type_data = FactShipment.objects.values(
        'vehicleid__type'
    ).annotate(
        shipment_count=Count('shipmentid')
    ).order_by('-shipment_count')

    df_vehicle_pie = pd.DataFrame(list(vehicle_type_data))

    if df_vehicle_pie.empty:
        df_vehicle_pie = pd.DataFrame(columns=['vehicleid__type', 'shipment_count'])

    fig_vehicle_pie = go.Figure()

    fig_vehicle_pie.add_trace(go.Pie(
        labels=df_vehicle_pie['vehicleid__type'].tolist(), 
        values=df_vehicle_pie['shipment_count'].tolist(),
        pull=[0.05] + [0] * (len(df_vehicle_pie) - 1), 
        
        textinfo='label+percent',
        insidetextorientation='radial'
    ))

    fig_vehicle_pie.update_layout(
        title='Járműtípusok Használatának Aránya (Szállítások Száma Alapján)'
    )

    chart_vehicle_pie_div = fig_vehicle_pie.to_html(include_plotlyjs=False, full_html=False)

    #####################################################################
    ###Leggyakoribb útvonalak
    #####################################################################


    route_data = FactShipment.objects.values(
        'routeid__startcity',
        'routeid__endcity',
    ).annotate(
        shipment_count=Count('shipmentid')
    ).order_by('-shipment_count')[:10]

    df_route_count = pd.DataFrame(list(route_data))

    if not df_route_count.empty:
        df_route_count['route_label'] = df_route_count['routeid__startcity'] + " - " + df_route_count['routeid__endcity']
    else:
        df_route_count = pd.DataFrame(columns=['route_label', 'shipment_count'])

    fig_route_count = go.Figure()

    fig_route_count.add_trace(go.Bar(
        x=df_route_count['route_label'].tolist(),
        y=df_route_count['shipment_count'].tolist(),
        
        text=df_route_count['shipment_count'].tolist(),
        textposition='auto',
    ))

    fig_route_count.update_layout(
        title='Leggyakrabban Használt Útvonalak',
        xaxis_title='Útvonal',
        yaxis_title='Használat Száma (db)'
    )

    chart_route_count_div = fig_route_count.to_html(include_plotlyjs=False, full_html=False)

    # data to template
    context = {
        'chart_co2_volume': chart_co2_volume_div, 
        'chart_vehicle_co2': chart_vehicle_co2_div,
        'chart_vehicle_cost': chart_vehicle_cost_div,
        'chart_vehicle_speed': chart_vehicle_speed_div,
        'chart_co2_dist': chart_co2_dist_div,
        'chart_prod_co2': chart_prod_co2_div,
        'chart_vehicle_pie':chart_vehicle_pie_div,
        'chart_route_count':chart_route_count_div
    }

    return render(request, 'internal_dm/dashboards.html', context)
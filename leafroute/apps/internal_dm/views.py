import plotly.express as px
import pandas as pd
from django.shortcuts import render
from django.db.models import Sum, Value, F,FloatField
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

    print(df_monthly['co2_per_volume_kg_m3'].tolist())
    chart_co2_volume_div = fig_co2_volume.to_html(include_plotlyjs=False, full_html=False)

    # Giving back data to template
    context = {
        'chart_co2_volume': chart_co2_volume_div, 
    }

    return render(request, 'internal_dm/dashboards.html', context)
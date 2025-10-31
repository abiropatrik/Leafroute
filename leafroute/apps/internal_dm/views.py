import plotly.express as px
import pandas as pd
from django.shortcuts import render
from django.db.models import Sum

# Importáld a modelledet (feltételezve, hogy a neve Factshipment és Dimorder)
from .models import FactShipment, DimOrder 

def dashboards_page(request):
    
    # --- Példa: 7. pont (CO2 Megrendelőnként)  ---

    # 1. Adatlekérdezés (ORM)
    # Hatékony lekérdezés: Csak a szükséges mezőket kérjük le
    # és az adatbázissal végeztetjük az aggregálást (Sum).
    customer_co2_data = FactShipment.objects.values(
        'orderid__userfirstname', # DIMORDER kapcsolat [cite: 585, 597]
        'orderid__userlastname'   # DIMORDER kapcsolat [cite: 585, 601]
    ).annotate(
        total_co2=Sum('co2emission') # FACTSHIPMENT mező [cite: 607]
    ).order_by('-total_co2') # Sorba rendezve

    # 1. Adatlekérdezés (ORM)
    # Hatékony lekérdezés: Csak a szükséges mezőket kérjük le 
    # és az adatbázissal végeztetjük az aggregálást (Sum).
    customer_co2_data = FactShipment.objects.values(
        'orderid__userfirstname', # DIMORDER kapcsolat [cite: 585, 597]
        'orderid__userlastname'   # DIMORDER kapcsolat [cite: 585, 601]
    ).annotate(
        total_co2=Sum('co2emission') # FACTSHIPMENT mező [cite: 607]
    ).order_by('-total_co2') # Sorba rendezve

    # 2. Adatfeldolgozás (Pandas)
    df_customer_co2 = pd.DataFrame(list(customer_co2_data))
    
    # Szebb nevek létrehozása a grafikonhoz
    if not df_customer_co2.empty:
        df_customer_co2['customer_name'] = df_customer_co2['orderid__userfirstname'] + ' ' + df_customer_co2['orderid__userlastname']
    else:
        # Kezeljük le az üres adatbázist
        df_customer_co2 = pd.DataFrame(columns=['customer_name', 'total_co2'])


    # 3. Ábra generálás (Plotly Express)
    fig_customer = px.bar(
        df_customer_co2.head(15), # Csak a top 15-öt mutatjuk
        x='customer_name',
        y='total_co2',
        title='Top 15 Megrendelő CO2 Kibocsátás Alapján',
        labels={'customer_name': 'Megrendelő', 'total_co2': 'Összes CO2 (kg)'}
    )

    # 4. Konvertálás HTML-be
    # include_plotlyjs=False -> A JS fájlt elég egyszer behúzni a template-ben
    # full_html=False -> Csak magát a <div>-et adja vissza, nem egy teljes HTML oldalt
    chart_customer_div = fig_customer.to_html(include_plotlyjs=False, full_html=False)

    
    # --- Itt jönne a többi 8 dashboard generálása hasonló logikával ---
    # ...
    # chart_vehicle_div = ...
    # chart_age_fuel_div = ...
    
    
    # 5. Adatok átadása a template-nek
    context = {
        'chart_customer': chart_customer_div,
        # 'chart_vehicle': chart_vehicle_div,
        # 'chart_age_fuel': chart_age_fuel_div,
    }

    return render(request, 'yourapp/dashboards.html', context)
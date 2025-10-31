from dataclasses import fields
from django import forms
from leafroute.apps.internal_stage.models import Shipment_ST, Address_ST, City_ST, Order_ST, Product_ST, Route_ST, Warehouse_ST, WarehouseConnection_ST, WorkSchedule_ST,Vehicle_ST, WarehouseProduct_ST

class WorkScheduleForm(forms.ModelForm):
    class Meta:
        model = WorkSchedule_ST
        fields = ['work_day', 'start_time', 'end_time']
        labels = {
            'work_day': 'Munkanap',
            'start_time': 'Munkaidő kezdete',
            'end_time': 'Munkaidő vége',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Calendar for work_day
        self.fields['work_day'].widget = forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        )
        # Time pickers
        self.fields['start_time'].widget = forms.TimeInput(
            attrs={'type': 'time', 'class': 'form-control'}
        )
        self.fields['end_time'].widget = forms.TimeInput(
            attrs={'type': 'time', 'class': 'form-control'}
        )


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle_ST
        fields = ['brand', 'model', 'production_year', 'type', 'fuel_type', 'consumption', 'full_capacity', 'free_capacity', 'status', 'avg_distance_per_hour', 'fuel_cost']
        labels = {
            'brand': 'Márka',
            'model': 'Típus',
            'production_year': 'Gyártási év',
            'type': 'Járműtípus',
            'fuel_type': 'Üzemanyag típusa',
            'consumption': 'Fogyasztás',
            'full_capacity': 'Teljes kapacitás',
            'free_capacity': 'Szabad kapacitás',
            'status': 'Állapot',
            'avg_distance_per_hour': 'Átlagos távolság óránként',
            'fuel_cost': 'Üzemanyagköltség',
        }

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            for field_name in list(self.fields):
                if field_name not in allowed:
                    self.fields.pop(field_name)

        if 'brand' in self.fields:
            self.fields['brand'].widget = forms.TextInput(attrs={'class': 'form-control'})
        if 'model' in self.fields:
            self.fields['model'].widget = forms.TextInput(attrs={'class': 'form-control'})
        if 'production_year' in self.fields:
            self.fields['production_year'].widget = forms.NumberInput(attrs={'class': 'form-control'})
        if 'type' in self.fields:
            self.fields['type'].widget = forms.TextInput(attrs={'class': 'form-control'})
        if 'fuel_type' in self.fields:
            self.fields['fuel_type'].widget = forms.TextInput(attrs={'class': 'form-control'})
        if 'consumption' in self.fields:
            self.fields['consumption'].widget = forms.NumberInput(attrs={'class': 'form-control','step':'0.01'})
        if 'full_capacity' in self.fields:
            self.fields['full_capacity'].widget = forms.NumberInput(attrs={'class': 'form-control','step':'0.01'})
        if 'free_capacity' in self.fields:
            self.fields['free_capacity'].widget = forms.NumberInput(attrs={'class': 'form-control','step':'0.01'})
        if 'status' in self.fields:
            self.fields['status'].widget = forms.TextInput(attrs={'class': 'form-control'})
        if 'avg_distance_per_hour' in self.fields:
            self.fields['avg_distance_per_hour'].widget = forms.NumberInput(attrs={'class': 'form-control','step':'0.01'})
        if 'fuel_cost' in self.fields:
            self.fields['fuel_cost'].widget = forms.NumberInput(attrs={'class': 'form-control'})

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse_ST
        fields = ['capacity', 'fullness', 'contact_email']
        labels = {
            'capacity': 'Kapacitás',
            'fullness': 'Telítettség',
            'contact_email': 'Kapcsolattartó email',
        }

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            for field_name in list(self.fields):
                if field_name not in allowed:
                    self.fields.pop(field_name)

        # Time pickers
        if 'capacity' in self.fields:
            self.fields['capacity'].widget = forms.NumberInput(attrs={'class': 'form-control'})
        if 'fullness' in self.fields:
            self.fields['fullness'].widget = forms.NumberInput(attrs={'class': 'form-control'})
        if 'contact_email' in self.fields:
            self.fields['contact_email'].widget = forms.TextInput(attrs={'class': 'form-control'})

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route_ST
        fields = ['warehouse_connection']
        labels = {
            'warehouse_connection': 'Raktár kapcsolat',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['warehouse_connection'].required = False
        self.fields['warehouse_connection'].queryset = WarehouseConnection_ST.objects.using('stage').all()
        self.fields['warehouse_connection'].widget.attrs.update({'class': 'form-control'})


class WarehouseConnectionForm(forms.ModelForm):
    class Meta:
        model = WarehouseConnection_ST
        fields = ['warehouse1', 'warehouse2', 'is_in_different_country', 'is_in_different_continent']
        labels = {
            'warehouse1': 'Raktár 1',
            'warehouse2': 'Raktár 2',
            'is_in_different_country': 'Különböző országban van?',
            'is_in_different_continent': 'Különböző kontinensen van?',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['warehouse1'].queryset = Warehouse_ST.objects.using('stage').all()
        self.fields['warehouse2'].queryset = Warehouse_ST.objects.using('stage').all()

        self.fields['warehouse1'].widget.attrs.update({'class': 'form-control'})
        self.fields['warehouse2'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_in_different_country'].widget = forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        )
        self.fields['is_in_different_continent'].widget = forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        )

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address_ST
        fields = [ 'street', 'house_number','institution_name']
        labels = {
            'street': 'Utca',
            'house_number': 'Házszám',
            'institution_name': 'Intézmény neve',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['street'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['house_number'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['institution_name'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )


class CityForm(forms.ModelForm):
    class Meta:
        model = City_ST
        fields = [ 'country', 'continent','name','has_airport','has_harbour','longitude_coordinate','latitude_coordinate']
        labels = {
            'country': 'Ország',
            'continent': 'Kontinens',
            'name': 'Város neve',
            'has_airport': 'Van repülőtere?',
            'has_harbour': 'Van kikötője?',
            'longitude_coordinate': 'Hosszúsági fok',
            'latitude_coordinate': 'Szélességi fok',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['country'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['continent'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['name'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['has_airport'].widget = forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        )
        self.fields['has_harbour'].widget = forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        )
        self.fields['longitude_coordinate'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['latitude_coordinate'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order_ST
        fields = ['product', 'warehouse_connection', 'route', 'quantity', 'order_date', 'expected_fullfillment_date', 'fulfillment_date', 'order_status', 'expected_co2_emission', 'co2_emmission', 'cost']
        labels = {
            'product': 'Termék',
            'warehouse_connection': 'Raktár kapcsolat',
            'route': 'Útvonal',
            'quantity': 'Mennyiség',
            'order_date': 'Megrendelés dátuma',
            'expected_fullfillment_date': 'Várt teljesítési dátum',
            'fulfillment_date': 'Teljesítési dátum',
            'order_status': 'Megrendelés állapota',
            'expected_co2_emission': 'Várt CO2 kibocsátás',
            'co2_emmission': 'CO2 kibocsátás',
            'cost': 'Költség',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['route'].required = False
        self.fields['product'].queryset = Product_ST.objects.none()
        self.fields['warehouse_connection'].queryset = WarehouseConnection_ST.objects.using('stage').all()
        self.fields['route'].queryset = Route_ST.objects.none()

        if 'warehouse_connection' in self.data:
            try:
                connection_id = int(self.data.get('warehouse_connection'))
                connection = WarehouseConnection_ST.objects.using('stage').get(pk=connection_id)

                warehouse_id = connection.warehouse1_id
                warehouse_connection_id = connection.warehouse_connection_id

                products = Product_ST.objects.using('stage').filter(
                    warehouseproduct_st__warehouse_id=warehouse_id
                ).distinct()
                routes = Route_ST.objects.using('stage').filter(
                    warehouse_connection_id=warehouse_connection_id
                ).distinct()
                self.fields['product'].queryset = products
                self.fields['route'].queryset = routes
            except (ValueError, WarehouseConnection_ST.DoesNotExist):
                pass
        elif self.instance.pk:
            connection = self.instance.warehouse_connection
            warehouse_id = connection.warehouse1_id
            self.fields['product'].queryset = Product_ST.objects.using('stage').filter(
                warehouseproduct_st__warehouse_id=warehouse_id
            ).distinct()
            self.fields['route'].queryset = Route_ST.objects.using('stage').filter(
                warehouse_connection_id=connection
            ).distinct()

        self.fields['quantity'].widget = forms.NumberInput(attrs={'class': 'form-control'})
        self.fields['order_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['expected_fullfillment_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['fulfillment_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['order_status'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['expected_co2_emission'].widget = forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        self.fields['co2_emmission'].widget = forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        self.fields['cost'].widget = forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        warehouse_connection = cleaned_data.get('warehouse_connection')
        quantity = float(cleaned_data.get('quantity', 0))

        if product and warehouse_connection and quantity:
            warehouse1 = warehouse_connection.warehouse1


            warehouse_product = WarehouseProduct_ST.objects.using('stage').get(
                product=product,
                warehouse=warehouse1
            )
            free_stock = float(warehouse_product.free_stock or 0)

            if quantity > free_stock:
                self.add_error('quantity', f'Nincs elegendő készlet a kiválasztott termékből a(z) {warehouse1.address.institution_name} raktárban. Elérhető mennyiség: {free_stock}.')


        return cleaned_data


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment_ST
        fields = ['order', 'vehicle', 'product', 'route_part','shipment_start_date', 'shipment_end_date', 'duration','quantity_transported', 'fuel_consumed', 'status','co2_emission', 'transport_cost']
        labels = {
            'order': 'Megrendelés',
            'vehicle': 'Jármű',
            'product': 'Termék',
            'route_part': 'Útszakasz',
            'shipment_start_date': 'Szállítás kezdete',
            'shipment_end_date': 'Szállítás vége',
            'duration': 'Időtartam',
            'quantity_transported': 'Szállított mennyiség',
            'fuel_consumed': 'Felhasznált üzemanyag',
            'status': 'Állapot',
            'co2_emission': 'CO2 kibocsátás',
            'transport_cost': 'Szállítási költség',
        }

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            for field_name in list(self.fields):
                if field_name not in allowed:
                    self.fields.pop(field_name)

        if 'shipment_start_date' in self.fields:
            self.fields['shipment_start_date'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD'})
        if 'shipment_end_date' in self.fields:
            self.fields['shipment_end_date'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD'})
        if 'duration' in self.fields:
            self.fields['duration'].widget = forms.TextInput(attrs={'class': 'form-control'})
        if 'quantity_transported' in self.fields:
            self.fields['quantity_transported'].widget = forms.NumberInput(attrs={'class': 'form-control'})
        if 'fuel_consumed' in self.fields:
            self.fields['fuel_consumed'].widget = forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        if 'co2_emission' in self.fields:
            self.fields['co2_emission'].widget = forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        if 'transport_cost' in self.fields:
            self.fields['transport_cost'].widget = forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})

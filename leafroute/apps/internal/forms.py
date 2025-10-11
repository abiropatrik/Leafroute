from django import forms
from leafroute.apps.internal_stage.models import Address_ST, City_ST, Warehouse_ST, WarehouseConnection_ST, WorkSchedule_ST,Vehicle_ST

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
        super().__init__(*args, **kwargs)

        # Calendar for brand
        self.fields['brand'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        # Time pickers
        self.fields['model'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['production_year'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['type'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['fuel_type'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['consumption'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['full_capacity'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['free_capacity'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['status'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['avg_distance_per_hour'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
        self.fields['fuel_cost'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )

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
        super().__init__(*args, **kwargs)

        # Time pickers
        self.fields['capacity'].widget = forms.NumberInput(
            attrs={'class': 'form-control'}
        )
        self.fields['fullness'].widget = forms.NumberInput(
            attrs={'class': 'form-control'}
        )
        self.fields['contact_email'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )

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

        # self.fields['warehouse1'].widget = forms.Select(
        #     attrs={'class': 'form-control'}
        # )
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
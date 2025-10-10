from django import forms
from leafroute.apps.internal_stage.models import Warehouse_ST, WorkSchedule_ST,Vehicle_ST

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
        fields = ['address', 'capacity', 'fullness', 'contact_email']
        labels = {
            'address': 'Cím',
            'capacity': 'Kapacitás',
            'fullness': 'Telítettség',
            'contact_email': 'Kapcsolattartó email',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Calendar for address
        self.fields['address'].widget = forms.TextInput(
            attrs={'class': 'form-control'}
        )
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
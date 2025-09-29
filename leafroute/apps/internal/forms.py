from django import forms
from leafroute.apps.internal_stage.models import WorkSchedule_ST

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
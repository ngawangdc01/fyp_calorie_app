# activity_log/forms.py
from django import forms
from datetime import date
from .models import ActivityLog, Activity

class ActivityLogForm(forms.ModelForm):
    activity = forms.ModelChoiceField(
        queryset=Activity.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    duration = forms.FloatField(
        label="Duration (min)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutes'})
    )

    logged_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=date.today
    )

    weight_kg = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Weight for selected date (kg)'
        })
    )

    class Meta:
        model = ActivityLog
        fields = ['activity', 'duration', 'logged_date']
        widgets = {
            'activity': forms.Select(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutes'}),
            'logged_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

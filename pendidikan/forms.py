from django import forms
from .models import Rencana

class RencanaForm(forms.ModelForm):
    class Meta:
        model = Rencana
        fields = ['rencana_tahun', 'rencana_dana', 'rencana_subopd']
        widgets = {
            'rencana_tahun': forms.NumberInput(attrs={'class': 'form-control'}),
            'rencana_dana': forms.Select(attrs={'class': 'form-control select2'}),
            'rencana_subopd': forms.Select(attrs={'class': 'form-control select2'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

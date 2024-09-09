from django import forms
from .models import Rencana

class RencanaFilterForm(forms.ModelForm):
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


class RencanaForm(forms.ModelForm):
    class Meta:
        model = Rencana
        fields = '__all__'
        widgets = {
            'rencana_tahun': forms.HiddenInput(),
            'rencana_dana': forms.HiddenInput(),
            'rencana_subopd': forms.HiddenInput(),
            'rencana_kegiatan': forms.Select(attrs={'class': 'form-control select2'}),
            'rencana_pagu': forms.NumberInput(attrs={'class': 'form-control'}),
            'rencana_output': forms.NumberInput(attrs={'class': 'form-control'}),
            'rencana_ket': forms.TextInput(attrs={'class': 'form-control'}),
            'rencana_pagudpa': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



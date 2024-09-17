from django import forms
from .models import Rencana, Rencanaposting,Subkegiatan, Subopd

class RencanaFilterForm(forms.ModelForm):
    rencana_tahun = forms.ChoiceField(label='Tahun', widget=forms.Select(attrs={'class': 'form-control select2'}))
    class Meta:
        model = Rencana
        fields = ['rencana_tahun', 'rencana_dana', 'rencana_subopd']
        widgets = {
            'rencana_dana': forms.Select(attrs={'class': 'form-control select2'}),
            'rencana_subopd': forms.Select(attrs={'class': 'form-control select2'}),
        }
    
    def __init__(self, *args, **kwargs):
        tahun = kwargs.pop('tahun', None)
        sesidana = kwargs.pop('sesidana', None)
        sesisubopd = kwargs.pop('sesisubopd', None)
        super().__init__(*args, **kwargs)
        
        if sesisubopd is not None and sesisubopd not in [124,70,67]:
            self.fields['rencana_subopd'].queryset = Subopd.objects.filter(id=sesisubopd)
        else:
            self.fields['rencana_subopd'].queryset = Subopd.objects.all()            
        
        if sesidana is not None:
            self.fields['rencana_dana'].queryset = Subkegiatan.objects.filter(sub_slug=sesidana)
        else:
            self.fields['rencana_dana'].queryset = Subkegiatan.objects.all()
        
        if tahun is not None:
            tahun_choices = [(tahun, tahun) for tahun in tahun]
            self.fields['rencana_tahun'].choices = tahun_choices
        else:
            self.fields['rencana_tahun'].choices = []


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



class RencanaPostingForm(forms.ModelForm):
    class Meta:
        model = Rencanaposting
        fields = ['posting_jadwal','posting_subopd']
        
        widgets = {
            'posting_jadwal': forms.Select(attrs={'class': 'form-control select2'}),
            'posting_subopd': forms.Select(attrs={'class': 'form-control select2'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
from django import forms
from .models import Rencanakesehatan, Rencanakesehatanposting,Subkegiatan, Subopd, Realisasikesehatan

class RencanakesehatanFilterForm(forms.ModelForm):
    # rencana_tahun = forms.ChoiceField(label='Tahun', widget=forms.Select(attrs={'class': 'form-control select2'}))
    class Meta:
        model = Rencanakesehatan
        fields = ['rencana_tahun', 'rencana_dana', 'rencana_subopd']
        widgets = {
            'rencana_tahun': forms.HiddenInput(attrs={'class': 'form-control'}),
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


class RencanakesehatanForm(forms.ModelForm):
    class Meta:
        model = Rencanakesehatan
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



class RencanakesehatanPostingForm(forms.ModelForm):
    class Meta:
        model = Rencanakesehatanposting
        fields = ['posting_jadwal','posting_subopd']
        
        widgets = {
            'posting_jadwal': forms.Select(attrs={'class': 'form-control select2'}),
            'posting_subopd': forms.Select(attrs={'class': 'form-control select2'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RealisasikesehatanFilterForm(forms.ModelForm):
    realisasi_tahun = forms.ChoiceField(label='Tahun', widget=forms.Select(attrs={'class': 'form-control select2'}))
    class Meta:
        model = Realisasikesehatan
        fields = ['realisasi_tahun', 'realisasi_dana', 'realisasi_subopd','realisasi_tahap']
        widgets = {
            'realisasi_dana': forms.Select(attrs={'class': 'form-control select2'}),
            'realisasi_subopd': forms.Select(attrs={'class': 'form-control select2'}),
            'realisasi_tahap': forms.Select(attrs={'class': 'form-control select2'}),
        }
    
    def __init__(self, *args, **kwargs):
        tahun = kwargs.pop('tahun', None)
        sesidana = kwargs.pop('sesidana', None)
        sesisubopd = kwargs.pop('sesisubopd', None)
        super().__init__(*args, **kwargs)
        
        if sesisubopd is not None and sesisubopd not in [124,70,67]:
            self.fields['realisasi_subopd'].queryset = Subopd.objects.filter(id=sesisubopd)
        else:
            self.fields['realisasi_subopd'].queryset = Subopd.objects.all()            
        
        if sesidana is not None:
            self.fields['realisasi_dana'].queryset = Subkegiatan.objects.filter(sub_slug=sesidana)
        else:
            self.fields['realisasi_dana'].queryset = Subkegiatan.objects.all()
        
        if tahun is not None:
            tahun_choices = [(tahun, tahun) for tahun in tahun]
            self.fields['realisasi_tahun'].choices = tahun_choices
        else:
            self.fields['realisasi_tahun'].choices = []


class RealisasikesehatanForm(forms.ModelForm):
    class Meta:
        model = Realisasikesehatan
        fields = '__all__'
        widgets = {
            'realisasi_tahun': forms.HiddenInput(),
            'realisasi_dana': forms.HiddenInput(),
            'realisasi_tahap': forms.HiddenInput(),
            'realisasi_subopd': forms.HiddenInput(),
            'realisasi_rencanaposting': forms.Select(attrs={'class': 'form-control select2'}),
            'realisasi_sp2d': forms.TextInput(attrs={'class': 'form-control'}),
            'realisasi_tgl': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'realisasi_nilai': forms.NumberInput(attrs={'class': 'form-control'}),
            'realisasi_output': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
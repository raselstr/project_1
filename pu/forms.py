from django import forms
from .models import Rencanapu, Rencanapuposting,Subkegiatan, Subopd, Realisasipu

model_rencana = Rencanapu
model_posting = Rencanapuposting
model_subkegiatan = Subkegiatan
model_subopd = Subopd
model_realisasi = Realisasipu

class RencanapuFilterForm(forms.ModelForm):
    # rencana_tahun = forms.ChoiceField(label='Tahun', widget=forms.Select(attrs={'class': 'form-control select2'}))
    class Meta:
        model = model_rencana
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
            self.fields['rencana_subopd'].queryset = model_subopd.objects.filter(id=sesisubopd)
        else:
            self.fields['rencana_subopd'].queryset = model_subopd.objects.all()            
        
        if sesidana is not None:
            self.fields['rencana_dana'].queryset = model_subkegiatan.objects.filter(sub_slug=sesidana)
        else:
            self.fields['rencana_dana'].queryset = model_subkegiatan.objects.all()
        
        if tahun is not None:
            tahun_choices = [(tahun, tahun) for tahun in tahun]
            self.fields['rencana_tahun'].choices = tahun_choices
        else:
            self.fields['rencana_tahun'].choices = []


class RencanapuForm(forms.ModelForm):
    class Meta:
        model = model_rencana
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



class RencanapuPostingForm(forms.ModelForm):
    class Meta:
        model = model_posting
        fields = ['posting_jadwal','posting_subopd']
        
        widgets = {
            'posting_jadwal': forms.Select(attrs={'class': 'form-control select2'}),
            'posting_subopd': forms.Select(attrs={'class': 'form-control select2'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RealisasipuFilterForm(forms.ModelForm):
    realisasi_tahun = forms.ChoiceField(label='Tahun', widget=forms.Select(attrs={'class': 'form-control select2'}))
    class Meta:
        model = Realisasipu
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


class RealisasipuForm(forms.ModelForm):
    class Meta:
        model = model_realisasi
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
        initial_data = kwargs.pop('initial_data', None)
        super().__init__(*args, **kwargs)
        
        if initial_data:
            tahun = initial_data.get('realisasi_tahun')
            dana = initial_data.get('realisasi_dana')
            subopd = initial_data.get('realisasi_subopd')
            jadwal = initial_data.get('jadwal')
            
            queryset = model_posting.objects.filter(
                posting_tahun = tahun,
                posting_dana = dana,
                posting_subopd = subopd,
                posting_jadwal = jadwal,
            )
            self.fields['realisasi_rencanaposting'].queryset = queryset
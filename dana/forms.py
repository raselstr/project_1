from django import forms
from django.urls import reverse
from .mixins import BaseFormMixin
from .models import Dana, Program, Kegiatan, Subkegiatan, SubRincian

class DanaForm(forms.ModelForm):
    class Meta:
        model = Dana
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dana_nama'].widget.attrs.update({'class':'form-control','placeholder': 'Jenis Dana'})
        # print(f"Field 'dana_nama' attrs: {self.fields['dana_nama'].widget.attrs}")

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['program_dana'].widget.attrs.update({'class':'form-control'})
        self.fields['program_nama'].widget.attrs.update({'class':'form-control','placeholder': 'Nama Program'})


class KegiatanForm(forms.ModelForm):
    class Meta:
        model = Kegiatan
        fields = '__all__'
        widgets = {
            'kegiatan_dana': forms.Select(attrs={'class': 'form-control', 'hx-target': '#id_kegiatan_program'}),
            'kegiatan_program': forms.Select(attrs={'class': 'form-control'}),
            'kegiatan_nama': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kegiatan_dana'].widget.attrs['hx-get'] = reverse('load_program')
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class SubkegiatanForm(forms.ModelForm):
    class Meta:
        model = Subkegiatan
        fields = '__all__'
        widgets = {
            'sub_dana': forms.Select(attrs={'class': 'form-control', 'hx-target': '#id_sub_prog'}),
            'sub_prog': forms.Select(attrs={'class': 'form-control', 'hx-target': '#id_sub_keg'}),
            'sub_keg': forms.Select(attrs={'class': 'form-control'}),
            'sub_nama': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_dana'].widget.attrs['hx-get'] = reverse('load_dana')
        
        

class SubrRincianForm(forms.ModelForm):
    class Meta:
        model = SubRincian
        fields = '__all__'


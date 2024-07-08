from django import forms
from ..models import RealisasiDankel
from django.utils import timezone

CURRENT_YEAR = timezone.now().year
YEAR_CHOICES = [(r, r) for r in range(CURRENT_YEAR - 2, CURRENT_YEAR + 3)]

class RealisasiDankelFilterForm(forms.ModelForm):
    realisasidankel_tahun = forms.ChoiceField(choices=YEAR_CHOICES, label='Tahun',widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = RealisasiDankel
        fields = ['realisasidankel_tahun', 'realisasidankel_dana', 'realisasidankel_tahap', 'realisasidankel_subopd']

        widgets = {
            # 'realisasidankel_tahun': forms.Select(attrs={'class': 'form-control'}),
            'realisasidankel_dana': forms.Select(attrs={'class': 'form-control'}),
            'realisasidankel_tahap': forms.Select(attrs={'class': 'form-control'}),
            'realisasidankel_subopd': forms.Select(attrs={'class': 'form-control'}),
        }

class RealisasiDankelForm(forms.ModelForm):
    class Meta:
        model = RealisasiDankel
        fields = '__all__'
        widgets = {
            'realisasidankel_tahun': forms.NumberInput(attrs={'class': 'form-control'}),
            'realisasidankel_dana': forms.Select(attrs={'class': 'form-control'}),
            'realisasidankel_tahap': forms.Select(attrs={'class': 'form-control'}),
            'realisasidankel_subopd': forms.Select(attrs={'class': 'form-control'}),
            'realisasidankel_sp2dtu': forms.TextInput(attrs={'class': 'form-control'}),
            'realisasidankel_tgl': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'realisasidankel_nilai': forms.NumberInput(attrs={'class': 'form-control'}),
            'realisasidankel_lpj': forms.TextInput(attrs={'class': 'form-control'}),
            'realisasidankel_lpjtgl': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'realisasidankel_lpjnilai': forms.NumberInput(attrs={'class': 'form-control'}),
            'realisasidankel_sts': forms.TextInput(attrs={'class': 'form-control'}),
            'realisasidankel_ststgl': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'realisasidankel_stsnilai': forms.NumberInput(attrs={'class': 'form-control'}),
            'realisasidankel_verif': forms.Select(attrs={'class': 'form-control'}),
        }

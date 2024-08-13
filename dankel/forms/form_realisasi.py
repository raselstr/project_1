from django import forms
from ..models import RealisasiDankel, Subopd, Subkegiatan, RencDankeljadwal
# from django.utils import timezone

# CURRENT_YEAR = timezone.now().year
# YEAR_CHOICES = [(r, r) for r in range(CURRENT_YEAR - 2, CURRENT_YEAR + 3)]

class RealisasiDankelFilterForm(forms.ModelForm):
    realisasidankel_tahun = forms.ChoiceField(label='Tahun', widget=forms.Select(attrs={'class': 'form-control select2'}))
    class Meta:
        model = RealisasiDankel
        fields = ['realisasidankel_tahun', 'realisasidankel_dana', 'realisasidankel_tahap', 'realisasidankel_subopd']

        widgets = {
            # 'realisasidankel_tahun': forms.Select(attrs={'class': 'form-control select2'}),
            'realisasidankel_dana': forms.Select(attrs={'class': 'form-control select2'}),
            'realisasidankel_tahap': forms.Select(attrs={'class': 'form-control select2'}),
            'realisasidankel_subopd': forms.Select(attrs={'class': 'form-control select2'}),
        }
    
    def __init__(self, *args, **kwargs):
        sesiidopd = kwargs.pop('sesiidopd', None)
        sesidana = kwargs.pop('sesidana', None)
        tahunrencana = kwargs.pop('tahunrencana', None)
        super().__init__(*args, **kwargs)
        
        if sesiidopd is not None:
            self.fields['realisasidankel_subopd'].queryset = Subopd.objects.filter(id=sesiidopd)
        else:
            self.fields['realisasidankel_subopd'].queryset = Subopd.objects.all()
            
        if sesidana is not None:
            self.fields['realisasidankel_dana'].queryset = Subkegiatan.objects.filter(sub_slug=sesidana)
        else:
            self.fields['realisasidankel_dana'].queryset = Subkegiatan.objects.all()
        
        if tahunrencana is not None:
            tahun_choices = [(tahun, tahun) for tahun in tahunrencana]
            self.fields['realisasidankel_tahun'].choices = tahun_choices
        else:
            self.fields['realisasidankel_tahun'].choices = []
        
        

class RealisasiDankelForm(forms.ModelForm):
    class Meta:
        model = RealisasiDankel
        fields = '__all__'
        widgets = {
            'realisasidankel_tahun': forms.HiddenInput(),
            'realisasidankel_dana': forms.HiddenInput(),
            'realisasidankel_tahap': forms.HiddenInput(),
            'realisasidankel_subopd': forms.HiddenInput(),
            'realisasidankel_rencana': forms.Select(attrs={'class': 'form-control select2'}),
            'realisasidankel_idrencana': forms.HiddenInput(),
            'realisasidankel_output': forms.NumberInput(attrs={'class': 'form-control'}),
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
    
    def __init__(self, *args, **kwargs):
        keg = kwargs.pop('keg', None)
        super().__init__(*args, **kwargs)
        print(keg)
        if keg:
            subopd = keg.get('subopd', None)
            dana = keg.get('dana', None)
            tahun = keg.get('tahun', None)
            jadwal = keg.get('jadwal', None)

            if subopd and dana and tahun and jadwal:
                self.fields['realisasidankel_rencana'].queryset = RencDankeljadwal.objects.filter(
                    rencdankel_subopd=subopd,
                    rencdankel_dana=dana,
                    rencdankel_tahun=tahun,
                    rencdankel_jadwal=jadwal,
                )
            else:
                self.fields['realisasidankel_rencana'].queryset = RencDankeljadwal.objects.none()
        
            

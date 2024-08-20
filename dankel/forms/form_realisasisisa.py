from django import forms
from ..models import RealisasiDankelsisa, Subopd, Subkegiatan, RencDankeljadwalsisa
# from django.utils import timezone

# CURRENT_YEAR = timezone.now().year
# YEAR_CHOICES = [(r, r) for r in range(CURRENT_YEAR - 2, CURRENT_YEAR + 3)]

class RealisasiDankelsisaFilterForm(forms.ModelForm):
    realisasidankelsisa_tahun = forms.ChoiceField(label='Tahun', widget=forms.Select(attrs={'class': 'form-control select2'}))
    class Meta:
        model = RealisasiDankelsisa
        fields = ['realisasidankelsisa_tahun', 'realisasidankelsisa_dana', 'realisasidankelsisa_tahap', 'realisasidankelsisa_subopd']

        widgets = {
            # 'realisasidankelsisa_tahun': forms.Select(attrs={'class': 'form-control select2'}),
            'realisasidankelsisa_dana': forms.Select(attrs={'class': 'form-control select2'}),
            'realisasidankelsisa_tahap': forms.Select(attrs={'class': 'form-control select2'}),
            'realisasidankelsisa_subopd': forms.Select(attrs={'class': 'form-control select2'}),
        }
    
    def __init__(self, *args, **kwargs):
        sesiidopd = kwargs.pop('sesiidopd', None)
        sesidana = kwargs.pop('sesidana', None)
        tahunrencana = kwargs.pop('tahunrencana', None)
        super().__init__(*args, **kwargs)
        
        if sesiidopd is not None and sesiidopd != 125 and sesiidopd != 70:
            self.fields['realisasidankelsisa_subopd'].queryset = Subopd.objects.filter(id=sesiidopd)
        else:
            self.fields['realisasidankelsisa_subopd'].queryset = Subopd.objects.all()
            
        if sesidana is not None:
            self.fields['realisasidankelsisa_dana'].queryset = Subkegiatan.objects.filter(sub_slug=sesidana)
        else:
            self.fields['realisasidankelsisa_dana'].queryset = Subkegiatan.objects.all()
        
        if tahunrencana is not None:
            tahun_choices = [(tahun, tahun) for tahun in tahunrencana]
            self.fields['realisasidankelsisa_tahun'].choices = tahun_choices
        else:
            self.fields['realisasidankelsisa_tahun'].choices = []
        
        

class RealisasiDankelsisaForm(forms.ModelForm):
    class Meta:
        model = RealisasiDankelsisa
        fields = '__all__'
        widgets = {
            'realisasidankelsisa_tahun': forms.HiddenInput(),
            'realisasidankelsisa_dana': forms.HiddenInput(),
            'realisasidankelsisa_tahap': forms.HiddenInput(),
            'realisasidankelsisa_subopd': forms.HiddenInput(),
            'realisasidankelsisa_rencana': forms.Select(attrs={'class': 'form-control select2'}),
            'realisasidankelsisa_idrencana': forms.HiddenInput(),
            'realisasidankelsisa_output': forms.NumberInput(attrs={'class': 'form-control'}),
            'realisasidankelsisa_sp2dtu': forms.TextInput(attrs={'class': 'form-control'}),
            'realisasidankelsisa_tgl': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'realisasidankelsisa_nilai': forms.NumberInput(attrs={'class': 'form-control'}),
            'realisasidankelsisa_lpj': forms.TextInput(attrs={'class': 'form-control'}),
            'realisasidankelsisa_lpjtgl': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'realisasidankelsisa_lpjnilai': forms.NumberInput(attrs={'class': 'form-control'}),
            'realisasidankelsisa_sts': forms.TextInput(attrs={'class': 'form-control'}),
            'realisasidankelsisa_ststgl': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'realisasidankelsisa_stsnilai': forms.NumberInput(attrs={'class': 'form-control'}),
            'realisasidankelsisa_verif': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        keg = kwargs.pop('keg', None)
        super().__init__(*args, **kwargs)
        # print(keg)
        if keg:
            subopd = keg.get('subopd', None)
            dana = keg.get('dana', None)
            tahun = keg.get('tahun', None)
            jadwal = keg.get('jadwal', None)

            if subopd and dana and tahun and jadwal:
                self.fields['realisasidankelsisa_rencana'].queryset = RencDankeljadwalsisa.objects.filter(
                    rencdankelsisa_subopd=subopd,
                    rencdankelsisa_dana=dana,
                    rencdankelsisa_tahun=tahun,
                    rencdankelsisa_jadwal=jadwal,
                )
            else:
                self.fields['realisasidankelsisa_rencana'].queryset = RencDankeljadwalsisa.objects.none()
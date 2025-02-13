from django import forms
from ..models import RencDankeljadwalsisa
from jadwal.models import Jadwal

model_jadwal = Jadwal

class RencDankeljadwalsisaForm(forms.ModelForm):
    class Meta:
        model = RencDankeljadwalsisa
        fields = ['rencdankelsisa_jadwal','rencdankelsisa_subopd']
        
        widgets = {
            'rencdankelsisa_jadwal': forms.Select(attrs={'class': 'form-control select2'}),
            'rencdankelsisa_subopd': forms.Select(attrs={'class': 'form-control select2'})
        }
        
    def __init__(self, *args, **kwargs):
        tahun = kwargs.pop('tahun', None)
        postingid = kwargs.pop('jadwal', None)
        super().__init__(*args, **kwargs)
        self.fields['rencdankelsisa_jadwal'].queryset = model_jadwal.objects.filter(jadwal_tahun=tahun, id=postingid)

        
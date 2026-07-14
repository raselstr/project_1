from django import forms
from ..models import RencDankeljadwalsisa
from jadwal.models import Jadwal
from core.forms.budget_opd import allow_all_budgeted_subopd, budgeted_subopd_queryset

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
        sesidana = kwargs.pop('sesidana', None)
        sesiidopd = kwargs.pop('sesiidopd', None)
        super().__init__(*args, **kwargs)
        self.fields['rencdankelsisa_jadwal'].queryset = model_jadwal.objects.filter(jadwal_tahun=tahun, id=postingid)
        self.fields['rencdankelsisa_subopd'].queryset = budgeted_subopd_queryset(tahun=tahun, dana_slug=sesidana, opd_id=sesiidopd)
        allow_all_budgeted_subopd(self.fields['rencdankelsisa_subopd'])

        

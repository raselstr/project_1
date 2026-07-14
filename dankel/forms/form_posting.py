from django import forms
from ..models import RencDankeljadwal
from jadwal.models import Jadwal
from core.forms.budget_opd import budgeted_subopd_queryset

model_jadwal = Jadwal

class RencDankeljadwalForm(forms.ModelForm):
    class Meta:
        model = RencDankeljadwal
        fields = ['rencdankel_jadwal','rencdankel_subopd']
        
        widgets = {
            'rencdankel_jadwal': forms.Select(attrs={'class': 'form-control select2'}),
            'rencdankel_subopd': forms.Select(attrs={'class': 'form-control select2'}),
        }
        
    def __init__(self, *args, **kwargs):
        tahun = kwargs.pop('tahun', None)
        postingid = kwargs.pop('jadwal', None)
        sesidana = kwargs.pop('sesidana', None)
        sesiidopd = kwargs.pop('sesiidopd', None)
        super().__init__(*args, **kwargs)
        self.fields['rencdankel_jadwal'].queryset = model_jadwal.objects.filter(jadwal_tahun=tahun, id=postingid)
        self.fields['rencdankel_subopd'].queryset = budgeted_subopd_queryset(tahun=tahun, dana_slug=sesidana, opd_id=sesiidopd)

        

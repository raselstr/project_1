from django import forms
from ..models import RencDankel, Subopd, Subkegiatan
from core.forms.budget_opd import budgeted_subopd_queryset

class RencDankelForm(forms.ModelForm):
    class Meta:
        model = RencDankel
        fields = '__all__'
        
        widgets = {
            'rencdankel_tahun': forms.TextInput(attrs={'class': 'form-control'}),
            'rencdankel_dana': forms.Select(attrs={'class': 'form-control select2'}),
            'rencdankel_subopd': forms.Select(attrs={'class': 'form-control select2'}),
            'rencdankel_sub': forms.Select(attrs={'class': 'form-control select2'}),
            'rencdankel_pagu': forms.NumberInput(attrs={'class': 'form-control'}),
            'rencdankel_output': forms.NumberInput(attrs={'class': 'form-control'}),
            'rencdankel_ket': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        sesiidopd = kwargs.pop('sesiidopd', None)
        sesidana = kwargs.pop('sesidana', None)
        tahun = kwargs.pop('tahun', None)
        super().__init__(*args, **kwargs)
        
        self.fields['rencdankel_subopd'].queryset = budgeted_subopd_queryset(tahun=tahun, dana_slug=sesidana, opd_id=sesiidopd)
            
        if sesidana is not None:
            self.fields['rencdankel_dana'].queryset = Subkegiatan.objects.filter(sub_slug=sesidana)
        else:
            self.fields['rencdankel_dana'].queryset = Subkegiatan.objects.all()

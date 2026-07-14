from django import forms
from ..models import RencDankelsisa, Subopd, Subkegiatan
from core.forms.budget_opd import budgeted_subopd_queryset

class RencDankelsisaForm(forms.ModelForm):
    class Meta:
        model = RencDankelsisa
        fields = '__all__'
        
        widgets = {
            'rencdankelsisa_tahun': forms.TextInput(attrs={'class': 'form-control'}),
            'rencdankelsisa_dana' : forms.Select(attrs={'class': 'form-control select2'}),
            'rencdankelsisa_subopd': forms.Select(attrs={'class': 'form-control select2'}),
            'rencdankelsisa_sub': forms.Select(attrs={'class': 'form-control select2'}),
            'rencdankelsisa_pagu': forms.NumberInput(attrs={'class': 'form-control'}),
            'rencdankelsisa_output': forms.NumberInput(attrs={'class': 'form-control'}),
            'rencdankelsisa_ket': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        sesiidopd = kwargs.pop('sesiidopd', None)
        sesidana = kwargs.pop('sesidana', None)
        tahun = kwargs.pop('tahun', None)
        super().__init__(*args, **kwargs)
        
        self.fields['rencdankelsisa_subopd'].queryset = budgeted_subopd_queryset(tahun=tahun, dana_slug=sesidana, opd_id=sesiidopd)
            
        if sesidana is not None:
            self.fields['rencdankelsisa_dana'].queryset = Subkegiatan.objects.filter(sub_slug=sesidana)
        else:
            self.fields['rencdankelsisa_dana'].queryset = Subkegiatan.objects.all()
        
        
    
   

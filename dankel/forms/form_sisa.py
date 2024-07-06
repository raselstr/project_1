from django import forms
from ..models import RencDankelsisa, Subopd, Subrinc

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
        super().__init__(*args, **kwargs)
        
        if sesiidopd is not None:
            self.fields['rencdankelsisa_subopd'].queryset = Subopd.objects.filter(id=sesiidopd)
        else:
            self.fields['rencdankelsisa_subopd'].queryset = Subopd.objects.all()
            
        if sesidana is not None:
            self.fields['rencdankelsisa_dana'].queryset = Subrinc.objects.filter(subrinc_slug=sesidana)
        else:
            self.fields['rencdankelsisa_dana'].queryset = Subrinc.objects.all()
        
        
    
   
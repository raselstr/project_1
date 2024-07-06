from django import forms
from ..models import RencDankel, Subopd, Subrinc

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
        super().__init__(*args, **kwargs)
        
        if sesiidopd is not None:
            self.fields['rencdankel_subopd'].queryset = Subopd.objects.filter(id=sesiidopd)
        else:
            self.fields['rencdankel_subopd'].queryset = Subopd.objects.all()
            
        if sesidana is not None:
            self.fields['rencdankel_dana'].queryset = Subrinc.objects.filter(subrinc_slug=sesidana)
        else:
            self.fields['rencdankel_dana'].queryset = Subrinc.objects.all()

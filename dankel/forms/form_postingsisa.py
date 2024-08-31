from django import forms
from ..models import RencDankeljadwalsisa

class RencDankeljadwalsisaForm(forms.ModelForm):
    class Meta:
        model = RencDankeljadwalsisa
        fields = ['rencdankelsisa_jadwal','rencdankelsisa_subopd']
        
        widgets = {
            'rencdankelsisa_jadwal': forms.Select(attrs={'class': 'form-control select2'}),
            'rencdankelsisa_subopd': forms.Select(attrs={'class': 'form-control select2'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
from django import forms
from ..models import RencDankeljadwal

class RencDankeljadwalForm(forms.ModelForm):
    class Meta:
        model = RencDankeljadwal
        fields = ['rencdankel_jadwal']
        
        widgets = {
            'rencdankel_jadwal': forms.Select(attrs={'class': 'form-control select2'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
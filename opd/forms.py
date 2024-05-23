from django import forms
from .models import Opd

class OpdForm(forms.ModelForm):
    class Meta:
        model = Opd
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kode_opd'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Kode OPD'})
        self.fields['nama_opd'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama OPD'})


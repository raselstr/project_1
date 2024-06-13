from django import forms
from .models import Penerimaan

class PenerimaanForm(forms.ModelForm):
    class Meta:
        model = Penerimaan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['penerimaan_tahun'].widget.attrs.update({'class': 'form-control'})
        self.fields['penerimaan_dana'].widget.attrs.update({'class': 'form-control select2'})
        self.fields['penerimaan_tahap'].widget.attrs.update({'class': 'form-control select2'})
        self.fields['penerimaan_tgl'].widget.attrs.update({'class': 'form-control datepicker'})
        self.fields['penerimaan_ket'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Keterangan Dana'})
        self.fields['penerimaan_nilai'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Dana yang diterima'})
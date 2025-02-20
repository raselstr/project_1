from django import forms
from jadwal import models

Model = models.Jadwal

class JadwalForm(forms.ModelForm):
    class Meta:
        model = models.Jadwal
        fields = '__all__'
        exclude = ('id', 'user')
        widgets = {
            'jadwal_tahun': forms.NumberInput(),
            'jadwal_keterangan': forms.TextInput(),
            'jadwal_aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'jadwal_tahun': 'Tahun',
            'jadwal_keterangan': 'Keterangan',
            'jadwal_aktif': 'Aktif',
        }
        error_messages = {
            'jadwal_tahun': {'required': "Tahun harus diisi"},
            'jadwal_keterangan': {'required': "Keterangan harus diisi"},
        }

    def __init__(self, *args, **kwargs):
        tahun = kwargs.pop('tahun', None)
        super().__init__(*args, **kwargs)

        field_attrs = {
            'jadwal_tahun': {'class': 'form-control', 'readonly': True, 'placeholder': 'Tahun'},
            'jadwal_keterangan': {'class': 'form-control', 'placeholder': 'Keterangan'},
        }

        for field, attrs in field_attrs.items():
            self.fields[field].widget.attrs.update(attrs)

        if tahun is not None:
            self.fields['jadwal_tahun'].initial = tahun
        
from django import forms
from .models import Opd, Subopd, Pejabat

class OpdForm(forms.ModelForm):
    class Meta:
        model = Opd
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kode_opd'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Kode OPD'})
        self.fields['nama_opd'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama OPD'})

class SubopdForm(forms.ModelForm):
    class Meta:
        model = Subopd
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_opd'].widget.attrs.update({'class': 'form-control'})
        self.fields['sub_nama'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama Sub OPD'})

class PejabatForm(forms.ModelForm):
    class Meta:
        model = Pejabat
        fields = ['pejabat_sub', 'pejabat_jabatan', 'pejabat_nama','pejabat_nip','pejabat_lokasi']

    def __init__(self, *args, **kwargs):
        idsubopd = kwargs.pop('idsubopd', None)
        super().__init__(*args, **kwargs)
        
        self.fields['pejabat_sub'].widget.attrs.update({'class': 'form-control'})
        self.fields['pejabat_jabatan'].widget.attrs.update({'class': 'form-control'})
        self.fields['pejabat_nama'].widget.attrs.update({'class': 'form-control'})
        self.fields['pejabat_nip'].widget.attrs.update({'class': 'form-control'})
        self.fields['pejabat_lokasi'].widget.attrs.update({'class': 'form-control'})
        
        if idsubopd is not None and idsubopd != 125: 
            self.fields['pejabat_sub'].queryset = Subopd.objects.filter(id=idsubopd)
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class PejabatFotoForm(forms.ModelForm):
    class Meta:
        model = Pejabat
        fields = ['pejabat_foto']  # Hanya field untuk upload foto
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pejabat_foto'].widget.attrs.update({'class': 'form-control-file'}) 
    
from django import forms
from .models import Penerimaan, DistribusiPenerimaan

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
        self.fields['penerimaan_nilai'].widget.attrs.update({'class': 'form-control currency'})

class DistribusiForm(forms.ModelForm):
    class Meta:
        model = DistribusiPenerimaan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        number = kwargs.pop('number', None)
        super().__init__(*args, **kwargs)
        
        self.fields['distri_penerimaan'].widget.attrs.update({'class': 'form-control select2'})
        self.fields['distri_subopd'].widget.attrs.update({'class': 'form-control select2'})
        self.fields['distri_nilai'].widget.attrs.update({'class': 'form-control'})
        self.fields['distri_ket'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Keterangan Dana'})
    
        if number is not None:
            self.fields['distri_penerimaan'].queryset = Penerimaan.objects.filter(id=number)
        else:
            self.fields['rencdankel_subopd'].queryset = Penerimaan.objects.all()
        
                
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance        
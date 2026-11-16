from django import forms
from django.urls import reverse
from ..models import DauGajiAsnProg, DauGajiAsnKeg, DauGajiAsnSub

class DauGajiAsnProgForm(forms.ModelForm):
    
    class Meta:
        model = DauGajiAsnProg
        fields = '__all__'
        widgets = {
            'daugajiprog_dana': forms.Select(attrs={
                'class': 'form-control', 
                'hx-target': '#id_daugajiprog_subrinc',
                'hx-trigger': 'click',
                }),
            'daugajiprog_prog': forms.TextInput(attrs={'class': 'form-control'}),
            'daugajiprog_tahun': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['daugajiprog_dana'].widget.attrs['hx-get'] = reverse('load_daugajiasnprog')
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
    

class DauGajiAsnKegForm(forms.ModelForm):
    
    class Meta:
        model = DauGajiAsnKeg
        fields = '__all__'
       
    def __init__(self, *args, **kwargs):
        number = kwargs.pop('number', None)
        super().__init__(*args, **kwargs)
       
        self.fields['daugajikeg_prog'].widget.attrs.update({'class':'form-control'})
        self.fields['daugajikeg_nama'].widget.attrs.update({'class':'form-control','placeholder': 'Nama Kegiatan'})
        
        if number:
            self.initial['daugajikeg_prog'] = number
                
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class DauGajiAsnSubForm(forms.ModelForm):
    
    class Meta:
        model = DauGajiAsnSub
        fields = '__all__'
       
    def __init__(self, *args, **kwargs):
        sub = kwargs.pop('sub', None)
        super().__init__(*args, **kwargs)
        self.fields['daugajisub_keg'].widget.attrs.update({'class':'form-control'})
        self.fields['daugajisub_nama'].widget.attrs.update({'class':'form-control','placeholder': 'Nama Sub Kegiatan'})
        self.fields['daugajisub_satuan'].widget.attrs.update({'class':'form-control'})
        
        if sub:
            self.initial['daugajisub_keg'] = sub
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

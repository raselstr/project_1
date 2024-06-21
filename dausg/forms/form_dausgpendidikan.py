from django import forms
from django.urls import reverse
from ..models import DausgpendidikanProg, DausgpendidikanKeg, DausgpendidikanSub

class DausgpendidikanProgForm(forms.ModelForm):
    
    class Meta:
        model = DausgpendidikanProg
        fields = '__all__'
        widgets = {
            'dausgpendidikan_dana': forms.Select(attrs={
                'class': 'form-control', 
                'hx-target': '#id_dausgpendidikan_subrinc',
                'hx-trigger': 'click',
                }),
            'dausgpendidikan_subrinc': forms.Select(attrs={
                'class': 'form-control', 
                }),
            'dausgpendidikan_prog': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dausgpendidikan_dana'].widget.attrs['hx-get'] = reverse('load_dausgpendidikanprog')
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
    

class DausgpendidikanKegForm(forms.ModelForm):
    
    class Meta:
        model = DausgpendidikanKeg
        fields = '__all__'
       
    def __init__(self, *args, **kwargs):
        number = kwargs.pop('number', None)
        super().__init__(*args, **kwargs)
       
        self.fields['dausgpendidikankeg_prog'].widget.attrs.update({'class':'form-control'})
        self.fields['dausgpendidikankeg_nama'].widget.attrs.update({'class':'form-control','placeholder': 'Nama Kegiatan'})
        
        if number:
            self.initial['dausgpendidikankeg_prog'] = number
                
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class DausgpendidikanSubForm(forms.ModelForm):
    
    class Meta:
        model = DausgpendidikanSub
        fields = '__all__'
       
    def __init__(self, *args, **kwargs):
        sub = kwargs.pop('sub', None)
        super().__init__(*args, **kwargs)
        self.fields['dausgpendidikansub_keg'].widget.attrs.update({'class':'form-control'})
        self.fields['dausgpendidikansub_nama'].widget.attrs.update({'class':'form-control','placeholder': 'Nama Sub Kegiatan'})
        self.fields['dausgpendidikansub_satuan'].widget.attrs.update({'class':'form-control'})
        
        if sub:
            self.initial['dausgpendidikansub_keg'] = sub
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
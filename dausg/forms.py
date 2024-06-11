from django import forms
from django.urls import reverse
from .models import DankelProg, DankelKeg, Dankelsub

class DankelProgForm(forms.ModelForm):
    
    class Meta:
        model = DankelProg
        fields = '__all__'
        widgets = {
            'dankel_dana': forms.Select(attrs={
                'class': 'form-control', 
                'hx-target': '#id_dankel_subrinc',
                'hx-trigger': 'click',
                }),
            'dankel_subrinc': forms.Select(attrs={
                'class': 'form-control', 
                }),
            'dankel_prog': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dankel_dana'].widget.attrs['hx-get'] = reverse('load_dankelprog')
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
    

class DankelKegForm(forms.ModelForm):
    
    class Meta:
        model = DankelKeg
        fields = '__all__'
       
    def __init__(self, *args, **kwargs):
        number = kwargs.pop('number', None)
        super().__init__(*args, **kwargs)
       
        self.fields['dankelkeg_prog'].widget.attrs.update({'class':'form-control'})
        self.fields['dankelkeg_nama'].widget.attrs.update({'class':'form-control','placeholder': 'Nama Kegiatan'})
        
        if number:
            self.initial['dankelkeg_prog'] = number
                
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class DankelSubForm(forms.ModelForm):
    
    class Meta:
        model = Dankelsub
        fields = '__all__'
       
    def __init__(self, *args, **kwargs):
        sub = kwargs.pop('sub', None)
        super().__init__(*args, **kwargs)
        self.fields['dankelsub_keg'].widget.attrs.update({'class':'form-control'})
        self.fields['dankelsub_nama'].widget.attrs.update({'class':'form-control','placeholder': 'Nama Sub Kegiatan'})
        
        if sub:
            self.initial['dankelsub_keg'] = sub
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance